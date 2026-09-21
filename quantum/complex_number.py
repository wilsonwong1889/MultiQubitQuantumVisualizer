"""Complex numbers for the quantum engine.

Python has a built-in ``complex`` type, but the project plan asks for the
arithmetic to be written out explicitly so that every operation a student sees
in the UI (addition, multiplication, conjugation, |z|^2) maps onto a small,
readable function here.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

TOLERANCE = 1e-9


@dataclass(frozen=True)
class Complex:
    real: float = 0.0
    imag: float = 0.0

    # --- constructors -----------------------------------------------------
    @classmethod
    def exp_i(cls, theta: float) -> Complex:
        """e^{i theta} = cos(theta) + i sin(theta)."""
        return cls(math.cos(theta), math.sin(theta))

    @classmethod
    def from_builtin(cls, z: complex) -> Complex:
        return cls(z.real, z.imag)

    # --- arithmetic -------------------------------------------------------
    def add(self, other: Complex) -> Complex:
        return Complex(self.real + other.real, self.imag + other.imag)

    def sub(self, other: Complex) -> Complex:
        return Complex(self.real - other.real, self.imag - other.imag)

    def mul(self, other: Complex) -> Complex:
        # (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        return Complex(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    def scale(self, factor: float) -> Complex:
        return Complex(self.real * factor, self.imag * factor)

    def neg(self) -> Complex:
        return Complex(-self.real, -self.imag)

    def conjugate(self) -> Complex:
        return Complex(self.real, -self.imag)

    def magnitude_squared(self) -> float:
        return self.real * self.real + self.imag * self.imag

    def magnitude(self) -> float:
        return math.sqrt(self.magnitude_squared())

    def phase(self) -> float:
        """Argument (angle) of the number in radians."""
        return math.atan2(self.imag, self.real)

    # --- comparisons ------------------------------------------------------
    def is_zero(self, tol: float = TOLERANCE) -> bool:
        return self.magnitude() < tol

    def is_close(self, other: Complex, tol: float = TOLERANCE) -> bool:
        return abs(self.real - other.real) < tol and abs(self.imag - other.imag) < tol

    # --- operator sugar so the engine code reads like maths ----------------
    def __add__(self, other: Complex) -> Complex:
        return self.add(other)

    def __sub__(self, other: Complex) -> Complex:
        return self.sub(other)

    def __mul__(self, other):
        if isinstance(other, Complex):
            return self.mul(other)
        return self.scale(float(other))

    __rmul__ = __mul__

    def __neg__(self) -> Complex:
        return self.neg()

    def __complex__(self) -> complex:
        return complex(self.real, self.imag)


ZERO = Complex(0.0, 0.0)
ONE = Complex(1.0, 0.0)
I = Complex(0.0, 1.0)
