#
#   Imports
#

import streamlit as st

# Perso

from llm import *
from corpus import *
from dialogs import *
from wikipedia import *
from constants import SOURCES
from sessions import *

#
#   Functions
#

def display_messages():
    """
        Display the messages history to the main page.
    """
    st.markdown("""
        <style>
        [data-testid="stChatMessageAvatarUser"] {
            background-color: #1d4ed8 !important;
            color: white !important;
        }

        [data-testid="stChatMessageAvatarAssistant"] {
            background-color: #0f766e !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True
    )

    for message in get_previous_messages():
        with st.chat_message(message["role"]):
            st.write(message["content"])

def main():
    #
    #   Init
    #
    
    st.title("Chatbot")
    session_init()

    #
    #   Chat
    #

    user_input = st.chat_input("Enter your message here ...")

    # Assistant message
    full_response = ""
    if user_input:
        display_messages()

        # Displaying the current user input as it has not yet
        # been added to the history.
        with st.chat_message("user"):
            st.write(user_input)

        # Creating the placeholder
        with st.chat_message("assistant"):
            ph = st.empty()
            ph.write("Thinking ...")

        # Displaying the cancel button
        cancel_ph = st.empty()
        cancel = cancel_ph.button("Cancel", width="stretch")

        stream = query(user_input)

        # Streaming the response
        for chunk in stream:
            if cancel:
                break
            
            content = chunk.message.content
            if content:
                full_response += content
                ph.write(full_response + "| ")

        cancel_ph.empty()
            
        # Displaying the final response
        full_response = full_response.strip("| ")
        ph.write(full_response)

        # Storing the llm response to the history
        add_message("assistant", full_response)
    else:
        # Displaying even without a user input
        # and twice to keep the placeholder to the
        # right position in the conversation.
        display_messages()

    #
    #   Sidebar
    #
    
    with st.sidebar:

        st.markdown("## Gestion des sessions")

        #
        #   Sessions management
        #

        st.markdown(f"### Session : {selected_session or "Nouvelle session"}")
        
        save_success = False
        col1, col2 = st.columns(2)
        with col1:
            st.button("Nouvelle", width="stretch", on_click=popup_nouvelle_session)
            st.button("Charger", width="stretch", on_click=popup_charger_session)
        with col2:
            if st.button("Enregistrer", width="stretch"):
                save_session(selected_session)
                save_success = True
            st.button("Supprimer", width="stretch", on_click=popup_supprimer_session)

        
        if save_success:
            st.success("Session enregistrée avec succès !")

        
        st.markdown("---\n## Paramètres")

        #
        #   Model selection
        #
        
        selected_model = st.selectbox(
            "Choisissez un modèle Ollama : ",
            get_list_model(),
            key="model",
        )

        if selected_model != get_model():
            change_model(selected_model)

        #
        #   Prompt selection
        #

        prompt = st.text_area(
            "Entrez votre prompt : ",
            key="prompt",
        )

        if prompt != get_prompt():
            change_prompt(prompt)

        #
        #   Sources selection
        #

        selected_sources = st.multiselect(
            "Choisissez les sources : ",
            SOURCES,
            key="sources",
        )

        if selected_sources != get_sources():
            change_sources(selected_sources)

        #
        #   Corpus selection
        #
        
        if "RAG" in selected_sources:
            selected_corpus = st.selectbox(
                "Corpus local (RAG):",
                get_corpus_list(),
                key="selected_corpus",
            )

            if selected_corpus != get_selected_corpus():
                if selected_corpus == "Aucun":
                    change_selected_corpus(None)
                else:
                    change_selected_corpus(selected_corpus)

            # Corpus' buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button(
                    "Nouveau",
                    width="stretch",
                    on_click=popup_ajout_corpus,
                )
            with col2:
                st.button(
                    "Modifier",
                    width="stretch",
                    on_click=popup_modifier_corpus,
                    args=(selected_corpus,),
                    disabled=selected_corpus == "Aucun",
                )
        
        #
        #   Wikipedia search
        #
        
        if "Wikipedia" in selected_sources:
            key_words = st.text_input(
                "Wikipedia",
                placeholder="Exemple: Chatbot, IA, etc.",
                key="wiki_key_words",
            )

            if key_words != get_wiki_key_words():
                change_wiki_key_words(key_words)

        #
        #   Web search
        #
        
        if "WEB" in selected_sources:
            web_search = st.text_input(
                "Recherche Web",
                placeholder="Exemple: Chat, Chien, animal, etc.",
                key="web_search",
            )

            if web_search != get_web_search():
                change_web_search(web_search)

        st.markdown("---")

        # Think mode
        think_mode = st.checkbox("Mode de réflexion", key="think_mode")
        if think_mode != get_think_mode():
            change_think_mode(think_mode)

        # Num ctx
        num_ctx = st.slider(
            "Contexte (tokens)",
            key="num_ctx",
            min_value=1024,
            max_value=16384,
            step=1024,
        )
        if num_ctx != get_num_ctx():
            change_num_ctx(num_ctx)

        # Reset conversation button
        if st.button("Réinitialiser la conversation", width="stretch"):
            reset_conversation()
            st.rerun()

if __name__ == "__main__":
    main()