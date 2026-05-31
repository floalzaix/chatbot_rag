#
#   Imports
#

import os

from typing import List, Dict, Optional
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Perso

from constants import BASE_DIR, K_RAG

#
#   Functions
#

_dbs: Dict[str, Chroma] = {}

embedding_model = OllamaEmbeddings(model="nomic-embed-text")

def get_db(corpus_name: str) -> Chroma:
    """
        Gets the database of the given corpus.

        Params:
            - corpus_name: The name of the corpus to get the database from.
    """
    global _dbs

    if corpus_name not in _dbs:
        _dbs[corpus_name] = Chroma(
            collection_name=corpus_name,
            embedding_function=embedding_model,
            persist_directory=os.path.join(BASE_DIR, corpus_name, "chroma_db"),
        )

    return _dbs[corpus_name]

def close_db(corpus_name: str):
    """
        Closes the database of the given corpus.

        Params:
            - corpus_name: The name of the corpus to close the database from.
    """
    global _dbs
    del _dbs[corpus_name]

def ingest_documents(corpus_name: str, list_documents: List[str]):
    """
        Ingests the given documents into the corpus to the chroma database.

        Params:
            - corpus_name: The name of the corpus to ingest the documents into.
            - list_documents: The list of documents to ingest into the corpus.
    """

    chroma_db = get_db(corpus_name)

    # Creating the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    # Creating the chroma client
    for doc in list_documents:
        with open(os.path.join(BASE_DIR, corpus_name, doc), "r") as f:
            content = f.read()

            langchain_document = Document(
                page_content=content,
                metadata={
                    "filename": doc,
                },
            )

            # Splitting the text
            chunks = text_splitter.split_documents([langchain_document])

            # Adding the chunks to the chroma database
            chroma_db.add_documents(
                documents=chunks,
            )

def purge_document(corpus_name: str, document_path: str):
    """
        Purges the given document from the chroma database.

        Params:
            - corpus_name: The name of the corpus to purge the document from.
            - document_path: The path of the document to purge from
            the corpus directory (file name).
    """

    chroma_db = get_db(corpus_name)

    db_files = chroma_db.get()

    ids_to_delete = [
        id for id, meta in zip(
            db_files["ids"],
            db_files["metadatas"]
        )
        if meta["filename"] == document_path
    ]

    chroma_db.delete(ids=ids_to_delete)

def deleting_database(corpus_name: str):
    """
        Deletes the database of the given corpus.

        Params:
            - corpus_name: The name of the corpus to delete the database from.
    """
    chroma_db = get_db(corpus_name)

    chroma_db.delete_collection()

    del chroma_db
    close_db(corpus_name)

def query_rag(corpus_name: str, query: str) -> Optional[str]:
    """
        Queries the RAG of the given corpus with the given query.

        Params:
            - corpus_name: The name of the corpus to query the RAG from.
            - query: The query to query the RAG with.

        Returns:
            The context of the RAG if found, otherwise None.
    """
    chroma_db = get_db(corpus_name)

    chunks = chroma_db.similarity_search(query, k=K_RAG)

    if len(chunks) <= 0:
        return None

    context = "RAG context:\n"
    for chunk in chunks:
        context += chunk.page_content + "\n"

    return context