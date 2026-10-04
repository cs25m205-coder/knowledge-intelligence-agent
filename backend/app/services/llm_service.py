import json
import urllib.request


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"


def generate_answer(question: str, evidence: list[dict]) -> str:
    evidence_text = "\n\n".join(
        [
            (
                f"[Source: {item['filename']}, "
                f"Page: {item['page_number']}]\n"
                f"{item['text']}"
            )
            for item in evidence
        ]
    )

    prompt = f"""
You are a knowledge-based decision intelligence assistant.

Answer the user's question using ONLY the evidence provided below.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. If the evidence is insufficient, clearly say that the knowledge base
   does not contain enough information.
4. Explain your reasoning clearly.
5. Cite the relevant source and page number in the answer.
6. Distinguish evidence from your analysis.

User question:
{question}

Available evidence:
{evidence_text}

Provide a concise, useful answer.
"""

    payload = {
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False,
        "keep_alive": "10m",
        "options": {
            "temperature": 0,
            "num_predict": 256
        }
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["response"]