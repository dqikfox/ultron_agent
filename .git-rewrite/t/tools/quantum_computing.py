import logging
import threading
import time
from qiskit import QuantumCircuit, Aer, execute
from .base import Tool

class QuantumComputingTool(Tool):
    def __init__(self, agent):
        self.name = "quantum_computer"
        self.description = "Perform quantum computations using a simulator."
        self.parameters = {
            "type": "object",
            "properties": {
                "num_qubits": {"type": "integer", "description": "Number of qubits for the circuit."},
                "operations": {"type": "array", "description": "List of quantum operations to perform."}
            },
            "required": ["num_qubits", "operations"]
        }
        self.agent = agent
        self.simulator = Aer.get_backend('qasm_simulator')
        self.lock = threading.Lock()
        # self.continuous_quantum_computing()

    def match(self, user_input: str) -> bool:
        return any(keyword in user_input.lower() for keyword in ["quantum", "qiskit", "qubit"])

    def execute(self, num_qubits: int, operations: list) -> str:
        try:
            qc = self._create_quantum_circuit(num_qubits)
            for op in operations:
                gate = op.get("gate")
                qubits = op.get("qubits")
                if not gate or qubits is None:
                    return f"Invalid operation format: {op}"
                self._add_gate(qc, gate, qubits)
            
            counts = self._execute_circuit(qc)
            return f"Quantum computation successful. Results: {counts}"

        except ValueError as e:
            return f"Error: {e}"
        except Exception as e:
            logging.error(f"Quantum computing error: {e} - quantum_computing.py:43")
            return f"An unexpected error occurred during quantum computation."

    def _create_quantum_circuit(self, num_qubits: int) -> QuantumCircuit:
        with self.lock:
            return QuantumCircuit(num_qubits, num_qubits) # Also add classical bits for measurement

    def _add_gate(self, qc: QuantumCircuit, gate: str, qubits):
        with self.lock:
            if gate == 'h':
                qc.h(qubits)
            elif gate == 'x':
                qc.x(qubits)
            elif gate == 'cx':
                qc.cx(qubits[0], qubits[1])
            elif gate == 'measure':
                qc.measure(qubits, qubits) # Measure qubits to classical bits
            else:
                raise ValueError(f"Unknown or unsupported gate: {gate}")
        return qc

    def _execute_circuit(self, qc: QuantumCircuit, shots: int = 1024) -> dict:
        with self.lock:
            job = execute(qc, self.simulator, shots=shots)
            result = job.result()
            return result.get_counts(qc)

