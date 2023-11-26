import math


# von Stackoverflow geklaut :O
# Adresse leider vergessen :-(
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       return None

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y


def parallel_line(g, h, dist_add):
    '''
    Erstellt eine parallele Linie zu der Linie, die durch die Punkte g und h geht.
    Die neue Linie ist dist_add von der alten Linie entfernt.
    '''
    line_vector = (h[0] - g[0], h[1] - g[1])

    angle_from_g = math.atan2(line_vector[0], line_vector[1])

    if angle_from_g < 0:
        angle_from_g += math.radians(360)

    if angle_from_g > math.radians(270) :
        return (g[0] - dist_add, g[1] - dist_add), (h[0] - dist_add, h[1] - dist_add)
    elif angle_from_g > math.radians(180):
        return (g[0] + dist_add, g[1] - dist_add), (h[0] + dist_add, h[1] - dist_add)
    elif angle_from_g > math.radians(90):
        return (g[0] + dist_add, g[1] + dist_add), (h[0] + dist_add, h[1] + dist_add)
    else:
        return (g[0] - dist_add, g[1] + dist_add), (h[0] - dist_add, h[1] + dist_add)

def orthogonal_line(g, h, t):
    '''
    Erstellt eine Linie, die orthogonal zu der Linie, die durch die Punkte g und h geht.
    Die neue Linie geht durch den Punkt t.
    '''
    vec = (h[0] - g[0], h[1] - g[1])

    return (t[0], t[1]), (t[0] - vec[1], t[1] + vec[0])

def redo_geometry(geometry: list[tuple[float, float]], dist):
    '''
    Erstellt eine neue Menge von Punkten, wobei die Zwischenpunkte so verschoben werden,
    dass die neue Linie parallel zur alten Linie ist und einen Abstand von dist hat. Damit lassen
    sich die Kanten des DiGraphen aufteilen und damit besser erkennen. osmnx mappt beide Kanten
    auf die gleichen Positionen, was die Visualisierung erschwert.
    '''

    # Code könnte wahrscheinlich noch deutlich optimeirt werden
    new_geometry = []

    dist_add = math.sqrt((dist ** 2) / 2)

    if len(geometry) == 2:
        a = geometry[0]
        b = geometry[1]

        parallel_line_a_b = parallel_line(a, b, dist_add)
        
        line_from_a = orthogonal_line(a, b, a)

        np = line_intersection(parallel_line_a_b, line_from_a)

        new_geometry.append(a)
        new_geometry.append(np)

        line_from_b = orthogonal_line(a, b, b)
    
        np = line_intersection(parallel_line_a_b, line_from_b)
        new_geometry.append(np)
        new_geometry.append(b)


    for i in range(len(geometry) - 2):
        a = geometry[i]
        b = geometry[i + 1]

        parallel_line_a_b = parallel_line(a, b, dist_add)

        if i == 0:
            line_from_a = orthogonal_line(a, b, a)

            np = line_intersection(parallel_line_a_b, line_from_a)

            new_geometry.append(a)
            new_geometry.append(np)

        c = geometry[i + 2]

        parallel_line_b_c = parallel_line(
            b,
            c,
            dist_add
        )

        new_b = line_intersection(parallel_line_a_b, parallel_line_b_c)
        if new_b is not None:
            new_geometry.append(new_b)

        if i == len(geometry) - 3:
            c = geometry[i + 2]

            line_from_c = orthogonal_line(b, c, c)

            np = line_intersection(parallel_line_b_c, line_from_c)
            new_geometry.append(np)
            new_geometry.append(c)

    return new_geometry

def show_geometry(original, new):
    '''
    Kleiner Helfer, um die Geometrie zu visualisieren.
    '''
    # draw with matplotlib
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots()

    ax.plot(np.array(original)[:, 0], np.array(original)[:, 1], 'o-')

    ax.plot(np.array(new)[:, 0], np.array(new)[:, 1], 'o-')
    plt.show()

# Ein paar Testfälle. Einfach einkommentieren und ausführen.
#
# geometry = [
#     (0, 0),
#     (0, 5),
#     (5, 5),
#     (5, 0),
# ]
#
# geometry.reverse()
#
# show_geometry(
#     geometry,
#     redo_geometry(geometry)
# )
#
#
# geometry = [
#     (5, 0),
#     (5, 5),
#     (0, 5),
#     (0, 0),
# ]
#
# show_geometry(
#     geometry,
#     redo_geometry(geometry)
# )

# diamond geometry
# geometry = [
#     (2, 1),
#     (1, 2),
#     (1, 3),
#     (2, 4),
#     (3, 3),
#     (3, 2),
# ]
#
# geometry.reverse()
#
# show_geometry(
#     geometry,
#     redo_geometry(geometry)
# )

#long diamond

# geometry = [
#     (2, 1),
#     (1, 2),
#     (1, 2.5),
#     (1, 3),
#     (2, 4),
#     (3, 3),
#     (3, 2.5),
#     (3, 2),
# ]
#
# show_geometry(
#     geometry,
#     redo_geometry(geometry)
# )

# only 2 points
# geometry = [
#     (1, 1),
#     (2, 2),
#
# ]
# show_geometry(
#     geometry,
#     redo_geometry(geometry, dist=0.1)
# )