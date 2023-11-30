from src.server.colormap.colormap import generate_distinguishable_colors


def test_generate_distinguishable_colors():
    colors = generate_distinguishable_colors(10)

    print(colors)


def test_generate_distinguishable_colors2():
    colors = generate_distinguishable_colors(100)

    for c in colors:
        print(f"color: {c};")

