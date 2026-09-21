# Extending the Qubit Visualizer

The app is built so that the three most likely next steps — more gates, more
qubits, and richer measurements — are additions rather than rewrites. This
page shows where each one plugs in.

## How the pieces fit

```
model.py            session state: num_qubits, init_q, ops[(symbol, targets)], step
   │
   ▼
quantum/circuit.py  Circuit(num_qubits, initial, operations) ──► simulate_circuit()
   │                                                                    │
   ▼                                                                    ▼
quantum/state.py    QuantumState (2**n amplitudes) ◄── apply_gate(state, gate, targets)
   │                    reduced_density_matrix / purity per qubit
   ▼
components/*        every panel is a pure function of states[step]
```

Nothing displayed is stored separately: the ket, vector, matrix calculation,
probabilities, Bloch arrows and measurement histogram are all derived from the
`QuantumState` at the current step.

## Adding a gate

1. **Define it** in `quantum/gates.py`:

   ```python
   RX90 = Gate(
       name="X rotation (90°)",
       symbol="RX",
       matrix=Matrix2x2(Complex(INV_SQRT2), Complex(0, -INV_SQRT2),
                        Complex(0, -INV_SQRT2), Complex(INV_SQRT2)),
       description="Quarter turn about the X axis.",
       axis=(1.0, 0.0, 0.0), rotation=math.pi / 2,   # Bloch rotation (single-qubit gates)
       color="#0284C7",                              # gate box colour in the UI
   )
   ```

   * `arity` defaults to 1; a two-qubit gate needs `arity=2` and a 4×4 `Matrix`.
   * A controlled gate is one line: `controlled(RX90, name=..., symbol="CRX", ...)`.
   * `display_matrix` / `display_scale_latex` let the UI print a tidy
     factorised matrix (see how `H` does it).

2. **Register it**: add the object to `GATES` and its symbol to
   `SINGLE_QUBIT_GATES` or `TWO_QUBIT_GATES`. The toolbar, circuit diagram,
   timeline, gate reference and coloured button CSS all read those lists.

3. **Describe it** in `data/gate_descriptions.py` (`GateDescription`) — the
   summary, basis-state actions, Bloch interpretation and tip shown under the
   maths.

4. **Test it**: `tests/test_gates.py` already checks unitarity and the
   display factorisation for every registered gate; add any identities
   specific to the new gate (e.g. `RX90⁴ = I`).

Optional: a preset in `data/presets.py` that shows the gate off.

## Adding more qubits

The engine already simulates any number of qubits (`QuantumState` is a
vector of `2**n` amplitudes and `apply_gate` takes explicit `targets`). The
UI caps the register with `MAX_QUBITS` / `QUBIT_OPTIONS` in `model.py`:

```python
MAX_QUBITS = 4
QUBIT_OPTIONS = [1, 2, 3, 4]
```

That is the only change needed for the selector; the circuit diagram grows a
wire per qubit, the state panel lists `2**n` amplitudes, one Bloch sphere is
drawn per qubit and the measurement panel shows `2**n` bars. Things to keep
in mind as `n` grows:

* Rendering cost is `O(4**k · 2**n)` per gate — fine to ~6 qubits in pure Python.
* The matrix-calculation panel shows the full register operator only for
  `n == 2`; for larger registers it shows the gate matrix and the vectors.
* Adding a three-qubit gate (Toffoli) is `controlled(CNOT, ...)` plus a
  `THREE_QUBIT_GATES` list and a third target picker in
  `components/toolbar.py`.

Convention: qubit 0 is the **leftmost** bit of a basis label (`|q0 q1 q2⟩`),
and `QuantumState.bit(index, qubit)` is the one place that encodes it.

## Adding measurements

`quantum/measurement.py` provides the building blocks:

| Function | What it does |
|---|---|
| `sample(state, shots, seed)` | Born-rule sampling of the whole register → `{label: count}` |
| `measure_once(state, seed)` | one shot → `(label, collapsed_state)` |
| `measure_qubit(state, qubit, seed)` | measure one qubit; the others are renormalised (partial collapse) |
| `collapse(state, label)` | post-measurement basis state |

The Measurement card (`components/measurement_panel.py`) uses the first two.
Ideas that slot straight in:

* **Measure a single qubit** — call `measure_qubit`, then show the remaining
  register (for a Bell pair, the other qubit's arrow snaps to a pole).
* **Mid-circuit measurement as an operation** — add a pseudo-gate symbol
  (e.g. `"M"`) to `Operation`, handle it in `simulate_circuit` by branching on
  a stored outcome, and draw it with a meter glyph in `components/circuit.py`.
* **Different measurement bases** — rotate into the basis first
  (`apply_gate(state, H, (q,))` for the X basis) and sample as usual.

## Where the maths formatting lives

`utils/format_state.py` turns amplitudes into exact LaTeX (`1/√2`, `i`,
`e^{iπ/4}`, factored kets, named states). To recognise a new named state, add
it to `NAMED_STATES` (one qubit) or `BELL_STATES` (two qubits) in
`quantum/state.py`.

## Running the checks

```bash
pip install -r requirements-dev.txt
pytest            # engine, formatting and a headless Streamlit UI smoke test
streamlit run app.py
```
