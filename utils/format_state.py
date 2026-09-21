"""Turn engine values into LaTeX for the maths panels.

Every amplitude produced by H, X, Y, Z from the four initial states is one of
0, +/-1, +/-i, +/-1/sqrt(2) or +/-i/sqrt(2), so we print those exactly and only
fall back to decimals for anything else.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

from quantum.complex_number import Complex
from quantum.matrix import Matrix2x2
from quantum.qubit import NAMED_STATES, QubitState

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


def complex_latex(z: Complex) -> str:
    re_zero = abs(z.real) < TOL
    im_zero = abs(z.imag) < TOL
    if re_zero and im_zero:
        return "0"
    if im_zero:
        return real_latex(z.real)
    if re_zero:
        return _imag_latex(z.imag)
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


def vector_latex(v: Tuple[Complex, Complex]) -> str:
    return r"\begin{bmatrix} %s \\ %s \end{bmatrix}" % (complex_latex(v[0]), complex_latex(v[1]))


def matrix_latex(m: Matrix2x2, scale_latex: str = "") -> str:
    body = r"\begin{bmatrix} %s & %s \\ %s & %s \end{bmatrix}" % (
        complex_latex(m.a), complex_latex(m.b), complex_latex(m.c), complex_latex(m.d),
    )
    return f"{scale_latex}{body}" if scale_latex else body


def ket_latex(state: QubitState) -> str:
    """alpha|0> + beta|1>, dropping zero terms and tidying +/- signs."""
    terms: List[str] = []
    for amplitude, basis in ((state.alpha, r"|0\rangle"), (state.beta, r"|1\rangle")):
        if amplitude.is_zero(TOL):
            continue
        terms.append(f"{coefficient_latex(amplitude)}{basis}")
    if not terms:
        return "0"
    out = terms[0]
    for term in terms[1:]:
        out += f" - {term[1:]}" if term.startswith("-") else f" + {term}"
    return out


def ket_latex_factored(state: QubitState) -> Optional[str]:
    """For equal-magnitude superpositions, (|0> +/- |1>)/sqrt 2 style output."""
    if abs(state.alpha.magnitude() - 1 / SQRT2) > 1e-6 or abs(state.beta.magnitude() - 1 / SQRT2) > 1e-6:
        return None
    global_phase = state.alpha.scale(SQRT2)          # unit-modulus factor in front
    relative = state.beta.mul(state.alpha.conjugate()).scale(2.0)  # beta/alpha for |alpha|^2 = 1/2
    prefix = coefficient_latex(global_phase)   # "", "-", "i", "-i" or "(a + bi)"
    rel = coefficient_latex(relative)
    if rel.startswith("-"):
        inner = r"|0\rangle - %s|1\rangle" % rel[1:]
    else:
        inner = r"|0\rangle + %s|1\rangle" % rel
    return r"%s\frac{%s}{\sqrt{2}}" % (prefix, inner)


@dataclass(frozen=True)
class RecognisedState:
    """A state matched (up to global phase) against one of the named states."""

    name_text: str        # e.g. "|−⟩"
    name_latex: str       # e.g. "|-\rangle"
    phase: Complex        # the global phase factor, e.g. -1
    phase_latex: str      # "", "-", "i", "-i", or e^{i phi}

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
    if text in ("-1", "i", "-i"):
        return "-" if text == "-1" else text
    return r"e^{i\,%.2f}" % phase.phase()


def recognise_state(state: QubitState) -> Optional[RecognisedState]:
    for name_text, name_latex, named in NAMED_STATES:
        phase = state.global_phase_relative_to(named)
        if phase is not None:
            return RecognisedState(name_text, name_latex, phase, _phase_latex(phase))
    return None


def state_chain_latex(state: QubitState, symbol: str = r"|\psi\rangle") -> str:
    """|psi> = a|0> + b|1> [= factored form] [= named state], on one line."""
    return f"{symbol} = " + " = ".join(state_chain_parts(state))


def state_chain_parts(state: QubitState) -> List[str]:
    """[expanded ket, factored form?, recognised name?] without duplicates."""
    parts = [ket_latex(state)]
    factored = ket_latex_factored(state)
    if factored and factored != parts[-1]:
        parts.append(factored)
    recognised = recognise_state(state)
    if recognised and recognised.latex not in parts:
        parts.append(recognised.latex)
    return parts


def state_chain_aligned(state: QubitState, symbol: str = r"|\psi\rangle") -> str:
    """Same as state_chain_latex but the simplifications go on a second line."""
    parts = state_chain_parts(state)
    if len(parts) == 1:
        return f"{symbol} = {parts[0]}"
    return (r"\begin{aligned} %s &= %s \\ &= %s \end{aligned}"
            % (symbol, parts[0], " = ".join(parts[1:])))


def state_name_text(state: QubitState) -> str:
    """Plain-text name for explanations, falling back to the ket expression."""
    recognised = recognise_state(state)
    if recognised:
        return recognised.text
    return "α|0⟩ + β|1⟩ with α = %s, β = %s" % (complex_text(state.alpha), complex_text(state.beta))


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


def coordinate_text(x: float) -> str:
    if abs(x) < 5e-4:
        x = 0.0
    return f"{x:.3f}"
