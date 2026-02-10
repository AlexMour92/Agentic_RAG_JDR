# Agentic RAG pour campagnes de JdR longue durée 
Pipeline d'ingestion, indexation et agent orchestration pour interroger l'histoire d'une campagne de jeu de rôle (sessions, personnages, événements) à l'aide d'un système RAG (Retrieval-Augmented Generation) agentique.

![Demo_RAG](https://github.com/user-attachments/assets/1c36422a-58a6-4859-8491-0359c0e199f9)

## Objectifs

Ce projet vise à fournir une base technique pour capturer, structurer, valider et interroger des transcripts/notes de parties de jeu de rôle sur table (TTRPG) afin de garder une mémoire cohérente d'une campagne longue durée et d'offrir un narrateur/assistant "persona" capable de répondre naturellement aux joueurs.

Le système combine :

* L'Extraction d'informations depuis du texte brut (résumés de sessions),

* Validation / réparation JSON via LLM (human-in-the-loop possible),

* Stockage sémantique (ChromaDB) et recherche vectorielle,

* Boucle de raisonnement agentique (ReAct / LangGraph) pour orchestrer outils et réponses.

## Ingestion

### Fonctionnalités

* Ingestion automatique de textes de session (chunking intelligent + métadonnées).

* Extracteur LLM transformant le texte brut en schéma JSON structuré (entités, événements, timeline, relations).

* Validation et réparation automatique du JSON via LLM (pipeline entièrement automatisable).

* Indexation des chunks et des métadonnées dans ChromaDB pour recherche sémantique.

* Option : contrôle manuel avant indexation (HITL) disponible si souhaité — non requis pour l'exécution normale du pipeline.

### Architecture & diagramme

Commentaire : Le pipeline d'ingestion prend en entrée le texte brut d'une session, applique un extracteur LLM qui produit un JSON structuré puis valide/répare automatiquement ce JSON si besoin. Les chunks et métadonnées sont ensuite indexés dans ChromaDB. Le système est conçu pour fonctionner de façon entièrement automatisée — idéal même si l'on n'ingère que quelques fichiers par mois.

![Agentic Ingestion for TTRPG](https://github.com/user-attachments/assets/4c5c3772-79fd-4662-88fa-6c7dfdfdccb1)

## Agentic RAG (Retrieval-Augmented Generation)

### Fonctionnalités

* Recherche sémantique sur l'historique de campagne (events / entities).

* Accès direct à des fiches d'entités et timelines (get_entity_card, get_timeline).

* Vue globale synthétique de la campagne (get_campaign_overview).

* Boucle de raisonnement agentique (ReAct / LangGraph) orchestrationnant les appels aux outils et synthétisant la réponse selon une persona (ex. narrateur, conteur mystérieux).

* Pré-traitement des requêtes utilisateur : correction orthographique et reconnaissance d'entités pour améliorer la robustesse.

### Architecture & diagramme

Commentaire : La partie RAG orchestre la recherche et la génération : un agent orchestration (LLM) décide si un outil est nécessaire (recherche sémantique, accès direct à une fiche, ou vue globale) puis combine les observations renvoyées par ChromaDB pour produire une réponse cohérente et persona-driven.

![Agentic RAG for TTRPG](https://github.com/user-attachments/assets/bdd64311-e043-401e-bbf8-c31abab766a5)

## Stack technique

**Langage :** Python 3.10+

**API backend :** FastAPI

**Serveur ASGI :** uvicorn (déploiement et exécution locale)

**LLM :** Gemini 2.5 Flash Preview (génération, extraction structurée, réparation JSON, raisonnement agentique)

**Framework RAG :** LangChain (intégration LLM, prompts, outils, chaînes)

**Orchestration agentique :** LangGraph (boucle ReAct, décision d’outils, gestion des états)

**Vector Store :** ChromaDB (embeddings, recherche sémantique, métadonnées)

**Prompt Engineering :** prompts spécialisés (extraction, validation/réparation JSON, synthèse persona)

**Data / NLP :** chunking de texte, extraction d’entités, structuration JSON

**Prototypage & debug :** Jupyter Notebooks
