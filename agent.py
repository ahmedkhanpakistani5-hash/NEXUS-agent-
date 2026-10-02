import json
import re
from typing import Any, Dict, List

import streamlit as st
from groq import Groq

from config import get_groq_api_key, get_groq_model
from tools.document_tool import extract_document_text
from tools.quiz_tool import generate_quiz
from tools.report_tool import create_report
from tools.study_tool import create_study_plan


class NexusAgent:
    def __init__(self):
        self.model = get_groq_model()
        self.client = None

    def _llm(self):
        api_key = get_groq_api_key()
        if not api_key:
            raise ValueError("Please add GROQ_API_KEY to Streamlit Secrets.")
        self.client = Groq(api_key=api_key)
        return self.client

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        raise ValueError("The AI planner returned invalid JSON.")

    def _make_plan(self, goal: str, has_document: bool) -> Dict[str, Any]:
        client = self._llm()
        system_prompt = (
            "You are NEXUS, an intelligent productivity agent. "
            "Create clear execution plans and choose the correct tools. "
            "Return valid JSON with the keys 'plan' and 'tools'."
        )
        document_hint = "The user has uploaded a document." if has_document else "No document was uploaded."
        prompt = (
            f"User goal: {goal}\n{document_hint}\n"
            "Return a short JSON object: {'plan': ['step1', 'step2'], 'tools': ['tool1', 'tool2']}. "
            "Use only these tools when relevant: 'document', 'study', 'quiz', 'report'. "
            "Keep the plan realistic and action-oriented."
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=400,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("The planner did not return a valid response.")
            payload = self._extract_json(content)
            plan = payload.get("plan", [])
            tools = payload.get("tools", [])
            if not isinstance(plan, list) or not isinstance(tools, list):
                raise ValueError("Planner response was malformed.")
            return {"plan": plan, "tools": tools}
        except Exception:
            fallback = {
                "plan": [
                    "Analyze the user goal",
                    "Review uploaded material if available",
                    "Select the best tools for the task",
                    "Execute the selected tools",
                    "Synthesize the final result",
                ],
                "tools": ["document" if has_document else "study", "study", "quiz", "report"],
            }
            if not has_document and "study" not in fallback["tools"]:
                fallback["tools"].append("study")
            if "report" not in fallback["tools"]:
                fallback["tools"].append("report")
            return fallback

    def _summarize_document(self, document_text: str) -> str:
        text = (document_text or "").strip()
        if not text:
            return "No document text was available."
        sentences = re.split(r"(?<=[.!?])\s+", text)
        summary_parts = []
        for sentence in sentences[:4]:
            cleaned = sentence.strip()
            if cleaned:
                summary_parts.append(cleaned)
        summary = " ".join(summary_parts)
        return summary[:500] if len(summary) > 500 else summary

    def run(self, goal: str, uploaded_file=None) -> Dict[str, Any]:
        if not goal or not goal.strip():
            raise ValueError("Please enter a goal before running the agent.")

        execution: List[str] = ["🟢 Goal received"]
        document_text = ""
        if uploaded_file is not None:
            try:
                document_text = extract_document_text(uploaded_file)
                execution.append("📄 Document received")
                if document_text.strip():
                    execution.append("📄 Document analyzed")
                else:
                    execution.append("⚠️ Document was empty or unreadable")
            except ValueError as exc:
                execution.append(f"⚠️ {str(exc)}")
                document_text = ""
            except Exception:
                execution.append("⚠️ Unable to process this document.")
                document_text = ""
        else:
            execution.append("📄 No document uploaded")

        execution.append("🧠 Goal analyzed")
        plan = self._make_plan(goal, bool(document_text.strip()))
        execution.append("📋 Execution plan created")

        selected_tools = []
        for tool_name in plan.get("tools", []):
            tool_name = tool_name.lower().strip()
            if tool_name in {"document", "study", "quiz", "report"} and tool_name not in selected_tools:
                selected_tools.append(tool_name)

        if not selected_tools:
            selected_tools = ["study", "quiz", "report"]

        results: Dict[str, Any] = {}
        llm = self._llm()

        if "document" in selected_tools and document_text.strip():
            results["document"] = {
                "status": "Document analyzed",
                "summary": self._summarize_document(document_text),
            }
            execution.append("📄 Document analysis tool executed")

        if "study" in selected_tools:
            results["study"] = create_study_plan(goal, document_text, llm)
            execution.append("📚 Study planning tool executed")

        if "quiz" in selected_tools:
            results["quiz"] = generate_quiz(goal, document_text, llm)
            execution.append("❓ Quiz generation tool executed")

        if "report" in selected_tools:
            results["report"] = create_report(goal, document_text, llm)
            execution.append("📝 Report generation tool executed")

        execution.append("✅ Final result generated")

        final_result = self._synthesize_final(goal, plan, results)

        return {
            "goal": goal,
            "plan": plan.get("plan", []),
            "tools_used": selected_tools,
            "execution": execution,
            "results": results,
            "final_result": final_result,
        }

    def _synthesize_final(self, goal: str, plan: Dict[str, Any], results: Dict[str, Any]) -> str:
        llm = self._llm()
        tool_summary = json.dumps(results, ensure_ascii=False, indent=2)
        prompt = (
            "You are NEXUS, an autonomous productivity agent. "
            "Synthesize the final answer from the tool outputs and provide a clear result for the user. "
            "Keep it professional, structured, and concise. Do not claim you did actions you did not perform.\n\n"
            f"Original goal: {goal}\n\n"
            f"Planned execution: {json.dumps(plan, ensure_ascii=False)}\n\n"
            f"Tool outputs: {tool_summary}"
        )
        try:
            response = llm.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are NEXUS, an autonomous AI productivity agent."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=600,
            )
            content = response.choices[0].message.content
            if content:
                return content.strip()
        except Exception:
            pass

        sections = [
            "## Final Outcome",
            f"Your goal was: {goal}",
            "",
            "### What NEXUS did",
            f"- Planned steps: {', '.join(plan.get('plan', [])) if plan.get('plan') else 'No explicit plan generated'}",
            f"- Tools used: {', '.join(plan.get('tools', [])) if plan.get('tools') else 'No tools selected'}",
            "",
            "### Result summary",
        ]
        for tool_name, tool_result in results.items():
            if isinstance(tool_result, dict):
                overview = tool_result.get("summary") or tool_result.get("executive_summary") or tool_result.get("title") or "Tool completed successfully."
                sections.append(f"- {tool_name.title()}: {str(overview)[:220]}")
            else:
                sections.append(f"- {tool_name.title()}: {str(tool_result)[:220]}")
        return "\n".join(sections)
