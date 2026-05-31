#
#   Imports
#

import httpx
import bs4
import ollama
import streamlit as st

from typing import List, Optional
from ddgs import DDGS # type: ignore

# Perso

from constants import (
    HTTP_HEADERS,
    NUM_WEB_RESULTS_MAX,
    NUM_CHARS_PER_WEB_PAGE_MAX,
    SUMMARIZE_PROMPT
)
from sessions import *

#
#   Functions
#

def get_urls(key_words: str, max_results: int = NUM_WEB_RESULTS_MAX) -> List[str]:
    """
        Lists all the urls linked to the given key words,
        according to the duckduckgo search engine.

        Params:
            - key_words: The keywords to search for.
            - max_results: The maximum number of results to return.

        Returns:
            - A list of urls.
    """
    with DDGS() as ddgs:
        results = ddgs.text(
            key_words,
            max_results=max_results,
        )
        return [result["href"] for result in results]


def get_page_content(url: str, max_char_number: int = NUM_CHARS_PER_WEB_PAGE_MAX) -> Optional[str]:
    """
        Gets the content of the given url by web scrapping.

        Params:
            - url: The url to get the content from.
            - max_char_number: The maximum number of characters to return.

        Returns:
            - The content of the given url.
            - None if the url is not found.
    """
    try:
        content_raw = httpx.get(url, headers=HTTP_HEADERS)
    except Exception:
        st.warning(f"Error getting the content of the url {url}")
        return None

    if content_raw.status_code == 200:
        try:
            soup = bs4.BeautifulSoup(content_raw.text, "html.parser")
        except Exception:
            st.warning(f"Error parsing the content of the url {url}")
            return None

        # Deleting by reference the useless tags
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()

        # Getting the text content
        text_content = soup.get_text()

        # Removing extra whitespace
        text_content = " ".join(text_content.split())

        # Truncating the text content
        text_content = text_content[:max_char_number]

        return text_content
    
    return None

def web_query(urls: List[str]) -> List[Optional[str]]:
    """
        For each given url, it gets the text content from the page.

        Params:
            - urls: The urls to get the content from.

        Returns:
            A list of text contents.
    """
    ret: List[Optional[str]] = []
    for url in urls:
        content = get_page_content(url)
        ret.append(content)
    return ret

def summarize_content(content: str, user_input: str) -> str:
    """
        Summarizes the given content. It takes into consideration
        the user input to better understand the context.

        Params:
            - content: The content to summarize.
            - user_input: The user input to better understand the context.

        Returns:
            he summarized content.
    """
    
    # Preparing the payload
    payload = [{
        "role": "system",
        "content": SUMMARIZE_PROMPT
    }]

    payload.append({
        "role": "user",
        "content": "Résume ce contenu sachant que je cherche:" +
        user_input + "\n" +
        "Voici le contenu:\n" +
        content
    })

    # Infering the summarize
    stream = ollama.chat(
        model=get_model(),
        messages=payload,
        stream=True,
        think=get_think_mode(),
        options={
            "num_ctx": get_num_ctx(),
        },
    )

    response = ""
    for chunk in stream:
        content = chunk.message.content or ""
        if content:
            response += content
    return response