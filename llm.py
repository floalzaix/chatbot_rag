#
#   Imports
#

import ollama
import streamlit as st

from typing import List

# Perso

from rag import *
from web import *
from wikipedia import *
from sessions import *

#
#   Ollama metadata
#

def get_list_model() -> List[str]:
    l = [model.model for model in ollama.list().models]
    if "nomic-embed-text:latest" in l:
        l.remove("nomic-embed-text:latest")
    return l

#
#   LLM interactions
#

def query(user_input: str):
    """
        Query the llm with the user input.

        It stores the user input in the session state
        and streams the response from the llm.
    """

    # Stream response
    payload = [
        {"role": "system", "content": st.session_state["prompt"]},
        *st.session_state["messages"],
    ]

    context = False

    # Web search
    web_search = get_web_search()
    if "WEB" in st.session_state["sources"] and web_search:
        urls = get_urls(web_search)
        st.caption(f"Urls found: {urls}")
        content = web_query(urls)

        # Summarizing the content
        for i, c in enumerate(content):
            if c:
                st.caption(f"Summarizing page {urls[i]}")
                content[i] = summarize_content(c, user_input)

        # Removing the None values
        content = [c for c in content if c]

        st.caption(f"Content: {content}")

        if content:
            payload.append(
                {
                    "role": "system",
                    "content": "Voici le contenu des pages web trouvées "
                    "d'aprés la recherche utilisateur:\n" + 
                    "\n".join(content)
                }
            )

    # RAG context
    selected_corpus = get_selected_corpus()
    if "RAG" in st.session_state["sources"] and selected_corpus:
        context = True
        payload.append(
            {
                "role": "system",
                "content": query_rag(selected_corpus, user_input) or 
                "No RAG context found."
            }
        )

    # Wikipedia context
    wiki_key_words = get_wiki_key_words()
    if "Wikipedia" in st.session_state["sources"] and wiki_key_words:
        context = True
        payload.append(
            {
                "role": "system",
                "content": wikipedia_query(wiki_key_words, user_input) or 
                "No Wikipedia context found."
            }
        )

    # Instructions for the context
    if context:
        payload.append(
            {
                "role": "system",
                "content": "Sers-toi du contexte du rag et "
                "de la wikipedia pour répondre à ma demande."
            }
        )
    
    # Adding the user message to the payload
    payload.append(
        {"role": "user", "content": user_input}
    )

    stream = ollama.chat(
        model=st.session_state["model"],
        messages=payload,
        stream=True,
        think=get_think_mode(),
        options={
            "num_ctx": get_num_ctx(),
        },
    )

    # Adding user message to history
    st.session_state["messages"].append(
        {"role": "user", "content": user_input}
    )

    return stream