import vtracer

input_png = "PrimaryLogo.png"
output_svg = "PrimaryLogo.svg"

vtracer.convert_image_to_svg_py(
    input_png,
    output_svg,
    colormode="binary",
    hierarchical="stacked",
    mode="spline",
    filter_speckle=4,
    color_precision=6,
    layer_difference=16,
    corner_threshold=60,
    length_threshold=4,
    max_iterations=10,
    splice_threshold=45,
    path_precision=3
)

print("SVG created:", output_svg)
