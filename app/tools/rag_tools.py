from langchain_core.tools import tool
from app.core.database import events_collection, entities_collection

@tool
def search_events(query: str) -> str:
    """Recherche sémantique dans les événements de la campagne.

    Utilise cette fonction pour trouver des événements en rapport avec un sujet,
    un lieu, un personnage ou une action.
    Pour filtrer par session, utilise plutôt get_session_timeline.

    Args:
        query: Termes de recherche en langage naturel.
    """
    count = events_collection.count()
    if count == 0:
        return "Aucun événement en base."

    results = events_collection.query(
        query_texts=[query],
        n_results=min(8, count),
    )

    if not results["ids"][0]:
        return "Aucun événement trouvé pour cette recherche."

    lines = []
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        lines.append(
            f"[Session {meta['session']}, événement {meta['order']}] "
            f"({meta['event_type']}) "
            f"{doc}\n"
            f"  Entités impliquées : {meta['entities']}\n"
            f"  Pertinence : {1 - dist:.2f}"
        )
    return "\n\n".join(lines)


@tool
def search_entities(query: str) -> str:
    """Recherche sémantique dans les entités de la campagne.

    Utilise cette fonction pour trouver des entités (personnages, lieux, objets,
    factions, quêtes) en rapport avec un sujet donné.
    Pour une entité précise dont tu connais le nom, utilise plutôt get_entity_card.

    Args:
        query: Termes de recherche en langage naturel.
    """
    count = entities_collection.count()
    if count == 0:
        return "Aucune entité en base."

    results = entities_collection.query(
        query_texts=[query],
        n_results=min(5, count),
    )

    if not results["ids"][0]:
        return "Aucune entité trouvée pour cette recherche."

    lines = []
    for eid, doc, meta in zip(
        results["ids"][0], results["documents"][0], results["metadatas"][0]
    ):
        lines.append(
            f"[{eid}] (type: {meta['type']}, statut: {meta['status']}, "
            f"sessions: {meta['first_session']}-{meta['last_session']})\n"
            f"  {doc}"
        )
    return "\n\n".join(lines)


@tool
def get_entity_card(entity_name: str) -> str:
    """Récupère la fiche complète d'une entité par son nom exact.

    Utilise cette fonction quand l'utilisateur demande des informations sur
    une entité nommée spécifique ("Qui est Thalantyr ?", "Parle-moi de Beregost").
    La recherche est insensible à la casse.

    Si le nom exact n'est pas connu, utilise d'abord search_entities pour
    identifier le nom canonique.

    Args:
        entity_name: Nom exact de l'entité recherchée.
    """
    all_entities = entities_collection.get()
    name_lower = entity_name.strip().lower()

    for i, eid in enumerate(all_entities["ids"]):
        if eid.strip().lower() == name_lower:
            meta = all_entities["metadatas"][i]
            doc = all_entities["documents"][i]
            return (
                f"Entité : {eid}\n"
                f"Type : {meta['type']}\n"
                f"Statut : {meta['status']}\n"
                f"Présente de la session {meta['first_session']} "
                f"à la session {meta['last_session']}\n\n"
                f"Fiche :\n{doc}"
            )

    return (
        f"Aucune entité trouvée avec le nom exact '{entity_name}'. "
        f"Essaie search_entities pour une recherche approximative."
    )


@tool
def get_session_timeline(session_number: int) -> str:
    """Récupère tous les événements d'une session dans l'ordre chronologique.

    Utilise cette fonction quand l'utilisateur demande ce qui s'est passé
    durant une session spécifique ("Raconte la session 2", "Que s'est-il
    passé à la session 1 ?").

    Args:
        session_number: Numéro de la session (1, 2, 3, etc.).
    """
    results = events_collection.get(where={"session": session_number})

    if not results["ids"]:
        return f"Aucun événement trouvé pour la session {session_number}."

    indexed = sorted(
        zip(results["documents"], results["metadatas"]),
        key=lambda x: x[1].get("order", 0),
    )

    lines = [f"Session {session_number} — {len(indexed)} événements :"]
    for doc, meta in indexed:
        lines.append(
            f"  {meta['order']}. ({meta['event_type']}) {doc}\n"
            f"     Entités : {meta['entities']}"
        )
    return "\n\n".join(lines)


@tool
def get_entity_events(entity_name: str) -> str:
    """Récupère tous les événements impliquant une entité donnée.

    Utilise cette fonction pour reconstituer l'historique d'un personnage,
    d'un lieu ou d'un objet à travers les sessions ("Qu'a fait Tungdill ?",
    "Que s'est-il passé aux ruines d'Ulcaster ?").

    Args:
        entity_name: Nom de l'entité recherchée.
    """
    all_events = events_collection.get()

    if not all_events["ids"]:
        return "Aucun événement en base."

    name_lower = entity_name.strip().lower()
    matches = []

    for doc, meta in zip(all_events["documents"], all_events["metadatas"]):
        entity_list = [e.strip().lower() for e in meta["entities"].split(",")]
        if name_lower in entity_list:
            matches.append((doc, meta))

    if not matches:
        return (
            f"Aucun événement impliquant '{entity_name}'. "
            f"Vérifie le nom exact avec search_entities."
        )

    matches.sort(key=lambda x: (x[1]["session"], x[1].get("order", 0)))

    lines = [ f"Événements impliquant '{entity_name}' ({len(matches)} résultats) :" ]
    for doc, meta in matches:
        lines.append(
            f"  [S{meta['session']}.{meta['order']}] ({meta['event_type']}) {doc}"
        )
    return "\n\n".join(lines)


@tool
def get_campaign_overview() -> str:
    """Fournit une vue d'ensemble de la campagne : nombre de sessions,
    d'événements, d'entités, ainsi que la liste des entités par type.

    Utilise cette fonction pour les questions générales sur la campagne
    ("Résume la campagne", "Où en est-on ?", "Quels personnages sont en jeu ?").
    """
    n_events = events_collection.count()
    n_entities = entities_collection.count()

    all_events = events_collection.get()
    sessions = set()
    for meta in all_events["metadatas"]:
        sessions.add(meta["session"])

    all_entities = entities_collection.get()
    by_type = {}
    for eid, meta in zip(all_entities["ids"], all_entities["metadatas"]):
        t = meta["type"]
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(f"{eid} ({meta['status']})")

    lines = [
        f"Campagne : {len(sessions)} session(s), "
        f"{n_events} événements, {n_entities} entités.",
        f"Sessions enregistrées : {sorted(sessions)}",
        "",
        "Entités par type :",
    ]

    for t in sorted(by_type.keys()):
        lines.append(f"  {t} : {', '.join(by_type[t])}")

    return "\n".join(lines)

# Liste exportable pour l'initialisation de l'agent
ALL_TOOLS = [
    search_events,
    search_entities,
    get_entity_card,
    get_session_timeline,
    get_entity_events,
    get_campaign_overview,
]