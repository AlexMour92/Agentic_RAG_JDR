import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from app.core.config import settings
from app.core.database import entities_collection
from app.tools.rag_tools import ALL_TOOLS
from prompts import AGENT_SYSTEM_PROMPT, SPELLCHECK_PROMPT

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL,
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)

agent = create_react_agent(model=llm, tools=ALL_TOOLS, prompt=AGENT_SYSTEM_PROMPT)

# --- Spellcheck Logic ---
_all_names = sorted(entities_collection.get()["ids"])
_spellcheck_system = SPELLCHECK_PROMPT.format(entity_names=", ".join(_all_names))

def _extract_text(content) -> str:
    if isinstance(content, list):
        return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    return str(content)

async def spellcheck_question(question: str) -> str:
    try:
        response = await asyncio.to_thread(
            llm.invoke,
            [{"role": "system", "content": _spellcheck_system}, {"role": "user", "content": question}]
        )
        corrected = _extract_text(response.content).strip()
        return corrected if corrected and len(corrected) <= len(question) * 2 else question
    except Exception:
        return question