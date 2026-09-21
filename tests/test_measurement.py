import pytest

from quantum.gates import CNOT, H
from quantum.measurement import collapse, measure_once, measure_qubit, sample
from quantum.state import apply_gate, basis_state, ket0, ket1, ket_plus


def _bell():
    return apply_gate(apply_gate(basis_state("00"), H, (0,)), CNOT, (0, 1))


def test_sampling_follows_the_born_rule():
    counts = sample(ket_plus(), 20000, seed=7)
    assert set(counts) == {"0", "1"}
    assert sum(counts.values()) == 20000
    assert abs(counts["0"] / 20000 - 0.5) < 0.02


def test_sampling_a_definite_state_is_deterministic():
    assert sample(ket1(), 50, seed=1) == {"0": 0, "1": 50}


def test_bell_state_only_ever_gives_correlated_outcomes():
    counts = sample(_bell(), 5000, seed=3)
    assert counts["01"] == 0 and counts["10"] == 0
    assert counts["00"] + counts["11"] == 5000


def test_collapse_and_measure_once():
    outcome, after = measure_once(ket_plus(), seed=11)
    assert outcome in ("0", "1")
    assert after.is_close(basis_state(outcome))
    with pytest.raises(ValueError):
        collapse(ket0(), "1")


def test_measuring_one_qubit_of_a_bell_pair_fixes_the_other():
    for seed in range(5):
        bit, after = measure_qubit(_bell(), 0, seed=seed)
        assert after.is_normalized()
        assert after.probability_of(f"{bit}{bit}") == pytest.approx(1.0)


def test_shots_must_be_positive():
    with pytest.raises(ValueError):
        sample(ket0(), 0)
