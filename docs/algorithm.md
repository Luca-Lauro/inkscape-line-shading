# Algorithm Overview — Line Shading

Line Shading is a vector-based shading engine that converts an embedded raster image
into modulated line patterns. The algorithm is designed for artistic hatching,
cross‑hatching, plotter output, and stylized shading.

## 1. Luminance Extraction
The image is converted to gamma‑corrected luminance using:

    L = (0.21 R + 0.72 G + 0.07 B) / 255
    L = L^(1/gamma)

This produces a perceptually uniform grayscale matrix.

## 2. Rotated Sampling
For each direction (angle), the algorithm defines a rotated coordinate system:

    x' =  cos(a) * x + sin(a) * y
    y' = -sin(a) * x + cos(a) * y

Sampling is performed along x' while lines are distributed along y'.

## 3. Constant Density
Line spacing is constant in the direction perpendicular to the line orientation:

    N_lines = L_perp / spacing

This ensures uniform density across all directions.

## 4. Bilinear Interpolation
Luminance is sampled using bilinear interpolation to avoid aliasing:

    f(x,y) = weighted average of 4 surrounding pixels

A light smoothing filter reduces diagonal aliasing.

## 5. Modulation
Each line is modulated using:

- waveform: sin, sin_b, saw, square
- amplitude: based on luminance
- period: based on luminance

The modulation creates the shading effect.

## 6. Clipping
Lines are clipped using a buffer-based approach:

- segments outside the image are ignored
- segments inside are preserved
- direction is never lost

This ensures clean borders.

## 7. SVG Output
All lines are written as SVG paths with:

- round caps
- round joins
- configurable stroke width

The result is a clean, plotter-friendly vector shading.
