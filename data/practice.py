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
