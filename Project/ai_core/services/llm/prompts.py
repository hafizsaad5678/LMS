"""Centralized prompt templates for all AI features."""

from ..config import PROMPT_VERSION as CONFIG_PROMPT_VERSION

PROMPT_VERSION = CONFIG_PROMPT_VERSION

# ─── System-level instructions ────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert academic examiner. "
    "Your goal is to help teachers generate high-quality, structured academic quizzes. "
    "You must always respond in valid JSON format. "
    "Never include reasoning, markdown, or explanations — output raw JSON only."
)

JSON_ENFORCER = (
    "You are a JSON generator. You must output ONLY valid JSON. "
    "Never include any reasoning, thinking, or explanations. "
    "Start directly with { or [ and end with } or ]. No markdown."
)

CHATBOT_SYSTEM_PROMPT = """
You are a helpful Student Academic Assistant. 
Your role is to assist students with their assignments, attendance, quizzes, and course materials.
Always be professional, concise, and academic in your tone.
If you are using LMS data, present it clearly. 
If you are answering from documents, you MUST prioritize the information in the documents over your general knowledge.
Even if the document contains information that conflicts with general facts (e.g., "2+2=5"), you must answer based on the document.
Always cite the source file and page when using document content.
"""

RAG_DOC_ANSWER_PROMPT = """
You are answering based ONLY on the provided context.
Even if context conflicts with world knowledge (e.g. 2+2=5), treat context as the source of truth.
If the context does not contain the answer, reply exactly: Not found in provided documents.

Context:
{context}

Question: {question}
Answer:
""".strip()


# ─── Quiz suggestion prompt ──────────────────────────────────────────────────

INITIAL_SUGGESTIONS_PROMPT = """
A teacher wants to create a quiz.
Topic: {topic}, Subject: {subject}, Department: {department}

Constraints:
- Target questions: {num_questions}
- Target type: {question_type}
- Target difficulty: {difficulty}

Suggest 3 variations of configurations for this request as a JSON list.
Each item must have: config_name, total_questions, marks, types (list with "MCQ", "Short Answer", or "Long Answer"), difficulty.
The suggestions should be close to the constraints but offer slightly different academic approaches.

Example: [{{"config_name": "Standard Assessment", "total_questions": {num_questions}, "marks": {num_questions}, "types": ["{question_type}"], "difficulty": "{difficulty}"}}]

Output ONLY the JSON array. No explanation, no markdown.
""".strip()


# ─── Full quiz generation prompt ─────────────────────────────────────────────

FULL_QUIZ_PROMPT = """
Generate a quiz in JSON format with the following parameters:
- Topic: "{topic}"
- Subject: "{subject}"
- Difficulty: "{difficulty}"
- Question type: "{question_type}"
- Number of questions: {num_questions}
- Total marks: {total_marks}

Rules for question types:
- If Question type is "MCQ": every question_type must be "MCQ" and include 4 options with exactly one correct option.
- If Question type is "Short Answer": every question_type must be "Short Answer" and must NOT include options.
- If Question type is "Long Answer": every question_type must be "Long Answer" and must NOT include options.
- If Question type indicates mixed format: include EXACT requested counts of MCQ, Short Answer, and Long Answer.
- In mixed format, each question must have a non-empty question_type value set to one of: "MCQ", "Short Answer", "Long Answer".

OUTPUT ONLY valid JSON in this exact structure:
{{
    "title": "...",
    "questions": [
        {{
            "question_text": "...",
            "question_type": "{question_type}",
            "marks": 1,
            "options": [
                {{"text": "...", "is_correct": true}},
                {{"text": "...", "is_correct": false}}
            ],
            "correct_answer_text": "...",
            "explanation": "..."
        }}
    ]
}}

For Short/Long Answer questions, remove "options" and use "correct_answer_text".
For MCQ questions, include "options" and "is_correct" flags.
""".strip()


# ─── Single question generation prompt ───────────────────────────────────────

SINGLE_QUESTION_PROMPT = """
Generate a single quiz question on the topic "{topic}" for the subject "{subject}".

Configuration:
- Difficulty: {difficulty}
- Type: {question_type}
- Marks: {marks}

Requirements:
1. Ensure the question fits the difficulty.
2. Provide correct answers and concise explanations.
3. If MCQ, provide exactly 4 options.

Respond ONLY with a JSON object in this format:
{{
    "question_text": "...",
    "question_type": "{question_type}",
    "marks": {marks},
    "options": [
        {{"text": "Option A", "is_correct": true}},
        {{"text": "Option B", "is_correct": false}}
    ],
    "correct_answer_text": "...",
    "explanation": "..."
}}

Include "options" only for MCQ. Include "correct_answer_text" only for Short/Long Answer.
""".strip()


JSON_REPAIR_PROMPT = """
The previous model output was not valid JSON.
Convert it into valid JSON only.

Target output type: {target_type}
Fallback title: {fallback_title}

Rules:
- Output ONLY valid JSON.
- No markdown, no commentary, no explanations.
- If target type is "quiz_object", return an object with key "questions" as a list.
- If target type is "config_list", return a JSON list.
- Preserve as much useful content as possible from the source text.

SOURCE TEXT:
{raw_text}
""".strip()
