# Chatbot RAG

Interface Streamlit de chatbot local branché sur Ollama, avec enrichissement
contextuel via corpus local (RAG), recherche web et Wikipedia.

## Objectif

Permettre de converser avec un modèle LLM local tout en injectant du contexte
externe selon les sources activées dans la barre latérale :

- **RAG** : recherche sémantique dans un corpus de documents texte indexés
  (ChromaDB + embeddings Ollama).
- **Wikipedia** : récupération d'une page Wikipédia (fr), création automatique
  d'un corpus temporaire, puis interrogation RAG.
- **WEB** : recherche DuckDuckGo, scraping des pages, résumé du contenu par le
  LLM avant injection dans le prompt.

Les sessions (historique, paramètres, corpus sélectionné) peuvent être
enregistrées et rechargées depuis l'interface.

## Prérequis

- Python 3.11+
- [Ollama](https://ollama.com/) installé et démarré localement
- Les modèles suivants doivent être disponibles dans Ollama :
  - un modèle de chat (ex. `qwen3.5:2b`, utilisé par défaut)
  - `nomic-embed-text` (embeddings pour le RAG)

```bash
ollama pull qwen3.5:2b
ollama pull nomic-embed-text
```

## Installation

Depuis la racine du projet :

```bash
pip install -r requirements.txt
```

Les dossiers `corpus/` et `sessions/` sont créés au besoin ; ils ne sont pas
versionnés.

## Lancement

```bash
streamlit run app.py
```

L'application s'ouvre par défaut sur `http://localhost:8501`.

## Fonctionnement

### Pipeline d'une requête

1. L'utilisateur envoie un message dans le chat.
2. Selon les sources cochées dans la barre latérale, du contexte est ajouté au
   payload Ollama sous forme de messages `system` :
   - **RAG** : les `K_RAG` chunks les plus proches de la question sont
     récupérés dans ChromaDB.
   - **Wikipedia** : la première page trouvée est découpée en sections, indexée
     dans un corpus `Wikipedia_<mots_clés>`, puis interrogée comme un RAG
     classique.
   - **WEB** : DuckDuckGo retourne jusqu'à 4 URLs ; chaque page est scrapée
     (BeautifulSoup), nettoyée, tronquée, puis résumée par le LLM avant d'être
     injectée.
3. Le modèle Ollama sélectionné génère la réponse en streaming.
4. L'échange est ajouté à l'historique de la session courante.

### Gestion des corpus (RAG)

- Créer un corpus via **Nouveau** dans la barre latérale.
- Ajouter des fichiers `.txt` (ou `.pdf` via l'upload) via **Modifier**.
- Les documents sont découpés (`chunk_size=1000`, `overlap=200`) puis indexés
  dans `corpus/<nom>/chroma_db/`.
- Sélectionner le corpus actif dans la liste déroulante et cocher la source
  **RAG**.

### Sessions

Depuis la barre latérale :

- **Nouvelle** : réinitialise l'état (modèle, prompt, historique, etc.).
- **Charger** / **Enregistrer** : lit ou écrit un fichier JSON dans
  `sessions/`.
- **Supprimer** : supprime la session sélectionnée.

### Paramètres disponibles

| Paramètre              | Description                                      |
|------------------------|--------------------------------------------------|
| Modèle Ollama          | Modèle de chat (liste des modèles locaux)        |
| Prompt système         | Instructions de base du LLM                      |
| Sources                | RAG, WEB, Wikipedia (combinables)                |
| Mode de réflexion      | Active le mode `think` d'Ollama                  |
| Contexte (tokens)      | Taille du contexte (`num_ctx`, 1024 à 16384)     |

## Arborescence

```text
.
├── app.py           # Interface Streamlit (chat + barre latérale)
├── llm.py           # Orchestration des sources et appel Ollama
├── rag.py           # Indexation et recherche ChromaDB
├── corpus.py        # CRUD des corpus et documents
├── web.py           # Recherche DuckDuckGo et scraping
├── wikipedia.py     # Récupération et indexation Wikipedia
├── sessions.py      # État Streamlit et persistance des sessions
├── dialogs.py       # Popups (corpus, sessions)
├── constants.py     # Sources, chemins, limites web/RAG
├── requirements.txt
├── corpus/          # Documents et bases Chroma (non versionné)
└── sessions/        # Fichiers JSON de session (non versionné)
```

## Dépendances principales

- **Ollama** : inférence LLM et embeddings locaux
- **LangChain + ChromaDB** : découpage, indexation et recherche vectorielle
- **Streamlit** : interface utilisateur
- **ddgs** : recherche web DuckDuckGo
- **BeautifulSoup + httpx** : extraction du texte des pages web
- **wikipedia-api** : accès aux pages Wikipédia (fr)

## Conseils

- Vérifier qu'Ollama tourne (`ollama list`) avant de lancer Streamlit.
- Sans `nomic-embed-text`, le RAG ne peut pas indexer ni interroger les corpus.
- Pour la recherche web, renseigner les mots-clés dans le champ **Recherche
  Web** ; pour Wikipedia, le champ **Wikipedia** (ex. `Chatbot`, `IA`).
- Les fichiers uploadés doivent être lisibles en texte brut pour un indexage
  correct.
