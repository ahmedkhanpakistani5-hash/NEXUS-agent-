from config import get_groq_model
from utils.helpers import safe_json_loads, truncate_text


def create_study_plan(goal: str, document_text: str, llm) -> dict:
    if llm is None:
        return {
            "title": "Study Plan",
            "important_topics": ["Clarify the objective", "Review key material", "Practice recall"],
            "priorities": ["Focus on the user goal first", "Break work into small tasks"],
            "daily_tasks": ["Read key sections", "Summarize insights", "Review before sleeping"],
            "revision_strategy": "Review the most important concepts multiple times across the week.",
            "suggested_schedule": "A 7-day plan with daily study blocks and a final review session.",
        }

    material = truncate_text(document_text, 4000) if document_text else "No uploaded material was provided. Use general study planning based on the goal."
    prompt = (
        "Create a practical study plan. Return valid JSON with keys: "
        "title, important_topics, priorities, daily_tasks, revision_strategy, suggested_schedule. "
        f"Goal: {goal}\nMaterial:\n{material}"
    )

    try:
        response = llm.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": "You are NEXUS, a study planning assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )
        content = response.choices[0].message.content
        payload = safe_json_loads(content)
        if payload and isinstance(payload, dict):
            return payload
    except Exception:
        pass

    sample_topic = goal.strip() or "Core learning objectives"
    return {
        "title": "7-Day Study Plan",
        "important_topics": [sample_topic, "Key concepts from the uploaded material", "Application and review"],
        "priorities": ["Focus on major ideas first", "Use active recall and practice questions", "Review difficult topics daily"],
        "daily_tasks": [
            "Read a focused set of notes or sections",
            "Write a 5-10 bullet summary of the day’s key ideas",
            "Solve 3-5 review questions or flashcards",
            "End the day with a short recap and revision"
        ],
        "revision_strategy": "Use spaced repetition. Revisit difficult topics after 24 and 72 hours.",
        "suggested_schedule": "Day 1: Understand the material. Day 2: Review and summarize. Day 3: Practice. Day 4: Deepen understanding. Day 5: Drill. Day 6: Mix practice. Day 7: Final review.",
    }
