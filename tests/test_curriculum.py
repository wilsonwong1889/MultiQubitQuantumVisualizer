"""The curriculum's structure, and every factual claim its sections make."""
import pytest

from data.curriculum import MODULES, MODULES_BY_KEY
from data.practice import questions_for
from quantum.bloch import bloch_vector, length
from quantum.circuit import simulate_circuit
from quantum.gates import GATES
from quantum.matrix import Matrix
from quantum.state import apply_gate, basis_state, ket0, ket_plus
from utils.format_state import ket_text, recognise_state
import data.curriculum as c


def _name(spec):
    state = spec.final_state()
    recognised = recognise_state(state)
    return recognised.text if recognised else ket_text(state)


# --- structure ---------------------------------------------------------------
def test_modules_are_numbered_in_order_and_uniquely_keyed():
    assert [m.number for m in MODULES] == list(range(1, len(MODULES) + 1))
    assert len(MODULES_BY_KEY) == len(MODULES)


def test_every_module_has_sections_and_questions():
    for m in MODULES:
        assert m.sections, f"{m.key} has no sections"
        assert m.summary and m.title and m.icon
        assert questions_for(m.key), f"{m.key} has no practice questions"


def test_prerequisites_form_a_chain_back_to_the_first_module():
    for previous, module in zip(MODULES, MODULES[1:]):
        assert module.prerequisite == previous.key, f"{module.key} does not follow {previous.key}"
    assert MODULES[0].prerequisite == ""


def test_the_course_ends_at_bell_states():
    assert MODULES[-1].key == "bell"


def test_every_section_circuit_is_valid():
    for m in MODULES:
        for sec in m.sections:
            if sec.circuit is not None:
                circuit = sec.circuit.to_circuit()       # raises if invalid
                assert 1 <= circuit.num_qubits <= 3
                simulate_circuit(circuit)


def test_every_section_has_a_takeaway():
    for m in MODULES:
        for sec in m.sections:
            assert sec.takeaway, f"{m.key}/{sec.key} has no takeaway"


# --- the claims the lessons make ---------------------------------------------
@pytest.mark.parametrize("spec, expected", [
    (c.KET_PLUS_BY_H, "|+⟩"),        # module 1: H|0> = |+>
    (c.KET_MINUS_BY_H, "|−⟩"),       # module 4: H|1> = |->
    (c.BIT_FLIP, "|1⟩"),             # module 4: X|0> = |1>
    (c.H_THEN_H, "|0⟩"),             # module 1: interference, H^2 = I
    (c.Z_ON_PLUS, "|−⟩"),            # module 2/3: Z|+> = |->
    (c.Y_ON_KET0, "i|1⟩"),           # module 4: Y|0> = i|1>
    (c.X_ON_MINUS, "−|−⟩"),          # module 3: global phase only
    (c.S_ON_PLUS, "|+i⟩"),           # module 5: S|+> = |+i>
    (c.T_TWICE, "|+i⟩"),             # module 5: T T = S
    (c.HZH, "|1⟩"),                  # module 4: HZH = X
    (c.CNOT_BASIS, "|11⟩"),          # module 7: CNOT|10> = |11>
    (c.CNOT_INERT, "|01⟩"),          # module 7: control 0 does nothing
    (c.CZ_BASIS, "−|11⟩"),           # module 7: CZ|11> = -|11>
    (c.SWAP_01, "|10⟩"),             # module 7: SWAP|01> = |10>
    (c.CNOT_ON_SUPERPOSITION, "|Φ⁺⟩"),  # module 7 -> 8: the entangling moment
])
def test_lesson_circuits_produce_the_states_the_text_claims(spec, expected):
    assert _name(spec) == expected


def test_module1_interference_is_certain_not_fifty_fifty():
    assert c.H_THEN_H.final_state().probability_of("0") == pytest.approx(1.0)


def test_module3_bloch_claims():
    # |0> at the north pole, |1> at the south pole, |+i> on +y
    assert bloch_vector(ket0()) == pytest.approx((0.0, 0.0, 1.0))
    assert bloch_vector(basis_state("1")) == pytest.approx((0.0, 0.0, -1.0))
    assert bloch_vector(c.S_ON_PLUS.final_state()) == pytest.approx((0.0, 1.0, 0.0), abs=1e-9)
    # a global phase does not move the arrow: X|-> = -|-> sits exactly where |-> does
    from quantum.state import ket_minus
    assert bloch_vector(c.X_ON_MINUS.final_state()) == pytest.approx(bloch_vector(ket_minus()), abs=1e-9)
    assert bloch_vector(ket_minus()) == pytest.approx((-1.0, 0.0, 0.0), abs=1e-9)


def test_module4_identities():
    identity = Matrix.identity(2)
    for symbol in ("X", "Y", "Z", "H"):
        assert GATES[symbol].matrix.multiply(GATES[symbol].matrix).is_close(identity)
    # HZH = X
    h, z = GATES["H"].matrix, GATES["Z"].matrix
    assert h.multiply(z).multiply(h).is_close(GATES["X"].matrix)


def test_module5_phase_gates_never_change_probabilities():
    for symbol in ("S", "T", "Z"):
        for start in (ket0(), ket_plus()):
            after = apply_gate(start, GATES[symbol])
            assert after.probabilities() == pytest.approx(start.probabilities())
    assert GATES["S"].matrix.multiply(GATES["S"].matrix).is_close(GATES["Z"].matrix)
    assert GATES["T"].matrix.multiply(GATES["T"].matrix).is_close(GATES["S"].matrix)


def test_module6_single_qubit_gates_never_entangle():
    state = c.TWO_INDEPENDENT.final_state()
    assert state.is_pure_on(0) and state.is_pure_on(1)
    assert all(length(bloch_vector(state, q)) == pytest.approx(1.0) for q in (0, 1))
    # and the product state from H on q0 alone
    product = c.TWO_PRODUCT.final_state()
    assert product.probability_of("00") == pytest.approx(0.5)
    assert product.probability_of("10") == pytest.approx(0.5)
    assert product.is_pure_on(0) and product.is_pure_on(1)


def test_module7_superposed_control_creates_entanglement():
    state = c.CNOT_ON_SUPERPOSITION.final_state()
    assert not state.is_pure_on(0) and not state.is_pure_on(1)
    assert all(length(bloch_vector(state, q)) == pytest.approx(0.0, abs=1e-9) for q in (0, 1))
