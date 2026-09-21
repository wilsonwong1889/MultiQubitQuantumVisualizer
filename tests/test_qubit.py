import itertools
import math

import pytest

from quantum.complex_number import Complex
from quantum.gates import GATES, H, X, Y, Z
from quantum.state import (
    INITIAL_STATES,
    QubitState,
    apply_gate,
    ket0,
    ket1,
    ket_minus,
    ket_minus_i,
    ket_plus,
    ket_plus_i,
    simulate,
)


def test_x_is_a_bit_flip():
    assert apply_gate(ket0(), X).is_close(ket1())
    assert apply_gate(ket1(), X).is_close(ket0())


def test_h_creates_superposition():
    assert apply_gate(ket0(), H).is_close(ket_plus())
    assert apply_gate(ket1(), H).is_close(ket_minus())


def test_z_is_a_phase_flip():
    assert apply_gate(ket_plus(), Z).is_close(ket_minus())
    assert apply_gate(ket0(), Z).is_close(ket0())


def test_y_maps_0_to_i_1():
    out = apply_gate(ket0(), Y)
    assert out.is_close(QubitState(Complex(0, 0), Complex(0, 1)))


def test_h_twice_returns_to_start():
    for start in INITIAL_STATES.values():
        assert apply_gate(apply_gate(start, H), H).is_close(start)


def test_worked_example_from_the_plan():
    # |0> - H - Z - X  gives  |0>, |+>, |->, -|->
    states = simulate(ket0(), [H, Z, X])
    assert len(states) == 4
    assert states[0].is_close(ket0())
    assert states[1].is_close(ket_plus())
    assert states[2].is_close(ket_minus())
    minus_minus = QubitState(-ket_minus().alpha, -ket_minus().beta)
    assert states[3].is_close(minus_minus)
    # ... and the last step changed only a global phase.
    phase = states[3].global_phase_relative_to(ket_minus())
    assert phase is not None and phase.is_close(Complex(-1, 0))


def test_probabilities_follow_the_born_rule():
    p0, p1 = ket_plus().probabilities()
    assert math.isclose(p0, 0.5) and math.isclose(p1, 0.5)
    assert ket1().probabilities() == (0.0, 1.0)


@pytest.mark.parametrize("start", list(INITIAL_STATES.values()) + [ket_plus_i(), ket_minus_i()])
@pytest.mark.parametrize("sequence", list(itertools.product("HXYZ", repeat=3)))
def test_normalisation_is_preserved_by_every_gate_sequence(start, sequence):
    for state in simulate(start, [GATES[s] for s in sequence]):
        assert state.is_normalized(1e-12)


def test_global_phase_detection():
    assert ket_minus().equals_up_to_global_phase(QubitState(-ket_minus().alpha, -ket_minus().beta))
    assert not ket_plus().equals_up_to_global_phase(ket_minus())
    i_ket1 = QubitState(Complex(0, 0), Complex(0, 1))
    assert i_ket1.global_phase_relative_to(ket1()).is_close(Complex(0, 1))
