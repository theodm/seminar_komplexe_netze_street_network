import matplotlib

def colormap_for_range(upto: int, color_map="inferno"):
    cmap = matplotlib.cm.get_cmap(color_map)

    colors = []

    for i in range(upto):
        # Gibt die Farbe in folgendem Format zurück: (r, g, b, alpha)
        # z.B. (0.0, 0.0, 0.0, 1.0) für schwarz
        #      (1.0, 1.0, 1.0, 1.0) für weiß
        # color_in_floats_with_alpha = cmap((i**10) / (num_distinct_information**10))
        color_in_floats_with_alpha = cmap(i / upto)

        # Den Alpha-Wert entfernen
        color_in_floats = color_in_floats_with_alpha[:3]

        # Und dann einen hexadezimalen Wert
        # z.B. #000000 für schwarz
        #      #ffffff für weiß
        color_in_hex = matplotlib.colors.rgb2hex(color_in_floats)

        colors.append(color_in_hex)

    return colors

def colormap_for_float_range_fn(arr, color_map="inferno"):
    cmap = matplotlib.cm.get_cmap(color_map)

    _min = min(arr)
    _max = max(arr)

    def get_color_for_float(f):
        color_in_floats_with_alpha = cmap((f - _min) / (_max - _min))
        color_in_floats = color_in_floats_with_alpha[:3]
        color_in_hex = matplotlib.colors.rgb2hex(color_in_floats)
        return color_in_hex

    return get_color_for_float
