from flask import Flask, render_template, request, jsonify
from qiskit import QuantumCircuit
from qiskit_aer import StatevectorSimulator
from qiskit.quantum_info import Statevector
import numpy as np
import os
from openai import OpenAI

# Initialize the Flask application
app = Flask(__name__)

# This is the main page of your website
@app.route('/')
def index():
    # Flask will look in the 'templates' folder for this file
    return render_template('frontend.html')

# This is the API endpoint for running the quantum simulation
@app.route('/simulate', methods=['POST'])
def simulate():
    try:
        circuit_data = request.json['circuit']
        num_qubits = len(circuit_data)
        circuit_depth = len(circuit_data[0]) if num_qubits > 0 else 0
        
        qc = QuantumCircuit(num_qubits)

        # --- Build the circuit from the data ---
        processed_cnot_steps = set()
        for step_index in range(circuit_depth):
            control_qubit_index = -1
            target_qubit_indices = []
            for qubit_index in range(num_qubits):
                gate = circuit_data[qubit_index][step_index]
                if gate == 'C': control_qubit_index = qubit_index
                elif gate == 'TARGET': target_qubit_indices.append(qubit_index)
            
            if control_qubit_index != -1 and len(target_qubit_indices) > 0:
                for target_index in target_qubit_indices:
                    qc.cx(control_qubit_index, target_index)
                processed_cnot_steps.add(step_index)

            for qubit_index in range(num_qubits):
                gate = circuit_data[qubit_index][step_index]
                if gate == 'H': qc.h(qubit_index)
                elif gate == 'X': qc.x(qubit_index)
                elif gate == 'Y': qc.y(qubit_index)
                elif gate == 'Z': qc.z(qubit_index)
                elif gate == 'I': qc.i(qubit_index)
                elif gate == 'S': qc.s(qubit_index)
                elif gate == 'Sdg': qc.sdg(qubit_index)
                elif gate == 'T': qc.t(qubit_index)
                elif gate == 'Tdg': qc.tdg(qubit_index)
                elif gate == 'P': qc.p(np.pi/2, qubit_index)
                elif gate == 'SX': qc.sx(qubit_index)
                elif gate == 'SXdg': qc.sxdg(qubit_index)
                elif gate == 'U': qc.u(np.pi/2, np.pi/2, np.pi/2, qubit_index)
                elif gate == 'RX': qc.rx(np.pi/2, qubit_index)
                elif gate == 'RY': qc.ry(np.pi/2, qubit_index)
                elif gate == 'RZ': qc.rz(np.pi/2, qubit_index)
                elif gate == 'BARRIER': qc.barrier(qubit_index)
                elif gate == 'RESET': qc.reset(qubit_index)

        # Make sure there are operations before simulating
        if qc.size() == 0:
            initial_probs = {f'{"0"*num_qubits}': 1.0}
            initial_amps = {f'{"0"*num_qubits}': {'amp': [1.0, 0.0], 'prob': 1.0}}
            return jsonify({"probabilities": initial_probs, "state_amplitudes": initial_amps})

        # --- Use the Statevector Simulator ---
        simulator = StatevectorSimulator()
        result = simulator.run(qc).result()
        statevector = result.get_statevector(qc)

        # Calculate probabilities from the statevector
        probs = statevector.probabilities_dict()
        
        # Get complex amplitudes and format for JSON
        amplitudes = statevector.to_dict()
        formatted_amplitudes = {}
        for state, amp in amplitudes.items():
            probability = np.abs(amp)**2
            if probability > 1e-9: # Filter out negligible amplitudes
                 formatted_amplitudes[state] = {
                    "amp": [amp.real, amp.imag],
                    "prob": probability
                }

        return jsonify({"probabilities": probs, "state_amplitudes": formatted_amplitudes})

    except Exception as e:
        print(f"Error during simulation: {e}")
        return jsonify({"error": str(e)}), 500


# This is the API endpoint for the chatbot
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        api_key = data.get('apiKey')
        user_message = data.get('message')
        circuit_data = data.get('circuit')

        if not api_key:
            return jsonify({"reply": "API key is missing."}), 400
        
        client = OpenAI(api_key=api_key)
        
        circuit_description = "The user has built a quantum circuit. Here is the layout:\n"
        for i, qubit_line in enumerate(circuit_data):
            gates = [gate for gate in qubit_line if gate]
            if gates:
                circuit_description += f"Qubit {i}: [{' -> '.join(gates)}]\n"
            else:
                circuit_description += f"Qubit {i}: [Empty]\n"

        system_prompt = "You are a helpful assistant specializing in quantum computing. You are integrated into a web-based quantum circuit composer. The user will ask you questions, and you will be provided with the current state of their circuit. Use this circuit information to provide context-aware and accurate answers. Explain concepts clearly and concisely."
        
        full_prompt = f"{circuit_description}\nUser question: {user_message}"

        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({"reply": f"An error occurred: {e}"}), 500

# This makes the script runnable
if __name__ == '__main__':
    app.run(debug=True)
