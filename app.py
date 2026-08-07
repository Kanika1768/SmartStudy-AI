import streamlit as st
import json
import os

from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_splitter import split_documents
from src.quiz_generator import generate_quiz
from src.qa_engine import answer_question, store_chunks
from src.tracker import save_attempt, get_weak_chunks

st.title("SmartStudy AI")
st.write("Upload your notes — AI will quiz you, answer questions, and track your weak spots.")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")

if uploaded_file is not None:

    if "chunks" not in st.session_state:

        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        pages = load_pdf(
            "temp.pdf",
            document_name=uploaded_file.name
            )
        st.session_state.chunks = split_documents(pages)

        with st.spinner("Processing your PDF... this may take a moment for large files."):

            try:
                store_chunks(st.session_state.chunks)
                st.success(f"PDF loaded! Found {len(st.session_state.chunks)} sections.")

            except Exception as e:
                st.error(f"Failed to process PDF.\n\n{e}")
                del st.session_state.chunks

if "chunks" in st.session_state:

    tab1, tab2, tab3 = st.tabs(
        ["Quiz Me", "Ask a Question", "My Weak Spots"]
    )

    # ======================================================
    # QUIZ TAB
    # ======================================================

    with tab1:

        st.subheader("Quiz Generator")

        chunk_index = st.selectbox(
            "Pick a section:",
            range(len(st.session_state.chunks)),
            format_func=lambda x: f"Section {x + 1}"
        )

        if st.button("Generate Quiz"):

            with st.spinner("Generating questions..."):

                try:

                    raw = generate_quiz(
                        st.session_state.chunks[chunk_index]["text"]
                    )

                    if raw is None:

                        st.error("Failed after 3 retries. Try again.")

                    else:

                        raw = raw.replace(
                            "```json", ""
                        ).replace(
                            "```", ""
                        ).strip()

                        st.session_state.questions = json.loads(raw)
                        st.session_state.quiz_chunk_index = chunk_index

                except json.JSONDecodeError:

                    st.error("Quiz generator returned invalid JSON.")
                    st.code(raw)

                except Exception as e:

                    st.error(f"Error: {e}")

        if "questions" in st.session_state:

            for index, q in enumerate(st.session_state.questions):

                st.write(f"### Question {index + 1}")
                st.write(q["question"])

                with st.form(key=f"quiz_form_{index}"):

                    if q["type"] == "mcq":

                        user_choice = st.radio(
                            "Choose your answer:",
                            options=q["options"],
                            key=f"radio_{index}"
                        )

                    else:

                        user_choice = st.text_input(
                            "Your answer:",
                            key=f"text_{index}"
                        )

                    submit = st.form_submit_button("Submit Answer")

                    if submit:

                        is_correct = (
                            user_choice.strip().lower()
                            ==
                            q["answer"].strip().lower()
                        )

                        if is_correct:

                            st.success("✅ Correct!")

                        else:

                            st.error(
                                f"❌ Incorrect!\n\nCorrect answer: {q['answer']}"
                            )

                        save_attempt(
                            chunk_id=f"chunk_{st.session_state.quiz_chunk_index}",
                            question=q["question"],
                            correct=is_correct
                        )

                st.divider()

    # ======================================================
    # ASK QUESTION TAB
    # ======================================================

    with tab2:

        st.subheader("Ask Anything About Your Notes")

        question = st.text_input("Enter your question")

        if st.button("Get Answer"):

            if question.strip() == "":

                st.warning("Please enter a question.")

            else:

                with st.spinner("Searching notes..."):

                    result = answer_question(question)

                    st.success(result["answer"])

                    st.markdown("### 📚 Sources")

                    for source in result["sources"]:
                        st.write(f"📄 {source}")

    # ======================================================
    # WEAK SPOTS TAB
    # ======================================================

    with tab3:

        st.subheader("Your Weak Spots")

        stats = get_weak_chunks()

        if not stats:

            st.info(
                "Answer some quiz questions first to see your weak spots."
            )

        else:

            chart_data = {}

            for chunk_id, counts in stats.items():

                total = counts["correct"] + counts["wrong"]

                wrong_pct = round(
                    (counts["wrong"] / total) * 100
                )

                chart_data[
                    f"Section {chunk_id[-1]}"
                ] = wrong_pct

            st.write(
                "**Percentage of incorrectly answered questions**"
            )

            st.bar_chart(chart_data)