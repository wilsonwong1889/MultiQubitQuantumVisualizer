"""Bloch-sphere geometry: amplitudes -> (x, y, z), and gate rotations."""
from __future__ import annotations

import math
from typing import List, Tuple

from .qubit import QubitState

Vec3 = Tuple[float, float, float]


def bloch_vector(state: QubitState) -> Vec3:
    """Bloch coordinates computed directly from the amplitudes.

        x = 2 Re(alpha* beta)
        y = 2 Im(alpha* beta)
        z = |alpha|^2 - |beta|^2
    """
    cross_term = state.alpha.conjugate().mul(state.beta)
    x = 2.0 * cross_term.real
    y = 2.0 * cross_term.imag
    z = state.alpha.magnitude_squared() - state.beta.magnitude_squared()
    return (x, y, z)


def length(v: Vec3) -> float:
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def normalize(v: Vec3) -> Vec3:
    n = length(v)
    if n == 0.0:
        return (0.0, 0.0, 0.0)
    return (v[0] / n, v[1] / n, v[2] / n)


def dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def rotate_about_axis(v: Vec3, axis: Vec3, angle: float) -> Vec3:
    """Rodrigues' rotation formula (right-hand rule about a unit axis).

    v_rot = v cos(t) + (k x v) sin(t) + k (k . v)(1 - cos(t))
    """
    k = normalize(axis)
    c, s = math.cos(angle), math.sin(angle)
    kxv = cross(k, v)
    kdv = dot(k, v)
    return tuple(v[i] * c + kxv[i] * s + k[i] * kdv * (1.0 - c) for i in range(3))  # type: ignore[return-value]


def rotation_path(start: Vec3, axis: Vec3, angle: float, steps: int = 30) -> List[Vec3]:
    """Points along the arc the Bloch arrow sweeps out while a gate is applied."""
    return [rotate_about_axis(start, axis, angle * k / steps) for k in range(steps + 1)]
