#
#   Imports
#

import os
import json
import streamlit as st

from typing import List

# Perso

from constants import BASE_DIR, SESSION_DIR

#
#   Session handler
#

def session_init():
    """
        Initialize the session state.

        Variables:
            - messages: The history of the discussion
            with the llm.
            - model: The model to use for the llm.
            - prompt: The base prompt given to the llm.
            - sources: The sources used to generate the response.
            - corpus_list: The list of corpora available.
            - documents: The documents available in the corpora.
            - selected_corpus: The corpus selected by the user.
            - wiki_key_words: The keywords used to search for wikipedia articles.
            - web_search: The search query used to search for web pages.
            - web_contents: The contents of the web pages found.
    """
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "model" not in st.session_state:
        st.session_state["model"] = "qwen3.5:2b"

    if "prompt" not in st.session_state:
        st.session_state["prompt"] = "You are a helpful assistant."

    if "corpus_list" not in st.session_state:
        st.session_state["corpus_list"] = []

    if "documents" not in st.session_state:
        st.session_state["documents"] = {}

    if "sources" not in st.session_state:
        st.session_state["sources"] = []
    
    if "selected_corpus" not in st.session_state:
        st.session_state["selected_corpus"] = None

    if "wiki_key_words" not in st.session_state:
        st.session_state["wiki_key_words"] = None

    if "web_search" not in st.session_state:
        st.session_state["web_search"] = None

    if "think_mode" not in st.session_state:
        st.session_state["think_mode"] = False

    if "num_ctx" not in st.session_state:
        st.session_state["num_ctx"] = 8192

def get_previous_messages():
    return st.session_state.get("messages", [])

def get_prompt():
    return st.session_state.get("prompt", "You are a helpful assistant.")

def get_model():
    return st.session_state.get("model", "qwen3.5:2b")

def change_prompt(prompt: str):
    st.session_state["prompt"] = prompt

def change_model(model: str):
    st.session_state["model"] = model

def add_message(role: str, content: str):
    st.session_state["messages"].append(
        {"role": role, "content": content}
    )

def get_corpus_list() -> List[str]:
    return ["Aucun"] + st.session_state.get("corpus_list", [])

def add_corpus(name: str):
    # Validation of the corpus name
    if not name:
        raise ValueError("Le nom du corpus est requis !")

    os.makedirs(os.path.join(BASE_DIR, name), exist_ok=True)

    if name not in st.session_state["corpus_list"]:
        st.session_state["corpus_list"].append(name)

def get_sources():
    return st.session_state.get("sources", [])

def change_sources(sources: list[str]):
    st.session_state["sources"] = sources

def get_selected_corpus():
    return st.session_state.get("selected_corpus", None)

def change_selected_corpus(corpus: str | None):
    st.session_state["selected_corpus"] = corpus

def reset_conversation():
    st.session_state["messages"] = []

def get_wiki_key_words():
    return st.session_state.get("wiki_key_words", None)

def change_wiki_key_words(key_words: str | None):
    st.session_state["wiki_key_words"] = key_words

def get_web_search():
    return st.session_state.get("web_search", None)

def change_web_search(web_search: str | None):
    st.session_state["web_search"] = web_search

def get_think_mode():
    return st.session_state.get("think_mode", False)

def change_think_mode(think_mode: bool):
    st.session_state["think_mode"] = think_mode

def get_num_ctx():
    return st.session_state.get("num_ctx", 8192)

def change_num_ctx(num_ctx: int):
    st.session_state["num_ctx"] = num_ctx

#
#   Conversation history management (session)
#

def reset_session():
    """
        Clears all the session state and reinitializes it
        with the default values.
    """
    st.session_state.clear()
    session_init()

def new_session():
    """
        Creates a new session by resetting the session state and
        reinitializing it with the default values.
    """
    reset_session()

def save_session(session_name: str):
    """
        Saves the current session state to a file.
        It first validates the session name. Because the way the file
        is thought to be loaded by the get all sessions function.
    """
    if not session_name:
        st.error("Le nom de la session est requis !")
        return

    if session_name.count(".") >= 2:
        st.error("Le nom de la session ne peut pas contenir plus de deux points !")
        return
    
    with open(os.path.join(SESSION_DIR, session_name + ".json"), "w") as f:
        json.dump(st.session_state.to_dict(), f)

def get_all_sessions():
    """
        Lists the existing sessions by listing the files in the
        session directory and returning the names of the files
        without the .json extension.
    """
    return [
        f.split(".")[0]
        for f in os.listdir(SESSION_DIR) if f.endswith(".json")
    ]

def load_session(session_name: str):
    with open(os.path.join(SESSION_DIR, session_name + ".json"), "r") as f:
        st.session_state.update(json.load(f))

def delete_session(session_name: str):
    """
        Deletes a session by deleting the file in the
        session directory. Then resets the session state.
    """
    if os.path.exists(os.path.join(SESSION_DIR, session_name + ".json")):
        os.remove(os.path.join(SESSION_DIR, session_name + ".json"))
        reset_session()
    else:
        st.error("La session n'existe pas !")