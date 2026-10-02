import json
from typing import List

import streamlit as st

from agent import NexusAgent


st.set_page_config(
    page_title="NEXUS AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b1020;
            --panel: #121a2d;
            --panel-soft: #172339;
            --surface: #1a2540;
            --accent: #7c6ef6;
            --accent-2: #4cc9f0;
            --text: #edf2ff;
            --muted: #b9c5e1;
            --border: rgba(149, 166, 214, 0.2);
            --success: #5ae6a8;
            --warning: #ffd166;
            --danger: #ff7b7b;
        }
        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0b1020 0%, #111827 100%);
            color: var(--text);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .card {
            background: rgba(18, 26, 45, 0.9);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        }
        .section-title {
            color: var(--text);
            font-weight: 700;
            letter-spacing: 0.02em;
            margin-bottom: 0.5rem;
        }
        .subtle {
            color: var(--muted);
        }
        .status-step {
            border-left: 3px solid var(--accent);
            padding-left: 0.7rem;
            margin: 0.4rem 0;
            color: var(--text);
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--accent) 0%, #6a8dff 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.55rem 1rem;
        }
        .stDownloadButton > button {
            background: rgba(124, 110, 246, 0.12);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 10px;
        }
        .stTextArea textarea {
            background: rgba(8, 13, 26, 0.7);
            color: var(--text);
            border: 1px solid var(--border);
        }
        .stFileUploader {
            background: rgba(8, 13, 26, 0.7);
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _seed_examples() -> List[str]:
    return [
        "Analyze this document, identify the most important topics, create a 7-day study plan and generate practice questions.",
        "Read this document and create 10 MCQs with answers.",
        "Analyze this material and create a structured report.",
        "Summarize this material and create an actionable plan.",
    ]


def _display_status_list(items: List[str]) -> None:
    if not items:
        st.info("The agent has not started yet.")
        return
    for item in items:
        st.markdown(f"<div class='status-step'>{item}</div>", unsafe_allow_html=True)


def main() -> None:
    _apply_theme()

    st.title("🤖 NEXUS AI Agent")
    st.caption("Transform goals into plans, actions and results.")

    if "result" not in st.session_state:
        st.session_state.result = None
    if "execution" not in st.session_state:
        st.session_state.execution = []
    if "context" not in st.session_state:
        st.session_state.context = {}

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        goal = st.text_area(
            "User goal",
            value=st.session_state.get("goal", ""),
            height=120,
            placeholder="Example: Analyze this document and create a study plan and quiz.",
        )
        uploaded_file = st.file_uploader(
            "Upload a file (PDF, TXT, DOCX)",
            type=["pdf", "txt", "docx"],
            accept_multiple_files=False,
        )
        run_button = st.button("Run Agent", type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    if not st.session_state.get("result"):
        st.session_state.goal = goal

    example_goals = _seed_examples()
    st.write("### Example goals")
    cols = st.columns(2)
    for idx, example in enumerate(example_goals):
        with cols[idx % 2]:
            if st.button(example, key=f"example_{idx}"):
                st.session_state.goal = example
                st.rerun()

    if run_button:
        if not goal.strip():
            st.warning("Please enter a user goal before running the agent.")
            return

        agent = NexusAgent()
        try:
            st.session_state.execution = []
            result = agent.run(goal=goal, uploaded_file=uploaded_file)
            st.session_state.result = result
            st.session_state.execution = result.get("execution", [])
            st.session_state.context = {
                "goal": goal,
                "plan": result.get("plan", []),
                "tools_used": result.get("tools_used", []),
            }
            st.success("✅ Final result generated")
        except ValueError as exc:
            st.error(str(exc))
            st.session_state.result = None
            st.session_state.execution = [f"⚠️ {str(exc)}"]
        except Exception:
            st.error("The AI service could not complete the request. Please try again.")
            st.session_state.result = None
            st.session_state.execution = ["⚠️ The AI service could not complete the request. Please try again."]

    if st.session_state.get("result"):
        st.markdown("## Agent execution")
        _display_status_list(st.session_state.execution)

        st.markdown("## Agent plan")
        plan = st.session_state.result.get("plan", [])
        if plan:
            for step in plan:
                st.markdown(f"- {step}")
        else:
            st.info("No plan was generated.")

        st.markdown("## Tools used")
        tools_used = st.session_state.result.get("tools_used", [])
        if tools_used:
            for tool_name in tools_used:
                st.markdown(f"- {tool_name}")
        else:
            st.info("No tools were used.")

        st.markdown("## Final result")
        final_text = st.session_state.result.get("final_result", "")
        st.markdown(final_text)

        st.markdown("## Download result")
        download_data = json.dumps(st.session_state.result, indent=2, ensure_ascii=False)
        st.download_button(
            label="Download result as JSON",
            data=download_data,
            file_name="nexus_result.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
