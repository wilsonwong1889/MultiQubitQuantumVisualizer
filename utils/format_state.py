"""Turn engine values into LaTeX for the maths panels.

Every amplitude produced by the gate library from the four initial states is
one of 0, +/-1, +/-i, +/-1/sqrt(2), +/-i/sqrt(2), 1/2 or a unit phase
e^{i k pi/4}, so we print those exactly and only fall back to decimals for
anything else.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from quantum.complex_number import Complex
from quantum.matrix import Matrix
from quantum.state import BELL_STATES, NAMED_STATES, QuantumState

TOL = 1e-9
SQRT2 = math.sqrt(2.0)

# (value, LaTeX) pairs checked before falling back to decimals.
_SPECIAL_REALS: List[Tuple[float, str]] = [
    (0.0, "0"),
    (1.0, "1"),
    (-1.0, "-1"),
    (1 / SQRT2, r"\frac{1}{\sqrt{2}}"),
    (-1 / SQRT2, r"-\frac{1}{\sqrt{2}}"),
    (0.5, r"\frac{1}{2}"),
    (-0.5, r"-\frac{1}{2}"),
    (1 / (2 * SQRT2), r"\frac{1}{2\sqrt{2}}"),
    (-1 / (2 * SQRT2), r"-\frac{1}{2\sqrt{2}}"),
    (SQRT2, r"\sqrt{2}"),
    (-SQRT2, r"-\sqrt{2}"),
    (2.0, "2"),
    (-2.0, "-2"),
]

_SPECIAL_IMAGS: List[Tuple[float, str]] = [
    (1.0, "i"),
    (-1.0, "-i"),
    (1 / SQRT2, r"\frac{i}{\sqrt{2}}"),
    (-1 / SQRT2, r"-\frac{i}{\sqrt{2}}"),
    (0.5, r"\frac{i}{2}"),
    (-0.5, r"-\frac{i}{2}"),
]

# unit phases that are not on the real/imaginary axes: e^{i k pi/4}, k odd
_PHASES: List[Tuple[int, str]] = [(1, r"e^{i\pi/4}"), (3, r"e^{3i\pi/4}"), (-1, r"e^{-i\pi/4}"), (-3, r"e^{-3i\pi/4}")]
_PHASE_MAGNITUDES: List[Tuple[float, str]] = [(1.0, "%s"), (1 / SQRT2, r"\frac{%s}{\sqrt{2}}"), (0.5, r"\frac{%s}{2}")]


def real_latex(x: float) -> str:
    for value, text in _SPECIAL_REALS:
        if abs(x - value) < TOL:
            return text
    return f"{x:.3f}"


def _imag_latex(y: float) -> str:
    for value, text in _SPECIAL_IMAGS:
        if abs(y - value) < TOL:
            return text
    return f"{y:.3f}i"


def _polar_latex(z: Complex) -> Optional[str]:
    """e^{i pi/4}-style output for the phases the S and T gates produce."""
    angle = z.phase()
    for k, phase_text in _PHASES:
        if abs(angle - k * math.pi / 4) < 1e-9:
            for magnitude, template in _PHASE_MAGNITUDES:
                if abs(z.magnitude() - magnitude) < 1e-9:
                    return template % phase_text
    return None


def complex_latex(z: Complex) -> str:
    re_zero = abs(z.real) < TOL
    im_zero = abs(z.imag) < TOL
    if re_zero and im_zero:
        return "0"
    if im_zero:
        return real_latex(z.real)
    if re_zero:
        return _imag_latex(z.imag)
    polar = _polar_latex(z)
    if polar:
        return polar
    sign = "+" if z.imag > 0 else "-"
    return f"{real_latex(z.real)} {sign} {_imag_latex(abs(z.imag))}"


def _needs_parens(text: str) -> bool:
    return text.startswith("-") or " + " in text or " - " in text


def coefficient_latex(z: Complex) -> str:
    """Coefficient in front of a ket: 1 -> '', -1 -> '-', a+bi -> '(a+bi)'."""
    text = complex_latex(z)
    if text == "1":
        return ""
    if text == "-1":
        return "-"
    if " + " in text or " - " in text:
        return f"({text})"
    return text


def factor_latex(z: Complex) -> str:
    """A factor inside a product: wraps negatives and sums in parentheses."""
    text = complex_latex(z)
    return f"({text})" if _needs_parens(text) else text


def basis_ket(label: str) -> str:
    return rf"|{label}\rangle"


def table_cell(text: str) -> str:
    """Escape pipes so a cell containing kets does not split a markdown table.

    "|0⟩" would otherwise be read as a column separator; &#124; renders as a
    vertical bar but is invisible to the table parser.
    """
    return text.replace("|", "&#124;")


def ket_vert(label: str) -> str:
    r"""A ket in LaTeX using \vert, so the cell contains no literal pipe."""
    return rf"\vert {label}\rangle"


def gate_symbol_latex(symbol: str) -> str:
    """Single letters stay italic (H, X); multi-letter names are set upright (CNOT)."""
    return symbol if len(symbol) == 1 else r"\mathrm{%s}" % symbol


def vector_latex(v: Sequence[Complex]) -> str:
    return r"\begin{bmatrix} " + r" \\ ".join(complex_latex(a) for a in v) + r" \end{bmatrix}"


def matrix_latex(m: Matrix, scale_latex: str = "") -> str:
    body = r"\begin{bmatrix} " + r" \\ ".join(
        " & ".join(complex_latex(a) for a in row) for row in m.rows
    ) + r" \end{bmatrix}"
    return f"{scale_latex}{body}" if scale_latex else body


def _join_terms(terms: List[str]) -> str:
    out = terms[0]
    for term in terms[1:]:
        out += f" - {term[1:]}" if term.startswith("-") else f" + {term}"
    return out


def ket_latex(state: QuantumState) -> str:
    """sum of amplitude|label>, dropping zero terms and tidying +/- signs."""
    terms = [
        f"{coefficient_latex(amplitude)}{basis_ket(label)}"
        for amplitude, label in zip(state.amplitudes, state.basis_labels())
        if not amplitude.is_zero(TOL)
    ]
    return _join_terms(terms) if terms else "0"


def ket_latex_factored(state: QuantumState) -> Optional[str]:
    """(|0> +/- |1>)/sqrt 2 style output when every non-zero amplitude has the same size."""
    nonzero = [(label, a) for a, label in zip(state.amplitudes, state.basis_labels()) if not a.is_zero(TOL)]
    if len(nonzero) < 2:
        return None
    magnitude = nonzero[0][1].magnitude()
    if any(abs(a.magnitude() - magnitude) > 1e-6 for _, a in nonzero):
        return None
    if abs(magnitude - 1 / SQRT2) < 1e-6:
        wrap = r"\frac{%s}{\sqrt{2}}"
    elif abs(magnitude - 0.5) < 1e-6:
        wrap = r"\frac{1}{2}\left(%s\right)"
    elif abs(magnitude - 1 / (2 * SQRT2)) < 1e-6:
        wrap = r"\frac{1}{2\sqrt{2}}\left(%s\right)"
    else:
        return None
    global_phase = nonzero[0][1].scale(1.0 / magnitude)         # unit modulus
    undo_phase = global_phase.conjugate()
    inner_terms = []
    for label, a in nonzero:
        unit = (a * undo_phase).scale(1.0 / magnitude)           # +/-1, +/-i or e^{i k pi/4}
        inner_terms.append(f"{coefficient_latex(unit)}{basis_ket(label)}")
    return coefficient_latex(global_phase) + wrap % _join_terms(inner_terms)


@dataclass(frozen=True)
class RecognisedState:
    """A state matched (up to global phase) against one of the named states."""

    name_text: str        # e.g. "|−⟩"
    name_latex: str       # e.g. "|-\rangle"
    phase: Complex        # the global phase factor, e.g. -1
    phase_latex: str      # "", "-", "i", "-i", or e^{i k pi/4}

    @property
    def latex(self) -> str:
        return f"{self.phase_latex}{self.name_latex}"

    @property
    def text(self) -> str:
        prefix = {"": "", "-": "−", "i": "i", "-i": "−i"}.get(self.phase_latex, self.phase_latex)
        return f"{prefix}{self.name_text}"

    @property
    def has_phase(self) -> bool:
        return self.phase_latex != ""


def _phase_latex(phase: Complex) -> str:
    text = complex_latex(phase)
    if text == "1":
        return ""
    if text == "-1":
        return "-"
    if text in ("i", "-i") or text.startswith("e^"):
        return text
    return r"e^{i\,%.2f}" % phase.phase()


def recognise_state(state: QuantumState) -> Optional[RecognisedState]:
    catalogue = NAMED_STATES if state.num_qubits == 1 else BELL_STATES if state.num_qubits == 2 else []
    for name_text, name_latex, named in catalogue:
        phase = state.global_phase_relative_to(named)
        if phase is not None:
            return RecognisedState(name_text, name_latex, phase, _phase_latex(phase))
    return None


def state_chain_parts(state: QuantumState) -> List[str]:
    """[expanded ket, factored form?, recognised name?] without duplicates."""
    parts = [ket_latex(state)]
    factored = ket_latex_factored(state)
    if factored and factored != parts[-1]:
        parts.append(factored)
    recognised = recognise_state(state)
    if recognised and recognised.latex not in parts:
        parts.append(recognised.latex)
    return parts


def state_chain_latex(state: QuantumState, symbol: str = r"|\psi\rangle") -> str:
    """|psi> = a|0> + b|1> [= factored form] [= named state], on one line."""
    return f"{symbol} = " + " = ".join(state_chain_parts(state))


def state_chain_aligned(state: QuantumState, symbol: str = r"|\psi\rangle") -> str:
    """Same as state_chain_latex but the simplifications go on a second line."""
    parts = state_chain_parts(state)
    if len(parts) == 1:
        return f"{symbol} = {parts[0]}"
    return (r"\begin{aligned} %s &= %s \\ &= %s \end{aligned}"
            % (symbol, parts[0], " = ".join(parts[1:])))


def complex_text(z: Complex) -> str:
    """Compact plain-text version (for captions and tooltips)."""
    re_zero = abs(z.real) < TOL
    im_zero = abs(z.imag) < TOL
    if re_zero and im_zero:
        return "0"
    if im_zero:
        return f"{z.real:.3f}".rstrip("0").rstrip(".")
    if re_zero:
        return f"{z.imag:.3f}".rstrip("0").rstrip(".") + "i"
    sign = "+" if z.imag > 0 else "−"
    return f"{z.real:.3f} {sign} {abs(z.imag):.3f}i"


def ket_text(state: QuantumState) -> str:
    """Plain-text ket, e.g. '0.707|00⟩ + 0.707|11⟩'."""
    terms = []
    for amplitude, label in zip(state.amplitudes, state.basis_labels()):
        if amplitude.is_zero(TOL):
            continue
        coefficient = complex_text(amplitude)
        if coefficient == "1":
            coefficient = ""
        elif coefficient == "-1":
            coefficient = "−"
        elif " " in coefficient:
            coefficient = f"({coefficient})"
        terms.append(f"{coefficient}|{label}⟩")
    if not terms:
        return "0"
    out = terms[0]
    for term in terms[1:]:
        # a leading minus becomes a binary minus: "a + -b" reads as "a − b"
        out += f" − {term[1:]}" if term.startswith(("-", "−")) else f" + {term}"
    return out


def state_name_text(state: QuantumState) -> str:
    """Plain-text name for explanations, falling back to the ket expression."""
    recognised = recognise_state(state)
    return recognised.text if recognised else ket_text(state)


def coordinate_text(x: float) -> str:
    if abs(x) < 5e-4:
        x = 0.0
    return f"{x:.3f}"
