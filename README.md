# ⚛️Quantum Prisoner’s Dilemma 

This is a browser-based quantum game developed for **UTS Introduction to Quantum Computing**.

## 🎮 Game Overview

Two players choose to **Cooperate** or **Defect**.  
Their choices dynamically generate an **OpenQASM quantum circuit**, which is executed using either:

- A local quantum simulator (Qiskit Aer), or  
- The Quokka quantum computing backend (when available)

The resulting measurement is mapped to a **Prisoner’s Dilemma payoff table**, and scores are tracked across multiple rounds.

The game demonstrates how quantum operations (such as entanglement) can influence classical game theory outcomes.

---

##  Features

- Interactive Prisoner’s Dilemma gameplay
- Dynamic OpenQASM circuit generation
- Quantum entanglement simulation
- Multiple execution backends:
  - Local Qiskit simulator
  - Quokka quantum backend (optional)
- Shot-based probabilistic outcomes
- Score tracking across rounds
- Game history and payoff visualization

---

## 🌐 Live Deployment

https://quantum-prisoners-dilemma-ela4awpnhamip5yt6kpgrf.streamlit.app/

---

## ▶️ How to Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
