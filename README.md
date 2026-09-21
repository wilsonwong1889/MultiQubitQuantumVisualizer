# ⚛️ Multi-Qubit Quantum Visualizer

An interactive learning website that shows what happens to qubits as they pass
through quantum gates — visually, algebraically, and on the Bloch sphere.

Set up a register of 1–3 qubits, add gates (H, X, Y, Z, S, T, CNOT, CZ, SWAP),
and step through the circuit one gate at a time. At every step the circuit
diagram, state vector, ket notation, gate matrix, matrix multiplication,
measurement probabilities and Bloch spheres all update from the same
underlying state — and you can run a measurement experiment to compare
observed frequencies with the theory.

Built in Python: a dependency-free quantum engine, a [Streamlit](https://streamlit.io)
UI, and [Plotly](https://plotly.com/python/) 3D Bloch spheres.

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

The suite (1,300+ checks) covers the project plan's mathematical tests
(X|0⟩ = |1⟩, H|0⟩ = |+⟩, Z|+⟩ = |−⟩, H² = X² = Y² = Z² = I, normalisation after
every gate, unit-length Bloch vectors, the named-state Bloch table), the
multi-qubit engine (tensor ordering, CNOT/CZ/SWAP, Bell and GHZ states,
reduced density matrices, Born-rule sampling), a check that each single-qubit
gate's rotation axis reproduces the amplitude result, the LaTeX formatting, and
a headless Streamlit `AppTest` smoke test that drives the real UI.

## What you can do in the app

* **Set up the register** — 1, 2 or 3 qubits, each starting in |0⟩, |1⟩, |+⟩ or |−⟩.
* **Add gates** — coloured buttons for H, X, Y, Z, S, T; pick a target qubit and a
  control/target pair for CNOT, CZ and SWAP.
* **Step through** — an SVG circuit with the current gate highlighted, a clickable
  step timeline, Previous / Next / Undo / Reset.
* **Read the maths** — ket and vector notation with exact values (1/√2, i, e^{iπ/4}),
  factored forms, named states (|+⟩, |−i⟩, |Φ⁺⟩ …), and the full matrix
  multiplication for the current step.
* **Watch the Bloch sphere** — one sphere per qubit, the previous arrow, the path the
  arrow takes, the gate's rotation axis, and a ▶ button to replay the move. Entangled
  qubits show a shrunken arrow (their reduced state is mixed).
* **Measure** — probabilities for every outcome, then run 1 / 10 / 100 / 1000 shots and
  compare observed vs. theoretical frequencies.
* **Examples** — one-click circuits from "Create superposition" to Bell and GHZ states.

## Project structure

```
MultiQubitQuantumVisualizer/
  app.py                      Streamlit entry point: page layout
  model.py                    Session state + callbacks (qubits, ops, step, measurement)
  quantum/                    Quantum engine (no UI dependencies)
    complex_number.py         Complex: add, sub, mul, conjugate, |z|, |z|^2, e^{iθ}
    matrix.py                 Square complex matrices, tensor products
    gates.py                  H X Y Z S T, CNOT CZ SWAP, controlled(); the gate registry
    state.py                  QuantumState (n qubits), apply_gate(targets), reduced states
    circuit.py                Circuit / Operation / simulate_circuit
    measurement.py            Born-rule sampling, collapse, single-qubit measurement
    bloch.py                  amplitudes -> (x, y, z), rotation and straight paths
  components/                 UI panels
    toolbar.py                Register setup, gate palette, examples
    circuit.py                SVG circuit diagram + step timeline
    controls.py               Previous / Next / Undo / Reset
    state_panel.py            Ket, vector and amplitudes
    matrix_calculation.py     Before -> gate matrix -> multiplication -> after
    explanation.py            Gate-specific teaching text, entanglement notes
    bloch_sphere.py           Plotly 3D spheres, arrows, paths and animation
    measurement_panel.py      Probability bars + sampling experiment
    gate_panel.py             Gate reference
    theme.py, widgets.py      CSS and small widget helpers
  data/
    gate_descriptions.py      Plain-language descriptions per gate
    presets.py                One-click example circuits
  utils/
    format_state.py           Exact LaTeX for 0, ±1, ±i, ±1/√2, e^{iπ/4} ...
  docs/EXTENDING.md           How to add gates, qubits and measurements
  tests/                      pytest suite
```

## How it works

The app stores only the register setup, the list of operations and the current
step (`model.py`). On every rerun it asks the engine for
`simulate_circuit(circuit)`, which returns the state after each operation, and
every panel is derived from `states[step]`. Nothing displayed is stored
separately, so the panels can never disagree.

A qubit's Bloch vector comes from its reduced density matrix ρ:

```
x = 2 Re(ρ₁₀)      y = 2 Im(ρ₁₀)      z = ρ₀₀ − ρ₁₁
```

which for a single qubit is exactly `x = 2 Re(α*β), y = 2 Im(α*β), z = |α|² − |β|²`.
Every single-qubit gate is a rotation of the sphere (X, Y, Z about their own
axis; H about the (x + z)/√2 diagonal; S and T by 90° and 45° about z). The
animation sweeps the arrow along that rotation using Rodrigues' formula, and a
test asserts that the geometric end point matches the algebraic one for every
gate and named state. Entangling gates shrink the arrow toward the centre.

## Deploy to Streamlit Community Cloud

The repo is ready for [Streamlit Community Cloud](https://share.streamlit.io):
sign in with GitHub, choose **New app**, pick this repository, branch `main`,
main file `app.py`, and deploy. Dependencies come from `requirements.txt`.

## Extending it

See [docs/EXTENDING.md](docs/EXTENDING.md) for adding gates (one registry
entry), more qubits (one constant), and measurement features (the
`quantum/measurement.py` building blocks).

## Author

Made by **Wilson Wong** — undergraduate in Computer Science, researching quantum computing.
