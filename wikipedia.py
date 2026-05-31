#
#   Imports
#

import tempfile
import io
import wikipediaapi

from wikipediaapi import WikipediaPage, WikipediaPageSection

from typing import Optional

# Perso

from corpus import *

#
#   Functions
#

def get_wikipedia_page(key_words: str) -> Optional[WikipediaPage]:
    """
        Gets the wikipedia page of the given page name.

        Params:
            - page_name: The name of the wikipedia page to get.
    """
    wiki = wikipediaapi.Wikipedia(
        language="fr",
        user_agent="wikipedia-api/1.0(floalzaix@gmail.com)",
    )

    pages = wiki.search(key_words)
    pages = list(pages.pages.keys())
    if len(pages) <= 0:
        return None

    page = wiki.page(pages[0])

    return page

def _recursive_section_exploration(
    section: WikipediaPageSection | WikipediaPage
) -> List[WikipediaPageSection]:
    """
        Recursively explores the given section and returns a
        list of all the sections.
    """
    sections: List[WikipediaPageSection] = section.sections
    for subsection in section.sections:
        sections.extend(_recursive_section_exploration(subsection))
    return sections

def create_corpus(key_words: str, page: WikipediaPage) -> str:
    """
        Creates a new corpus based from the given Wiipedia pages and 
        creates small pieces of document from the page's sections.

        Params:
            - key_words: The keywords to search for in Wikipedia.
            - page: The Wikipedia page to create the corpus from.

        Returns:
            The name of the created corpus.
    """
    corpus_name = "Wikipedia_" + key_words.replace(" ", "_")
    add_corpus(corpus_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        all_sections = _recursive_section_exploration(page)
        for section in all_sections:
            if section.text:
                with open(
                    os.path.join(
                        temp_dir,
                        section.title.replace(" ", "_") + ".txt"
                    ),
                    "w",
                    encoding="utf-8"
                ) as file:
                    file.write(section.text)

        for file in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, file)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    bytes_content = f.read()
                uploaded_file = io.BytesIO(bytes_content)
                uploaded_file.name = file
                add_documents_to_corpus(corpus_name, [uploaded_file])

    return corpus_name

def wikipedia_query(key_words: str, user_input: str) -> Optional[str]:
    """
        Queries the Wikipedia page with the given keywords and user input.
        It then creates a new corpus from the page and queries the RAG.

        Params:
            - key_words: The keywords to search for in Wikipedia.
            - user_input: The user input to query the Wikipedia page with.

        Returns:
            The context of the Wikipedia page if found, otherwise None.
    """
    page = get_wikipedia_page(key_words)

    if page:
        corpus_name = create_corpus(key_words, page)
        context = query_rag(corpus_name, user_input)
        return context

    return None