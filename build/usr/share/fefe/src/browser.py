import requests 
from bs4 import BeautifulSoup
from src import functions
import subprocess
import webbrowser
import os
import brotli
import gzip
import zlib

spec =     {
        "type": "function",
        "function": {
            "name": "browser",
            "description": """
You can use the `browser` to read text on a website or to search for things, such as recipes, using Google, Bing.
Pull textual data from websites. When asked to search, use the `/search?q=<query>` endpoint.
For example, if asked to search for a recipe for homemade lemonade,
```
https://www.google.com/search?q=homemade+lemonade
https://www.allrecipes.com/search?q=homemade+lemonade
https://www.duckduckgo.com/search?q=homemade+lemonade
```
If asked to search for something or pull up results from the web, use the `browser` to search bing, google, or duckduckgo. 
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The website url to fetch data from."
                    },
                    "open_for_user": {
                        "type":"boolean",
                        "Description": "Defaults to False. If True, the URL will open for the user in a browser. Do so only if the user requests that you open it for them.",
                        "enum":[True,False],
                        "default": False
                    }
                },
                "required": ["url"]
            }
        }
    }


def get_soup(url):
    headers = {
        "method": "GET",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }

    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url}")
    
    content_encoding = response.headers.get('content-encoding')
    
    # Handle Brotli encoding
    if content_encoding == 'br':
        try:
            decoded_content = brotli.decompress(response.content)
        except Exception as e:
            decoded_content = response.content
    # Handle Gzip encoding
    elif content_encoding == 'gzip':
        try:
            decoded_content = gzip.decompress(response.content)
        except:
            decoded_content = response.content
    
    # Handle Deflate encoding
    elif content_encoding == 'deflate':
        try:
            decoded_content = zlib.decompress(response.content)
        except:
            decoded_content = response.content
    
    # If no encoding, just use the response content
    else:
        decoded_content = response.content

    # Parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(decoded_content, 'html.parser')
    return soup

def extract_text_and_links_from_body(soup):
    body_text = soup.body.get_text(separator=' ', strip=True)
    links = [(a.get_text(strip=True), a['href']) for a in soup.body.find_all('a', href=True)]
    return body_text, links

def extract_metadata(soup):
    # Extract metadata
    metadata = {}
    for meta in soup.find_all('meta'):
        # Use the name attribute if available, otherwise use the property attribute
        name = meta.get('name', meta.get('property'))
        content = meta.get('content')
        if name and content:
            metadata[name] = content
    
    return metadata


def browser(url,open_for_user=False):
    if open_for_user:
        if functions.is_wsl():
            subprocess.run(["wslview",f"{url}"])
        else:
            webbrowser.open(url)
    
    soup = get_soup(url)  # Await the get_soup call
    metadata = extract_metadata(soup)
    body_text, links = extract_text_and_links_from_body(soup) # Await the extract_text_from_body call
    formatted_links = '\n'.join([f'{text}: {href}' for text, href in links])
    return f"""
metadata: 
```
{metadata}
```

web page:
```
{body_text}
```

Links:
```
{formatted_links}
```
"""
