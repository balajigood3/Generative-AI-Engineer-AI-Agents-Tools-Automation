"""OpenAI chat agent with RAG context and function tools."""
import json
import os
from openai import OpenAI
from app.tools import safe_calculate

SYSTEM_PROMPT = """You are Career & Research Copilot, a precise and helpful AI assistant.
Help with learning, career preparation, coding, document understanding and research.
Use retrieved document excerpts when relevant. Cite their source filenames in answers.
If the documents do not contain the answer, say so rather than inventing citations.
Be transparent about uncertainty. Do not claim to have browsed the live internet.
Use the calculator tool for arithmetic instead of mental calculation."""

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Evaluate a basic arithmetic expression.",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    }
]


def run_agent(client: OpenAI, messages: list[dict], retrieved: list[dict], model: str) -> str:
    context = "\n\n".join(
        f"[Source: {item['source']} | relevance: {item['score']:.3f}]\n{item['text']}"
        for item in retrieved
    ) or "No uploaded-document context was retrieved."
    working = [{"role": "system", "content": SYSTEM_PROMPT + "\n\nRetrieved context:\n" + context}]
    working.extend(messages[-12:])

    for _ in range(4):
        response = client.chat.completions.create(
            model=model, messages=working, tools=TOOL_SCHEMA, tool_choice="auto", temperature=0.2
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return message.content or "I could not generate a response."
        working.append(message)
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            if call.function.name == "calculator":
                result = safe_calculate(args["expression"])
            else:
                result = "Unknown tool."
            working.append({
                "role": "tool", "tool_call_id": call.id, "content": str(result)
            })
    return "I reached the tool-call limit. Please simplify the request."
