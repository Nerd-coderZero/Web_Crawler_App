from fastapi import FastAPI, Query
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Set

app = FastAPI()

def crawl_website(root_url: str, depth: int) -> Dict[str, List[str]]:
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
    
    crawled_links: Set[str] = set()
    queue = [(root_url, 0)]  # Store URLs with their current depth level
    
    while queue:
        url, current_depth = queue.pop(0)
        
        # Stop if we've reached the specified depth
        if current_depth >= depth:
            continue
        
        # Avoid re-processing the same URL
        if url in crawled_links:
            continue
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            for link in soup.find_all("a", href=True):
                href = link["href"]
                full_url = requests.compat.urljoin(url, href)
                
                if full_url not in crawled_links and full_url.startswith("http"):
                    queue.append((full_url, current_depth + 1))
                    
            crawled_links.add(url)
        
        except (requests.exceptions.RequestException, ValueError):
            continue
    
    return {"links": list(crawled_links)}

# Streamlit App
if __name__ == '__main__':
    import streamlit as st
    st.title("Web Crawler API")
    st.write(crawl_website.__doc__)
    
    root_url = st.text_input("Root URL to crawl")
    depth = st.number_input("Crawl Depth", min_value=1, step=1, value=1)
    
    if st.button("Crawl"):
        if root_url:
            result = crawl_website(root_url, depth)
            st.write(result)
        else:
            st.warning("Please enter a root URL.")
