#!/usr/bin/env python3
import math
import base64
from io import BytesIO

import inkex
from inkex import PathElement, EffectExtension
from PIL import Image


def sin_b(x):
    s = math.sin(x)
    return math.copysign(abs(s)**3, s)


def saw(x):
    x = math.fmod(x, 4.0)
    x = abs(x)
    return 3 - x if x > 2.0 else x - 1


def square(x):
    x = math.fmod(x, 4.0)
    return 1.0 if 1.0 < x < 3.0 else -1.0


def bilinear_sample(matrix, w, h, x, y):
    if x < 0: x = 0
    if y < 0: y = 0
    if x > w - 1: x = w - 1
    if y > h - 1: y = h - 1

    x0 = int(math.floor(x))
    x1 = min(x0 + 1, w - 1)
    y0 = int(math.floor(y))
    y1 = min(y0 + 1, h - 1)

    dx = x - x0
    dy = y - y0

    v00 = matrix[y0][x0]
    v10 = matrix[y0][x1]
    v01 = matrix[y1][x0]
    v11 = matrix[y1][x1]

    return (
        v00 * (1 - dx) * (1 - dy) +
        v10 * dx       * (1 - dy) +
        v01 * (1 - dx) * dy       +
        v11 * dx       * dy
    )


class LineShading(EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--waveform", type=str, default="sin")

        # densità costante → distanziamento tra linee
        pars.add_argument("--line_spacing", type=float, default=3.0)

        pars.add_argument("--min_period", type=float, default=2.0)
        pars.add_argument("--max_period", type=float, default=10.0)
        pars.add_argument("--min_amplitude", type=float, default=0.2)
        pars.add_argument("--max_amplitude", type=float, default=3.0)
        pars.add_argument("--gamma", type=float, default=1.0)
        pars.add_argument("--line_width", type=float, default=0.3)
        pars.add_argument("--units", type=str, default="px")
        pars.add_argument("--remove", type=bool, default=False)

        pars.add_argument("--modulation", type=str, default="both")
        pars.add_argument("--angles", type=str, default="0")

    def read_embedded_image(self, node):
        href = node.get('{http://www.w3.org/1999/xlink}href')
        if href is None:
            href = node.get('href')

        if href is None or not href.startswith("data:image"):
            raise Exception("Image is not embedded (no base64 href). Please embed the image first.")

        header, b64data = href.split(",", 1)
        raw = base64.b64decode(b64data)

        img = Image.open(BytesIO(raw)).convert("RGB")
        w, h = img.size
        pixels = img.load()
        return w, h, pixels

    def build_matrix(self, w, h, pixels):
        gamma = self.options.gamma
        matrix = [[1.0 for _ in range(w)] for _ in range(h)]

        for y in range(h):
            for x in range(w):
                r, g, b = pixels[x, y]
                p = 1.0 - (r * 0.21 + g * 0.72 + b * 0.07) / 255.0
                matrix[y][x] = math.pow(p, 1.0 / gamma)

        return matrix

    def drawfunction(self, image_w, image_h, node, angle_deg):
        w, h, pixels = self.read_embedded_image(node)
        matrix = self.build_matrix(w, h, pixels)

        a = math.radians(angle_deg)
        ca = math.cos(a)
        sa = math.sin(a)

        cx = image_w / 2.0
        cy = image_h / 2.0

        points = []

        # constant density
        base_spacing = float(self.options.line_spacing)

        # lenght along direction
        L_dir = abs(image_w * ca) + abs(image_h * sa)

        # lenght perpendicular to direction
        L_perp = abs(image_w * sa) + abs(image_h * ca)

        # number of lines
        num = max(1, int(L_perp / base_spacing))
        step_perp = L_perp / num

        # sample resolution along direction
        pixel_size = min(image_w / w, image_h / h)
        N_samples = max(2, int(L_dir / pixel_size))
        step_dir = L_dir / (N_samples - 1)

        sx = w / image_w
        sy = h / image_h

        min_amp = self.options.min_amplitude * base_spacing / 2
        max_amp = self.options.max_amplitude * base_spacing / 2
        min_period = self.options.min_period * base_spacing
        max_period = self.options.max_period * base_spacing

        for i in range(num):
            y_perp = -L_perp / 2 + (i + 0.5) * step_perp

            inside = False  # clipping buffer

            for k in range(N_samples):
                x_dir = -L_dir / 2 + k * step_dir

                # base point
                Xb = cx + ca * x_dir - sa * y_perp
                Yb = cy + sa * x_dir + ca * y_perp

                # sampling
                lum = bilinear_sample(matrix, w, h, Xb * sx, Yb * sy)

                # light luminance smoothing
                if k == 0:
                    prev_lum = lum
                else:
                    lum = (lum + prev_lum) * 0.5
                    prev_lum = lum

                # PERIOD modulation
                if self.options.modulation in ("both", "period"):
                    period = min_period + (max_period - min_period) * (1 - lum)
                else:
                    period = (min_period + max_period) / 2.0

                d_phase = 2 * math.pi / period * step_dir

                # AMPLITUDE modulation
                if self.options.modulation in ("both", "amplitude"):
                    amp_step = min_amp + (max_amp - min_amp) * lum
                else:
                    amp_step = (min_amp + max_amp) / 2.0

                # waveform
                if self.options.waveform == "sin":
                    mod = math.sin(d_phase * k)
                elif self.options.waveform == "saw":
                    mod = saw(d_phase * k)
                elif self.options.waveform == "square":
                    mod = square(d_phase * k)
                elif self.options.waveform == "sin_b":
                    mod = sin_b(d_phase * k)
                else:
                    mod = math.sin(d_phase * k)

                # light damping
                mod *= 0.9

                # final modulation
                y_perp_mod = y_perp + amp_step * mod

                X = cx + ca * x_dir - sa * y_perp_mod
                Y = cy + sa * x_dir + ca * y_perp_mod

                # buffer-based clipping
                if 0 <= X <= image_w and 0 <= Y <= image_h:
                    if not inside:
                        points.append(["M", [X, Y]])
                        inside = True
                    else:
                        points.append(["L", [X, Y]])
                else:
                    inside = False

        return points

    def create_path(self, points, node):
        path = PathElement()
        path.style = {
            "stroke": "#000",
            "fill": "none",
            "stroke-width": str(self.svg.unittouu(str(self.options.line_width) + self.options.units)),
            "stroke-linejoin": "round",
            "stroke-linecap": "round"
        }

        d = []
        for cmd, vals in points:
            if cmd == "M":
                d.append(f"M {vals[0]},{vals[1]}")
            elif cmd == "L":
                d.append(f"L {vals[0]},{vals[1]}")

        path.set("d", " ".join(d))

        x = float(node.get("x") or 0)
        y = float(node.get("y") or 0)
        path.set("transform", f"translate({x},{y})")

        return path

    def draw_paths_multi_direction(self, node):
        def parse_length(v):
            if v is None:
                raise Exception("Image has no width/height")
            try:
                return float(v)
            except ValueError:
                for suf in ("px", "mm", "cm", "in"):
                    if v.endswith(suf):
                        return float(v[:-len(suf)])
                raise

        image_w = parse_length(node.get("width"))
        image_h = parse_length(node.get("height"))

        new_layer = inkex.Group()
        new_layer.set(inkex.addNS('label', 'inkscape'), 'Line Shading')
        self.svg.get_current_layer().add(new_layer)

        try:
            angles = [float(a.strip()) for a in self.options.angles.split(",") if a.strip() != ""]
        except Exception:
            angles = [0.0]

        if not angles:
            angles = [0.0]

        for angle in angles:
            points = self.drawfunction(image_w, image_h, node, angle)
            path = self.create_path(points, node)
            new_layer.add(path)

    def effect(self):
        selected = list(self.svg.selected.values())
        if not selected:
            inkex.utils.debug("Please select an image")
            return

        image_node = None
        for node in selected:
            if node.tag.endswith("image"):
                image_node = node
                break

        if image_node is None:
            inkex.utils.debug("Please select an embedded image")
            return

        try:
            self.draw_paths_multi_direction(image_node)
        except Exception as e:
            inkex.utils.debug(f"Error: {e}")

        if self.options.remove:
            image_node.getparent().remove(image_node)


if __name__ == "__main__":
    LineShading().run()
