"""The lesson's claims must match what the quantum engine actually computes."""
import pytest

from data.lesson import BELL_RECIPES, SECTIONS, SECTIONS_BY_KEY, bell_circuit
from quantum.bloch import bloch_vector, length
from quantum.state import BELL_STATES, basis_state
from utils.format_state import recognise_state


@pytest.mark.parametrize("name, latex, initial", BELL_RECIPES)
def test_each_recipe_produces_the_bell_state_it_claims(name, latex, initial):
    """H on q0 then CNOT, from the stated inputs, really gives that Bell state."""
    state = bell_circuit(initial).final_state()
    recognised = recognise_state(state)
    assert recognised is not None and recognised.text == name


def test_the_four_recipes_cover_all_four_bell_states():
    produced = {recognise_state(bell_circuit(i).final_state()).text for _n, _l, i in BELL_RECIPES}
    assert produced == {name for name, _latex, _state in BELL_STATES}


@pytest.mark.parametrize("initial", [i for _n, _l, i in BELL_RECIPES])
def test_every_bell_state_is_maximally_entangled(initial):
    state = bell_circuit(initial).final_state()
    for qubit in (0, 1):
        assert length(bloch_vector(state, qubit)) == pytest.approx(0.0, abs=1e-9)
        assert state.purity(qubit) == pytest.approx(0.5)


def test_phi_states_agree_and_psi_states_disagree():
    for name, _latex, initial in BELL_RECIPES:
        state = bell_circuit(initial).final_state()
        outcomes = {l for l, p in zip(state.basis_labels(), state.probabilities()) if p > 1e-9}
        assert outcomes == ({"00", "11"} if name.startswith("|Φ") else {"01", "10"})
        for label in outcomes:
            assert state.probability_of(label) == pytest.approx(0.5)


def test_build_section_matches_its_equation():
    """|00> -H-> (|00>+|10>)/sqrt2 -CNOT-> |Phi+>, exactly as the section states."""
    from quantum.circuit import simulate_circuit
    states = simulate_circuit(SECTIONS_BY_KEY["build"].circuit.to_circuit())
    assert states[1].probability_of("00") == pytest.approx(0.5)
    assert states[1].probability_of("10") == pytest.approx(0.5)
    assert states[1].is_pure_on(0) and states[1].is_pure_on(1)   # still a product state
    assert recognise_state(states[2]).text == "|Φ⁺⟩"
    assert not states[2].is_pure_on(0)                            # now entangled


def test_undo_section_really_returns_to_the_product_state():
    state = SECTIONS_BY_KEY["undo"].circuit.final_state()
    assert state.is_close(basis_state("00"))
    assert all(length(bloch_vector(state, q)) == pytest.approx(1.0) for q in (0, 1))


def test_ghz_section_claims():
    state = SECTIONS_BY_KEY["beyond"].circuit.final_state()
    assert state.num_qubits == 3
    assert state.probability_of("000") == pytest.approx(0.5)
    assert state.probability_of("111") == pytest.approx(0.5)
    assert all(length(bloch_vector(state, q)) == pytest.approx(0.0, abs=1e-9) for q in range(3))


def test_sections_are_well_formed():
    assert len(SECTIONS) == len(SECTIONS_BY_KEY) >= 5
    for sec in SECTIONS:
        assert sec.title and sec.body and sec.icon
        assert sec.takeaway, f"{sec.key} has no takeaway"
        if sec.circuit is not None:
            sec.circuit.to_circuit()      # raises if the circuit is invalid
