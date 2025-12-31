# Personal AI Assistant

A private, personal AI assistant that knows only the owner, interacts naturally via text and voice, and responds in a streaming, conversational manner. Built with a modular architecture combining LLMs, RAG, and real-time voice interfaces.

---

## System Architecture


- **Strict Boundary Rule:** Only answers questions related to the owner; politely refuses everything else.  
- **Interruptible:** Ongoing speech or streaming responses can be interrupted by new user input.  
- **Modular:** Each component — STT, RAG, LLM, TTS — is replaceable.

---

## Tech Stack

- **Frontend:** React.js, CSS Modules  
- **Backend:** Flask (Python)  
- **Voice:** Web Speech API (SpeechRecognition + SpeechSynthesis)  
- **RAG / Vector Store:** FAISS + Sentence-Transformers  
- **LLM:** OpenAI GPT-4o-mini (or compatible)  
- **Tools:** Server-side (notes search, profile fetch), Client-side (clear conversation, push-to-talk control)  

---

## Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Linux / Mac
venv\Scripts\activate      # Windows
```

```bash
pip install -r requirements.txt
```

```bash
python rag/ingest.py
```

```bash
python app.py
```
### Frontend

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```
---
## Design Decisions & Trade-Offs

- Frontend TTS vs Backend TTS:
- Chose browser SpeechSynthesis for simplicity and low latency, trading off control over voice quality. Chunked streaming ensures reliability during long responses.

- RAG over Full LLM Prompting:
- Using FAISS + embeddings ensures assistant strictly answers owner-related questions and avoids hallucination, at the cost of maintaining a separate vector store.

- Progressive Streaming:
- Implemented progressive token display and TTS for a conversational feel. Slightly more complex than sending a single response, but greatly improves user experience.

- Modular Architecture:
- Each stage (STT → RAG → LLM → TTS) is replaceable, enabling future upgrades like switching LLMs or TTS engines without full rewrites.

- Voice Input Modes:
- Supports both automatic VAD and push-to-talk to demonstrate concurrency and real-time interaction handling.

---

## Future Improvements

- Backend TTS integration for better voice quality and multilingual support.
- WebSocket streaming for smoother real-time token delivery.
- Multi-user support with separate owner contexts.
- Persistent conversation memory across sessions.
