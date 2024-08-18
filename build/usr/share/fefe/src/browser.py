import requests 
from bs4 import BeautifulSoup
from src import functions
import webbrowser

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
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url}")
    
    # Parse the content of the request with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
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
