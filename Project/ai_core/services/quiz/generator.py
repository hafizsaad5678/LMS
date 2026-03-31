"""Quiz Generator Service.

Uses configured LLM provider via call_llm() and
pulls all prompt templates from the shared prompts module.
"""

import json
import logging
import re

from ..llm.provider import call_llm
from ..config import (
    QUIZ_DEFAULT_DIFFICULTY,
    QUIZ_DEFAULT_NUM_QUESTIONS,
    QUIZ_DEFAULT_QUESTION_MARKS,
    QUIZ_DEFAULT_QUESTION_TYPE,
    QUIZ_DEFAULT_TEMPERATURE,
    QUIZ_DEFAULT_TOTAL_MARKS,
    QUIZ_LLM_REQUEST_RETRIES,
    QUIZ_LLM_TIMEOUT_SECONDS,
)
from ..llm.prompts import (
    FULL_QUIZ_PROMPT,
    INITIAL_SUGGESTIONS_PROMPT,
    JSON_ENFORCER,
    JSON_REPAIR_PROMPT,
    SINGLE_QUESTION_PROMPT,
    SYSTEM_PROMPT,
)

logger = logging.getLogger(__name__)


class QuizGeneratorService:
    """Stateless service that generates quizzes through configured LLM provider."""

    @staticmethod
    def get_initial_suggestions(
        topic: str,
        subject: str,
        department: str,
        num_questions: int = QUIZ_DEFAULT_NUM_QUESTIONS,
        question_type: str = QUIZ_DEFAULT_QUESTION_TYPE,
        difficulty: str = QUIZ_DEFAULT_DIFFICULTY,
    ) -> list:
        prompt = INITIAL_SUGGESTIONS_PROMPT.format(
            topic=topic,
            subject=subject,
            department=department,
            num_questions=num_questions,
            question_type=question_type,
            difficulty=difficulty,
        )

        response = call_llm(
            prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=QUIZ_DEFAULT_TEMPERATURE,
            request_timeout=QUIZ_LLM_TIMEOUT_SECONDS,
            request_retries=QUIZ_LLM_REQUEST_RETRIES,
        )
        logger.debug("initial_suggestions raw (500): %s", response[:500])

        return _extract_json_with_repair(response, expect_list=True, fallback_title=f"Quiz on {topic}")

    @staticmethod
    def generate_full_quiz(
        topic: str,
        subject: str,
        config: dict,
        temperature: float = QUIZ_DEFAULT_TEMPERATURE,
    ) -> dict:
        prompt = FULL_QUIZ_PROMPT.format(
            topic=topic,
            subject=subject,
            difficulty=config.get("difficulty", QUIZ_DEFAULT_DIFFICULTY),
            question_type=config.get("question_type", QUIZ_DEFAULT_QUESTION_TYPE),
            num_questions=config.get("num_questions", QUIZ_DEFAULT_NUM_QUESTIONS),
            total_marks=config.get("total_marks", QUIZ_DEFAULT_TOTAL_MARKS),
        )

        response = call_llm(
            prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=temperature,
            request_timeout=QUIZ_LLM_TIMEOUT_SECONDS,
            request_retries=QUIZ_LLM_REQUEST_RETRIES,
        )
        logger.debug("generate_full_quiz raw (500): %s", response[:500])

        quiz_data = _extract_json_with_repair(response, expect_list=False, fallback_title=f"Quiz on {topic}")
        requested_type = str(config.get("question_type", "MCQ"))
        return _enforce_requested_question_type(quiz_data, requested_type)

    @staticmethod
    def generate_single_question(
        topic: str,
        subject: str,
        config: dict,
        temperature: float = QUIZ_DEFAULT_TEMPERATURE,
    ) -> dict:
        prompt = SINGLE_QUESTION_PROMPT.format(
            topic=topic,
            subject=subject,
            difficulty=config.get("difficulty", QUIZ_DEFAULT_DIFFICULTY),
            question_type=config.get("question_type", QUIZ_DEFAULT_QUESTION_TYPE),
            marks=config.get("marks", QUIZ_DEFAULT_QUESTION_MARKS),
        )

        response = call_llm(
            prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=temperature,
            request_timeout=QUIZ_LLM_TIMEOUT_SECONDS,
            request_retries=QUIZ_LLM_REQUEST_RETRIES,
        )
        logger.debug("generate_single_question raw (500): %s", response[:500])

        return _extract_json_with_repair(response, expect_list=False, fallback_title="Question")


def _extract_json(response: str, expect_list: bool = False, fallback_title: str = "Quiz"):
    if not response or not isinstance(response, str):
        raise Exception("Empty or invalid response from AI.")

    data = _try_parse(response.strip())

    if isinstance(data, dict):
        if "questions" in data and not expect_list:
            return data

        if expect_list and all(k in data for k in ["config_name", "total_questions"]):
            return [data]

        for key in ("content", "reasoning_content", "text", "result", "choices"):
            if key == "choices" and isinstance(data.get(key), list) and data[key]:
                msg = data[key][0].get("message", {})
                content = msg.get("content") or msg.get("reasoning_content") or ""
                if content:
                    nested = _find_json_in_text(content, expect_list, fallback_title)
                    if nested is not None:
                        return nested

            val = data.get(key)
            if isinstance(val, str) and ("{" in val or "[" in val):
                nested = _find_json_in_text(val, expect_list, fallback_title)
                if nested is not None:
                    return nested
            if isinstance(val, list) and expect_list:
                return val

    if isinstance(data, list):
        return data if expect_list else {"title": fallback_title, "questions": data}

    if isinstance(data, str):
        logger.debug("Attempting to find JSON in raw string: %s", data[:200])
        found = _find_json_in_text(data, expect_list, fallback_title)
        if found is not None:
            return found
        raise ValueError(f"AI returned invalid format. Expected JSON, got text: {data[:200]}...")

    if expect_list:
        return []

    if not isinstance(data, dict):
        raise ValueError(f"Expected a dictionary for the quiz, but got {type(data).__name__}.")
    if "questions" not in data and "options" not in data:
        raise ValueError(
            f"AI returned a dictionary but it does not look like a quiz. Data: {str(data)[:200]}"
        )

    return data


def _extract_json_with_repair(response: str, expect_list: bool = False, fallback_title: str = "Quiz"):
    try:
        return _extract_json(response, expect_list=expect_list, fallback_title=fallback_title)
    except ValueError as exc:
        logger.warning("Primary JSON extraction failed, attempting repair pass: %s", exc)
        repaired_response = _repair_non_json_response(
            response=response,
            expect_list=expect_list,
            fallback_title=fallback_title,
        )
        return _extract_json(repaired_response, expect_list=expect_list, fallback_title=fallback_title)


def _repair_non_json_response(response: str, expect_list: bool, fallback_title: str) -> str:
    target_type = "config_list" if expect_list else "quiz_object"
    safe_text = (response or "")[:6000]
    repair_prompt = JSON_REPAIR_PROMPT.format(
        target_type=target_type,
        fallback_title=fallback_title,
        raw_text=safe_text,
    )
    return call_llm(
        repair_prompt,
        system_prompt=JSON_ENFORCER,
        request_timeout=QUIZ_LLM_TIMEOUT_SECONDS,
        request_retries=QUIZ_LLM_REQUEST_RETRIES,
    )


def _try_parse(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return text


def _find_json_in_text(text: str, expect_list: bool = False, fallback_title: str = "Quiz"):
    # Reverse boundary scanning is quadratic in the worst case but acceptable
    # here because model outputs are typically small text payloads.
    text = re.sub(r"```json\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
    text = re.sub(r"```\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)

    pairs = [("[", "]"), ("{", "}")] if expect_list else [("{", "}"), ("[", "]")]

    for open_ch, close_ch in pairs:
        curr_start = 0
        while True:
            start = text.find(open_ch, curr_start)
            if start == -1:
                break

            curr_end = len(text)
            while curr_end > start:
                end = text.rfind(close_ch, start, curr_end)
                if end == -1:
                    break

                candidate = text[start : end + 1].strip()
                if not candidate:
                    curr_end = end
                    continue

                try:
                    parsed = json.loads(candidate)

                    if isinstance(parsed, dict) and "quiz" in parsed and isinstance(parsed["quiz"], dict):
                        return parsed["quiz"]

                    if expect_list:
                        if isinstance(parsed, list) and len(parsed) > 0:
                            return parsed
                        if isinstance(parsed, dict):
                            for key in ["suggestions", "variations", "configs", "configurations"]:
                                if isinstance(parsed.get(key), list):
                                    return parsed[key]
                    else:
                        if isinstance(parsed, dict):
                            return parsed
                        if isinstance(parsed, list):
                            return {"title": fallback_title, "questions": parsed}

                except (json.JSONDecodeError, ValueError):
                    pass

                curr_end = end

            curr_start = start + 1

    return None


def _normalize_question_type(question_type: str) -> str:
    value = (question_type or "").strip().lower()
    if "mixed" in value:
        return "Mixed"
    if "long" in value or "essay" in value:
        return "Long Answer"
    if "short" in value:
        return "Short Answer"
    return "MCQ"


def _enforce_requested_question_type(quiz_data: dict, requested_type: str) -> dict:
    normalized_type = _normalize_question_type(requested_type)
    questions = quiz_data.get("questions", [])
    if not isinstance(questions, list):
        return quiz_data

    if normalized_type == "Mixed":
        _enforce_mixed_question_types(questions, requested_type)
        return quiz_data

    for question in questions:
        if not isinstance(question, dict):
            continue

        question["question_type"] = normalized_type

        if normalized_type == "MCQ":
            if not isinstance(question.get("options"), list):
                question["options"] = []
        else:
            question.pop("options", None)
            if not question.get("correct_answer_text") and isinstance(question.get("correct_answer"), str):
                question["correct_answer_text"] = question["correct_answer"]

    return quiz_data


def _parse_mixed_targets(requested_type: str) -> dict:
    text = (requested_type or "").lower()

    patterns = {
        "MCQ": [r"(\d+)\s*(multiple\s*choice|mcq)"],
        "Short Answer": [r"(\d+)\s*(short\s*answer|short)"],
        "Long Answer": [r"(\d+)\s*(long\s*answer|essay|long)"],
    }

    result = {"MCQ": 0, "Short Answer": 0, "Long Answer": 0}
    for label, regex_list in patterns.items():
        for pattern in regex_list:
            match = re.search(pattern, text)
            if match:
                result[label] = int(match.group(1))
                break

    return result


def _apply_question_type_shape(question: dict, q_type: str):
    question["question_type"] = q_type
    if q_type == "MCQ":
        if not isinstance(question.get("options"), list) or len(question.get("options", [])) == 0:
            question["options"] = []
    else:
        question.pop("options", None)
        if not question.get("correct_answer_text") and isinstance(question.get("correct_answer"), str):
            question["correct_answer_text"] = question["correct_answer"]


def _enforce_mixed_question_types(questions: list, requested_type: str):
    targets = _parse_mixed_targets(requested_type)
    total_target = sum(targets.values())

    if total_target <= 0:
        for question in questions:
            if not isinstance(question, dict):
                continue
            inferred = _normalize_question_type(str(question.get("question_type", "")))
            _apply_question_type_shape(question, inferred)
        return

    assigned = {"MCQ": 0, "Short Answer": 0, "Long Answer": 0}

    for question in questions:
        if not isinstance(question, dict):
            continue

        existing = _normalize_question_type(str(question.get("question_type", "")))
        if existing in assigned and assigned[existing] < targets.get(existing, 0):
            _apply_question_type_shape(question, existing)
            assigned[existing] += 1
        else:
            question["question_type"] = ""

    remaining = []
    for label in ("MCQ", "Short Answer", "Long Answer"):
        needed = max(targets.get(label, 0) - assigned[label], 0)
        remaining.extend([label] * needed)

    rem_idx = 0
    for question in questions:
        if not isinstance(question, dict):
            continue
        if question.get("question_type"):
            continue

        if rem_idx < len(remaining):
            chosen = remaining[rem_idx]
            rem_idx += 1
        else:
            chosen = _normalize_question_type(str(question.get("question_type", "")))
            if chosen == "MCQ" and not (isinstance(question.get("options"), list) and question.get("options")):
                chosen = "Short Answer"

        _apply_question_type_shape(question, chosen)
