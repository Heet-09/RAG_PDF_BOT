# 📄 PDF AI Chat - A Beginner's Guide

Welcome to **PDF AI Chat**! This is a web application that lets you upload PDF documents and ask an AI questions about them. The AI reads through your documents and answers questions based on their content.

---

## 🎯 What Does This Project Do?

Imagine you have a 100-page PDF manual, and you want to ask "What's the warranty period?" Instead of reading all 100 pages, this app:

1. **Uploads your PDF** to the system
2. **Remembers everything** in that PDF using AI (specifically, something called "Retrieval-Augmented Generation" or RAG)
3. **Answers your questions** by finding the relevant information in the PDF
4. **Keeps your chats** so you can come back and see previous conversations

### Key Features:
- 👤 **Multiple Users**: Each user has their own account with login
- 💬 **Multiple Chats**: Have different conversations for different PDFs
- 📄 **PDF Upload**: Upload up to 3 PDFs at once per chat
- 💾 **Chat History**: All your conversations are saved
- ⚡ **Real-time Responses**: Get answers as they're being generated (streaming)
- 🔐 **Secure**: Login required, your data is private

---

## 📁 Project Structure

Here's what each folder does:

```
project/
├── backend/              # The "brain" of the app (Python code)
│   ├── main.py          # Main server code (FastAPI)
│   ├── rag.py           # PDF reading & AI logic
│   ├── db.py            # Database connections
│   ├── models.py        # Data structure definitions
│   ├── chat_history.py  # Managing conversations
│   ├── requirements.txt # Python packages needed
│   ├── uploads/         # Where uploaded PDFs are stored
│   └── chroma_db/       # Vector database (stores PDF memories)
│
├── frontend/            # The "face" of the app (what you see)
│   ├── index.html       # Main chat page
│   ├── login.html       # Login page
│   ├── signup.html      # Sign up page
│   ├── auth.js          # Login logic
│   ├── script.js        # Chat logic
│   └── styles.css       # Look and feel
│
└── evaluation/          # Testing & quality checks
    ├── run_rag_eval.py  # Tests if the AI answers correctly
    └── tests.csv        # Test questions and expected answers
```

### Key Folders Explained:

- **backend/**: This is a Python server. When you click "Send" on the chat, it goes here
- **frontend/**: This is HTML/CSS/JavaScript. What you see in your browser
- **chroma_db/**: A special database that remembers PDF content using AI vectors
- **uploads/**: Your uploaded PDFs live here

---

## 🛠️ Technology Stack (What Powers It?)

### Backend
- **FastAPI**: A Python web framework (handles requests from your browser)
- **SQLAlchemy**: A database tool (stores users, chats, messages)
- **LangChain**: An AI framework (helps the AI understand PDFs)
- **Groq API**: The AI engine that answers questions
- **Chroma**: A vector database (remembers PDF content in a special way)

### Frontend
- **HTML/CSS/JavaScript**: Standard web technologies (what your browser understands)

### Database
- **MySQL**: Stores users, conversations, and chat history
- **SQLite** (Chroma): Stores AI "memories" of your PDFs

---

## 🚀 Getting Started (For Beginners)

### Prerequisites
You need to have these installed:
- **Python 3.9+** ([Download here](https://www.python.org/downloads/))
- **Node.js** (Optional, if you want to run the frontend as a server)
- **MySQL** or another database (for production)

### Step 1: Set Up the Backend

1. Open a terminal and go to the backend folder:
   ```bash
   cd backend
   ```

2. Create a Python virtual environment (keeps packages isolated):
   ```bash
   python -m venv venv
   ```

3. Activate it:
   - **Windows**: `venv\Scripts\activate`
   - **Mac/Linux**: `source venv/bin/activate`

4. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a `.env` file with your API keys:
   ```
   GROQ_API_KEY=your_api_key_here
   DATABASE_URL=mysql://username:password@localhost/dbname
   ```

6. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
   You should see: `Uvicorn running on http://127.0.0.1:8000`

### Step 2: Set Up the Frontend

1. Go to the frontend folder:
   ```bash
   cd frontend
   ```

2. Open `index.html` in your browser, or use a simple server:
   ```bash
   python -m http.server 8080
   ```
   Then visit: `http://localhost:8080`

3. Sign up for an account and start uploading PDFs!

---

## 💻 How It Works (High-Level)

### The Flow:

1. **You upload a PDF**
   ```
   Browser → FastAPI Server → PDF saved to disk
   ```

2. **Server reads the PDF**
   ```
   FastAPI → LangChain → Splits PDF into chunks
   ```

3. **AI learns the content**
   ```
   Chunks → Groq AI → Converts to "vectors" (AI numbers)
   Vectors → Chroma DB → Stored for fast lookup
   ```

4. **You ask a question**
   ```
   Browser → FastAPI → LangChain → Groq AI
   ```

5. **AI finds relevant parts**
   ```
   Your question → Convert to vector → Find similar vectors in Chroma
   → Retrieve matching PDF chunks
   ```

6. **AI generates an answer**
   ```
   LangChain → Groq → Uses relevant chunks + your question
   → Streams answer back to your browser
   ```

---

## 📚 Important Files Explained

### `backend/main.py`
This is the entry point. It:
- Sets up the web server (FastAPI)
- Handles file uploads (`/upload` endpoint)
- Handles chat messages (`/chat` endpoint)
- Manages user authentication

### `backend/rag.py`
This handles the RAG (Retrieval-Augmented Generation) logic:
- Reads PDFs
- Splits them into chunks
- Sends chunks to Groq AI
- Stores in Chroma vector database
- Retrieves relevant chunks when you ask a question

### `backend/models.py`
Defines the data structures:
- `User`: Login info
- `Conversation`: A chat session
- `Message`: Individual messages in a chat
- `UserPDF`: Which PDFs belong to which user

### `backend/db.py`
Handles database connections and setup

### `frontend/script.js`
The brain of the front-end:
- Handles chat messages
- Uploads PDFs
- Creates new conversations
- Displays messages in real-time

---

## 🔄 Typical User Journey

1. **User visits the website**
   - Sees login page (`login.html`)

2. **User signs up**
   - Creates username & password
   - Account stored in database

3. **User logs in**
   - Sees main chat interface (`index.html`)
   - Left sidebar shows chat history
   - Right side is the chat area

4. **User uploads a PDF**
   - Clicks "📄 PDFs"
   - Selects a PDF file
   - Backend processes it in `rag.py`
   - PDF content stored in Chroma

5. **User asks a question**
   - Types in chat box
   - Backend finds relevant PDF chunks
   - Groq AI generates answer
   - Answer streams to browser

6. **Chat is saved**
   - Both question and answer stored in MySQL database
   - User can resume later

---

## 🐛 Troubleshooting

### Backend won't start
- Check if Python is installed: `python --version`
- Check if packages installed: `pip list`
- Look for error messages about missing dependencies

### Frontend won't connect to backend
- Make sure backend is running on `http://localhost:8000`
- Check browser console for errors (F12 → Console tab)
- CORS (cross-origin) is configured, so it should work

### PDF upload fails
- Check file size (very large PDFs may timeout)
- Ensure file is a valid PDF
- Check `backend/uploads/` folder has write permissions

### AI gives wrong answers
- Make sure your question is answerable from the PDF
- AI can only answer from PDF content (it doesn't use general knowledge)
- Try uploading the PDF again

---

## 📖 Key Concepts for Beginners

### **RAG (Retrieval-Augmented Generation)**
Instead of the AI using its general knowledge, it:
1. Retrieves (finds) relevant information from your PDF
2. Uses that as context
3. Generates (creates) an answer based on the context

**Why?** More accurate answers about YOUR specific documents!

### **Vectors**
AI doesn't understand text like humans. It converts text to "vectors" (lists of numbers).
- Similar meanings = similar numbers
- The Chroma database stores these numbers for fast lookup

### **Chunking**
PDFs are split into small pieces (chunks) so:
- The AI doesn't get overwhelmed
- Relevant chunks can be found quickly
- Context is maintained

### **Streaming**
Instead of waiting for the entire answer:
- Words appear one-by-one as they're generated
- Feels more responsive
- Better user experience

---

## 🔐 Security Notes

This is a learning project. For production use:
- ✅ User authentication is implemented
- ✅ PDFs are private to each user
- ⚠️ You should add HTTPS
- ⚠️ You should use a strong database password
- ⚠️ You should validate file uploads better
- ⚠️ You should add rate limiting (prevent spam)

---

## 🎓 Learning Resources

If you want to understand the code better:

1. **FastAPI**: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
2. **LangChain**: [https://python.langchain.com/](https://python.langchain.com/)
3. **Chroma DB**: [https://docs.trychroma.com/](https://docs.trychroma.com/)
4. **SQLAlchemy**: [https://docs.sqlalchemy.org/](https://docs.sqlalchemy.org/)

---

## 📝 Next Steps

If you want to improve this project:

1. **Add React Frontend**: Replace HTML/JS with a React app
2. **Better UI**: Improve the design with Tailwind CSS
3. **Rate Limiting**: Prevent users from spamming requests
4. **Admin Dashboard**: Monitor system health and usage
5. **More PDF Features**: Search, delete, organize PDFs
6. **Better Error Handling**: User-friendly error messages

---

## ❓ FAQ

**Q: Can the AI access the internet?**
A: No, it only reads PDFs you upload. It can't search the web.

**Q: Is my data private?**
A: Yes, each user only sees their own PDFs and chats.

**Q: Can I upload any file?**
A: Currently only PDFs, but you could extend it for Word docs, images, etc.

**Q: How much does it cost?**
A: Free if using Groq's free tier. Costs depend on API usage.

**Q: Can multiple users use this at once?**
A: Yes! The database and authentication support multiple users.

---

## 📞 Need Help?

- Check the error messages in the terminal
- Look at the browser console (F12)
- Review the code comments
- Check the documentation links above

---

**Happy learning! 🚀**

This is a great project to understand:
- Full-stack web development
- AI/ML integration
- Database design
- User authentication
- Real-time communication

Good luck! 💪
