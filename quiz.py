import json

from config import get_groq_model
from utils.helpers import safe_json_loads, truncate_text


def generate_quiz(goal: str, document_text: str, llm) -> dict:
    if llm is None:
        return {"title": "Quiz", "questions": []}

    material = truncate_text(document_text, 4000) if document_text else "No document uploaded. Generate general questions based on the stated goal."
    prompt = (
        "Generate 10 multiple-choice questions. "
        "Each question must include exactly four options and a correct answer. "
        "Return valid JSON with a 'questions' list. Each item must contain: question, options, correct_answer, explanation. "
        f"Goal: {goal}\nMaterial:\n{material}"
    )

    try:
        response = llm.chat.completions.create(
            model=get_groq_model(),
            messages=[
                {"role": "system", "content": "You are NEXUS, a quiz generator."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )
        content = response.choices[0].message.content
        payload = safe_json_loads(content)
        if isinstance(payload, dict) and isinstance(payload.get("questions"), list):
            return payload
    except Exception:
        pass

    fallback_questions = []
    base_topics = [
        "Core idea",
        "Most important topic",
        "Key concept",
        "Practical application",
        "Reasoning step",
        "Main takeaway",
        "Evidence or example",
        "Potential risk",
        "Best action",
        "Summary point",
    ]
    for index, topic in enumerate(base_topics, start=1):
        fallback_questions.append({
            "question": f"Q{index}: Which statement best reflects the {topic.lower()} in this task?",
            "options": [
                "It is the primary focus that should be understood clearly.",
                "It is irrelevant to the outcome.",
                "It should be ignored unless time allows.",
                "It is only useful for a final summary.",
            ],
            "correct_answer": "It is the primary focus that should be understood clearly.",
            "explanation": "The most relevant idea should be identified and prioritized before making decisions.",
        })

    return {"title": "10-question quiz", "questions": fallback_questions}
