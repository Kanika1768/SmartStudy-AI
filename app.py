import streamlit as st
import json
import requests
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_splitter import split_documents
from src.qa_engine import (
    store_chunks,
    retrieve_chunks_by_document,
    retrieve_random_chunks
)
from src.tracker import (
    save_attempt,
    get_weak_chunks,
    get_weakest_document
)
st.title("SmartStudy AI")
st.write("Upload one or more PDFs. SmartStudy AI will answer questions, generate quizzes, and identify weak topics.")
uploaded_files = st.file_uploader(
    "Upload one or more PDFs",
    type="pdf",
    accept_multiple_files=True
)
if uploaded_files:

    current_files = sorted([file.name for file in uploaded_files])

    if (st.session_state.get("uploaded_files") != current_files 
        or "chunks" not in st.session_state):

        st.session_state.uploaded_files = current_files

        all_chunks = []

        with st.spinner("Processing uploaded PDFs..."):

            try:

                for uploaded_file in uploaded_files:

                    with open("temp.pdf", "wb") as f:
                        f.write(uploaded_file.read())

                    pages = load_pdf(
                        "temp.pdf",
                        document_name=uploaded_file.name
                    )

                    chunks = split_documents(pages)

                    all_chunks.extend(chunks)

                st.session_state.chunks = all_chunks

                st.session_state.pop("questions", None)
                st.session_state.pop("quiz_document", None)
                store_chunks(all_chunks)

                st.success(
                f"Successfully indexed {len(uploaded_files)} PDFs "
                f"({len(all_chunks)} chunks)"
                )

            except Exception as e:

                st.error(str(e))

                if "chunks" in st.session_state:
                    del st.session_state["chunks"]
                if "uploaded_files" in st.session_state:
                    del st.session_state["uploaded_files"]

if "chunks" in st.session_state:
    st.markdown("### 📚 Uploaded Documents")

    for file_name in st.session_state.get("uploaded_files", []):
        st.success(file_name)
    st.divider()

    tab1, tab2, tab3 , tab4 , tab5= st.tabs(
        ["Quiz Me",
        "Ask a Question",
        "My Weak Spots",
        "Flashcards",
        "Study Summary"
        ]
    )

    

    with tab1:

        st.subheader("Quiz Generator")

        documents = sorted({
        chunk["document"]
        for chunk in st.session_state.chunks
        })

        selected_document = st.selectbox(
        "Choose Document",
        documents
        )
        quiz_mode = st.selectbox(
            "Choose Quiz Mode",
            [
                "Entire Document",
                "Weak Topics",
                "Random Revision",
                "Exam Mode"
        ]
        )
        difficulty = st.selectbox(
            "Choose Difficulty",
            [
                "Easy",
                "Medium",
                "Hard"
            ]
        )

        if quiz_mode == "Entire Document":
            document_chunks = retrieve_chunks_by_document(
                selected_document
            )

            quiz_document = selected_document
            st.caption(
                f"Using {len(document_chunks)} sections from {selected_document}."
            )

        elif quiz_mode == "Weak Topics":

            weakest_document = get_weakest_document()

            if weakest_document is None:

                st.warning(
                    "Answer some quiz questions first."
                )

                document_chunks = []
                quiz_document = None

            else:
                st.success(
                    f"Weakest document: {weakest_document}"
                )

                document_chunks = retrieve_chunks_by_document(
                    weakest_document
                )

                quiz_document = weakest_document

                st.caption(
                    f"Using {len(document_chunks)} sections from {weakest_document}."
                )

        elif quiz_mode == "Random Revision":
            document_chunks = retrieve_random_chunks()

            quiz_document = "Random Revision"

            st.success(
                "Generating a mixed revision quiz."
           )

            st.caption(
                f"Using {len(document_chunks)} random sections from all uploaded PDFs."
         )

        elif quiz_mode == "Exam Mode":
            document_chunks = retrieve_chunks_by_document(
                selected_document
                )

            quiz_document = selected_document
            st.success("Exam Mode")

            st.caption(
                f"Generating a 20-question exam from {selected_document}."
            )

        else:
            st.info("Invalid quiz mode.")
            document_chunks = []
            quiz_document = None

        if st.button("Generate Quiz") and document_chunks:
            with st.spinner("Generating questions..."):
                try:
                    st.session_state.pop("questions", None)
                    document_text = "\n\n".join(
                        chunk["text"]
                        for chunk in document_chunks
                    )
                    

                    question_count = 3
                    if quiz_mode == "Exam Mode":
                          question_count = 20

                    response = requests.post(
                         "http://127.0.0.1:8000/quiz/generate",
                         json={
                              "document_text": document_text,
                              "difficulty": difficulty,
                              "num_questions": question_count
                            }
                    )
                    if response.status_code != 200:
                         st.error(f"Backend Error: {response.text}")
                         st.stop()

                    raw = response.json()["quiz"]
                    

                    if raw is None:
                        st.error("Failed after 3 retries. Try again.")

                    else:
                        raw = raw.replace(
                            "```json", ""
                        ).replace(
                            "```", ""
                        ).strip()

                        st.session_state.questions = json.loads(raw)

                        st.session_state.quiz_document = quiz_document

                        if quiz_document == "Random Revision":
                            st.success(
                                "Random Revision quiz generated successfully."
                           )

                        elif quiz_mode == "Exam Mode":
                            st.success(
                                "Exam generated successfully."
                            )

                        else:
                            st.success(
                                f"Quiz generated successfully from {quiz_document}."
                            )

                except json.JSONDecodeError:
                    st.error("Quiz generator returned invalid JSON.")
                    st.code(raw)

                except Exception as e:
                    st.error(f"Error: {e}")

        if "questions" in st.session_state:

            # -------------------------------
            # EXAM MODE
            # -------------------------------
            if quiz_mode == "Exam Mode":

                with st.form("exam_form"):

                    user_answers = {}

                    for index, q in enumerate(st.session_state.questions):

                        st.write(f"### Question {index + 1}")
                        st.write(q["question"])

                        if q["type"] == "mcq":

                            user_answers[index] = st.radio(
                                "Choose your answer:",
                                options=q["options"],
                                key=f"exam_radio_{index}"
                            )

                        else:

                            user_answers[index] = st.text_input(
                                "Your answer:",
                                key=f"exam_text_{index}"
                            )

                        st.divider()

                    submit_exam = st.form_submit_button("Submit Exam")

                if submit_exam:

                    score = 0

                    for index, q in enumerate(st.session_state.questions):

                        is_correct = (
                            user_answers[index].strip().lower()
                            ==
                            q["answer"].strip().lower()
                        )

                        if is_correct:
                            score += 1

                        save_attempt(
                            chunk_id=st.session_state.quiz_document,
                            document=st.session_state.quiz_document,
                            question=q["question"],
                            correct=is_correct
                        )

                    total = len(st.session_state.questions)

                    st.success("🎉 Exam Completed!")

                    st.metric("Score", f"{score}/{total}")

                    st.metric(
                        "Percentage",
                        f"{round(score * 100 / total)}%"
                    )

                    st.write(f"✅ Correct: {score}")
                    st.write(f"❌ Wrong: {total - score}")
                    st.markdown("---")
                    st.subheader("📝 Review Answers")

                    for index, q in enumerate(st.session_state.questions):

                        user_answer = user_answers[index]

                        correct_answer = q["answer"]

                        if user_answer.strip().lower() == correct_answer.strip().lower():

                            st.success(f"Q{index + 1}: {q['question']}")
                            st.write(f"Your answer: {user_answer}")

                        else:

                            st.error(f"Q{index + 1}: {q['question']}")
                            st.write(f"Your answer: {user_answer}")
                            st.write(f"Correct answer: {correct_answer}")

                        st.divider()
                   

                    if score >= 18:
                        st.balloons()
                        st.success("Excellent performance! 🌟")

                    elif score >= 14:
                        st.success("Good job! Keep practicing.")

                    elif score >= 10:
                        st.warning("Decent score. Review weak topics.")

                    else:
                        st.error("You need more revision. Try Weak Topics mode.")

            # -------------------------------
            # NORMAL QUIZ
            # -------------------------------
            else:

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
                                chunk_id=st.session_state.quiz_document,
                                document=st.session_state.quiz_document,
                                question=q["question"],
                                correct=is_correct
                            )

                    st.divider()   

    with tab2:

        st.subheader("Ask Anything About Your Study Material")

        question = st.text_input("Enter your question")

        if st.button("Get Answer"):

            if question.strip() == "":

                st.warning("Please enter a question.")

            else:

                with st.spinner("Searching study material..."):

                    response = requests.post(
                        "http://127.0.0.1:8000/qa/ask",
                        json={
                            "question": question
                        }
                    )

                    if response.status_code != 200:
                        st.error(f"Backend Error: {response.text}")
                        st.stop()

                    result = response.json()

                    st.success(result["answer"])

                    st.markdown("### 📚 Sources")

                    for source in result["sources"]:
                        st.write(f"📄 {source}")

   

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

                chart_data[chunk_id] = wrong_pct

            st.write(
                "**Percentage of incorrectly answered questions**"
            )

            st.bar_chart(chart_data)

    with tab4:

        st.subheader("📖 AI Flashcards")

        documents = sorted({
            chunk["document"]
            for chunk in st.session_state.chunks
        })

        flash_document = st.selectbox(
            "Choose Document",
            documents,
            key="flash_doc"
        )

        if st.button("Generate Flashcards"):

            with st.spinner("Creating flashcards..."):

                try:

                    document_chunks = retrieve_chunks_by_document(
                        flash_document
                    )

                    document_text = "\n\n".join(
                        chunk["text"]
                        for chunk in document_chunks
                    )

                    response = requests.post(
                        "http://127.0.0.1:8000/flashcards/generate",
                        json={
                            "document_text": document_text
                        }
                    )

                    if response.status_code != 200:
                        st.error(f"Backend Error: {response.text}")
                        st.stop()

                    raw = response.json()["flashcards"]

                    raw = raw.replace(
                        "```json", ""
                    ).replace(
                        "```", ""
                    ).strip()

                    st.session_state.flashcards = json.loads(raw)

                    st.session_state.flash_index = 0
                    st.session_state.show_answer = False

                    st.success(
                        "Flashcards generated successfully!"
                    )

                except json.JSONDecodeError:

                    st.error(
                        "Flashcards returned invalid JSON."
                    )

                except Exception as e:

                    st.error(f"Error: {e}")

        if "flashcards" in st.session_state:

            if "flash_index" not in st.session_state:
                st.session_state.flash_index = 0

            if "show_answer" not in st.session_state:
                st.session_state.show_answer = False

            card = st.session_state.flashcards[
                st.session_state.flash_index
            ]

            st.markdown("---")

            st.write(
                f"### Card {st.session_state.flash_index + 1} of {len(st.session_state.flashcards)}"
            )

            st.info(card["front"])

            if st.session_state.show_answer:
                st.success(card["back"])

            col1, col2, col3 = st.columns(3)

            with col1:

                if st.button("⬅ Previous"):

                    if st.session_state.flash_index > 0:

                        st.session_state.flash_index -= 1
                        st.session_state.show_answer = False
                        st.rerun()

            with col2:

                if st.button("🔄 Flip Card"):

                    st.session_state.show_answer = (
                        not st.session_state.show_answer
                    )

                    st.rerun()

            with col3:

                if st.button("Next ➡"):

                    if (
                        st.session_state.flash_index
                        < len(st.session_state.flashcards) - 1
                    ):

                        st.session_state.flash_index += 1
                        st.session_state.show_answer = False
                        st.rerun()

    with tab5:

        st.subheader("📄 AI Study Summary")

        documents = sorted({
            chunk["document"]
            for chunk in st.session_state.chunks
        })

        summary_document = st.selectbox(
            "Choose Document",
            documents,
            key="summary_doc"
        )

        if st.button("Generate Summary"):

            with st.spinner("Generating study summary..."):

                try:

                    document_chunks = retrieve_chunks_by_document(
                        summary_document
                    )

                    document_text = "\n\n".join(
                        chunk["text"]
                        for chunk in document_chunks
                    )

                    response = requests.post(
                        "http://127.0.0.1:8000/summary/generate",
                        json={
                            "document_text": document_text
                        }
                    )

                    if response.status_code != 200:
                        st.error(f"Backend Error: {response.text}")
                        st.stop()

                    raw = response.json()["summary"]

                    raw = raw.replace(
                        "```json", ""
                    ).replace(
                        "```", ""
                    ).strip()

                    st.session_state.summary = json.loads(
                        raw
                    )

                    st.success(
                        "Study Summary generated successfully!"
                    )

                except json.JSONDecodeError:

                    st.error(
                        "Summary generator returned invalid JSON."
                    )

                except Exception as e:

                    st.error(f"Error: {e}")

        if "summary" in st.session_state:

            summary = st.session_state.summary

            st.markdown("---")

            st.subheader("📚 Summary")

            st.write(summary.get("summary", ""))

            st.markdown("---")

            st.subheader("Key Concepts")

            for concept in summary.get(
                "key_concepts", []
            ):

                st.markdown(f"- {concept}")

            st.markdown("---")

            st.subheader("📖 Important Definitions")

            for definition in summary.get(
                "definitions", []
            ):

                st.markdown(f"- {definition}")

            st.markdown("---")

            st.subheader("Exam Tips")

            for tip in summary.get(
                "exam_tips", []
            ):

                st.markdown(f"- {tip}")