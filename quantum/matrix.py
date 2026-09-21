"""2x2 complex matrices and 2-component state vectors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .complex_number import Complex, ONE, TOLERANCE, ZERO

Vector2 = Tuple[Complex, Complex]


@dataclass(frozen=True)
class Matrix2x2:
    """Row-major 2x2 complex matrix [[a, b], [c, d]]."""

    a: Complex
    b: Complex
    c: Complex
    d: Complex

    @property
    def rows(self) -> Tuple[Tuple[Complex, Complex], Tuple[Complex, Complex]]:
        return ((self.a, self.b), (self.c, self.d))

    def multiply_vector(self, v: Vector2) -> Vector2:
        """Matrix-vector product M.v for a column vector v = [v0, v1]^T."""
        v0, v1 = v
        return (self.a * v0 + self.b * v1, self.c * v0 + self.d * v1)

    def multiply(self, other: Matrix2x2) -> Matrix2x2:
        """Matrix product self . other."""
        return Matrix2x2(
            self.a * other.a + self.b * other.c,
            self.a * other.b + self.b * other.d,
            self.c * other.a + self.d * other.c,
            self.c * other.b + self.d * other.d,
        )

    def scale(self, factor: float) -> Matrix2x2:
        return Matrix2x2(
            self.a.scale(factor), self.b.scale(factor),
            self.c.scale(factor), self.d.scale(factor),
        )

    def conjugate_transpose(self) -> Matrix2x2:
        return Matrix2x2(
            self.a.conjugate(), self.c.conjugate(),
            self.b.conjugate(), self.d.conjugate(),
        )

    def is_close(self, other: Matrix2x2, tol: float = TOLERANCE) -> bool:
        return (
            self.a.is_close(other.a, tol) and self.b.is_close(other.b, tol)
            and self.c.is_close(other.c, tol) and self.d.is_close(other.d, tol)
        )

    def is_unitary(self, tol: float = TOLERANCE) -> bool:
        """A gate is valid only if U . U^dagger = I (it preserves normalisation)."""
        return self.multiply(self.conjugate_transpose()).is_close(IDENTITY, tol)


IDENTITY = Matrix2x2(ONE, ZERO, ZERO, ONE)
