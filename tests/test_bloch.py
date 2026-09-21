import itertools
import math

import pytest

from quantum.bloch import bloch_vector, length, rotate_about_axis, rotation_path
from quantum.gates import GATES, SINGLE_QUBIT_GATES
from quantum.state import (
    INITIAL_STATES,
    apply_gate,
    ket0,
    ket1,
    ket_minus,
    ket_minus_i,
    ket_plus,
    ket_plus_i,
    simulate,
)


def _close(a, b, tol=1e-9):
    return all(math.isclose(x, y, abs_tol=tol) for x, y in zip(a, b))


@pytest.mark.parametrize(
    "state, expected",
    [
        (ket0(), (0, 0, 1)),
        (ket1(), (0, 0, -1)),
        (ket_plus(), (1, 0, 0)),
        (ket_minus(), (-1, 0, 0)),
        (ket_plus_i(), (0, 1, 0)),
        (ket_minus_i(), (0, -1, 0)),
    ],
)
def test_named_states_sit_on_the_axes(state, expected):
    assert _close(bloch_vector(state), expected)


@pytest.mark.parametrize("start", INITIAL_STATES.values())
@pytest.mark.parametrize("sequence", list(itertools.product("HXYZST", repeat=3)))
def test_bloch_vector_stays_on_the_unit_sphere(start, sequence):
    for state in simulate(start, [GATES[s] for s in sequence]):
        assert math.isclose(length(bloch_vector(state)), 1.0, abs_tol=1e-9)


def test_global_phase_does_not_move_the_bloch_vector():
    # X|-> = -|->, which must land on the same point of the sphere.
    before = ket_minus()
    after = apply_gate(before, GATES["X"])
    assert _close(bloch_vector(before), bloch_vector(after))


@pytest.mark.parametrize("gate", [GATES[s] for s in SINGLE_QUBIT_GATES])
@pytest.mark.parametrize("start", [ket0(), ket1(), ket_plus(), ket_minus(), ket_plus_i(), ket_minus_i()])
def test_gate_rotation_axis_reproduces_the_amplitude_result(gate, start):
    # Rotating the Bloch vector about the gate's axis must give the same point
    # as multiplying the amplitudes by the gate matrix -- this is what makes
    # the animation trustworthy.
    geometric = rotate_about_axis(bloch_vector(start), gate.axis, gate.rotation)
    algebraic = bloch_vector(apply_gate(start, gate))
    assert _close(geometric, algebraic)


def test_rotation_path_endpoints_and_length():
    path = rotation_path((0, 0, 1), (1, 0, 0), math.pi, steps=10)
    assert len(path) == 11
    assert _close(path[0], (0, 0, 1))
    assert _close(path[-1], (0, 0, -1))
    for point in path:
        assert math.isclose(length(point), 1.0, abs_tol=1e-9)
