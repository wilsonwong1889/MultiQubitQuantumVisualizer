import math

from quantum.complex_number import Complex, I, ONE, ZERO


def test_addition_and_subtraction():
    a, b = Complex(1, 2), Complex(3, -4)
    assert a.add(b) == Complex(4, -2)
    assert a.sub(b) == Complex(-2, 6)
    assert (a + b) == a.add(b)
    assert (a - b) == a.sub(b)


def test_multiplication_follows_i_squared_equals_minus_one():
    assert I.mul(I) == Complex(-1, 0)
    assert (Complex(1, 2) * Complex(3, 4)) == Complex(-5, 10)


def test_scalar_multiplication_from_both_sides():
    assert (2 * Complex(1, -1)) == Complex(2, -2)
    assert (Complex(1, -1) * 0.5) == Complex(0.5, -0.5)


def test_conjugate_and_magnitude():
    z = Complex(3, 4)
    assert z.conjugate() == Complex(3, -4)
    assert z.magnitude_squared() == 25
    assert z.magnitude() == 5
    assert math.isclose(I.phase(), math.pi / 2)


def test_conjugate_times_self_is_magnitude_squared():
    z = Complex(0.6, -0.8)
    product = z.conjugate().mul(z)
    assert math.isclose(product.real, z.magnitude_squared())
    assert math.isclose(product.imag, 0.0)


def test_helpers():
    assert ZERO.is_zero()
    assert not ONE.is_zero()
    assert Complex(1e-12, 0).is_close(ZERO)
    assert complex(Complex(1, 2)) == 1 + 2j
    assert Complex.from_builtin(1 - 1j) == Complex(1, -1)
