# Line Shading Inkscape Extension
Line Shading is an advanced extension for Inkscape that generates vector shading using modulated lines, with support for:

- Multi-direction cross-hatching
- Constant density
- Rotated sampling
- Period and amplitude modulation
- Sin, saw, square, sin_b waveform
- Robust clipping
- Shading consistent with image luminance
- Perfect output for plotters, CNC, laser, and pen plotters

## Key Features
Constant density: Lines maintain the same distance in all directions.

True cross-hatching: Specify angles such as 0, 45, 90, or 135 for multiple line directions.

Bilinear sampling: Luminance is precisely interpolated.

Advanced modulation: Period and amplitude vary based on luminance.

Smart clipping: Lines do not extend beyond the image edges.

Multiple waveforms: sin, sin_b, saw, square.

Pure vector output: perfect for plotters and lasers.

## Examples

![alt text](https://github.com/Luca-Lauro/inkscape-line-shading/blob/main/examples/sphere.png "sphere")

![alt text](https://github.com/Luca-Lauro/inkscape-line-shading/blob/main/examples/multi-direction.png "multi-direction")

## Installation
Copy line-shading folder with its content to the Inkscape extensions folder:

- Linux

`
~/.config/inkscape/extensions/
`

- Windows

`
C:\Users\<user>\AppData\Roaming\Inkscape\extensions\
`

- macOS

`
/Users/<user>/Library/Application Support/org.inkscape.Inkscape/config/inkscape/extensions/
`

Restart Inkscape.

## Usage
Select an embedded image.

Open:
Extensions → Render → Line Shading

Set:

Line spacing

Angles (e.g., 0, 45, 90, 135)

Waveform

Modulation

Press Apply.

## Parameters
| Parameter | Description |
| --------- | ----------- |
| Line spacing | Distance between lines (constant density) |
| Angles | Cross-hatching directions |
| Waveform | Modulation waveform |
| Modulation | Period, amplitude, or both |
| Gamma | Luminance correction |
| Line width | Line thickness |

## Algorithm
The algorithm performs:

Image conversion to gamma-corrected luminance

Rotated bilinear sampling

Sinusoidal modulation (sin, sin_b, saw, square)

Constant density fill perpendicular to direction

Buffer-based clipping

SVG vector output
