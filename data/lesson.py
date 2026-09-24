"""The Bell-state lesson: structured content, verified against the engine.

Each section carries an optional circuit so the reader can open exactly that
circuit in the Explore view, and the facts quoted in the text (states, Bloch
arrow lengths, probabilities) are checked against the quantum engine by
tests/test_lesson.py — the teaching material cannot drift from the physics.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from quantum.circuit import Circuit, Operation, simulate_circuit
from quantum.state import QuantumState

OperationSpec = Tuple[str, Tuple[int, ...]]


@dataclass(frozen=True)
class CircuitSpec:
    """A circuit a lesson section refers to, in the same shape model.py stores."""

    num_qubits: int
    initial: Tuple[str, ...]
    operations: Tuple[OperationSpec, ...]

    def to_circuit(self) -> Circuit:
        return Circuit(self.num_qubits, self.initial,
                       tuple(Operation(sym, tuple(t)) for sym, t in self.operations))

    def final_state(self) -> QuantumState:
        return simulate_circuit(self.to_circuit())[-1]


@dataclass(frozen=True)
class Module:
    """One page of the course: a few lesson sections plus its practice questions."""

    key: str
    number: int
    title: str
    icon: str
    summary: str                    # one line, shown under the page title
    sections: Tuple["Section", ...]
    prerequisite: str = ""          # key of the module this one follows

    @property
    def tab_label(self) -> str:
        return f"{self.icon} {self.number}. {self.title}"


@dataclass(frozen=True)
class Section:
    key: str
    title: str
    icon: str
    body: str                                   # markdown, may contain $latex$
    equations: Tuple[str, ...] = ()             # display equations under the body
    circuit: Optional[CircuitSpec] = None       # "try this in Explore"
    try_it_label: str = "Open this circuit in Explore"
    takeaway: str = ""                          # the one sentence to remember


# The standard recipe: H on the control, then CNOT. Which Bell state comes out
# depends only on what the two qubits started in.
BELL_RECIPES: List[Tuple[str, str, Tuple[str, str]]] = [
    ("|Φ⁺⟩", r"|\Phi^{+}\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}", ("0", "0")),
    ("|Φ⁻⟩", r"|\Phi^{-}\rangle = \frac{|00\rangle - |11\rangle}{\sqrt{2}}", ("1", "0")),
    ("|Ψ⁺⟩", r"|\Psi^{+}\rangle = \frac{|01\rangle + |10\rangle}{\sqrt{2}}", ("0", "1")),
    ("|Ψ⁻⟩", r"|\Psi^{-}\rangle = \frac{|01\rangle - |10\rangle}{\sqrt{2}}", ("1", "1")),
]


def bell_circuit(initial: Tuple[str, str]) -> CircuitSpec:
    """H on q0 then CNOT q0→q1 — the circuit that makes every Bell state."""
    return CircuitSpec(2, initial, (("H", (0,)), ("CNOT", (0, 1))))


SECTIONS: List[Section] = [
    Section(
        key="what",
        title="What a Bell state is",
        icon="🔗",
        body=(
            "A **Bell state** is one of four two-qubit states that are *maximally entangled*. "
            "They are the simplest states in quantum computing that cannot be described by "
            "giving each qubit its own state — the pair has a state, but neither member does.\n\n"
            "Compare two two-qubit states that both give 50/50 measurement statistics on each qubit:"
        ),
        equations=(
            r"\text{product: } |+\rangle \otimes |+\rangle = \frac{|00\rangle + |01\rangle + |10\rangle + |11\rangle}{2}",
            r"\text{entangled: } |\Phi^{+}\rangle = \frac{|00\rangle + |11\rangle}{\sqrt{2}}",
        ),
        takeaway="The first factorises into one state per qubit; the second provably does not.",
    ),
    Section(
        key="build",
        title="Building one: H then CNOT",
        icon="🔨",
        body=(
            "Every Bell state is two gates away from a computational basis state. Starting from "
            "$|00\\rangle$:\n\n"
            "**Step 1 — H on q0** puts the control qubit in superposition. The register is still a "
            "*product*: q0 is $|+\\rangle$, q1 is $|0\\rangle$, and both Bloch arrows have full length.\n\n"
            "**Step 2 — CNOT (control q0, target q1)** flips q1 only in the half of the superposition "
            "where q0 is $|1\\rangle$. That ties the two qubits together: the $|01\\rangle$ and "
            "$|10\\rangle$ amplitudes are gone, and only the *correlated* outcomes survive.\n\n"
            "Watch the Bloch arrows during step 2 — both shrink from full length to zero. That collapse "
            "is the visual signature of entanglement: neither qubit has a direction of its own any more."
        ),
        equations=(
            r"|00\rangle \;\xrightarrow{\;H \text{ on } q_0\;}\; \frac{|00\rangle + |10\rangle}{\sqrt{2}}"
            r" \;\xrightarrow{\;\mathrm{CNOT}\;}\; \frac{|00\rangle + |11\rangle}{\sqrt{2}} = |\Phi^{+}\rangle",
        ),
        circuit=bell_circuit(("0", "0")),
        try_it_label="Build |Φ⁺⟩ step by step",
        takeaway="H creates superposition; CNOT converts that superposition into correlation.",
    ),
    Section(
        key="four",
        title="The four Bell states",
        icon="🎼",
        body=(
            "The same two-gate circuit produces all four Bell states — the only thing that changes is "
            "what the two qubits started in. Together they form the **Bell basis**: four mutually "
            "orthogonal states that span the whole two-qubit space, just as $|00\\rangle, |01\\rangle, "
            "|10\\rangle, |11\\rangle$ do.\n\n"
            "The pattern is easy to remember: **q0 = |1⟩ gives the minus sign**, and "
            "**q1 = |1⟩ swaps Φ for Ψ** (that is, it makes the outcomes anti-correlated)."
        ),
        circuit=bell_circuit(("1", "1")),
        try_it_label="Build |Ψ⁻⟩ (the singlet)",
        takeaway="One circuit, four states: the inputs decide the sign and the correlation.",
    ),
    Section(
        key="entangled",
        title="Why it is really entangled",
        icon="🧪",
        body=(
            "It is worth proving, not just asserting. Suppose $|\\Phi^{+}\\rangle$ *were* a product state "
            "$(a|0\\rangle + b|1\\rangle) \\otimes (c|0\\rangle + d|1\\rangle)$. Multiplying out gives "
            "amplitudes $ac, ad, bc, bd$ for $|00\\rangle, |01\\rangle, |10\\rangle, |11\\rangle$. Matching "
            "them against $|\\Phi^{+}\\rangle$ requires\n\n"
            "$ac = \\tfrac{1}{\\sqrt{2}}$ (so $a \\ne 0$ and $c \\ne 0$) and "
            "$bd = \\tfrac{1}{\\sqrt{2}}$ (so $b \\ne 0$ and $d \\ne 0$),\n\n"
            "but also $ad = 0$ and $bc = 0$ — which forces one of them to be zero. **Contradiction**, so no "
            "such factorisation exists.\n\n"
            "The app shows the same fact geometrically. Tracing out q1 leaves q0 in the **maximally mixed** "
            "reduced state $\\rho = I/2$, whose Bloch vector is the origin. An arrow of length 0 means "
            "\"this qubit has no state of its own\"."
        ),
        equations=(
            r"\rho_{q_0} = \mathrm{Tr}_{q_1}|\Phi^{+}\rangle\langle\Phi^{+}| = \frac{1}{2}\begin{bmatrix} 1 & 0 \\ 0 & 1 \end{bmatrix}"
            r", \qquad (x,\ y,\ z) = (0,\ 0,\ 0)",
        ),
        circuit=bell_circuit(("0", "0")),
        try_it_label="See both arrows collapse to the origin",
        takeaway="Entanglement is not hidden information — the single-qubit description genuinely does not exist.",
    ),
    Section(
        key="measure",
        title="What measurement reveals",
        icon="🎯",
        body=(
            "Measure $|\\Phi^{+}\\rangle$ in the computational basis and you only ever see $|00\\rangle$ or "
            "$|11\\rangle$, each about half the time. $|01\\rangle$ and $|10\\rangle$ **never** occur — their "
            "amplitudes are exactly zero.\n\n"
            "Look at one qubit alone and it looks like a fair coin: q0 is $|0\\rangle$ half the time. The "
            "structure is in the *correlation*, not in either qubit. And the correlation is instant in the "
            "sense that once you measure q0, the state of q1 is fixed — measuring q0 and getting $1$ leaves "
            "q1 in $|1\\rangle$ with certainty.\n\n"
            "For $|\\Psi^{+}\\rangle$ and $|\\Psi^{-}\\rangle$ it is the opposite: the outcomes are perfectly "
            "**anti**-correlated, so you only ever see $|01\\rangle$ or $|10\\rangle$.\n\n"
            "Try it: load the circuit, then run 1000 shots in the Measurement card and watch two bars sit at "
            "~50% while the other two stay empty."
        ),
        circuit=bell_circuit(("0", "0")),
        try_it_label="Run 1000 shots on |Φ⁺⟩",
        takeaway="Each qubit alone looks random; the pair is perfectly correlated.",
    ),
    Section(
        key="undo",
        title="Entanglement can be undone",
        icon="↩️",
        body=(
            "Entangling is not a one-way door. The Bell circuit is built from gates that are their own "
            "inverses, so running it **backwards** — CNOT, then H on q0 — turns $|\\Phi^{+}\\rangle$ back into "
            "the plain product state $|00\\rangle$. The arrows grow back to full length.\n\n"
            "That reverse circuit is exactly how a quantum algorithm *reads* which Bell state it holds: it "
            "maps the four Bell states onto the four basis states $|00\\rangle, |10\\rangle, |01\\rangle, "
            "|11\\rangle$, which you can then simply measure. This **Bell measurement** is the key step in "
            "quantum teleportation and superdense coding."
        ),
        equations=(
            r"|\Phi^{+}\rangle \;\xrightarrow{\;\mathrm{CNOT}\;}\; \frac{|00\rangle + |10\rangle}{\sqrt{2}}"
            r" \;\xrightarrow{\;H \text{ on } q_0\;}\; |00\rangle",
        ),
        circuit=CircuitSpec(2, ("0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (0, 1)), ("H", (0,)))),
        try_it_label="Entangle, then disentangle",
        takeaway="Unitary gates are reversible — including the ones that create entanglement.",
    ),
    Section(
        key="beyond",
        title="Beyond two qubits",
        icon="🌐",
        body=(
            "Chaining another CNOT spreads the entanglement to a third qubit, giving the **GHZ state** "
            "$(|000\\rangle + |111\\rangle)/\\sqrt{2}$. Measure any one of the three and all three snap to the "
            "same value. Every arrow sits at the origin.\n\n"
            "This is where the Bloch sphere finally runs out: it can only ever draw one qubit's reduced "
            "state, so a three-way correlation is invisible in the three pictures. The state vector — and "
            "the measurement histogram — is what carries the information from here on."
        ),
        circuit=CircuitSpec(3, ("0", "0", "0"), (("H", (0,)), ("CNOT", (0, 1)), ("CNOT", (1, 2)))),
        try_it_label="Build the GHZ state",
        takeaway="Entanglement scales past two qubits, but the Bloch picture does not.",
    ),
]

SECTIONS_BY_KEY = {s.key: s for s in SECTIONS}
