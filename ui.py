import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/ask"

st.set_page_config(
    page_title="AI Query Agent",
    page_icon="🎓",
    layout="wide"
)

st.title("AI Query Agent ")

st.markdown("Ask questions about **students, teachers, assignments, attendance, and exams**.")

# Session history
if "history" not in st.session_state:
    st.session_state.history = []

# Input box
question = st.text_input("💬 Ask a question about the school data")

col1, col2 = st.columns([1,1])

with col1:
    submit = st.button("Ask AI")

with col2:
    clear = st.button("Clear Chat")

# Clear history
if clear:
    st.session_state.history = []

# Submit query
if submit and question:

    with st.spinner("🤖 AI is thinking..."):

        try:
            res = requests.post(
                API_URL,
                json={"question": question, "verbose": False},
                timeout=60
            )

            if res.status_code == 200:

                answer = res.json()["answer"]

                st.session_state.history.append(
                    {"question": question, "answer": answer}
                )

            else:
                st.error(res.json().get("detail", "API Error"))

        except Exception as e:
            st.error(f"Server error: {e}")

# Chat display
st.markdown("---")
st.subheader("Conversation")

for chat in reversed(st.session_state.history):

    with st.container():
        st.markdown(f"🧑 **You:** {chat['question']}")
        st.markdown(f"🤖 **AI:** {chat['answer']}")
        st.markdown("---")