import re
import streamlit as st

import api_client
from session import get_auth_headers, logout


def render_flashcards_page():
    st.title("Flashcards & Quiz")
    st.caption("Generate study flashcards and a practice quiz from your active PDF.")

    if not st.session_state.pdf_id:
        st.warning("No active PDF. Set one as active from **My Library** first.")
        return

    st.info(f"Active PDF ID: **{st.session_state.pdf_id}**")

    headers = get_auth_headers()

    tab_flash, tab_quiz = st.tabs(["Flashcards", "Quiz"])

    with tab_flash:
        _render_flashcards_tab(headers)

    with tab_quiz:
        _render_quiz_tab(headers)


def _render_flashcards_tab(headers: dict):
    st.subheader("Generate Flashcards")

    col_num, col_diff = st.columns(2)
    with col_num:
        num_cards = st.number_input(
            "Number of flashcards", min_value=1, max_value=20, value=5, step=1
        )
    with col_diff:
        difficulty = st.select_slider(
            "Difficulty", options=["Easy", "Medium", "Hard"], value="Medium"
        )

    if st.button("Generate Flashcards", type="primary", use_container_width=True):
        with st.spinner("Generating flashcards... this may take a moment."):
            try:
                result = api_client.generate_flashcards(
                    st.session_state.pdf_id,
                    int(num_cards),
                    difficulty,
                    headers,
                )
                raw = result.get("HERE ARE Your Flashcards", "")
                cards = _parse_flashcards(raw)
                st.session_state.flashcards = cards
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))

    cards = st.session_state.get("flashcards", [])
    if not cards:
        st.info("No flashcards yet. Click **Generate Flashcards** above.")
        return

    st.caption(f"{len(cards)} flashcard(s) generated")
    _render_card_browser(cards)


def _render_card_browser(cards: list):
    if "flashcard_index" not in st.session_state:
        st.session_state.flashcard_index = 0
    if "flashcard_flipped" not in st.session_state:
        st.session_state.flashcard_flipped = False

    idx = st.session_state.flashcard_index
    idx = max(0, min(idx, len(cards) - 1))
    st.session_state.flashcard_index = idx

    card = cards[idx]
    front, back = card

    st.progress((idx + 1) / len(cards))
    st.caption(f"Card {idx + 1} of {len(cards)}")

    if st.session_state.flashcard_flipped:
        st.success("**Answer**")
        st.markdown(back)
    else:
        st.info("**Question**")
        st.markdown(front)

    col_flip, col_prev, col_next = st.columns([1, 1, 1])

    with col_flip:
        if st.button("Flip", use_container_width=True):
            st.session_state.flashcard_flipped = not st.session_state.flashcard_flipped
            st.rerun()

    with col_prev:
        if st.button("‹ Previous", use_container_width=True, disabled=(idx == 0)):
            st.session_state.flashcard_index = idx - 1
            st.session_state.flashcard_flipped = False
            st.rerun()

    with col_next:
        if st.button("Next ›", use_container_width=True, disabled=(idx == len(cards) - 1)):
            st.session_state.flashcard_index = idx + 1
            st.session_state.flashcard_flipped = False
            st.rerun()


def _parse_flashcards(raw: str) -> list:
    cards = []
    pattern = re.compile(
        r"Front:\s*(.*?)\s*Back:\s*(.*?)(?=### Flashcard|\Z)",
        re.DOTALL,
    )
    for match in pattern.finditer(raw):
        front = match.group(1).strip()
        back = match.group(2).strip()
        if front and back:
            cards.append((front, back))
    return cards


def _render_quiz_tab(headers: dict):
    st.subheader("Generate Quiz")

    if st.button("Generate Quiz", type="primary", use_container_width=True):
        with st.spinner("Generating quiz... this may take a moment."):
            try:
                result = api_client.get_quiz(st.session_state.pdf_id, headers)
                raw = result.get("Here are your questions", "")
                questions = _parse_quiz(raw)
                st.session_state.quiz_questions = questions
                st.session_state.quiz_answers = {}
            except api_client.APIError as exc:
                _handle_api_error(exc)
            except Exception as exc:
                if api_client.is_connection_error(exc):
                    st.error(_backend_unreachable_message())
                else:
                    st.error(str(exc))

    questions = st.session_state.get("quiz_questions", [])
    if not questions:
        st.info("No quiz yet. Click **Generate Quiz** above.")
        return

    st.caption(f"{len(questions)} question(s) in this quiz")
    _render_quiz_form(questions)


def _render_quiz_form(questions: list):
    answers = st.session_state.get("quiz_answers", {})

    for i, q in enumerate(questions):
        question_text, options, correct = q
        st.markdown(f"**Q{i + 1}. {question_text}**")
        choice = st.radio(
            f"Question {i + 1}",
            options=options,
            index=None,
            key=f"quiz_q_{i}",
            label_visibility="collapsed",
        )
        answers[i] = choice
        st.divider()

    st.session_state.quiz_answers = answers

    if st.button("Submit Quiz", type="primary", use_container_width=True):
        _grade_quiz(questions, answers)


def _grade_quiz(questions: list, answers: dict):
    total = len(questions)
    score = 0
    for i, q in enumerate(questions):
        _, _, correct = q
        if answers.get(i) and answers[i].startswith(correct):
            score += 1

    percentage = (score / total) * 100 if total else 0

    if percentage >= 80:
        st.success(f"Excellent! You scored **{score}/{total}** ({percentage:.0f}%).")
    elif percentage >= 50:
        st.info(f"Good effort! You scored **{score}/{total}** ({percentage:.0f}%).")
    else:
        st.warning(f"You scored **{score}/{total}** ({percentage:.0f}%). Keep practicing!")

    st.caption("Review the correct answers below:")
    for i, q in enumerate(questions):
        question_text, _, correct = q
        user_ans = answers.get(i, "Not answered")
        if user_ans and user_ans.startswith(correct):
            st.markdown(f"✅ **Q{i + 1}:** Correct — {correct}")
        else:
            st.markdown(f"❌ **Q{i + 1}:** Correct answer: **{correct}** (you: {user_ans})")


def _parse_quiz(raw: str) -> list:
    questions = []
    blocks = re.split(r"(?=\*\*\d+[\.\)]|^\d+[\.\)]\s)", raw, flags=re.MULTILINE)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        q_match = re.match(
            r"(?:\*\*)?\d+[\.\)]\s*(.*?)(?=\n[\(\[]?[A-Da-d][\)\]])",
            block,
            re.DOTALL,
        )
        if not q_match:
            continue
        question_text = q_match.group(1).strip()

        opts = re.findall(
            r"[\(\[]?([A-Da-d])[\)\]]\s*(.*?)(?=\n[\(\[]?[A-Da-d][\)\]]|Correct Answer:|\Z)",
            block,
            re.DOTALL,
        )
        options = [f"{letter}) {text.strip()}" for letter, text in opts]

        correct_match = re.search(r"Correct Answer:\s*([A-Da-d])", block)
        correct = correct_match.group(1).upper() if correct_match else ""

        if question_text and len(options) == 4 and correct:
            questions.append((question_text, options, correct))
    return questions


def _handle_api_error(exc: api_client.APIError):
    if exc.status_code == 401:
        logout()
        st.error("Session expired. Please log in again.")
        st.rerun()
    else:
        st.error(str(exc))


def _backend_unreachable_message() -> str:
    return (
        "Could not reach the backend. Start FastAPI first:\n\n"
        "`uvicorn database:app --reload` from the `backend` folder."
    )
