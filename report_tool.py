from config import get_groq_model
from utils.helpers import safe_json_loads, truncate_text


def create_report(goal: str, document_text: str, llm) -> dict:
    if llm is None:
        return {
            "title": "Project Report",
            "executive_summary": "A structured analysis was not completed because the AI service was unavailable.",
            "key_findings": ["Goal reviewed", "Document context considered", "Action plan prepared"],
            "analysis": "The user needs a simple plan and clear next steps.",
            "recommendations": ["Clarify the objective", "Break the work into milestones", "Track the outcome"],
            "action_items": ["Review the goal", "Create a task list", "Monitor progress"],
        }

    material = truncate_text(document_text, 4000) if document_text else "No document uploaded. Use general report writing with the user goal."
    prompt = (
        "Create a professional report. Return valid JSON with keys: "
        "title, executive_summary, key_findings, analysis, recommendations, action_items. "
        f"Goal: {goal}\nMaterial:\n{material}"
    )

    try:
        response = llm.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": "You are NEXUS, a report generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=700,
        )
        content = response.choices[0].message.content
        payload = safe_json_loads(content)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass

    return {
        "title": "Operational Report",
        "executive_summary": f"This report addresses the goal: {goal}. The objective is to convert the material into a clear action plan with measurable progress points.",
        "key_findings": [
            "The task requires a structured and realistic workflow.",
            "Key information should be extracted before planning begins.",
            "Actionable outcomes are more valuable than generic summaries."
        ],
        "analysis": "The content, when paired with the user's objective, supports a practical study, review, and execution framework.",
        "recommendations": [
            "Define the main objective clearly.",
            "Prioritize the most important concepts.",
            "Build daily actions around the highest-value outputs."
        ],
        "action_items": [
            "Review the uploaded material and highlight the core concepts.",
            "Create a step-by-step study or execution plan.",
            "Generate measurable progress checkpoints."
        ],
    }
