# ⚛️ Qubit Visualizer

An interactive learning website that shows what happens to a qubit as it passes
through quantum gates — visually, algebraically, and on the Bloch sphere.

Pick an initial state (|0⟩, |1⟩, |+⟩, |−⟩), add H / X / Y / Z gates to a circuit,
and step through it one gate at a time. At every step the circuit, state vector,
ket notation, gate matrix, matrix multiplication, measurement probabilities,
Bloch coordinates and Bloch-sphere arrow all update from the same underlying state.

Built in Python: a dependency-free quantum engine, a [Streamlit](https://streamlit.io)
UI, and a [Plotly](https://plotly.com/python/) 3D Bloch sphere.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Streamlit opens the site at <http://localhost:8501>.

## Run the tests

```bash
pip install -r requirements-dev.txt
pytest
```

The tests cover the plan's mathematical testing plan (X|0⟩ = |1⟩, H|0⟩ = |+⟩,
Z|+⟩ = |−⟩, H² = X² = Y² = Z² = I, normalisation after every gate, unit-length
Bloch vectors, the named-state Bloch table) plus a check that each gate's
rotation axis reproduces the amplitude result, the LaTeX formatting, and a
headless Streamlit `AppTest` smoke test that drives the real UI.

## Project structure

```
qubit-visualizer/
  app.py                      Streamlit entry point: layout + session state
  quantum/                    Quantum engine (no UI dependencies)
    complex_number.py         Complex: add, sub, mul, conjugate, |z|, |z|^2
    matrix.py                 Matrix2x2 and matrix-vector multiplication
    gates.py                  X, Y, Z, H with Bloch rotation axis/angle
    qubit.py                  QubitState, initial states, apply_gate, simulate
    bloch.py                  amplitudes -> (x, y, z), Rodrigues rotation path
  components/                 UI panels
    circuit.py                Horizontal wire with clickable gate nodes
    controls.py               Previous / Next / Undo / Reset
    state_panel.py            Ket, vector and amplitudes
    probability_panel.py      P(0), P(1) with bars
    matrix_calculation.py     Before -> gate matrix -> multiplication -> after
    explanation.py            Gate-specific teaching text
    bloch_sphere.py           Plotly 3D sphere, arrow, path and animation
    gate_panel.py             Gate reference
  data/
    gate_descriptions.py      Plain-language descriptions per gate
    presets.py                One-click example circuits
  utils/
    format_state.py           Exact LaTeX for 0, ±1, ±i, ±1/√2 ...
  tests/                      pytest suite (engine, formatting, UI smoke test)
```

## How it works

The app stores only three things in session state — the initial state, the
list of gate symbols, and the current step. On every rerun it asks the engine
for `simulate(initial, gates)`, which returns the state after each gate, and
every panel is derived from `states[step]`. Nothing displayed is stored
separately, so the panels can never disagree.

The Bloch vector is computed directly from the amplitudes:

```
x = 2 Re(α* β)      y = 2 Im(α* β)      z = |α|² − |β|²
```

Every Version-1 gate is a 180° rotation of the sphere (X, Y, Z about their own
axis; H about the (x + z)/√2 diagonal). The animation sweeps the arrow along
that rotation using Rodrigues' formula, and a test asserts that the geometric
end point matches the algebraic one for every gate and named state.

## Deploy to Streamlit Community Cloud

The repo is ready for [Streamlit Community Cloud](https://share.streamlit.io):
sign in with GitHub, choose **New app**, pick this repository, branch `main`,
main file `app.py`, and deploy. Dependencies come from `requirements.txt`.

## Version 2 ideas (from the project plan)

Two qubits, CNOT / CZ, tensor products, |00⟩…|11⟩, entanglement and Bell
states — at which point a single Bloch arrow is no longer enough, which is the
lesson.
