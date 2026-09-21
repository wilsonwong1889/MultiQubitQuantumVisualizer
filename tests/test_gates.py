import math

import pytest

from quantum.gates import (
    CNOT, CZ, GATE_ORDER, GATES, H, S, SINGLE_QUBIT_GATES, SWAP, T, TWO_QUBIT_GATES, X, Y, Z,
    controlled, get_gate,
)
from quantum.matrix import IDENTITY, Matrix


@pytest.mark.parametrize("gate", list(GATES.values()))
def test_every_gate_is_unitary(gate):
    assert gate.matrix.is_unitary()


@pytest.mark.parametrize("gate", [X, Y, Z, H, CNOT, CZ, SWAP])
def test_self_inverse_gates_square_to_identity(gate):
    # X^2 = Y^2 = Z^2 = H^2 = CNOT^2 = CZ^2 = SWAP^2 = I
    assert gate.matrix.multiply(gate.matrix).is_close(Matrix.identity(gate.matrix.size))


def test_phase_gate_square_roots():
    assert S.matrix.multiply(S.matrix).is_close(Z.matrix)   # S^2 = Z
    assert T.matrix.multiply(T.matrix).is_close(S.matrix)   # T^2 = S


def test_display_factorisation_matches_real_matrix():
    for gate in GATES.values():
        shown = gate.shown_matrix.scale(gate.display_scale)
        assert shown.is_close(gate.matrix)


def test_single_qubit_gates_are_bloch_rotations_about_unit_axes():
    for symbol in SINGLE_QUBIT_GATES:
        gate = GATES[symbol]
        assert gate.arity == 1 and gate.is_rotation
        assert math.isclose(sum(c * c for c in gate.axis), 1.0, abs_tol=1e-12)
    assert math.isclose(H.rotation, math.pi)
    assert math.isclose(S.rotation, math.pi / 2)
    assert math.isclose(T.rotation, math.pi / 4)


def test_two_qubit_gates_have_arity_two():
    for symbol in TWO_QUBIT_GATES:
        assert GATES[symbol].arity == 2 and GATES[symbol].matrix.size == 4


def test_controlled_builds_block_diagonal_matrix():
    cx = controlled(X, name="c", symbol="c", description="", color="#000")
    assert cx.matrix.is_close(CNOT.matrix)
    assert cx.arity == 2
    # top-left block is the identity, bottom-right block is X
    assert cx.matrix.rows[0][0].real == 1 and cx.matrix.rows[2][3].real == 1


def test_gate_lookup():
    assert [get_gate(s).symbol for s in GATE_ORDER] == ["H", "X", "Y", "Z", "S", "T", "CNOT", "CZ", "SWAP"]
    with pytest.raises(KeyError):
        get_gate("TOFFOLI")
