import pytest

from quantum.circuit import Circuit, Operation, simulate_circuit
from quantum.state import basis_state, ket_minus, ket_plus, tensor


def test_single_qubit_circuit_matches_the_plan_example():
    circuit = Circuit(1, ("0",), (Operation("H", (0,)), Operation("Z", (0,)), Operation("X", (0,))))
    states = simulate_circuit(circuit)
    assert len(states) == 4
    assert states[1].is_close(ket_plus())
    assert states[2].is_close(ket_minus())
    assert states[3].equals_up_to_global_phase(ket_minus())


def test_two_qubit_circuit_with_mixed_initial_states():
    circuit = Circuit(2, ("+", "1"))
    assert simulate_circuit(circuit)[0].is_close(tensor(ket_plus(), basis_state("1")))


def test_with_operation_and_without_last():
    circuit = Circuit(2, ("0", "0")).with_operation(Operation("H", (0,))).with_operation(Operation("CNOT", (0, 1)))
    assert [op.gate for op in circuit.operations] == ["H", "CNOT"]
    assert circuit.without_last().operations == (Operation("H", (0,)),)
    assert simulate_circuit(circuit)[-1].probability_of("11") == pytest.approx(0.5)


def test_operation_labels():
    assert Operation("H", (1,)).label == "H on q1"
    assert Operation("CNOT", (0, 1)).label == "CNOT on q0, q1"


def test_invalid_circuits_are_rejected():
    with pytest.raises(ValueError):
        Circuit(1, ("0", "0"))
    with pytest.raises(ValueError):
        Circuit(1, ("2",))
    with pytest.raises(ValueError):
        Circuit(1, ("0",), (Operation("CNOT", (0, 1)),))
    with pytest.raises(ValueError):
        Circuit(2, ("0", "0"), (Operation("H", (2,)),))
