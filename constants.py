SOURCES = [
    "RAG",
    "WEB",
    "Wikipedia",
]

BASE_DIR = "corpus"

K_RAG = 4

HTTP_HEADERS = {
    "User-Agent": "search-api/1.0(floalzaix@gmail.com)",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

NUM_WEB_RESULTS_MAX = 4

NUM_CHARS_PER_WEB_PAGE_MAX = 5000

SUMMARIZE_PROMPT = f"""
    Tu est un professionel des résumé. Quand je te donne,
    du contenu, identifié les données clefs et résume le tout
    en moins de {NUM_CHARS_PER_WEB_PAGE_MAX / 5} caractères.
    Il ne faut pas que tu répètes les mêmes informations.
    Il ne faut pas que tu oublies des informations importantes.
    N'inclut pas de formules de politesse et de cadre autour va
    à l'essentiel. Tu n'est pas en train de répondre à quelqu'un
    juste du génère un résumé.
"""

SESSION_DIR = "sessions"