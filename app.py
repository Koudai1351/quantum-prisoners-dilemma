import json
import requests
import urllib3
from collections import Counter

import streamlit as st

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PAYOFF_TABLE = {
    "00": (3, 3),
    "01": (0, 5),
    "10": (5, 0),
    "11": (1, 1),
}

OUTCOME_EXPLANATION = {
    "00": "Both players receive the cooperation outcome.",
    "01": "Player 1 receives the lower payoff, while Player 2 receives the higher payoff.",
    "10": "Player 1 receives the higher payoff, while Player 2 receives the lower payoff.",
    "11": "Both players receive the mutual defection outcome.",
}


def choice_to_code(choice):
    if choice == "Cooperate":
        return "C"
    if choice == "Defect":
        return "D"
    raise ValueError("Invalid choice")


def generate_pd_qasm(player1, player2, use_quantum=True):
    player1 = player1.upper()
    player2 = player2.upper()

    if player1 not in ["C", "D"] or player2 not in ["C", "D"]:
        raise ValueError("Choices must be C or D.")

    program = """OPENQASM 2.0;
qreg q[2];
creg c[2];
"""

    # Entanglement layer
    if use_quantum:
        program += """
// Entanglement layer
h q[0];
cx q[0], q[1];
"""

    # Player input layer
    if player1 == "D":
        program += """
// Player 1 defects: apply X gate to q[0]
x q[0];
"""
    else:
        program += """
// Player 1 cooperates: identity operation on q[0]
"""

    if player2 == "D":
        program += """
// Player 2 defects: apply X gate to q[1]
x q[1];
"""
    else:
        program += """
// Player 2 cooperates: identity operation on q[1]
"""

    # Disentanglement layer
    if use_quantum:
        program += """
// Disentanglement layer
cx q[0], q[1];
h q[0];
"""

    # Measurement
    program += """
// Measurement
measure q[0] -> c[0];
measure q[1] -> c[1];
"""

    return program


def send_to_quokka(program, my_quokka="quokka1", count=20):
    url = f"http://{my_quokka}.quokkacomputing.com/qsim/qasm"

    data = {
        "script": program,
        "count": count,
    }

    response = requests.post(url, json=data, verify=False, timeout=30)
    response.raise_for_status()

    json_obj = json.loads(response.content)
    return json_obj["result"]["c"]


def shots_to_bitstrings(shots):
    bitstrings = []
    for shot in shots:
        bitstring = "".join(str(bit) for bit in shot)
        bitstrings.append(bitstring)
    return bitstrings


def fallback_quantum_result(player1, player2):
    """
    Fallback only for testing when Quokka is unavailable.
    Final marking should use the Quokka result when possible.
    """
    if player1 == "C" and player2 == "C":
        return "00"
    if player1 == "C" and player2 == "D":
        return "01"
    if player1 == "D" and player2 == "C":
        return "01"
    if player1 == "D" and player2 == "D":
        return "00"
    return "00"


def get_most_common_result(bitstrings):
    counts = Counter(bitstrings)
    most_common = counts.most_common(1)[0][0]
    return most_common, counts


def get_payoff(bitstring):
    return PAYOFF_TABLE.get(bitstring, (0, 0))


st.set_page_config(
    page_title="Quantum Prisoner's Dilemma",
    page_icon="⚛️",
    layout="wide",
)

st.title("⚛️ Quantum Prisoner’s Dilemma")
st.write(
    "A playable quantum game where two players choose to cooperate or defect. "
    "Their choices dynamically generate an OpenQASM circuit, which is executed on Quokka."
)

if "total_p1" not in st.session_state:
    st.session_state.total_p1 = 0
if "total_p2" not in st.session_state:
    st.session_state.total_p2 = 0
if "round" not in st.session_state:
    st.session_state.round = 0
if "history" not in st.session_state:
    st.session_state.history = []

st.header("1. Choose player strategies")

col1, col2 = st.columns(2)

with col1:
    p1_choice_text = st.selectbox(
        "Player 1 choice",
        ["Cooperate", "Defect"],
        key="p1_choice",
    )

with col2:
    p2_choice_text = st.selectbox(
        "Player 2 choice",
        ["Cooperate", "Defect"],
        key="p2_choice",
    )

p1 = choice_to_code(p1_choice_text)
p2 = choice_to_code(p2_choice_text)

st.header("2. Quantum execution settings")

col3, col4, col5 = st.columns(3)

with col3:
    use_quantum = st.checkbox(
        "Use entanglement and disentanglement",
        value=True,
    )

with col4:
    shots = st.slider(
        "Number of Quokka shots",
        min_value=1,
        max_value=100,
        value=20,
    )

with col5:
    quokka_device = st.selectbox(
        "Quokka device",
        ["quokka1", "quokka2", "quokka3"],
    )

allow_fallback = st.checkbox(
    "Allow simulation fallback if Quokka is unavailable",
    value=True,
)

st.header("3. Run the game")

if st.button("Run Quantum Game"):
    qasm = generate_pd_qasm(p1, p2, use_quantum=use_quantum)

    used_fallback = False

    try:
        raw_results = send_to_quokka(qasm, my_quokka=quokka_device, count=shots)
        bitstrings = shots_to_bitstrings(raw_results)
        final_bitstring, counts = get_most_common_result(bitstrings)

    except Exception as e:
        if allow_fallback:
            used_fallback = True
            final_bitstring = fallback_quantum_result(p1, p2)
            counts = Counter([final_bitstring])
            st.warning(
                "Quokka could not be reached, so the app used the fallback mode. "
                "For final submission, try to demonstrate the Quokka mode when possible."
            )
            st.error(f"Quokka error: {e}")
        else:
            st.error(f"Quokka execution failed: {e}")
            st.stop()

    payoff_p1, payoff_p2 = get_payoff(final_bitstring)

    st.session_state.total_p1 += payoff_p1
    st.session_state.total_p2 += payoff_p2
    st.session_state.round += 1

    st.session_state.history.append(
        {
            "Round": st.session_state.round,
            "Player 1 Choice": p1,
            "Player 2 Choice": p2,
            "Measured Bitstring": final_bitstring,
            "Player 1 Payoff": payoff_p1,
            "Player 2 Payoff": payoff_p2,
            "Used Fallback": used_fallback,
        }
    )

    st.subheader("Game Result")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Measured bitstring", final_bitstring)

    with c2:
        st.metric("Player 1 payoff", payoff_p1)

    with c3:
        st.metric("Player 2 payoff", payoff_p2)

    st.write(OUTCOME_EXPLANATION.get(final_bitstring, "Unknown outcome."))

    st.subheader("Shot counts")
    st.write(dict(counts))

    st.subheader("Generated QASM")
    st.code(qasm, language="text")

st.header("4. Scoreboard")

score_col1, score_col2, score_col3 = st.columns(3)

with score_col1:
    st.metric("Rounds played", st.session_state.round)

with score_col2:
    st.metric("Player 1 total score", st.session_state.total_p1)

with score_col3:
    st.metric("Player 2 total score", st.session_state.total_p2)

if st.session_state.history:
    st.subheader("Game history")
    st.dataframe(st.session_state.history, use_container_width=True)

if st.button("Reset game"):
    st.session_state.total_p1 = 0
    st.session_state.total_p2 = 0
    st.session_state.round = 0
    st.session_state.history = []
    st.rerun()

st.header("Payoff table")

st.table(
    {
        "Measured bitstring": ["00", "01", "10", "11"],
        "Meaning": [
            "Both cooperate outcome",
            "P1 cooperates / P2 defects outcome",
            "P1 defects / P2 cooperates outcome",
            "Both defect outcome",
        ],
        "Player 1 payoff": [3, 0, 5, 1],
        "Player 2 payoff": [3, 5, 0, 1],
    }
)

st.header("How quantum mechanics is used")

st.write(
    "The game begins with two qubits in the |00⟩ state. "
    "When quantum mode is enabled, the app applies H and CNOT gates to entangle the qubits. "
    "Each player's choice is then converted into a quantum operation: Cooperate means no X gate, "
    "while Defect adds an X gate to that player's qubit. "
    "The circuit is then disentangled and measured. "
    "The measured bitstring is mapped to the Prisoner's Dilemma payoff table."
)