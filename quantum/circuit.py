"""The circuit model: a register of qubits plus an ordered list of operations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .gates import Gate, get_gate
from .state import INITIAL_STATES, QuantumState, apply_gate, tensor, validate_targets


@dataclass(frozen=True)
class Operation:
    """One gate placed on specific qubits. For CNOT/CZ the first target is the control."""

    gate: str                 # gate symbol, e.g. "H" or "CNOT"
    targets: Tuple[int, ...]  # qubit indices in gate order

    @property
    def gate_object(self) -> Gate:
        return get_gate(self.gate)

    @property
    def label(self) -> str:
        if len(self.targets) == 1:
            return f"{self.gate} on q{self.targets[0]}"
        return f"{self.gate} on q{', q'.join(str(t) for t in self.targets)}"


@dataclass(frozen=True)
class Circuit:
    num_qubits: int
    initial: Tuple[str, ...]                        # INITIAL_STATES key per qubit
    operations: Tuple[Operation, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if self.num_qubits < 1:
            raise ValueError("A circuit needs at least one qubit")
        if len(self.initial) != self.num_qubits:
            raise ValueError(f"Expected {self.num_qubits} initial states, got {len(self.initial)}")
        for key in self.initial:
            if key not in INITIAL_STATES:
                raise ValueError(f"Unknown initial state {key!r}")
        for op in self.operations:
            validate_targets(op.gate_object, op.targets, self.num_qubits)

    def initial_state(self) -> QuantumState:
        return tensor(*(INITIAL_STATES[key] for key in self.initial))

    def with_operation(self, op: Operation) -> Circuit:
        return Circuit(self.num_qubits, self.initial, self.operations + (op,))

    def without_last(self) -> Circuit:
        return Circuit(self.num_qubits, self.initial, self.operations[:-1])


def simulate_circuit(circuit: Circuit) -> List[QuantumState]:
    """states[0] is the initial register; states[k] is after operations[k-1]."""
    states = [circuit.initial_state()]
    for op in circuit.operations:
        states.append(apply_gate(states[-1], op.gate_object, op.targets))
    return states
