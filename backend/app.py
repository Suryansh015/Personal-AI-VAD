from flask import Flask, request, Response
from flask_cors import CORS
import time
import json

from config import generate_llm
from rag.retrieve import retrieve
from tool_registry import TOOLS   # make sure this exists

app = Flask(__name__)
CORS(app)

# -----------------------
# Utils
# -----------------------
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

    context_chunks = retrieve(user_input)

    if not context_chunks:
        def refuse():
            msg = (
                "I can help with things about you, your work, your notes, "
                "or your goals — but I can’t answer general questions."
            )
            for w in msg.split():
                yield f"data: {w}\n\n"
                time.sleep(0.05)

        return Response(refuse(), mimetype="text/event-stream")

    context = "\n".join(context_chunks)

    system_prompt = """
You are a private personal AI assistant.

You ONLY answer using the owner’s data.

If a tool is required, respond ONLY with valid JSON:
{
  "tool": "<tool_name>",
  "args": { ... }
}

Otherwise respond normally in plain text in 3-4 lines max.
"""

    user_prompt = f"""
Context:
{context}

User question:
{user_input}
"""

    llm_response = generate_llm(system_prompt, user_prompt)
    raw_output = llm_response["choices"][0]["message"]["content"]

    clean_output = extract_json(raw_output)

    # =========================
    # TOOL HANDLING
    # =========================
    try:
        parsed = json.loads(clean_output)
    except:
        parsed = None

    if parsed and "tool" in parsed:
        tool_name = parsed["tool"]
        args = parsed.get("args", {})

        if tool_name not in TOOLS:
            final_text = "Sorry, I can’t do that."
        else:
            tool_result = TOOLS[tool_name]["fn"](**args)

            followup_system = "Explain the result clearly and naturally."
            followup_user = f"Tool result:\n{tool_result}"

            final_response = generate_llm(followup_system, followup_user)
            final_text = final_response["choices"][0]["message"]["content"]

    else:
        final_text = raw_output

    # =========================
    # STREAM FINAL OUTPUT
    # =========================
    def stream():
        for word in final_text.split():
            yield f"data: {word}\n\n"
            time.sleep(0.04)

    return Response(stream(), mimetype="text/event-stream")



if __name__ == "__main__":
    app.run(debug=True, threaded=True)
