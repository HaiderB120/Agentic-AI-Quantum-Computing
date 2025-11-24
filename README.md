# **CircuitView: Interactive Quantum Composer and AI Assistant**

CircuitView is a web-based quantum circuit simulator for education and research. It combines a drag and drop quantum composer (similar to IBM's QC) with a 3D Bloch sphere visualization and integrated AI Chatbot powered by OpenAI to help users understand their circuit or quantum mechanics better.

## **Setup Instructions:**
	1. Install the folder from the github.
	2. Open powershell or terminal.
	3. Navigate to the project folder (cd).
	4. python -m venv venv (Windows) or python3 -m venv venv (Mac/Linux)
	5. .\venv\Scripts\Activate.ps1 (Windows) or source venv/bin/activate (Mac/Linux)
	6. Install the libraries: pip install Flask qiskit qiskit-aer numpy openai
	7. flask run
	8. Open your web browser and navigate to http://127.0.0.1:5000

## **Usage Guide:**
	1. Enter OpenAI API key in the top header and click "Save." It will be stored locally in 	your browser
	2. Build a Circuit: Drag gates from the palette onto the circuit lines.
		Adding/Removing Qubits: Use the + and - buttons next to Qubit count.
		Changing Circuit Size: Press + or - next to "Steps" to add or remove columns.
		Delete Gates: Right click on a gate to remove it.
		Move Gates: Drag and drop existing gates to move them, dragging one onto another will swap them.
	3. Click "Run Circuit" to see the probabilities chart and 3D Bloch Sphere of your
	current circuit
	4. Ask the AI any questions you may have. It knows your current configuration so can
	give you answers with that context.
