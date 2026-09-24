"""Practice questions on Bell states and entanglement.

Every question declares its correct option AND a `verify` function that
recomputes that option from the quantum engine. tests/test_practice.py asserts
the two agree for every question, so a question can never quietly disagree with
the simulator the student is using to check their work.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

from data.lesson import CircuitSpec, bell_circuit
from quantum.bloch import bloch_vector, length
from quantum.gates import GATES
from quantum.state import apply_gate, basis_state
from utils.format_state import recognise_state

DIFFICULTIES = ["Warm-up", "Core", "Challenge"]


@dataclass(frozen=True)
class Question:
    key: str
    module: str                          # key of the curriculum module it belongs to
    difficulty: str                      # one of DIFFICULTIES
    prompt: str                          # markdown, may contain $latex$
    options: Tuple[str, ...]             # exactly one is correct
    answer: str                          # must be a member of options
    solution: str                        # worked explanation (markdown)
    verify: Callable[[], str]            # recomputes `answer` from the engine
    hint: str = ""
    circuit: Optional[CircuitSpec] = None   # "check it in Explore"
    equations: Tuple[str, ...] = ()         # display equations in the solution

    def __post_init__(self) -> None:
        if self.answer not in self.options:
            raise ValueError(f"{self.key}: answer {self.answer!r} is not one of the options")
        if self.difficulty not in DIFFICULTIES:
            raise ValueError(f"{self.key}: unknown difficulty {self.difficulty!r}")
        from data.curriculum import MODULES_BY_KEY
        if self.module not in MODULES_BY_KEY:
            raise ValueError(f"{self.key}: unknown module {self.module!r}")

    @property
    def answer_index(self) -> int:
        return self.options.index(self.answer)

    def is_correct(self, choice: Optional[str]) -> bool:
        return choice == self.answer


# --- helpers the verifiers use ------------------------------------------------
def _bell_name(initial: Tuple[str, str]) -> str:
    """Run H + CNOT on the given inputs and ask the engine what came out."""
    return recognise_state(bell_circuit(initial).final_state()).text


def _percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def _arrow_length(spec: CircuitSpec, qubit: int) -> str:
    return f"{length(bloch_vector(spec.final_state(), qubit)):.2f}"


PHI_PLUS = bell_circuit(("0", "0"))
PSI_PLUS = bell_circuit(("0", "1"))

# |++> then CZ -- entangling without any CNOT
CZ_ON_PLUS_PLUS = CircuitSpec(2, ("+", "+"), (("CZ", (0, 1)),))

# The Bell circuit run forwards then backwards
DISENTANGLE = CircuitSpec(2, ("0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (0, 1)), ("H", (0,))))

# |Phi+> followed by Z on q0
PHI_PLUS_THEN_Z = CircuitSpec(2, ("0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("Z", (0,))))


QUESTIONS: List[Question] = [
    Question(
        key="q1_build",
        module="bell",
        difficulty="Warm-up",
        prompt=(
            "You start with two qubits in $|00\\rangle$, apply **H to q0**, then **CNOT with control q0 "
            "and target q1**. Which state do you end up with?"
        ),
        options=("|Φ⁺⟩", "|Φ⁻⟩", "|Ψ⁺⟩", "|Ψ⁻⟩"),
        answer="|Φ⁺⟩",
        verify=lambda: _bell_name(("0", "0")),
        hint="Write the state after H, then ask what CNOT does to each term of the superposition.",
        solution=(
            "H turns q0 into $|+\\rangle$, leaving the **product** state "
            "$(|00\\rangle + |10\\rangle)/\\sqrt{2}$.\n\n"
            "CNOT flips the target only where the control is $|1\\rangle$: the $|00\\rangle$ term is "
            "untouched and $|10\\rangle$ becomes $|11\\rangle$. The result is $|\\Phi^{+}\\rangle$ — the "
            "plus sign and the *same* bit values in both terms."
        ),
        equations=(r"\frac{|00\rangle + |10\rangle}{\sqrt{2}} \;\xrightarrow{\;\mathrm{CNOT}\;}\; \frac{|00\rangle + |11\rangle}{\sqrt{2}}",),
        circuit=PHI_PLUS,
    ),
    Question(
        key="q2_probability",
        module="bell",
        difficulty="Warm-up",
        prompt="Measuring $|\\Phi^{+}\\rangle$ in the computational basis, what is the probability of the outcome $|01\\rangle$?",
        options=("0%", "25%", "50%", "100%"),
        answer="0%",
        verify=lambda: _percent(PHI_PLUS.final_state().probability_of("01")),
        hint="Read the amplitude of $|01\\rangle$ straight off the state vector.",
        solution=(
            "$|\\Phi^{+}\\rangle = (|00\\rangle + |11\\rangle)/\\sqrt{2}$ has **no** $|01\\rangle$ term, so its "
            "amplitude is $0$ and $P(01) = |0|^2 = 0$.\n\n"
            "Only the perfectly correlated outcomes $|00\\rangle$ and $|11\\rangle$ occur, at 50% each. "
            "This is the whole point of the state: the two qubits always agree."
        ),
        circuit=PHI_PLUS,
    ),
    Question(
        key="q3_marginal",
        module="bell",
        difficulty="Warm-up",
        prompt="For the same state $|\\Phi^{+}\\rangle$, if you measure **q0 alone** and ignore q1, how often do you get $0$?",
        options=("0%", "25%", "50%", "100%"),
        answer="50%",
        verify=lambda: _percent(
            PHI_PLUS.final_state().probability_of("00") + PHI_PLUS.final_state().probability_of("01")
        ),
        hint="Add the probabilities of every outcome in which q0 reads 0.",
        solution=(
            "Sum over everything q1 could do: $P(q_0 = 0) = P(00) + P(01) = \\tfrac{1}{2} + 0 = \\tfrac{1}{2}$.\n\n"
            "On its own, q0 is an unbiased coin — exactly what the maximally mixed reduced state "
            "$\\rho = I/2$ predicts. All the structure lives in the correlation with q1, not in q0."
        ),
        circuit=PHI_PLUS,
    ),
    Question(
        key="q4_arrow",
        module="bell",
        difficulty="Core",
        prompt="What is the **length of q0's Bloch arrow** once the pair is in $|\\Phi^{+}\\rangle$?",
        options=("0.00", "0.50", "0.71", "1.00"),
        answer="0.00",
        verify=lambda: _arrow_length(PHI_PLUS, 0),
        hint="A Bloch arrow is drawn from the qubit's reduced density matrix. What is q0's?",
        solution=(
            "Tracing out q1 gives $\\rho_{q_0} = I/2$, the maximally mixed state. Its Bloch coordinates are "
            "$x = y = z = 0$, so the arrow has length **0** and sits at the centre of the sphere.\n\n"
            "That is the visual definition of maximal entanglement in this app: the qubit has no direction "
            "of its own. A length of $1$ would mean a pure, definite single-qubit state — a product state."
        ),
        circuit=PHI_PLUS,
    ),
    Question(
        key="q5_collapse",
        module="bell",
        difficulty="Core",
        prompt=(
            "The pair is in $|\\Psi^{+}\\rangle = (|01\\rangle + |10\\rangle)/\\sqrt{2}$. You measure **q0** "
            "and get $1$. What will a measurement of q1 give?"
        ),
        options=("0 with certainty", "1 with certainty", "0 or 1, 50/50", "q1 is unaffected"),
        answer="0 with certainty",
        verify=lambda: (
            "0 with certainty"
            if PSI_PLUS.final_state().probability_of("10") > 0 and PSI_PLUS.final_state().probability_of("11") == 0
            else "1 with certainty"
        ),
        hint="Which terms of the superposition survive once q0 is known to be 1?",
        solution=(
            "Measuring $q_0 = 1$ eliminates every term where q0 is $0$. Only $|10\\rangle$ survives, so after "
            "renormalising the pair is in $|10\\rangle$ and **q1 reads 0 with certainty**.\n\n"
            "The Ψ states are *anti*-correlated: the qubits always disagree. (For $|\\Phi^{+}\\rangle$ the same "
            "argument gives the opposite answer — they always agree.) Nothing travels between the qubits; the "
            "correlation was fixed when the state was prepared."
        ),
        circuit=PSI_PLUS,
    ),
    Question(
        key="q6_recipe",
        module="bell",
        difficulty="Core",
        prompt=(
            "Using the same **H then CNOT** circuit, which starting state produces $|\\Psi^{-}\\rangle = "
            "(|01\\rangle - |10\\rangle)/\\sqrt{2}$?"
        ),
        options=("|00⟩", "|01⟩", "|10⟩", "|11⟩"),
        answer="|11⟩",
        verify=lambda: next(
            f"|{a}{b}⟩" for a in "01" for b in "01" if _bell_name((a, b)) == "|Ψ⁻⟩"
        ),
        hint="q0 controls the sign; q1 controls whether the outcomes agree or disagree.",
        solution=(
            "Start from $|11\\rangle$. H turns q0 into $|-\\rangle$, giving "
            "$(|01\\rangle - |11\\rangle)/\\sqrt{2}$. CNOT leaves $|01\\rangle$ alone and sends "
            "$|11\\rangle \\to |10\\rangle$, producing $(|01\\rangle - |10\\rangle)/\\sqrt{2} = |\\Psi^{-}\\rangle$.\n\n"
            "The rule to remember: **q0 = |1⟩ gives the minus sign**, **q1 = |1⟩ turns Φ into Ψ**. So "
            "$|11\\rangle$ gives you both — the anti-correlated state with a minus sign, also called the *singlet*."
        ),
        equations=(r"|11\rangle \;\xrightarrow{\;H\;}\; \frac{|01\rangle - |11\rangle}{\sqrt{2}} \;\xrightarrow{\;\mathrm{CNOT}\;}\; \frac{|01\rangle - |10\rangle}{\sqrt{2}}",),
        circuit=bell_circuit(("1", "1")),
    ),
    Question(
        key="q7_phase_gate",
        module="bell",
        difficulty="Core",
        prompt="You hold $|\\Phi^{+}\\rangle$ and want $|\\Phi^{-}\\rangle$. Which single gate on **q0** does it?",
        options=("Z", "X", "H", "No single gate can"),
        answer="Z",
        verify=lambda: next(
            symbol for symbol in ("Z", "X", "H")
            if (r := recognise_state(apply_gate(PHI_PLUS.final_state(), GATES[symbol], (0,)))) is not None
            and r.text == "|Φ⁻⟩"
        ),
        hint="You need to flip the sign of the $|11\\rangle$ term and nothing else.",
        solution=(
            "Z leaves $|0\\rangle$ alone and multiplies $|1\\rangle$ by $-1$. Applied to q0 it therefore leaves "
            "the $|00\\rangle$ term untouched and flips the sign of $|11\\rangle$, turning "
            "$(|00\\rangle + |11\\rangle)/\\sqrt{2}$ into $(|00\\rangle - |11\\rangle)/\\sqrt{2} = |\\Phi^{-}\\rangle$.\n\n"
            "Note the measurement statistics are **identical** before and after — 50% $|00\\rangle$, 50% "
            "$|11\\rangle$. The difference is a relative phase, and telling $|\\Phi^{+}\\rangle$ from "
            "$|\\Phi^{-}\\rangle$ requires measuring in a different basis (run the Bell circuit backwards first)."
        ),
        circuit=PHI_PLUS_THEN_Z,
    ),
    Question(
        key="q8_cz",
        module="bell",
        difficulty="Challenge",
        prompt=(
            "Both qubits start in $|+\\rangle$, and you apply **CZ**. All four outcomes still have "
            "probability 25%. Are the qubits entangled afterwards?"
        ),
        options=(
            "Yes — the arrows shrink below full length",
            "No — the probabilities did not change",
            "No — CZ only ever adds a global phase",
            "Only if you measure them first",
        ),
        answer="Yes — the arrows shrink below full length",
        verify=lambda: (
            "Yes — the arrows shrink below full length"
            if not CZ_ON_PLUS_PLUS.final_state().is_pure_on(0)
            else "No — the probabilities did not change"
        ),
        hint="Equal probabilities do not imply a product state. Try to factorise the amplitudes.",
        solution=(
            "$|{+}{+}\\rangle = (|00\\rangle + |01\\rangle + |10\\rangle + |11\\rangle)/2$. CZ flips the sign of "
            "the $|11\\rangle$ term only, giving $(|00\\rangle + |01\\rangle + |10\\rangle - |11\\rangle)/2$.\n\n"
            "Try to factorise it as $(a|0\\rangle + b|1\\rangle)\\otimes(c|0\\rangle + d|1\\rangle)$: you would need "
            "$ac = ad = bc = +\\tfrac12$ but $bd = -\\tfrac12$, and multiplying the first three gives "
            "$bd = +\\tfrac12$. Contradiction — so the state **is entangled**.\n\n"
            "The engine agrees: both arrows collapse to length **0.00**. In fact this state is just a Bell state in disguise — applying H to q1 turns it into $|\\Phi^{+}\\rangle$ — so it is *maximally* entangled.\n\n"
            "That is the trap in the question: identical measurement probabilities say nothing about entanglement, "
            "because entanglement lives in the **phases** as much as the magnitudes. The only thing CZ changed was "
            "one minus sign."
        ),
        circuit=CZ_ON_PLUS_PLUS,
    ),
    Question(
        key="q9_undo",
        module="bell",
        difficulty="Challenge",
        prompt=(
            "Starting from $|00\\rangle$ you run **H(q0), CNOT, CNOT, H(q0)** — the Bell circuit forwards "
            "and then backwards. What is the final state?"
        ),
        options=("|00⟩", "|Φ⁺⟩", "|++⟩", "|11⟩"),
        answer="|00⟩",
        verify=lambda: (
            "|00⟩" if DISENTANGLE.final_state().is_close(basis_state("00")) else "|Φ⁺⟩"
        ),
        hint="What is CNOT·CNOT? What is H·H?",
        solution=(
            "Both gates are their own inverse: $\\mathrm{CNOT}^2 = I$ and $H^2 = I$. The two CNOTs cancel, then "
            "the two Hadamards cancel, so the whole circuit is the identity and you are back at "
            "$|00\\rangle$ — a plain product state with both arrows at full length.\n\n"
            "This matters beyond the algebra: **entanglement is reversible**. Running the Bell circuit backwards "
            "is exactly how a *Bell measurement* works — it maps the four Bell states onto the four basis "
            "states so you can just read them off, which is the key step in teleportation and superdense coding."
        ),
        circuit=DISENTANGLE,
    ),
    Question(
        key="q10_ghz",
        module="bell",
        difficulty="Challenge",
        prompt=(
            "The GHZ state is $(|000\\rangle + |111\\rangle)/\\sqrt{2}$. You measure **q1** and get $0$. "
            "What do q0 and q2 give when measured?"
        ),
        options=("Both 0, with certainty", "Both 1, with certainty", "Each 50/50, independently", "q0 gives 0, q2 is 50/50"),
        answer="Both 0, with certainty",
        verify=lambda: (
            "Both 0, with certainty"
            if CircuitSpec(3, ("0", "0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2)))
                           ).final_state().probability_of("000") > 0
            and all(
                CircuitSpec(3, ("0", "0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2)))
                            ).final_state().probability_of(label) == 0
                for label in ("001", "010", "011", "100", "101", "110")
            )
            else "Each 50/50, independently"
        ),
        hint="Which basis states have a non-zero amplitude, and which of those have q1 = 0?",
        solution=(
            "Only $|000\\rangle$ and $|111\\rangle$ have non-zero amplitudes. Measuring $q_1 = 0$ rules out "
            "$|111\\rangle$, leaving $|000\\rangle$ — so **q0 and q2 both read 0 with certainty**.\n\n"
            "One measurement fixes all three qubits: the correlation is three-way, not a chain of pairwise "
            "links. Notice that the three Bloch spheres show nothing at all here — every arrow sits at the "
            "origin, and a picture of one qubit simply cannot express a three-way correlation."
        ),
        circuit=CircuitSpec(3, ("0", "0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2)))),
    ),
]

QUESTIONS_BY_KEY = {q.key: q for q in QUESTIONS}


def questions_for(module_key: str) -> List[Question]:
    """The questions belonging to one curriculum module, in difficulty order."""
    order = {d: i for i, d in enumerate(DIFFICULTIES)}
    return sorted((q for q in QUESTIONS if q.module == module_key),
                  key=lambda q: (order[q.difficulty], QUESTIONS.index(q)))


# =============================================================================
# Modules 1-7: everything leading up to Bell states.
# =============================================================================
from data.curriculum import (  # noqa: E402  (placed here to keep the Bell set above self-contained)
    BIT_FLIP, CNOT_BASIS, CNOT_INERT, CNOT_ON_SUPERPOSITION, CZ_BASIS, HZH,
    H_THEN_H, KET_MINUS_BY_H, KET_PLUS_BY_H, S_ON_PLUS, SWAP_01, T_TWICE,
    TWO_INDEPENDENT, TWO_PRODUCT, X_ON_MINUS, Y_ON_KET0, Z_ON_PLUS,
)
from quantum.complex_number import Complex  # noqa: E402
from quantum.matrix import Matrix  # noqa: E402
from quantum.measurement import collapse, sample  # noqa: E402
from quantum.state import NAMED_STATES, QuantumState, QubitState, ket0, ket_plus  # noqa: E402
from utils.format_state import coordinate_text, ket_text  # noqa: E402


def _is_certain(probability: float) -> bool:
    """True when a probability is 1 up to floating-point error."""
    return abs(probability - 1.0) < 1e-9


def _name(spec: CircuitSpec) -> str:
    """What the engine calls the state this circuit produces."""
    state = spec.final_state()
    recognised = recognise_state(state)
    return recognised.text if recognised else ket_text(state)


def _coords(spec: CircuitSpec, qubit: int = 0) -> str:
    return "(" + ", ".join(coordinate_text(c) for c in bloch_vector(spec.final_state(), qubit)) + ")"


QUESTIONS += [
    # ---------------------------------------------------------------- module 1
    Question(
        key="qubits_h0",
        module="qubits",
        difficulty="Warm-up",
        prompt="A qubit starts in $|0\\rangle$ and you apply **H**. What state is it in?",
        options=("|+⟩", "|−⟩", "|1⟩", "|0⟩"),
        answer="|+⟩",
        verify=lambda: _name(KET_PLUS_BY_H),
        hint="H sends each pole of the Bloch sphere to the equator.",
        solution=(
            "H maps $|0\\rangle$ to the equal superposition with a **plus** sign:\n\n"
            "$H|0\\rangle = (|0\\rangle + |1\\rangle)/\\sqrt{2} = |+\\rangle$.\n\n"
            "Both amplitudes are now $1/\\sqrt{2}$, so measuring gives $0$ or $1$ with equal probability. "
            "(From $|1\\rangle$ the same gate gives $|-\\rangle$ — the minus sign is the only difference.)"
        ),
        circuit=KET_PLUS_BY_H,
    ),
    Question(
        key="qubits_norm",
        module="qubits",
        difficulty="Warm-up",
        prompt="Which of these is **not** a valid qubit state?",
        options=(
            "0.8|0⟩ + 0.8|1⟩",
            "0.6|0⟩ + 0.8|1⟩",
            "|0⟩",
            "(|0⟩ − |1⟩)/√2",
        ),
        answer="0.8|0⟩ + 0.8|1⟩",
        verify=lambda: next(
            text for text, state in (
                ("0.8|0⟩ + 0.8|1⟩", QubitState(Complex(0.8), Complex(0.8))),
                ("0.6|0⟩ + 0.8|1⟩", QubitState(Complex(0.6), Complex(0.8))),
                ("|0⟩", ket0()),
                ("(|0⟩ − |1⟩)/√2", KET_MINUS_BY_H.final_state()),
            ) if not state.is_normalized()
        ),
        hint="Add up the squared magnitudes of the amplitudes.",
        solution=(
            "Normalisation requires $|\\alpha|^2 + |\\beta|^2 = 1$.\n\n"
            "For the first option $0.8^2 + 0.8^2 = 0.64 + 0.64 = 1.28 \\ne 1$, so it is not a valid state — "
            "its \"probabilities\" would add up to 128%.\n\n"
            "The others all check out: $0.6^2 + 0.8^2 = 0.36 + 0.64 = 1$, $|0\\rangle$ trivially, and "
            "$(1/\\sqrt2)^2 + (-1/\\sqrt2)^2 = 1$ — note that a **negative** amplitude is perfectly fine, "
            "because it is the *squared magnitude* that has to behave."
        ),
    ),
    Question(
        key="qubits_plus_minus",
        module="qubits",
        difficulty="Core",
        prompt="$|+\\rangle$ and $|-\\rangle$ both measure 50/50 in the computational basis. What actually distinguishes them?",
        options=(
            "The relative phase — the sign of β",
            "Nothing; they are the same state written two ways",
            "Their normalisation",
            "|−⟩ has a higher probability of giving 1",
        ),
        answer="The relative phase — the sign of β",
        verify=lambda: (
            "The relative phase — the sign of β"
            if (KET_PLUS_BY_H.final_state().probabilities() == KET_MINUS_BY_H.final_state().probabilities()
                and not KET_PLUS_BY_H.final_state().equals_up_to_global_phase(KET_MINUS_BY_H.final_state()))
            else "Nothing; they are the same state written two ways"
        ),
        hint="Compare the probabilities, then compare the states themselves.",
        solution=(
            "Both have $|\\alpha|^2 = |\\beta|^2 = \\tfrac12$, so the probabilities are identical. But "
            "$|+\\rangle$ has $\\beta = +1/\\sqrt2$ and $|-\\rangle$ has $\\beta = -1/\\sqrt2$, and no global "
            "phase turns one into the other — they are genuinely different states.\n\n"
            "On the Bloch sphere they sit at **opposite ends of the x axis**. Apply H to each and the "
            "difference becomes plainly measurable: $H|+\\rangle = |0\\rangle$ but $H|-\\rangle = |1\\rangle$."
        ),
        circuit=Z_ON_PLUS,
    ),
    Question(
        key="qubits_interference",
        module="qubits",
        difficulty="Challenge",
        prompt=(
            "Apply **H twice** to $|0\\rangle$. If the first H left the qubit *secretly* 0 or 1, the second "
            "would give 50/50. What actually happens?"
        ),
        options=(
            "You get |0⟩ every time — the |1⟩ paths cancel",
            "50/50, as the secretly-0-or-1 picture predicts",
            "You get |1⟩ every time",
            "It depends on whether you measured in between",
        ),
        answer="You get |0⟩ every time — the |1⟩ paths cancel",
        verify=lambda: (
            "You get |0⟩ every time — the |1⟩ paths cancel"
            if _is_certain(H_THEN_H.final_state().probability_of("0"))
            else "50/50, as the secretly-0-or-1 picture predicts"
        ),
        hint="Write out both amplitudes of |1⟩ after the second H and add them.",
        solution=(
            "$H^2 = I$, so you get $|0\\rangle$ with certainty.\n\n"
            "Track the $|1\\rangle$ amplitude through the second H: one path contributes $+\\tfrac12$ and "
            "the other $-\\tfrac12$, and they **cancel exactly**. That is destructive interference, and it "
            "is only possible if both branches genuinely existed.\n\n"
            "The last option is a good instinct though — measuring in between *would* destroy the "
            "superposition and give you 50/50. Interference is exactly what measurement costs you."
        ),
        circuit=H_THEN_H,
    ),
    # ---------------------------------------------------------------- module 2
    Question(
        key="meas_born",
        module="measurement",
        difficulty="Warm-up",
        prompt="A qubit is in $|\\psi\\rangle = 0.6|0\\rangle + 0.8|1\\rangle$. What is $P(1)$?",
        options=("64%", "80%", "50%", "40%"),
        answer="64%",
        verify=lambda: _percent(QubitState(Complex(0.6), Complex(0.8)).probabilities()[1]),
        hint="The Born rule squares the amplitude.",
        solution=(
            "$P(1) = |\\beta|^2 = 0.8^2 = 0.64$, so **64%** — not 80%.\n\n"
            "The amplitude and the probability are different things, and confusing them is the single most "
            "common slip when starting out. Check: $P(0) = 0.6^2 = 0.36$, and $0.36 + 0.64 = 1$. ✓"
        ),
    ),
    Question(
        key="meas_repeat",
        module="measurement",
        difficulty="Core",
        prompt="You measure a qubit in $|+\\rangle$ and get $0$. You immediately measure the **same qubit** again. What do you get?",
        options=("0 with certainty", "0 or 1, 50/50 again", "1 with certainty", "The qubit returns to |+⟩"),
        answer="0 with certainty",
        verify=lambda: (
            "0 with certainty"
            if _is_certain(collapse(ket_plus(), "0").probability_of("0"))
            else "0 or 1, 50/50 again"
        ),
        hint="What is the state *after* the first measurement?",
        solution=(
            "The first measurement **collapses** the state: once you have seen $0$, the qubit is in "
            "$|0\\rangle$, full stop. Measuring $|0\\rangle$ gives $0$ with probability $|1|^2 = 1$.\n\n"
            "This is why the 1000-shot experiment in the app re-runs the whole circuit from scratch each "
            "time rather than measuring one qubit a thousand times — the latter would give you the same "
            "answer a thousand times over."
        ),
        circuit=KET_PLUS_BY_H,
    ),
    Question(
        key="meas_phase_invisible",
        module="measurement",
        difficulty="Core",
        prompt="You apply **Z** to $|+\\rangle$, turning it into $|-\\rangle$. How do the measurement probabilities change?",
        options=(
            "Not at all — still 50/50",
            "They flip: P(0) becomes 0",
            "P(1) rises to 100%",
            "They become 25/75",
        ),
        answer="Not at all — still 50/50",
        verify=lambda: (
            "Not at all — still 50/50"
            if Z_ON_PLUS.final_state().probabilities() == ket_plus().probabilities()
            else "They flip: P(0) becomes 0"
        ),
        hint="Z changes the sign of β. What does squaring do to a sign?",
        solution=(
            "Z sends $\\beta \\to -\\beta$, and $|-\\beta|^2 = |\\beta|^2$ — squaring throws the sign away. "
            "Both states measure 50/50.\n\n"
            "So has nothing happened? No: the *state* changed, and the Bloch arrow swung from $+x$ to "
            "$-x$. Follow Z with an H and the difference becomes completely measurable "
            "($H|+\\rangle = |0\\rangle$ versus $H|-\\rangle = |1\\rangle$). **Phase hides from measurement "
            "but not from later gates** — that is the loophole every quantum algorithm exploits."
        ),
        circuit=Z_ON_PLUS,
    ),
    Question(
        key="meas_shots",
        module="measurement",
        difficulty="Warm-up",
        prompt="You run the circuit for $|-\\rangle$ once and measure. What do you see?",
        options=(
            "A single outcome: either 0 or 1",
            "Both outcomes at once",
            "The amplitudes −0.707 and 0.707",
            "A 50/50 histogram",
        ),
        answer="A single outcome: either 0 or 1",
        verify=lambda: (
            "A single outcome: either 0 or 1"
            if len([c for c in sample(KET_MINUS_BY_H.final_state(), 1).values() if c == 1]) == 1
            else "A 50/50 histogram"
        ),
        hint="How many bits does one measurement give you?",
        solution=(
            "One shot gives **one** classical bit. You never observe an amplitude and you never observe "
            "\"both\" — the histogram only appears once you repeat the whole experiment many times.\n\n"
            "This is the practical reason quantum algorithms are designed so the *right* answer has a large "
            "probability: you only get one sample per run."
        ),
        circuit=KET_MINUS_BY_H,
    ),
    # ---------------------------------------------------------------- module 3
    Question(
        key="bloch_ket1",
        module="bloch",
        difficulty="Warm-up",
        prompt="Where does $|1\\rangle$ sit on the Bloch sphere?",
        options=("(0.000, 0.000, -1.000)", "(0.000, 0.000, 1.000)", "(1.000, 0.000, 0.000)", "(0.000, 1.000, 0.000)"),
        answer="(0.000, 0.000, -1.000)",
        verify=lambda: _coords(CircuitSpec(1, ("1",), ())),
        hint="Use z = |α|² − |β|² with α = 0, β = 1.",
        solution=(
            "With $\\alpha = 0$ and $\\beta = 1$: $x = 2\\,\\mathrm{Re}(\\alpha^{*}\\beta) = 0$, "
            "$y = 0$, and $z = |0|^2 - |1|^2 = -1$.\n\n"
            "So $|1\\rangle$ is the **south pole**, directly opposite $|0\\rangle$ at the north pole. Note "
            "that states which are *orthogonal* in the maths sit at *opposite* points on the sphere — the "
            "angles are doubled compared to the state vector."
        ),
        circuit=CircuitSpec(1, ("1",), ()),
    ),
    Question(
        key="bloch_plus_i",
        module="bloch",
        difficulty="Core",
        prompt="Which state sits on the **+y axis** of the Bloch sphere?",
        options=("|+i⟩", "|+⟩", "|0⟩", "|−⟩"),
        answer="|+i⟩",
        verify=lambda: next(
            name for name, _latex, state in NAMED_STATES
            if all(abs(c - t) < 1e-9 for c, t in zip(bloch_vector(state), (0.0, 1.0, 0.0)))
        ),
        hint="y = 2 Im(α*β), so you need an imaginary relative phase.",
        solution=(
            "$|{+i}\\rangle = (|0\\rangle + i|1\\rangle)/\\sqrt{2}$ gives "
            "$\\alpha^{*}\\beta = i/2$, so $y = 2 \\cdot \\tfrac12 = 1$ while $x = z = 0$.\n\n"
            "The equator holds all four 50/50 states: $|+\\rangle$ and $|-\\rangle$ on the $x$ axis, "
            "$|{+i}\\rangle$ and $|{-i}\\rangle$ on the $y$ axis. You can reach $|{+i}\\rangle$ from "
            "$|+\\rangle$ with a single **S** gate."
        ),
        circuit=S_ON_PLUS,
    ),
    Question(
        key="bloch_global",
        module="bloch",
        difficulty="Challenge",
        prompt="Applying **X** to $|-\\rangle$ gives $-|-\\rangle$. What happens to the Bloch arrow?",
        options=(
            "Nothing — it stays exactly where it was",
            "It flips to the opposite side",
            "It shrinks to zero",
            "It rotates 90° about x",
        ),
        answer="Nothing — it stays exactly where it was",
        verify=lambda: (
            "Nothing — it stays exactly where it was"
            if _coords(X_ON_MINUS) == _coords(CircuitSpec(1, ("-",), ()))
            else "It flips to the opposite side"
        ),
        hint="Is the minus sign a global phase or a relative one?",
        solution=(
            "$-|-\\rangle$ differs from $|-\\rangle$ by a **global phase**, which has no physical "
            "consequences whatsoever — no measurement in any basis can detect it, and the Bloch arrow "
            "does not move. Both sit at $(-1, 0, 0)$.\n\n"
            "This is the geometric reason the sphere works at all: it quotients out exactly the information "
            "that is unobservable. Careful though — a **relative** phase (between $\\alpha$ and $\\beta$) is "
            "very much physical, and does move the arrow."
        ),
        circuit=X_ON_MINUS,
    ),
    Question(
        key="bloch_length",
        module="bloch",
        difficulty="Core",
        prompt="For **any** single qubit in a definite (pure) state, how long is its Bloch arrow?",
        options=("Exactly 1", "Exactly 0", "Between 0 and 1, depending on the state", "Exactly 0.5"),
        answer="Exactly 1",
        verify=lambda: (
            "Exactly 1"
            if all(abs(length(bloch_vector(state)) - 1.0) < 1e-9 for _n, _l, state in NAMED_STATES)
            else "Between 0 and 1, depending on the state"
        ),
        hint="Try the formula on several different states and compare the lengths.",
        solution=(
            "For a pure state $x^2 + y^2 + z^2 = 1$ always — every pure state is **on the surface**, never "
            "inside. That is why the sphere is the right picture.\n\n"
            "Shorter arrows do exist, but they mean the qubit is in a *mixed* state — which for us happens "
            "only when the qubit is **entangled** with another one. That is exactly the signal you will "
            "watch for in the Bell-states module."
        ),
    ),
    # ---------------------------------------------------------------- module 4
    Question(
        key="gates_x_plus",
        module="gates",
        difficulty="Core",
        prompt="What is $X|+\\rangle$?",
        options=("|+⟩", "|−⟩", "|0⟩", "|1⟩"),
        answer="|+⟩",
        verify=lambda: _name(CircuitSpec(1, ("+",), (("X", (0,)),))),
        hint="X swaps α and β. What are they for |+⟩?",
        solution=(
            "$|+\\rangle$ has $\\alpha = \\beta = 1/\\sqrt2$, and X swaps them — which changes nothing. "
            "So $X|+\\rangle = |+\\rangle$.\n\n"
            "Geometrically $|+\\rangle$ lies **on** the x axis, and X is a rotation **about** the x axis: "
            "points on the axis of a rotation do not move. (The same argument gives $X|-\\rangle = -|-\\rangle$ "
            "— on the axis, so fixed, up to a global phase.)"
        ),
        circuit=CircuitSpec(1, ("+",), (("X", (0,)),)),
    ),
    Question(
        key="gates_hzh",
        module="gates",
        difficulty="Challenge",
        prompt="You run **H, then Z, then H** on $|0\\rangle$. Which single gate does the same thing?",
        options=("X", "Z", "H", "The identity"),
        answer="X",
        verify=lambda: next(
            symbol for symbol in ("X", "Z", "H")
            if HZH.final_state().equals_up_to_global_phase(apply_gate(ket0(), GATES[symbol]))
        ),
        hint="H swaps the x and z axes of the Bloch sphere. What does that do to a rotation about z?",
        solution=(
            "$HZH = X$. Starting from $|0\\rangle$: H takes you to $|+\\rangle$, Z flips it to "
            "$|-\\rangle$, and the final H maps $|-\\rangle$ to $|1\\rangle$ — which is exactly "
            "$X|0\\rangle$.\n\n"
            "Geometrically, H exchanges the $x$ and $z$ axes, so conjugating a rotation about $z$ by H "
            "turns it into a rotation about $x$. This **phase flip ↔ bit flip** conversion is the engine "
            "of quantum algorithms: write information into phases, then use H to turn it into something "
            "you can actually measure."
        ),
        circuit=HZH,
    ),
    Question(
        key="gates_y",
        module="gates",
        difficulty="Core",
        prompt="What is $Y|0\\rangle$?",
        options=("i|1⟩", "|1⟩", "−|1⟩", "|+i⟩"),
        answer="i|1⟩",
        verify=lambda: _name(Y_ON_KET0),
        hint="Read the first column of Y = [[0, −i], [i, 0]].",
        solution=(
            "The first column of $Y$ is $(0, i)^T$, so $Y|0\\rangle = i|1\\rangle$.\n\n"
            "The factor of $i$ is a **global** phase here, so this state is physically identical to "
            "$|1\\rangle$ — measurement gives $1$ either way and the Bloch arrow is at the south pole. "
            "The $i$ only becomes meaningful when Y acts on part of a superposition, where it contributes "
            "a *relative* phase."
        ),
        circuit=Y_ON_KET0,
    ),
    Question(
        key="gates_inverse",
        module="gates",
        difficulty="Core",
        prompt="Which of these gates is **not** its own inverse?",
        options=("S", "X", "Z", "H"),
        answer="S",
        verify=lambda: next(
            symbol for symbol in ("S", "X", "Z", "H")
            if not GATES[symbol].matrix.multiply(GATES[symbol].matrix).is_close(Matrix.identity(2))
        ),
        hint="Square each matrix and see which one fails to give the identity.",
        solution=(
            "$X^2 = Z^2 = H^2 = I$, so applying any of those twice undoes it. But $S^2 = Z$, not $I$ — "
            "you need **four** S gates to get back where you started.\n\n"
            "That is the geometric picture too: X, Z and H are all $180°$ rotations, and two half-turns "
            "make a full turn. S is only a quarter-turn."
        ),
    ),
    # ---------------------------------------------------------------- module 5
    Question(
        key="phase_ss",
        module="phase",
        difficulty="Warm-up",
        prompt="What does applying **S twice** equal?",
        options=("Z", "X", "I", "T"),
        answer="Z",
        verify=lambda: next(
            symbol for symbol in ("Z", "X", "I", "T")
            if symbol in GATES and GATES["S"].matrix.multiply(GATES["S"].matrix).is_close(GATES[symbol].matrix)
        ),
        hint="S multiplies |1⟩ by i. What is i²?",
        solution=(
            "S multiplies the $|1\\rangle$ amplitude by $i$, so doing it twice multiplies by "
            "$i^2 = -1$ — which is exactly Z.\n\n"
            "In rotation terms: S is a quarter-turn about the $z$ axis and Z is a half-turn, so $S^2 = Z$. "
            "Likewise $T^2 = S$, making T an eighth-turn."
        ),
    ),
    Question(
        key="phase_s_plus",
        module="phase",
        difficulty="Core",
        prompt="What is $S|+\\rangle$?",
        options=("|+i⟩", "|−i⟩", "|−⟩", "|+⟩"),
        answer="|+i⟩",
        verify=lambda: _name(S_ON_PLUS),
        hint="S leaves α alone and multiplies β by i.",
        solution=(
            "$S|+\\rangle = (|0\\rangle + i|1\\rangle)/\\sqrt{2} = |{+i}\\rangle$.\n\n"
            "On the sphere the arrow moves a quarter of the way round the equator, from the $+x$ axis to "
            "the $+y$ axis. The measurement probabilities stay at 50/50 throughout — nothing you could "
            "detect without a further gate."
        ),
        circuit=S_ON_PLUS,
    ),
    Question(
        key="phase_probabilities",
        module="phase",
        difficulty="Core",
        prompt="You apply **T** to a qubit several times. What happens to its computational-basis measurement probabilities?",
        options=(
            "Nothing — they never change",
            "They drift towards 50/50",
            "They flip each time",
            "They change by 45% each time",
        ),
        answer="Nothing — they never change",
        verify=lambda: (
            "Nothing — they never change"
            if T_TWICE.final_state().probabilities() == ket_plus().probabilities()
            else "They drift towards 50/50"
        ),
        hint="T multiplies β by a number of magnitude 1. What does that do to |β|²?",
        solution=(
            "T multiplies $\\beta$ by $e^{i\\pi/4}$, which has magnitude $1$, so $|\\beta|^2$ is completely "
            "unchanged. The same is true of S and Z — every gate in this module is invisible to a "
            "computational-basis measurement.\n\n"
            "They are still essential. Phases decide how amplitudes **interfere** when a later H (or any "
            "non-diagonal gate) mixes them, and that interference is what turns a phase back into a "
            "probability you can read."
        ),
        circuit=T_TWICE,
    ),
    Question(
        key="phase_tt",
        module="phase",
        difficulty="Warm-up",
        prompt="Starting from $|+\\rangle$, you apply **T twice**. Where do you end up?",
        options=("|+i⟩", "|+⟩", "|−⟩", "|0⟩"),
        answer="|+i⟩",
        verify=lambda: _name(T_TWICE),
        hint="T·T = S, and you already know what S does to |+⟩.",
        solution=(
            "$T\\,T = S$, and $S|+\\rangle = |{+i}\\rangle$. Two eighth-turns make a quarter-turn: the arrow "
            "travels from the $+x$ axis to the $+y$ axis.\n\n"
            "Keep going and you can see the whole hierarchy: four Ts make a Z (a half-turn), eight Ts bring "
            "you back to where you started."
        ),
        circuit=T_TWICE,
    ),
    # ---------------------------------------------------------------- module 6
    Question(
        key="two_amplitudes",
        module="two_qubits",
        difficulty="Warm-up",
        prompt="How many complex amplitudes does a **three**-qubit state need?",
        options=("8", "3", "6", "9"),
        answer="8",
        verify=lambda: str(basis_state("000").dimension),
        hint="Count the basis states: |000⟩, |001⟩, …",
        solution=(
            "$2^3 = 8$ — one amplitude per basis state, from $|000\\rangle$ to $|111\\rangle$.\n\n"
            "The exponential is the whole story of quantum computing. 300 qubits would need more "
            "amplitudes than there are atoms in the observable universe, which is why classical simulation "
            "stops being possible long before the hardware does. (This app caps out at 3 qubits, i.e. 8 "
            "amplitudes, for readability rather than for speed.)"
        ),
    ),
    Question(
        key="two_local",
        module="two_qubits",
        difficulty="Challenge",
        prompt="Can you entangle two qubits using **only single-qubit gates**, however many you apply?",
        options=(
            "No — single-qubit gates always leave a product state",
            "Yes, if you apply H to both",
            "Yes, if you apply enough of them",
            "Only if the qubits start in |+⟩",
        ),
        answer="No — single-qubit gates always leave a product state",
        verify=lambda: (
            "No — single-qubit gates always leave a product state"
            if TWO_INDEPENDENT.final_state().is_pure_on(0) and TWO_INDEPENDENT.final_state().is_pure_on(1)
            else "Yes, if you apply enough of them"
        ),
        hint="What does a gate on q1 do to q0's reduced state?",
        solution=(
            "A single-qubit gate on q1 acts as $I \\otimes U$ — it factorises, so it maps a product state to "
            "another product state. No sequence of such gates can ever create a correlation that was not "
            "there.\n\n"
            "Check it in the app: apply H to q0 and X to q1 and **both arrows keep full length 1.00**. To "
            "entangle you need a genuinely two-qubit gate like CNOT or CZ — which is the next module."
        ),
        circuit=TWO_INDEPENDENT,
    ),
    Question(
        key="two_product",
        module="two_qubits",
        difficulty="Core",
        prompt="Two qubits start in $|00\\rangle$ and you apply **H to q0 only**. What is the state?",
        options=(
            "(|00⟩ + |10⟩)/√2",
            "(|00⟩ + |01⟩)/√2",
            "(|00⟩ + |11⟩)/√2",
            "|++⟩",
        ),
        answer="(|00⟩ + |10⟩)/√2",
        verify=lambda: next(
            text for text, labels in (
                ("(|00⟩ + |10⟩)/√2", ("00", "10")),
                ("(|00⟩ + |01⟩)/√2", ("00", "01")),
                ("(|00⟩ + |11⟩)/√2", ("00", "11")),
            ) if all(TWO_PRODUCT.final_state().probability_of(l) > 0.49 for l in labels)
        ),
        hint="Qubit 0 is the leftmost bit of the label.",
        solution=(
            "H acts on q0, the **left** bit, so $|00\\rangle$ becomes "
            "$(|00\\rangle + |10\\rangle)/\\sqrt{2}$.\n\n"
            "This is still a **product** state: it factorises as $|+\\rangle \\otimes |0\\rangle$, and both "
            "Bloch arrows have full length. Getting the bit order backwards is the most common slip with "
            "multi-qubit states — the app always lists amplitudes as $|q_0 q_1\\rangle$."
        ),
        circuit=TWO_PRODUCT,
    ),
    Question(
        key="two_which_qubit",
        module="two_qubits",
        difficulty="Warm-up",
        prompt="In the basis state $|10\\rangle$, which qubit is in $|1\\rangle$?",
        options=("q0", "q1", "Both", "Neither"),
        answer="q0",
        verify=lambda: next(
            f"q{q}" for q in (0, 1) if basis_state("10").bit(int("10", 2), q) == 1
        ),
        hint="The app writes labels as |q₀ q₁⟩.",
        solution=(
            "Qubit 0 is the **leftmost** bit, so $|10\\rangle$ means q0 = 1 and q1 = 0.\n\n"
            "This convention is worth fixing in your head early, because it decides what "
            "$\\mathrm{CNOT}(q_0 \\to q_1)$ does versus $\\mathrm{CNOT}(q_1 \\to q_0)$ — and those are "
            "different circuits."
        ),
        circuit=CircuitSpec(2, ("1", "0"), ()),
    ),
    # ---------------------------------------------------------------- module 7
    Question(
        key="ctrl_inert",
        module="controlled",
        difficulty="Warm-up",
        prompt="You apply **CNOT** (control q0, target q1) to $|01\\rangle$. What comes out?",
        options=("|01⟩", "|11⟩", "|10⟩", "|00⟩"),
        answer="|01⟩",
        verify=lambda: _name(CNOT_INERT),
        hint="Look at the control qubit first.",
        solution=(
            "The control q0 is $|0\\rangle$, so CNOT does **nothing** — the state is unchanged at "
            "$|01\\rangle$.\n\n"
            "CNOT only acts when the control is $|1\\rangle$. On basis states it is completely classical: "
            "$|a,b\\rangle \\to |a, a \\oplus b\\rangle$, a reversible XOR."
        ),
        circuit=CNOT_INERT,
    ),
    Question(
        key="ctrl_cz",
        module="controlled",
        difficulty="Core",
        prompt="What does **CZ** do to $|11\\rangle$?",
        options=("−|11⟩", "|11⟩", "|00⟩", "|10⟩"),
        answer="−|11⟩",
        verify=lambda: _name(CZ_BASIS),
        hint="CZ applies Z to the target when the control is 1.",
        solution=(
            "Control is $|1\\rangle$, so Z is applied to the target — and the target is $|1\\rangle$, which Z "
            "multiplies by $-1$. So $\\mathrm{CZ}|11\\rangle = -|11\\rangle$, and the other three basis "
            "states are untouched.\n\n"
            "Notice this makes CZ **symmetric**: the description \"flip the sign of $|11\\rangle$\" doesn't "
            "care which qubit you called the control. CNOT has no such symmetry."
        ),
        circuit=CZ_BASIS,
    ),
    Question(
        key="ctrl_swap",
        module="controlled",
        difficulty="Warm-up",
        prompt="What is $\\mathrm{SWAP}|01\\rangle$?",
        options=("|10⟩", "|01⟩", "|11⟩", "|00⟩"),
        answer="|10⟩",
        verify=lambda: _name(SWAP_01),
        hint="SWAP exchanges the two qubits' states.",
        solution=(
            "SWAP exchanges the qubits, so q0 takes q1's value and vice versa: $|01\\rangle \\to |10\\rangle$.\n\n"
            "$|00\\rangle$ and $|11\\rangle$ are unaffected, since swapping two identical values changes "
            "nothing. SWAP can be built from three CNOTs with alternating control and target."
        ),
        circuit=SWAP_01,
    ),
    Question(
        key="ctrl_entangle",
        module="controlled",
        difficulty="Challenge",
        prompt=(
            "You put q0 in $|+\\rangle$ with an H, then apply CNOT (control q0, target q1) starting from "
            "$|00\\rangle$. Are the two qubits still independent afterwards?"
        ),
        options=(
            "No — they are entangled, and both arrows collapse to length 0",
            "Yes — CNOT is just a classical XOR",
            "Yes, but only q1 changed",
            "No, but only q1 loses its arrow",
        ),
        answer="No — they are entangled, and both arrows collapse to length 0",
        verify=lambda: (
            "No — they are entangled, and both arrows collapse to length 0"
            if not CNOT_ON_SUPERPOSITION.final_state().is_pure_on(0)
            and not CNOT_ON_SUPERPOSITION.final_state().is_pure_on(1)
            else "Yes — CNOT is just a classical XOR"
        ),
        hint="Apply CNOT to each branch of the superposition separately, then try to factorise the result.",
        solution=(
            "With the control in superposition, CNOT acts on both branches at once: $|00\\rangle$ is left "
            "alone and $|10\\rangle$ becomes $|11\\rangle$, giving "
            "$(|00\\rangle + |11\\rangle)/\\sqrt{2}$.\n\n"
            "That state does not factorise — it is the Bell state $|\\Phi^{+}\\rangle$, and **both** arrows "
            "collapse to length 0. Neither qubit has a state of its own any more.\n\n"
            "This is the punchline of the whole module: CNOT on basis states is classical and boring, but "
            "CNOT on a **superposed control** is where entanglement comes from. The next module is entirely "
            "about the four states you can make this way."
        ),
        circuit=CNOT_ON_SUPERPOSITION,
    ),
]

QUESTIONS_BY_KEY = {q.key: q for q in QUESTIONS}
