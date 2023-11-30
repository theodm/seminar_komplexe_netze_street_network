import random

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

import colorsys
from math import sqrt, fmod
def generate_distinguishable_colors(num_needed: int):
    if num_needed < 10:
        num = 10
    else:
        num = num_needed

    colors = []

    gr = (0.618033988749895 * 10) / num
    for i in range(num):
        # https://gamedev.stackexchange.com/questions/46463/how-can-i-find-an-optimum-set-of-colors-for-10-players
        colors.append(matplotlib.colors.rgb2hex(colorsys.hsv_to_rgb(
            fmod(i * gr, 1.0),
            0.5,
            sqrt(1.0 - fmod(i * gr, 0.5))
        )))

    # shuffle
    random.shuffle(colors)

    return colors
