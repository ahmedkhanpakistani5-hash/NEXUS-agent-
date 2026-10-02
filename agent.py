import json

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL

from tools.document_tool import extract_document
from tools.study_tool import create_study_plan
from tools.quiz_tool import generate_quiz
from tools.report_tool import create_report


class NexusAgent:

    def __init__(self):
        if not GROQ_API_KEY:
            raise ValueError(
                "Please add GROQ_API_KEY to Streamlit Secrets."
            )

        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def _llm(self, system_prompt, user_prompt):

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.2
        )

        return response.choices[0].message.content

    def _make_plan(self, goal, document_text):

        document_available = bool(document_text.strip())

        planner_prompt = f"""
You are the planning brain of NEXUS, an autonomous AI productivity agent.

Your job is to analyze the user's goal and decide which tools are actually
required.

Available tools:

1. document
   Used to analyze uploaded documents.

2. study
   Used to create study plans.

3. quiz
   Used to generate MCQs.

4. report
   Used to create structured reports.

The uploaded document is:
{"AVAILABLE" if document_available else "NOT AVAILABLE"}

User goal:
{goal}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "plan": [
        "step 1",
        "step 2"
    ],
    "tools": [
        "document",
        "study"
    ]
}}

Rules:

- Only select tools that are actually useful.
- If a document exists and the goal requires document analysis,
  include document.
- If the goal asks for studying or scheduling, include study.
- If the goal asks for questions or MCQs, include quiz.
- If the goal asks for a report, include report.
- Do not invent tools.
"""

        raw_response = self._llm(
            "You are NEXUS's execution planner.",
            planner_prompt
        )

        try:
            start = raw_response.find("{")
            end = raw_response.rfind("}")

            if start == -1 or end == -1:
                raise ValueError("Invalid planner response.")

            json_text = raw_response[start:end + 1]

            plan_data = json.loads(json_text)

            if not isinstance(plan_data.get("plan"), list):
                raise ValueError("Invalid plan.")

            if not isinstance(plan_data.get("tools"), list):
                raise ValueError("Invalid tools.")

            return plan_data

        except Exception:

            fallback_tools = []

            goal_lower = goal.lower()

            if document_available:
                fallback_tools.append("document")

            if any(
                word in goal_lower
                for word in [
                    "study",
                    "schedule",
                    "learn",
                    "revision",
                    "plan"
                ]
            ):
                fallback_tools.append("study")

            if any(
                word in goal_lower
                for word in [
                    "quiz",
                    "mcq",
                    "questions",
                    "practice"
                ]
            ):
                fallback_tools.append("quiz")

            if any(
                word in goal_lower
                for word in [
                    "report",
                    "analysis",
                    "analyze"
                ]
            ):
                fallback_tools.append("report")

            if not fallback_tools and document_available:
                fallback_tools.append("document")

            return {
                "plan": [
                    "Understand the user's goal",
                    "Execute the required tools",
                    "Combine the tool outputs",
                    "Generate the final result"
                ],
                "tools": fallback_tools
            }

    def run(self, goal, uploaded_file=None):

        execution = []

        execution.append("🟢 Goal received")

        document_text = ""

        if uploaded_file:

            execution.append("📄 Document received")

            try:
                document_text = extract_document(uploaded_file)

            except Exception:
                raise ValueError(
                    "Unable to process this document."
                )

            if not document_text.strip():
                raise ValueError(
                    "The uploaded document does not contain readable text."
                )

            execution.append("📄 Document analyzed")

        else:
            execution.append("📄 No document provided")

        execution.append("🧠 Goal analyzed")

        plan_data = self._make_plan(
            goal,
            document_text
        )

        plan = plan_data.get("plan", [])
        tools = plan_data.get("tools", [])

        execution.append("📋 Execution plan created")

        tool_outputs = {}

        if "document" in tools:

            if document_text:

                tool_outputs["document"] = document_text

            else:

                tool_outputs["document"] = (
                    "No document was uploaded."
                )

        if "study" in tools:

            execution.append(
                "📚 Study planning tool executed"
            )

            tool_outputs["study"] = create_study_plan(
                goal,
                document_text,
                self._llm
            )

        if "quiz" in tools:

            execution.append(
                "❓ Quiz generation tool executed"
            )

            tool_outputs["quiz"] = generate_quiz(
                goal,
                document_text,
                self._llm
            )

        if "report" in tools:

            execution.append(
                "📝 Report generation tool executed"
            )

            tool_outputs["report"] = create_report(
                goal,
                document_text,
                self._llm
            )

        synthesis_prompt = f"""
You are NEXUS, an autonomous AI productivity agent.

The user gave you this goal:

{goal}

The agent created this execution plan:

{json.dumps(plan, indent=2)}

The agent selected these tools:

{json.dumps(tools, indent=2)}

The actual tool outputs are:

{json.dumps(tool_outputs, indent=2)}

Now synthesize the outputs into one useful final response.

IMPORTANT:

- Do not claim that a tool was used if it was not used.
- Do not invent information.
- Base your answer on the actual tool outputs.
- Make the result clear and structured.
- Use Markdown.
- Directly address the user's goal.
"""

        final_result = self._llm(
            """
You are NEXUS, an intelligent autonomous productivity agent.

Your job is to combine real tool outputs into a useful final result.
Never pretend to have performed an action that did not happen.
""",
            synthesis_prompt
        )

        execution.append("🔄 Tool outputs combined")
        execution.append("🧠 Final result synthesized")
        execution.append("✅ Final result generated")

        return {
            "plan": plan,
            "tools": tools,
            "execution": execution,
            "final_result": final_result
        }
