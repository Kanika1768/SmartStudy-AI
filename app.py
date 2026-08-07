import streamlit as st
import json
from src.ingestion.pdf_loader import load_pdf
from src.ingestion.text_splitter import split_documents
from src.quiz_generator import generate_quiz
from src.qa_engine import (
    answer_question,
    store_chunks,
    retrieve_chunks_by_document
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

    tab1, tab2, tab3 = st.tabs(
        ["Quiz Me", "Ask a Question", "My Weak Spots"]
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

        else:
            st.info(f"{quiz_mode} mode is coming soon!")
            document_chunks = []
            quiz_document = None

        if st.button("Generate Quiz") and document_chunks:
            with st.spinner("Generating questions..."):
                try:
                    document_text = "\n\n".join(
                        chunk["text"]
                        for chunk in document_chunks
                    )

                    raw = generate_quiz(
                        document_text,
                        difficulty=difficulty
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

                        st.session_state.quiz_document = quiz_document

                        st.success(
                            f"Quiz generated successfully from {quiz_document}."
                        )

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

                    result = answer_question(question)

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