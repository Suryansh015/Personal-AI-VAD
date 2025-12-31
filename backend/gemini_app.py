from flask import Flask, request, Response
from flask_cors import CORS
import time

from config import generate_gemini
from rag.retrieve import retrieve

app = Flask(__name__)
CORS(app)

def extract_json(text: str):
    text = text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    return text

@app.route("/")
def health():
    return {"status": "Backend running"}

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "").strip()

    if not user_input:
        return {"error": "Empty message"}, 400

    # Retrieve owner-only context
    context_chunks = retrieve(user_input)

    # STRICT boundary rule
    if not context_chunks:
        def refuse_stream():
            msg = (
                "I can help with things about you, your work, your notes, "
                "or your goals — but I can’t answer general questions."
            )
            for word in msg.split():
                yield f"data: {word}\n\n"
                time.sleep(0.05)

        return Response(refuse_stream(), mimetype="text/event-stream")

    context = "\n".join(context_chunks)

    prompt = f"""
You are a private personal AI assistant.

You ONLY answer using the owner’s data.

If answering requires searching the owner’s notes,
respond ONLY in valid JSON like this:

{{
  "tool": "search_owner_notes",
  "args": {{ "query": "{user_input}" }}
}}

Otherwise, respond normally in plain text.

Context:
{context}

User question:
{user_input}
"""

    gemini_response = generate_gemini(prompt)
    llm_output = gemini_response["candidates"][0]["content"]["parts"][0]["text"]

    # =========================
    # TOOL CALL HANDLING
    # =========================
    raw_output = llm_output
    clean_output = extract_json(raw_output)

    try:
        parsed = json.loads(clean_output)
    except:
        parsed = None

    # If LLM requested a tool
    if parsed and "tool" in parsed:
        tool_name = parsed["tool"]
        args = parsed.get("args", {})

        if tool_name not in TOOLS:
            return {"error": "Invalid tool"}, 400

        tool_result = TOOLS[tool_name]["fn"](**args)

        followup_prompt = f"""
Tool result:
{tool_result}

Now respond to the user in a friendly, human-like way.
"""

        final_response = generate_gemini(followup_prompt)
        raw_final = final_response["candidates"][0]["content"]["parts"][0]["text"]
        final_text = extract_json(raw_final)

    else:
        final_text = llm_output

    # =========================
    # STREAM FINAL RESPONSE
    # =========================
    def stream():
        for word in final_text.split():
            yield f"data: {word}\n\n"
            time.sleep(0.04)

    return Response(stream(), mimetype="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
