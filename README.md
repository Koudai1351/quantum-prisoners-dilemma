# quantum-prisoners-dilemma

This is a playable quantum game for UTS Introduction to Quantum Computing.

Two players choose Cooperate or Defect. Their choices dynamically generate an OpenQASM circuit. The circuit is executed on Quokka, and the measured bitstring is mapped to a Prisoner's Dilemma payoff table.

## How to run locally

```bash
pip install -r requirements.txt
streamlit run app.py
