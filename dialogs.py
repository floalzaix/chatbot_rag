#
#   Imports
#

import streamlit as st

# Perso

from corpus import *

#
#   Dialogs
#

selected_session = "Nouvelle session"

@st.dialog("Ajouter un nouveau corpus")
def popup_ajout_corpus():
    new_corpus_name = st.text_input("Nom du nouveau corpus:")


    col1, col2 = st.columns(2)

    # Cancel button
    with col2:
        if st.button("Annuler", width="stretch"):
            st.rerun()


    # Validate button
    try:
        with col1:
            if st.button("Valider", width="stretch", type="primary"):
                add_corpus(new_corpus_name)
                st.rerun()

    except ValueError as e:
        st.error(e, width="stretch")

@st.dialog("Modifier un corpus")
def popup_modifier_corpus(selected_corpus: str):

    # Preparing the documents list
    documents_list = [
        {
            "Selectionner": False,
            "Fichiers": file,
        }
        for file in get_documents_from_corpus(selected_corpus)
    ]

    # Display the corpus documents list
    if documents_list:
        docs = st.data_editor(
            documents_list,
            column_config={
                "Selectionner": st.column_config.CheckboxColumn(
                    "Sélectionner",
                    width="small",
                ),
                "Fichiers": st.column_config.TextColumn(
                    "Fichiers",
                    width="medium",
                    disabled=True,
                ),
            },
        )

        # Delete selected documents button
        if st.button("Supprimer les documents sélectionnés", width="stretch"):
            for doc in docs:
                if doc["Selectionner"]:
                    delete_document_from_corpus(
                        selected_corpus,
                        doc["Fichiers"] # type: ignore
                    )
            
            st.rerun()
    else:
        st.warning("Aucun document trouvé dans ce corpus.")

    # Upload zone
    files = st.file_uploader(
        "Ajouter des documents à ce corpus",
        type=["txt", "pdf"],
        accept_multiple_files=True,
    )
    st.button(
        "Ajouter les fichiers",
        width="stretch",
        on_click=add_documents_to_corpus,
        args=(selected_corpus, files),
        disabled=len(files) == 0,
    )

    # Delete corpus button
    if st.button("Supprimer le corpus", width="stretch"):
        delete_corpus(selected_corpus)
        st.rerun()

@st.dialog("Nouvelle session")
def popup_nouvelle_session():
    global selected_session
    session_name = st.text_input("Nom de la nouvelle session : ")

    if st.button("Créer", width="stretch"):
        selected_session = session_name
        new_session()
        st.rerun()

@st.dialog("Charger une session")
def popup_charger_session():
    global selected_session

    session_list = get_all_sessions()
    session_name = st.selectbox("Choisissez une session : ", session_list)

    if st.button("Charger", width="stretch"):
        load_session(session_name)
        selected_session = session_name
        st.rerun()

@st.dialog("Etes-vous sûr de vouloir supprimer cette session ?")
def popup_supprimer_session():
    global selected_session
    if st.button("Supprimer", width="stretch"):
        delete_session(selected_session)
        selected_session = "Nouvelle session"
        st.rerun()

    if st.button("Annuler", width="stretch"):
        st.rerun()