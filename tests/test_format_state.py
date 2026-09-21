from quantum.complex_number import Complex
from quantum.gates import H, X, Y, Z
from quantum.state import QubitState, apply_gate, ket0, ket1, ket_minus, ket_plus, simulate
from utils.format_state import (
    complex_latex,
    ket_latex,
    ket_latex_factored,
    matrix_latex,
    recognise_state,
    state_chain_latex,
    vector_latex,
)


def test_special_values_print_exactly():
    assert complex_latex(Complex(0.7071067811865475)) == r"\frac{1}{\sqrt{2}}"
    assert complex_latex(Complex(0, -1)) == "-i"
    assert complex_latex(Complex(0, 0.7071067811865475)) == r"\frac{i}{\sqrt{2}}"
    assert complex_latex(Complex(0.5, -0.5)) == r"\frac{e^{-i\pi/4}}{\sqrt{2}}"   # the T gate's phase
    assert complex_latex(Complex(0.3, 0.4)) == r"0.300 + 0.400i"
    assert complex_latex(Complex(0.123456)) == "0.123"


def test_ket_latex_drops_zero_terms_and_tidies_signs():
    assert ket_latex(ket0()) == r"|0\rangle"
    assert ket_latex(ket_minus()) == r"\frac{1}{\sqrt{2}}|0\rangle - \frac{1}{\sqrt{2}}|1\rangle"
    assert ket_latex(apply_gate(ket0(), Y)) == r"i|1\rangle"


def test_factored_form_and_recognition():
    minus_minus = apply_gate(ket_minus(), X)
    assert ket_latex_factored(minus_minus) == r"-\frac{|0\rangle - |1\rangle}{\sqrt{2}}"
    recognised = recognise_state(minus_minus)
    assert recognised is not None
    assert recognised.latex == r"-|-\rangle"
    assert recognised.text == "−|−⟩"
    assert recognise_state(ket_plus()).latex == r"|+\rangle"
    assert ket_latex_factored(ket1()) is None


def test_matrix_and_vector_latex():
    assert matrix_latex(H.shown_matrix, H.display_scale_latex) == (
        r"\frac{1}{\sqrt{2}}\begin{bmatrix} 1 & 1 \\ 1 & -1 \end{bmatrix}"
    )
    assert matrix_latex(Z.matrix) == r"\begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}"
    assert vector_latex(ket0().as_vector()) == r"\begin{bmatrix} 1 \\ 0 \end{bmatrix}"


def test_state_chain_for_the_plan_example():
    states = simulate(ket0(), [H, Z, X])
    assert state_chain_latex(states[1]) == (
        r"|\psi\rangle = \frac{1}{\sqrt{2}}|0\rangle + \frac{1}{\sqrt{2}}|1\rangle"
        r" = \frac{|0\rangle + |1\rangle}{\sqrt{2}} = |+\rangle"
    )
    assert state_chain_latex(states[3]).endswith(r"= -|-\rangle")


def test_bell_state_is_recognised():
    from quantum.circuit import Circuit, Operation, simulate_circuit
    bell = simulate_circuit(Circuit(2, ("0", "0"), (Operation("H", (0,)), Operation("CNOT", (0, 1)))))[-1]
    assert state_chain_latex(bell) == (
        r"|\psi\rangle = \frac{1}{\sqrt{2}}|00\rangle + \frac{1}{\sqrt{2}}|11\rangle"
        r" = \frac{|00\rangle + |11\rangle}{\sqrt{2}} = |\Phi^{+}\rangle"
    )
    assert recognise_state(bell).text == "|Φ⁺⟩"


def test_t_gate_phase_prints_in_polar_form():
    from quantum.gates import T
    state = apply_gate(ket_plus(), T)
    assert ket_latex(state) == r"\frac{1}{\sqrt{2}}|0\rangle + \frac{e^{i\pi/4}}{\sqrt{2}}|1\rangle"
    assert ket_latex_factored(state) == r"\frac{|0\rangle + e^{i\pi/4}|1\rangle}{\sqrt{2}}"
