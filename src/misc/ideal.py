# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Draw the (inf, inf, inf) Hyperbolic Tiling in Poincaré's disk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import numpy as np
import cairocffi as cairo
from colorsys import hls_to_rgb


def hue(x):
    """
    Return a rgb color given x between [0, 1].
    """
    return hls_to_rgb(x, 0.7, 0.9)


def degree_to_angle(*args):
    return [x * np.pi / 180 for x in args]
    

def circle_to_matrix(z, r):
    """
    Inversion about a circle can be represented as a 2x2 complex matrix.
    This matrix is normalized to have determinat 1 to avoid floating errors.
    """
    return np.array([[z, r**2 - abs(z)**2],
                     [1, -z.conjugate()]], dtype=np.complex) / r


def matrix_to_circle(matrix):
    """Return the circle corresponding to this matrix."""
    center = matrix[0, 0] / matrix[1, 0]
    radius = abs(1 / matrix[1, 0].real)
    return center, radius


def reflect(circle, mirror):
    """
    The inversion of a circle about another circle (called the mirror) is also
    a circle. This function returns the matrix representing the resulting circle.
    """
    return np.dot(mirror, np.dot(circle.conjugate(), mirror))


def orthogonal_circle(alpha, beta):
    """
    alpha, beta: angles of two distinct points on the unit circle.
                 0 <= alpha, beta <= 2pi.
    return the matrix of the circle that passes through these 
    two points and is orthogonal to the unit circle.
    """
    z = complex(np.cos(alpha), np.sin(alpha))
    w = complex(np.cos(beta), np.sin(beta))
    center = 2 * (z - w) / (z * w.conjugate() - w * z.conjugate())
    radius = np.sqrt(center * center.conjugate() - 1)
    return circle_to_matrix(center, radius)


def compute_all_circles(alpha, beta, gamma, depth):
    """
    Given three points on the unit circle (by their angles alpha, beta and gamma),
    reflect the circles about the three mirrors up to a given depth and return
    all resulting circles.    
    """
    mA = orthogonal_circle(alpha, beta)
    mB = orthogonal_circle(beta, gamma)
    mC = orthogonal_circle(gamma, alpha)
    circles = [["A", mA], ["B", mB], ["C", mC]]
    result = [circles]

    for i in range(depth):
        next_circles = []
        for last_mirror, circle in circles:
            if last_mirror == "A":
                next_circles += [["B", reflect(circle, mB)],
                                 ["C", reflect(circle, mC)]]
            if last_mirror == "B":
                next_circles += [["C", reflect(circle, mC)],
                                 ["A", reflect(circle, mA)]]
            if last_mirror == "C":
                next_circles += [["A", reflect(circle, mA)],
                                 ["B", reflect(circle, mB)]]

        circles = next_circles
        result.append(circles)

    return result
            

def main(verts, depth, size):
    size = 600
    bg_color = (1, 1, 1)
    arc_color = (0, 0 ,0)
    funda_domain_color = (0.5, 0.5, 0.5)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
    ctx = cairo.Context(surface)
    ctx.translate(size / 2.0, size / 2.0)
    ctx.scale(size / 2.0, -size / 2.0)
    ctx.set_source_rgb(*bg_color)
    ctx.paint()

    ctx.set_line_width(0.01)
    ctx.set_source_rgb(*arc_color)
    ctx.arc(0, 0, 1, 0, 2*np.pi)
    ctx.stroke_preserve()
    ctx.set_source_rgb(0.5, 0.5, 0.5)
    ctx.fill_preserve()
    ctx.clip()

    alpha, beta, gamma = verts
    circles = compute_all_circles(alpha, beta, gamma, depth)
    for i in range(depth + 1):
        for _, circ in circles[i]:
            z, r = matrix_to_circle(circ)
            ctx.arc(z.real, z.imag, r, 0, 2*np.pi)
            ctx.set_source_rgb(*hue(float(i) / (depth + 1)))
            ctx.fill_preserve()
            ctx.set_source_rgb(*arc_color)
            ctx.set_line_width((i + 2) * 0.005 / (i + 1))
            ctx.stroke()

    surface.write_to_png("ideal_tiling.png")


if __name__ == "__main__":
    main(# use three random points: verts=np.random.random(3) * 2 * np.pi,
         verts=degree_to_angle(90, 210, 330),
         depth=8,
         size=600)