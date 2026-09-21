from quantum.complex_number import Complex, I, ONE, ZERO
from quantum.matrix import IDENTITY, Matrix2x2


def test_identity_leaves_vector_unchanged():
    v = (Complex(0.6, 0.1), Complex(-0.3, 0.7))
    out = IDENTITY.multiply_vector(v)
    assert out[0].is_close(v[0]) and out[1].is_close(v[1])


def test_matrix_vector_product_is_row_times_column():
    m = Matrix2x2(Complex(1), Complex(2), Complex(3), Complex(4))
    out = m.multiply_vector((Complex(5), Complex(6)))
    assert out == (Complex(17), Complex(39))


def test_matrix_product_and_conjugate_transpose():
    m = Matrix2x2(ONE, I, ZERO, ONE)
    dagger = m.conjugate_transpose()
    assert dagger == Matrix2x2(ONE, ZERO, -I, ONE)
    assert m.multiply(IDENTITY).is_close(m)
    assert m.multiply(dagger).is_close(Matrix2x2(Complex(2), I, -I, ONE))


def test_scale():
    m = Matrix2x2(ONE, ONE, ONE, -ONE).scale(0.5)
    assert m.a == Complex(0.5) and m.d == Complex(-0.5)


def test_is_unitary():
    assert IDENTITY.is_unitary()
    assert not Matrix2x2(ONE, ONE, ONE, ONE).is_unitary()
