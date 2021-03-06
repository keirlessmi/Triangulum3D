# Taken from http://nicky.vanforeest.com/misc/fitEllipse/fitEllipse.html

import numpy as np
import numpy.linalg as linalg

from triangulum.utils.shapes import Ellipse


def _fit_ellipse_a(x, y):
    x = x[:, np.newaxis]
    y = y[:, np.newaxis]
    D = np.hstack((x * x, x * y, y * y, x, y, np.ones_like(x)))
    S = np.dot(D.T, D)
    C = np.zeros([6, 6])
    C[0, 2] = C[2, 0] = 2
    C[1, 1] = -1
    E, V = linalg.eig(np.dot(linalg.inv(S), C))
    n = np.argmax(np.abs(E))
    a = V[:, n]
    return a


def _ellipse_center(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    num = b * b - a * c
    x0 = (c * d - b * f) / num
    y0 = (a * f - b * d) / num
    return np.array([x0, y0])


def _ellipse_angle_of_rotation(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    return 0.5 * np.arctan(2 * b / (a - c))


def _ellipse_axis_length(a):
    b, c, d, f, g, a = a[1] / 2, a[2], a[3] / 2, a[4] / 2, a[5], a[0]
    up = 2 * (a * f * f + c * d * d + g * b * b - 2 * b * d * f - a * c * g)
    down1 = (b * b - a * c) * ((c - a) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    down2 = (b * b - a * c) * ((a - c) * np.sqrt(1 + 4 * b * b / ((a - c) * (a - c))) - (c + a))
    res1 = np.sqrt(up / down1)
    res2 = np.sqrt(up / down2)
    return np.array([res1, res2])


def _deprecated_fit_ellipse(xys):
    assert len(xys) >= 5
    xys = np.float64(xys)
    x, y = xys[:, 0], xys[:, 1]
    x_mean = x.mean()
    y_mean = y.mean()
    x -= x_mean
    y -= y_mean
    a = _fit_ellipse_a(x, y)
    center = _ellipse_center(a)
    center[0] += x_mean
    center[1] += y_mean
    phi = _ellipse_angle_of_rotation(a)
    axes = _ellipse_axis_length(a)
    x += x_mean
    y += y_mean
    ellipse = Ellipse(center[0], center[1], axes[0], axes[1], np.rad2deg(phi))
    if np.any(np.isnan(np.float32(ellipse))):
        return None
    else:
        return ellipse


import b2ac.preprocess
import b2ac.fit
import b2ac.conversion


def fit_ellipse(xys):
    xys, x_mean, y_mean = b2ac.preprocess.remove_mean_values(xys)

    conic = b2ac.fit.fit_improved_B2AC_double(xys)

    general_form = b2ac.conversion.conic_to_general_1(conic)
    general_form[0][0] += x_mean
    general_form[0][1] += y_mean

    ellipse = Ellipse(general_form[0][0], general_form[0][1], general_form[1][0], general_form[1][1], np.rad2deg(general_form[2]))
    if ellipse.a < ellipse.b:
        ellipse = Ellipse(ellipse.x, ellipse.y, ellipse.b, ellipse.a, ellipse.angle + 90)
    return ellipse
