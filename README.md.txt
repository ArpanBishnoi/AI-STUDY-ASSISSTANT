📚 AI STUDY ASSISTANT

«An AI-powered study companion that transforms PDFs into interactive learning experiences using Retrieval-Augmented Generation (RAG), semantic search, and intelligent study tools.»

---

🚀 Overview

AI STUDY ASSISTANT is a full-stack AI application designed to help students study smarter, not harder.

Instead of reading hundreds of pages manually, students can upload PDFs and instantly generate summaries, ask questions, create flashcards, practice quizzes, review AI-generated notes, and much more—all from a single platform.

The project combines modern AI technologies with a scalable backend architecture to provide an intelligent and interactive learning experience.

---

✨ Features

📂 PDF Library

- Upload and organize study materials
- Manage multiple PDFs
- Secure document storage

📝 AI Summary

- Generate concise summaries of long PDFs
- Understand key concepts in seconds

❓ Ask Questions (RAG)

- Ask questions directly from uploaded PDFs
- Semantic search using vector embeddings
- Context-aware AI responses

🧠 Flashcards

- Automatically generate flashcards
- Perfect for active recall learning

📋 AI Quiz Generator

- Generate quizzes from study material
- Reinforce concepts through practice

📖 AI Study Notes

- Create structured revision notes
- Highlight important topics automatically

💡 Explain AI

- Simplify difficult concepts
- Easy-to-understand explanations

🏦 Question Bank

- Generate practice questions
- Useful for exam preparation

🔄 Revise AI

- Quick revision mode
- Refresh important concepts before exams

💬 Chat History

- Store previous AI conversations
- Continue learning seamlessly

📚 Summary History

- Access previously generated summaries anytime

🔐 Authentication

- Secure user registration & login
- Password hashing with BCrypt
- JWT Authentication

---

🛠 Tech Stack

Backend

- FastAPI
- PostgreSQL
- Neon Database
- ChromaDB

Frontend

- Streamlit

AI

- OpenRouter
- Jina Embeddings
- Retrieval-Augmented Generation (RAG)

Deployment

- Render
- Streamlit Community Cloud

---

🏗 Architecture

Student
   │
   ▼
Streamlit Frontend
   │
   ▼
FastAPI Backend
   │
   ├────────────► PostgreSQL (Neon)
   │
   ├────────────► ChromaDB
   │
   ├────────────► Jina Embeddings
   │
   └────────────► OpenRouter LLM

---

⚡ How It Works

1. User uploads a PDF.
2. Text is extracted from the document.
3. Text is divided into chunks.
4. Embeddings are generated.
5. Embeddings are stored in ChromaDB.
6. When the user asks a question:
   - Similar chunks are retrieved.
   - Relevant context is sent to the LLM.
   - AI generates an accurate answer.

This Retrieval-Augmented Generation (RAG) pipeline significantly improves answer quality while reducing hallucinations.

---

🌍 Live Demo

Frontend:

https://d3rp7pr5gcpuuwuutojqib.streamlit.app/

Backend API:

https://ai-study-assisstant-84vk.onrender.com

---

📂 Project Structure

AI_STUDY_ASSISTANT/

├── backend/
│   ├── database.py
│   ├── embedding.py
│   ├── llm.py
│   ├── search.py
│   ├── prompts.py
│   └── requirements.txt
│
├── streamlit_app/
│   ├── app.py
│   ├── config.py
│   └── pages/
│
└── README.md

---

🎯 Future Improvements

- Voice-based learning
- OCR support
- Image understanding
- YouTube lecture summarization
- Multi-language support
- AI study planner
- Spaced repetition system
- Mobile application

---

👨‍💻 Author

Arpan Bishnoi

AI & Software Developer

Passionate about Artificial Intelligence, Entrepreneurship, and building impactful products.

---

⭐ If you found this project interesting, consider giving it a star!



