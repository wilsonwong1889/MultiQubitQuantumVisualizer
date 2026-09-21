"""Square complex matrices (2x2 for single-qubit gates, 4x4 for two-qubit ...)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence, Tuple

from .complex_number import Complex, ONE, TOLERANCE, ZERO

Vector = Tuple[Complex, ...]


@dataclass(frozen=True)
class Matrix:
    """Row-major square matrix of Complex entries."""

    rows: Tuple[Tuple[Complex, ...], ...]

    def __post_init__(self) -> None:
        rows = tuple(tuple(row) for row in self.rows)
        if not rows or any(len(row) != len(rows) for row in rows):
            raise ValueError("Matrix must be square and non-empty")
        object.__setattr__(self, "rows", rows)

    # --- shape ------------------------------------------------------------
    @property
    def size(self) -> int:
        return len(self.rows)

    @property
    def num_qubits(self) -> int:
        """How many qubits a gate with this matrix acts on (size = 2**n)."""
        n = self.size.bit_length() - 1
        if 2 ** n != self.size:
            raise ValueError("Matrix size is not a power of two")
        return n

    def entry(self, i: int, j: int) -> Complex:
        return self.rows[i][j]

    # --- algebra ----------------------------------------------------------
    def multiply_vector(self, v: Sequence[Complex]) -> Vector:
        """Matrix-vector product M.v for a column vector v."""
        if len(v) != self.size:
            raise ValueError(f"Vector of length {len(v)} does not match {self.size}x{self.size} matrix")
        out = []
        for row in self.rows:
            acc = ZERO
            for m, x in zip(row, v):
                acc = acc + m * x
            out.append(acc)
        return tuple(out)

    def multiply(self, other: Matrix) -> Matrix:
        """Matrix product self . other."""
        if other.size != self.size:
            raise ValueError("Matrix sizes do not match")
        n = self.size
        rows = []
        for i in range(n):
            row = []
            for j in range(n):
                acc = ZERO
                for k in range(n):
                    acc = acc + self.rows[i][k] * other.rows[k][j]
                row.append(acc)
            rows.append(tuple(row))
        return Matrix(tuple(rows))

    def scale(self, factor: float) -> Matrix:
        return Matrix(tuple(tuple(m.scale(factor) for m in row) for row in self.rows))

    def conjugate_transpose(self) -> Matrix:
        n = self.size
        return Matrix(tuple(tuple(self.rows[j][i].conjugate() for j in range(n)) for i in range(n)))

    def tensor(self, other: Matrix) -> Matrix:
        """Kronecker product self (x) other -- how gates on different qubits combine."""
        rows = []
        for a_row in self.rows:
            for b_row in other.rows:
                rows.append(tuple(a * b for a in a_row for b in b_row))
        return Matrix(tuple(rows))

    # --- comparisons ------------------------------------------------------
    def is_close(self, other: Matrix, tol: float = TOLERANCE) -> bool:
        return self.size == other.size and all(
            a.is_close(b, tol) for ra, rb in zip(self.rows, other.rows) for a, b in zip(ra, rb)
        )

    def is_unitary(self, tol: float = TOLERANCE) -> bool:
        """A gate is valid only if U . U^dagger = I (it preserves normalisation)."""
        return self.multiply(self.conjugate_transpose()).is_close(Matrix.identity(self.size), tol)

    @staticmethod
    def identity(size: int) -> Matrix:
        return Matrix(tuple(tuple(ONE if i == j else ZERO for j in range(size)) for i in range(size)))


def Matrix2x2(a: Complex, b: Complex, c: Complex, d: Complex) -> Matrix:  # noqa: N802 - reads like a type
    """Convenience constructor for [[a, b], [c, d]]."""
    return Matrix(((a, b), (c, d)))


IDENTITY = Matrix.identity(2)
