import time
import asyncio
from fastapi import APIRouter, HTTPException
from app.schemas import QuestionRequest, AnswerResponse, ToolStep
from app.services.agent import agent, spellcheck_question, _extract_text

router = APIRouter()

# Limite à 2 requêtes simultanées pour protéger les ressources
AGENT_SEMAPHORE = asyncio.Semaphore(2)

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(req: QuestionRequest):
    """Point d'entrée principal : pose une question à l'Archiviste."""
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="La question ne peut pas être vide.")

    start_time = time.time()

    # 1. Correction orthographique des noms d'entités JDR
    corrected = await spellcheck_question(question)
    was_corrected = corrected != question

    # 2. Appel de l'agent avec gestion du sémaphore
    async with AGENT_SEMAPHORE:
        try:
            # On utilise asyncio.to_thread car agent.invoke est bloquant (synchrone)
            result = await asyncio.to_thread(
                agent.invoke,
                {"messages": [{"role": "user", "content": corrected}]},
                {"recursion_limit": 15},
            )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"L'Archiviste a rencontré une erreur : {str(e)}"
            )

    elapsed = time.time() - start_time
    messages = result["messages"]

    # 3. Extraction des étapes (outils appelés par l'agent)
    steps: list[ToolStep] = []
    pending_calls: dict[str, dict] = {}

    for msg in messages:
        # Si le message contient des appels d'outils (AI -> Tool)
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                pending_calls[tc["id"]] = {
                    "tool_name": tc["name"],
                    "arguments": tc["args"],
                }
        
        # Si le message est le résultat d'un outil (Tool -> AI)
        if hasattr(msg, "type") and msg.type == "tool":
            tool_call_id = getattr(msg, "tool_call_id", None)
            if tool_call_id and tool_call_id in pending_calls:
                info = pending_calls.pop(tool_call_id)
                text = _extract_text(msg.content)
                
                # Création d'une prévisualisation du résultat
                preview = text[:300] + ("..." if len(text) > 300 else "")
                
                steps.append(
                    ToolStep(
                        tool_name=info["tool_name"],
                        arguments=info["arguments"],
                        result_preview=preview,
                    )
                )

    # 4. Récupération de la réponse finale
    final_answer = _extract_text(messages[-1].content)

    return AnswerResponse(
        answer=final_answer,
        steps=steps,
        elapsed=round(elapsed, 1),
        original_question=question if was_corrected else None,
        corrected_question=corrected if was_corrected else None,
    )


@router.get("/health")
async def health():
    """Vérifie l'état de la base de données et de l'API."""
    from app.core.database import events_collection, entities_collection
    try:
        return {
            "status": "online",
            "stats": {
                "events_count": events_collection.count(),
                "entities_count": entities_collection.count(),
            }
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}