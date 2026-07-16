# Usage Guide — Line Shading

## 1. Prepare the Image
The image must be **embedded** in the SVG (not linked).

In Inkscape:
- Select the image
- Menu: `Extensions → Images → Embed Images`

## 2. Run the Extension
Menu:
`Extensions → Render → Line Shading`

## 3. Parameters

### Line spacing
Controls density. Lower values = more lines.

### Angles
Comma-separated list of directions:
Example:
    0,45,90,135

### Waveform
- sin: smooth shading
- sin_b: stronger contrast
- saw: linear ramps
- square: binary modulation

### Modulation
- period
- amplitude
- both

### Gamma
Controls luminance sensitivity.

### Line width
SVG stroke width.

## 4. Output
The extension creates a new layer named **Line Shading** containing all generated paths.

You can:
- change stroke color
- adjust stroke width
- export to PDF, PNG, or plotter
