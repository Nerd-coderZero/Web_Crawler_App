from fastapi import FastAPI, Query
import requests
from bs4 import BeautifulSoup
from typing import List

app = FastAPI()

@app.get("/crawl")
def crawl_website(
    root_url: str = Query(..., description="The root webpage to crawl"),
    depth: int = Query(..., description="The depth to which to crawl")
) -> dict:
    """
    Crawl a website up to a specified depth and return the links found.
    
    Parameters:
    root_url (str): The root webpage to start crawling from.
    depth (int): The depth to which to crawl. Must be a positive integer.
    
    Returns:
    dict: A JSON object containing the crawled links.
    """
    if depth <= 0:
        raise ValueError("Depth must be a positive integer")
    
    crawled_links = set()
    queue = [root_url]
    
    for _ in range(depth):
        if not queue:
            break
        
        url = queue.pop(0)
        if url in crawled_links:
            continue
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and href.startswith("http"):
                    queue.append(href)
            
            crawled_links.add(url)
        except (requests.exceptions.RequestException, ValueError):
            pass
    
        return {"links": list(crawled_links)}



if __name__ == '__main__':
    import streamlit as st
    st.title("Web Crawler API")
    st.write(crawl_website.__doc__)
    root_url = st.text_input("Root URL to crawl")
    depth = st.number_input("Crawl Depth", min_value=1, step=1)
    if st.button("Crawl"):
        result = crawl_website(root_url, depth)
        st.write(result)
