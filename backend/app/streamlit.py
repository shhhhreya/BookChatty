import streamlit as st
import requests

# FastAPI Backend URL
API_URL = "http://127.0.0.1:8000"  # Change if hosting on cloud

st.set_page_config(page_title="BookChatty", page_icon="📚")

# Title
st.title("BookChatty : AI-Powered Book Q&A")

# Upload PDF Section
st.header("📂 Upload a Book (PDF)")
uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])
book_title = st.text_input("Enter Book Title")

if uploaded_file and book_title:
    if st.button("Upload Book"):
        files = {"file": uploaded_file.getvalue()}
        data = {"book_title": book_title}

        response = requests.post(f"{API_URL}/upload/", files=files, data=data)
        if response.status_code == 200:
            st.success(f"✅ {book_title} uploaded successfully!")
        else:
            st.error("❌ Failed to upload. Check API connection.")

# Question-Answer Section
st.header("🤖 Ask a Question about the Book")
query = st.text_input("Enter your question")

if query:
    if st.button("Ask AI"):
        params = {"query": query}
        response = requests.get(f"{API_URL}/query/", params=params)

        if response.status_code == 200:
            answer = response.json()["answer"]
            st.subheader("💡 Answer:")
            st.write(answer)
        else:
            st.error("❌ Error retrieving answer. Try again!")

# About Sidebar
st.sidebar.title("ℹ️ About")
st.sidebar.info(
    "Upload books as PDFs and ask questions. The AI retrieves relevant information and provides accurate answers!"
)
