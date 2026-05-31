#
#   Imports
#

import os
import shutil
import streamlit as st

from pathlib import Path
from streamlit.runtime.uploaded_file_manager import UploadedFile
from typing import List

# Perso

from rag import *
from constants import BASE_DIR
from sessions import *

#
#   Functions
#

def add_documents_to_corpus(corpus_name: str, files: List[UploadedFile]):
    """
        Copies the given documents path to the corpus directory.

        Params:
            - corpus_name: The name of the corpus to add the documents to.
            - files: The files to add to the corpus.
    """

    for file in files:
        with open(os.path.join(BASE_DIR, corpus_name, file.name), "wb") as f:
            f.write(file.getvalue())

        ingest_documents(corpus_name, [file.name])

def get_documents_from_corpus(corpus_name: str) -> List[str]:
    """
        Lists the documents from the corpus by searching the corpus directory.

        Params:
            - corpus_name: The name of the corpus to list the documents from.

        Returns:
            - A list of the documents paths.
    """
    corpus_path = Path(os.path.join(BASE_DIR, corpus_name))
    return [
        file.name for file in corpus_path.iterdir()
        if file.is_file()
    ]

def delete_document_from_corpus(corpus_name: str, document_path: str):
    """
        Deletes the given document from the corpus.

        Params:
            - corpus_name: The name of the corpus to delete the document from.
            - document_path: The path of the document to delete from the corpus.
    """
    os.remove(os.path.join(BASE_DIR, corpus_name, document_path))
    purge_document(corpus_name, document_path)

def delete_corpus(corpus_name: str):
    """
        Deletes the given corpus.

        Params:
            - corpus_name: The name of the corpus to delete.
    """

    # Looping over the documents and deleting them
    for document_path in get_documents_from_corpus(corpus_name):
        delete_document_from_corpus(corpus_name, document_path)

    # Deleting the database
    deleting_database(corpus_name)

    # Deleting the corpus directory
    try:
        shutil.rmtree(os.path.join(BASE_DIR, corpus_name))
    except OSError:
        pass

    if corpus_name in st.session_state["corpus_list"]:
        st.session_state["corpus_list"].remove(corpus_name)