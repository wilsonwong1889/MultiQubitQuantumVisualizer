"""Multi-qubit register tests: tensor products, targets, entanglement, reduced states."""
import math

import pytest

from quantum.complex_number import Complex, ONE, ZERO
from quantum.gates import CNOT, CZ, H, S, SWAP, T, X, Z
from quantum.matrix import IDENTITY
from quantum.state import (
    QuantumState,
    apply_gate,
    basis_state,
    full_operator,
    ket0,
    ket1,
    ket_plus,
    ket_plus_i,
    tensor,
)


def _bell():
    return apply_gate(apply_gate(basis_state("00"), H, (0,)), CNOT, (0, 1))


def test_basis_labels_and_bit_order():
    state = basis_state("01")
    assert state.num_qubits == 2
    assert state.basis_labels() == ["00", "01", "10", "11"]
    assert state.amplitude_of("01") == ONE
    assert state.bit(int("01", 2), 0) == 0 and state.bit(int("01", 2), 1) == 1


def test_tensor_product_orders_qubit_zero_first():
    state = tensor(ket1(), ket0())            # |1> (x) |0> = |10>
    assert state.is_close(basis_state("10"))
    assert tensor(ket_plus(), ket0()).probability_of("00") == pytest.approx(0.5)


def test_single_qubit_gate_on_a_chosen_target():
    assert apply_gate(basis_state("00"), X, (1,)).is_close(basis_state("01"))
    assert apply_gate(basis_state("00"), X, (0,)).is_close(basis_state("10"))


def test_full_operator_matches_kronecker_products():
    assert full_operator(H, (0,), 2).is_close(H.matrix.tensor(IDENTITY))
    assert full_operator(H, (1,), 2).is_close(IDENTITY.tensor(H.matrix))
    assert full_operator(CNOT, (0, 1), 2).is_close(CNOT.matrix)


def test_cnot_flips_target_only_when_control_is_one():
    assert apply_gate(basis_state("10"), CNOT, (0, 1)).is_close(basis_state("11"))
    assert apply_gate(basis_state("01"), CNOT, (0, 1)).is_close(basis_state("01"))
    # reversed control/target
    assert apply_gate(basis_state("01"), CNOT, (1, 0)).is_close(basis_state("11"))


def test_cz_and_swap():
    assert apply_gate(basis_state("11"), CZ, (0, 1)).is_close(QuantumState((ZERO, ZERO, ZERO, -ONE)))
    assert apply_gate(basis_state("01"), SWAP, (0, 1)).is_close(basis_state("10"))


def test_bell_state_from_h_and_cnot():
    bell = _bell()
    expected = QuantumState((Complex(1 / math.sqrt(2)), ZERO, ZERO, Complex(1 / math.sqrt(2))))
    assert bell.is_close(expected)
    assert bell.is_normalized()


def test_entangled_qubits_have_no_bloch_arrow_of_their_own():
    bell = _bell()
    for qubit in (0, 1):
        assert bell.purity(qubit) == pytest.approx(0.5)
        assert not bell.is_pure_on(qubit)
    product = tensor(ket_plus(), ket1())
    for qubit in (0, 1):
        assert product.purity(qubit) == pytest.approx(1.0)
        assert product.is_pure_on(qubit)


def test_reduced_density_matrix_of_product_state_is_the_single_qubit_projector():
    state = tensor(ket_plus_i(), ket0())
    rho = state.reduced_density_matrix(0)
    expected = ket_plus_i()
    for a in (0, 1):
        for b in (0, 1):
            assert rho.rows[a][b].is_close(expected.amplitudes[a] * expected.amplitudes[b].conjugate())


def test_phase_gates():
    assert apply_gate(ket_plus(), S).is_close(ket_plus_i())
    assert apply_gate(apply_gate(ket_plus(), T), T).is_close(ket_plus_i())   # T^2 = S


def test_three_qubit_register():
    ghz = basis_state("000")
    ghz = apply_gate(ghz, H, (0,))
    ghz = apply_gate(ghz, CNOT, (0, 1))
    ghz = apply_gate(ghz, CNOT, (1, 2))
    assert ghz.probability_of("000") == pytest.approx(0.5)
    assert ghz.probability_of("111") == pytest.approx(0.5)
    assert ghz.num_qubits == 3 and ghz.is_normalized()


def test_target_validation():
    with pytest.raises(ValueError):
        apply_gate(basis_state("00"), CNOT, (0, 0))
    with pytest.raises(ValueError):
        apply_gate(basis_state("00"), X, (2,))
    with pytest.raises(ValueError):
        apply_gate(ket0(), CNOT)
    with pytest.raises(AttributeError):
        _ = basis_state("00").alpha
