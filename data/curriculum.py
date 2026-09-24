"""The course: eight pages building from a single qubit up to Bell states.

Each module is a page of lesson sections; the practice questions that go with it
live in data/practice.py, tagged with the same module key. Everything factual
here is checked against the quantum engine by tests/test_lesson.py.
"""
from __future__ import annotations

from typing import Dict, List

from data.lesson import CircuitSpec, Module, Section
from data.lesson import SECTIONS as BELL_SECTIONS

# --- circuits the lessons refer to -------------------------------------------
KET0 = CircuitSpec(1, ("0",), ())
KET_PLUS_BY_H = CircuitSpec(1, ("0",), (("H", (0,)),))
KET_MINUS_BY_H = CircuitSpec(1, ("1",), (("H", (0,)),))
BIT_FLIP = CircuitSpec(1, ("0",), (("X", (0,)),))
H_THEN_H = CircuitSpec(1, ("0",), (("H", (0,)), ("H", (0,))))
Z_ON_PLUS = CircuitSpec(1, ("+",), (("Z", (0,)),))
Y_ON_KET0 = CircuitSpec(1, ("0",), (("Y", (0,)),))
X_ON_MINUS = CircuitSpec(1, ("-",), (("X", (0,)),))
S_ON_PLUS = CircuitSpec(1, ("+",), (("S", (0,)),))
T_TWICE = CircuitSpec(1, ("+",), (("T", (0,)), ("T", (0,))))
HZH = CircuitSpec(1, ("0",), (("H", (0,)), ("Z", (0,)), ("H", (0,))))
PHASE_THEN_H = CircuitSpec(1, ("0",), (("H", (0,)), ("Z", (0,)), ("H", (0,))))

TWO_PRODUCT = CircuitSpec(2, ("0", "0"), (("H", (0,)),))
TWO_PLUS_PLUS = CircuitSpec(2, ("0", "0"), (("H", (0,)), ("H", (1,))))
TWO_INDEPENDENT = CircuitSpec(2, ("0", "0"), (("H", (0,)), ("X", (1,))))
SWAP_01 = CircuitSpec(2, ("0", "1"), (("SWAP", (0, 1)),))
CNOT_BASIS = CircuitSpec(2, ("1", "0"), (("CNOT", (0, 1)),))
CNOT_INERT = CircuitSpec(2, ("0", "1"), (("CNOT", (0, 1)),))
CZ_BASIS = CircuitSpec(2, ("1", "1"), (("CZ", (0, 1)),))
CNOT_ON_SUPERPOSITION = CircuitSpec(2, ("0", "0"), (("H", (0,)), ("CNOT", (0, 1))))


MODULES: List[Module] = [
    # ------------------------------------------------------------------ 1
    Module(
        key="qubits",
        number=1,
        title="Qubits & superposition",
        icon="🎲",
        summary="What a qubit is, what the numbers in front of the kets mean, and why superposition is not just uncertainty.",
        sections=(
            Section(
                key="bit_vs_qubit",
                title="From bit to qubit",
                icon="🎲",
                body=(
                    "A classical bit is either $0$ or $1$. A **qubit** can be in either of those states — "
                    "written $|0\\rangle$ and $|1\\rangle$ — but also in a **superposition** of both at once:"
                ),
                equations=(r"|\psi\rangle = \alpha|0\rangle + \beta|1\rangle",),
                circuit=KET0,
                try_it_label="Start with a qubit in |0⟩",
                takeaway="A qubit's state is two complex numbers, not one bit.",
            ),
            Section(
                key="amplitudes",
                title="Amplitudes and normalisation",
                icon="📏",
                body=(
                    "$\\alpha$ and $\\beta$ are **amplitudes**: complex numbers, not probabilities. They can be "
                    "negative or imaginary, which is exactly what makes quantum computing different from "
                    "flipping a weighted coin.\n\n"
                    "The one rule they must obey is **normalisation** — the squared magnitudes have to add to 1:"
                ),
                equations=(r"|\alpha|^2 + |\beta|^2 = 1",),
                circuit=KET_PLUS_BY_H,
                try_it_label="See α and β for |+⟩",
                takeaway="Amplitudes can be negative or complex; only their squared magnitudes must sum to 1.",
            ),
            Section(
                key="plus_minus",
                title="The states |+⟩ and |−⟩",
                icon="➕",
                body=(
                    "The two most important superpositions are the equal ones. They have **identical** "
                    "measurement statistics — 50/50 either way — and yet they are different states, because "
                    "the sign of $\\beta$ differs:"
                ),
                equations=(
                    r"|+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \qquad "
                    r"|-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}",
                ),
                circuit=KET_MINUS_BY_H,
                try_it_label="Build |−⟩ from |1⟩",
                takeaway="Two states can give identical measurement odds and still be genuinely different.",
            ),
            Section(
                key="not_ignorance",
                title="Superposition is not ignorance",
                icon="🧠",
                body=(
                    "It is tempting to read \"50/50\" as *the qubit is secretly 0 or 1 and I just don't know "
                    "which*. That reading is wrong, and this app can show you why.\n\n"
                    "Apply **H twice** to $|0\\rangle$. If the qubit were secretly $0$ or $1$ after the first H, "
                    "the second H would scramble it again and you would land on 50/50. Instead you get "
                    "$|0\\rangle$ **every time** — the two paths to $|1\\rangle$ cancel out.\n\n"
                    "That cancellation is **interference**, and it only makes sense if both branches were "
                    "genuinely there."
                ),
                equations=(r"H\,H|0\rangle = |0\rangle \quad\text{(not 50/50)}",),
                circuit=H_THEN_H,
                try_it_label="Apply H twice and watch it return",
                takeaway="Interference proves the superposition was real, not just unknown information.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 2
    Module(
        key="measurement",
        number=2,
        title="Measurement",
        icon="🎯",
        summary="The Born rule, why amplitudes get squared, and what collapse means for the rest of your circuit.",
        prerequisite="qubits",
        sections=(
            Section(
                key="born",
                title="The Born rule",
                icon="🎯",
                body=(
                    "You can never read $\\alpha$ and $\\beta$ off a qubit. Measuring in the computational "
                    "basis gives you a single bit, $0$ or $1$, with probabilities given by the **Born rule**:"
                ),
                equations=(r"P(0) = |\alpha|^2, \qquad P(1) = |\beta|^2",),
                circuit=KET_PLUS_BY_H,
                try_it_label="Measure |+⟩ — try 1 shot, then 1000",
                takeaway="Measurement turns two complex amplitudes into one classical bit.",
            ),
            Section(
                key="why_squared",
                title="Why squared?",
                icon="²",
                body=(
                    "Because an amplitude can be negative or imaginary, and a probability cannot. The squared "
                    "magnitude $|\\alpha|^2 = \\alpha^{*}\\alpha$ is always a non-negative real number, and "
                    "normalisation guarantees the outcomes sum to 100%.\n\n"
                    "This is also why $|+\\rangle$ and $|-\\rangle$ measure the same: "
                    "$|{-\\tfrac{1}{\\sqrt2}}|^2 = |{\\tfrac{1}{\\sqrt2}}|^2 = \\tfrac12$. The minus sign is "
                    "invisible to a measurement in this basis — but it is not invisible to later **gates**."
                ),
                circuit=Z_ON_PLUS,
                try_it_label="Flip |+⟩ to |−⟩ and watch the bars not move",
                takeaway="Squaring discards the sign, which is why phase hides from measurement but not from gates.",
            ),
            Section(
                key="collapse",
                title="Collapse",
                icon="💥",
                body=(
                    "Measurement is not a passive read. Once you observe $0$, the state **is** $|0\\rangle$ — "
                    "the other amplitude is gone, and measuring again gives $0$ forever.\n\n"
                    "That is why measuring in the middle of a circuit is destructive: it removes the very "
                    "superposition the rest of your gates were going to interfere. In the Measurement card, "
                    "run **1 shot** to see a single collapsed outcome, or **1000 shots** to rebuild the "
                    "distribution by repeating the whole experiment from scratch each time."
                ),
                circuit=KET_PLUS_BY_H,
                try_it_label="Run a single shot and see the collapse",
                takeaway="One shot gives one outcome; the distribution only appears over many repetitions.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 3
    Module(
        key="bloch",
        number=3,
        title="The Bloch sphere",
        icon="🌐",
        summary="The picture that makes phase visible: every single-qubit state as a point on a sphere.",
        prerequisite="measurement",
        sections=(
            Section(
                key="geometry",
                title="A sphere of states",
                icon="🌐",
                body=(
                    "Normalisation plus the fact that a global phase is unobservable leaves a qubit with "
                    "exactly two real degrees of freedom — so every pure state fits on the surface of a "
                    "sphere. The coordinates come straight from the amplitudes:"
                ),
                equations=(
                    r"x = 2\,\mathrm{Re}(\alpha^{*}\beta), \qquad y = 2\,\mathrm{Im}(\alpha^{*}\beta), "
                    r"\qquad z = |\alpha|^2 - |\beta|^2",
                ),
                circuit=KET0,
                try_it_label="See |0⟩ at the north pole",
                takeaway="North pole is |0⟩, south pole is |1⟩, and the equator is the equal superpositions.",
            ),
            Section(
                key="phase_visible",
                title="Where the phase went",
                icon="👁️",
                body=(
                    "This is what the Bloch sphere buys you: $|+\\rangle$ and $|-\\rangle$ have the same "
                    "probabilities but sit on **opposite sides** of the equator. The phase that measurement "
                    "throws away is a direction here.\n\n"
                    "Four equatorial states matter enough to have names: $|+\\rangle$ and $|-\\rangle$ on the "
                    "$x$ axis, $|{+i}\\rangle$ and $|{-i}\\rangle$ on the $y$ axis. All four are 50/50 in the "
                    "computational basis and all four are different states."
                ),
                circuit=Z_ON_PLUS,
                try_it_label="Watch |+⟩ swing to |−⟩",
                takeaway="Phase is invisible to measurement but perfectly visible as a direction.",
            ),
            Section(
                key="global_phase",
                title="Global vs relative phase",
                icon="🔄",
                body=(
                    "Multiplying the *whole* state by a phase — $|\\psi\\rangle \\to -|\\psi\\rangle$ — changes "
                    "nothing physical. The Bloch arrow does not move, and no measurement in any basis can "
                    "detect it. That is a **global phase**.\n\n"
                    "A **relative** phase between $\\alpha$ and $\\beta$ is different: it rotates the arrow "
                    "around the equator and is entirely physical. Applying X to $|-\\rangle$ gives "
                    "$-|-\\rangle$ — the maths changes, the arrow does not."
                ),
                equations=(r"X|-\rangle = -|-\rangle \quad\text{(same point on the sphere)}",),
                circuit=X_ON_MINUS,
                try_it_label="Apply X to |−⟩ — the arrow stays put",
                takeaway="Global phase: no physical effect. Relative phase: a real, visible rotation.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 4
    Module(
        key="gates",
        number=4,
        title="Single-qubit gates",
        icon="🎛️",
        summary="X, Y, Z and H as matrices — and as rotations of the Bloch sphere.",
        prerequisite="bloch",
        sections=(
            Section(
                key="unitary",
                title="Gates are matrices",
                icon="🎛️",
                body=(
                    "A gate acts on a qubit by matrix multiplication: the new amplitudes are the matrix "
                    "times the old ones. Every gate must be **unitary** ($U U^{\\dagger} = I$), which is "
                    "exactly the condition that keeps $|\\alpha|^2 + |\\beta|^2 = 1$.\n\n"
                    "Unitary also means **reversible** — every quantum gate can be undone, which is not true "
                    "of classical gates like AND."
                ),
                equations=(
                    r"\begin{bmatrix} \alpha' \\ \beta' \end{bmatrix} = U \begin{bmatrix} \alpha \\ \beta \end{bmatrix}",
                ),
                circuit=BIT_FLIP,
                try_it_label="See the full X multiplication",
                takeaway="Unitary = probability-preserving = reversible.",
            ),
            Section(
                key="paulis",
                title="The Pauli gates X, Y, Z",
                icon="🔀",
                body=(
                    "**X** is the quantum NOT — it swaps $\\alpha$ and $\\beta$, taking $|0\\rangle$ to "
                    "$|1\\rangle$.\n\n"
                    "**Z** leaves $|0\\rangle$ alone and flips the sign of $|1\\rangle$ — a *phase* flip, "
                    "invisible in the computational basis but a half-turn of the equator.\n\n"
                    "**Y** does both at once ($Y = iXZ$), which is where the factors of $i$ come from.\n\n"
                    "Each is a **180° rotation** of the Bloch sphere about its own axis, and each is its own "
                    "inverse: $X^2 = Y^2 = Z^2 = I$."
                ),
                circuit=Y_ON_KET0,
                try_it_label="Apply Y to |0⟩ and read off the i",
                takeaway="X flips the bit, Z flips the phase, Y flips both.",
            ),
            Section(
                key="hadamard",
                title="Hadamard: the superposition gate",
                icon="🌓",
                body=(
                    "H is the gate that takes you *into* and *out of* superposition. It maps the poles to the "
                    "equator and back:"
                ),
                equations=(
                    r"H|0\rangle = |+\rangle, \quad H|1\rangle = |-\rangle, \quad "
                    r"H|+\rangle = |0\rangle, \quad H|-\rangle = |1\rangle",
                ),
                circuit=KET_MINUS_BY_H,
                try_it_label="Apply H to |1⟩",
                takeaway="H swaps the Z axis with the X axis — it is a 180° turn about the diagonal.",
            ),
            Section(
                key="conjugation",
                title="Gates compose",
                icon="🔗",
                body=(
                    "Circuits are just matrix products, and the order matters. A classic identity worth "
                    "knowing is that H turns a phase flip into a bit flip:"
                ),
                equations=(r"H\,Z\,H = X",),
                circuit=HZH,
                try_it_label="Run H, Z, H from |0⟩ — you land on |1⟩",
                takeaway="Sandwiching a gate between Hadamards swaps the roles of bit flips and phase flips.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 5
    Module(
        key="phase",
        number=5,
        title="Phase gates: S and T",
        icon="🌀",
        summary="Smaller rotations about the Z axis — and why they matter even though they never change the odds.",
        prerequisite="gates",
        sections=(
            Section(
                key="s_gate",
                title="S: a quarter turn",
                icon="🌀",
                body=(
                    "Z is a half-turn about the $z$ axis. **S** is a quarter-turn: it multiplies the "
                    "$|1\\rangle$ amplitude by $i$ instead of $-1$. Two of them make a Z:"
                ),
                equations=(r"S = \begin{bmatrix} 1 & 0 \\ 0 & i \end{bmatrix}, \qquad S\,S = Z",),
                circuit=S_ON_PLUS,
                try_it_label="Apply S to |+⟩ — the arrow moves to |+i⟩",
                takeaway="S walks the state a quarter of the way around the equator.",
            ),
            Section(
                key="t_gate",
                title="T: an eighth turn",
                icon="⅛",
                body=(
                    "**T** goes smaller still — $45°$ about $z$, multiplying $|1\\rangle$ by "
                    "$e^{i\\pi/4}$. And $T\\,T = S$.\n\n"
                    "T matters out of proportion to its size: H and CNOT alone can only produce a limited set "
                    "of states, but **H, CNOT and T together are universal** — they can approximate any "
                    "quantum computation to any accuracy you like."
                ),
                equations=(r"T = \begin{bmatrix} 1 & 0 \\ 0 & e^{i\pi/4} \end{bmatrix}, \qquad T\,T = S",),
                circuit=T_TWICE,
                try_it_label="Apply T twice and confirm you get |+i⟩",
                takeaway="T is small, but it is what makes the gate set universal.",
            ),
            Section(
                key="phase_matters",
                title="Phase you cannot measure — yet",
                icon="🕵️",
                body=(
                    "Every gate in this module leaves the computational-basis probabilities **completely "
                    "unchanged**. Measure after any number of S and T gates and you will see exactly the "
                    "distribution you had before.\n\n"
                    "So why bother? Because a later gate can convert that phase into something measurable. "
                    "That is the whole shape of a quantum algorithm: **write information into phases, then "
                    "use interference to turn it back into probabilities.** The $H \\to Z \\to H$ sequence "
                    "from the last module is the smallest example — the phase Z wrote became a bit flip."
                ),
                circuit=Z_ON_PLUS,
                try_it_label="Confirm the bars do not move",
                takeaway="Phase is where quantum algorithms do their work; interference cashes it in.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 6
    Module(
        key="two_qubits",
        number=6,
        title="Two qubits",
        icon="🔢",
        summary="Tensor products, four basis states, and what it means for two qubits to be independent.",
        prerequisite="phase",
        sections=(
            Section(
                key="tensor",
                title="Four amplitudes, not two",
                icon="🔢",
                body=(
                    "Two qubits have **four** basis states — $|00\\rangle, |01\\rangle, |10\\rangle, "
                    "|11\\rangle$ — and therefore four amplitudes. In general $n$ qubits need $2^n$ of them, "
                    "which is why simulating many qubits classically gets expensive so fast.\n\n"
                    "In this app **qubit 0 is the leftmost bit** of a label, so $|10\\rangle$ means q0 is "
                    "$|1\\rangle$ and q1 is $|0\\rangle$."
                ),
                equations=(
                    r"|\psi\rangle = c_{00}|00\rangle + c_{01}|01\rangle + c_{10}|10\rangle + c_{11}|11\rangle",
                ),
                circuit=CircuitSpec(2, ("0", "1"), ()),
                try_it_label="Set up |01⟩ and read the vector",
                takeaway="n qubits carry 2ⁿ amplitudes — the source of quantum computing's power and of its simulation cost.",
            ),
            Section(
                key="product",
                title="Independent qubits: the tensor product",
                icon="⊗",
                body=(
                    "If two qubits have their own states, the pair's state is their **tensor product** — "
                    "multiply every amplitude of the first by every amplitude of the second:"
                ),
                equations=(
                    r"|+\rangle \otimes |0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}} \otimes |0\rangle"
                    r" = \frac{|00\rangle + |10\rangle}{\sqrt{2}}",
                ),
                circuit=TWO_PRODUCT,
                try_it_label="Put q0 in superposition, leave q1 alone",
                takeaway="A state that factorises like this is called a product state — both arrows stay full length.",
            ),
            Section(
                key="local",
                title="Gates act locally",
                icon="📍",
                body=(
                    "A single-qubit gate applied to q1 does nothing to q0. Formally the register operator is "
                    "$I \\otimes U$ — the identity on the qubit you are not touching.\n\n"
                    "So as long as you only use single-qubit gates, two qubits behave like two separate "
                    "one-qubit experiments that happen to be written on the same page. Nothing interesting "
                    "connects them yet."
                ),
                equations=(r"U \text{ on } q_1 \;\equiv\; I \otimes U",),
                circuit=TWO_INDEPENDENT,
                try_it_label="H on q0, X on q1 — two independent stories",
                takeaway="Single-qubit gates can never entangle qubits, however many you apply.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 7
    Module(
        key="controlled",
        number=7,
        title="Controlled gates",
        icon="🎚️",
        summary="CNOT, CZ and SWAP — the gates that let one qubit's state depend on another's.",
        prerequisite="two_qubits",
        sections=(
            Section(
                key="cnot",
                title="CNOT: flip, but only sometimes",
                icon="🎚️",
                body=(
                    "**CNOT** takes a **control** qubit and a **target** qubit. If the control is "
                    "$|1\\rangle$, it applies X to the target; if the control is $|0\\rangle$, it does "
                    "nothing. On basis states it is completely classical — it is just the reversible XOR:"
                ),
                equations=(r"\mathrm{CNOT}|a, b\rangle = |a,\; a \oplus b\rangle",),
                circuit=CNOT_BASIS,
                try_it_label="CNOT on |10⟩ → |11⟩",
                takeaway="On basis states, CNOT is nothing more exotic than a controlled bit flip.",
            ),
            Section(
                key="cz_swap",
                title="CZ and SWAP",
                icon="🔁",
                body=(
                    "**CZ** applies Z to the target when the control is $|1\\rangle$ — so it flips the sign of "
                    "$|11\\rangle$ and leaves the other three alone. That makes it perfectly **symmetric**: "
                    "swap the control and the target and you get the same gate.\n\n"
                    "**SWAP** exchanges the two qubits outright, and can be built from three CNOTs with "
                    "alternating control and target."
                ),
                equations=(r"\mathrm{CZ}|11\rangle = -|11\rangle, \qquad \mathrm{SWAP}|01\rangle = |10\rangle",),
                circuit=SWAP_01,
                try_it_label="Swap |01⟩ into |10⟩",
                takeaway="CZ is symmetric in its two qubits; CNOT is not.",
            ),
            Section(
                key="superposed_control",
                title="Now put the control in superposition",
                icon="✨",
                body=(
                    "Here is the step that makes two-qubit gates interesting. Everything above was classical "
                    "because the control was $|0\\rangle$ or $|1\\rangle$. Put the control in a "
                    "**superposition** and CNOT has to act on both branches at once:\n\n"
                    "the $|00\\rangle$ branch is left alone, and the $|10\\rangle$ branch becomes "
                    "$|11\\rangle$. What comes out is a state where the two qubits' values are linked and "
                    "neither has a value of its own.\n\n"
                    "That is **entanglement** — and the state you just built is the first Bell state, which "
                    "is where the next module starts."
                ),
                equations=(
                    r"\frac{|00\rangle + |10\rangle}{\sqrt{2}} \;\xrightarrow{\;\mathrm{CNOT}\;}\; "
                    r"\frac{|00\rangle + |11\rangle}{\sqrt{2}}",
                ),
                circuit=CNOT_ON_SUPERPOSITION,
                try_it_label="Step through the entangling moment",
                takeaway="A controlled gate plus a superposed control is exactly how entanglement is made.",
            ),
        ),
    ),
    # ------------------------------------------------------------------ 8
    Module(
        key="bell",
        number=8,
        title="Bell states",
        icon="🔗",
        summary="The four maximally entangled two-qubit states — how to build them, why they cannot be taken apart, and what measurement reveals.",
        prerequisite="controlled",
        sections=tuple(BELL_SECTIONS),
    ),
]

MODULES_BY_KEY: Dict[str, Module] = {m.key: m for m in MODULES}
MODULE_KEYS: List[str] = [m.key for m in MODULES]
