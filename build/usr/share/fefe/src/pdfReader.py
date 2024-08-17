import fitz 
from src import functions

spec = {
        "type": "function",
        "function": {
            "name": "pdfReader",
            "description": """
Used to extract content from PDFs on the user's filesystem. Provide the full path to the PDF.
""",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Full path to the PDF document"
                    }
                },
                "required": ["filepath"]
            }
        }
    }


def pdfReader(filepath):
    # Open the PDF file
    document = fitz.open(filepath)
    
    # Initialize an empty string to hold the text
    text = ""
    
    # Iterate through each page
    for page_num in range(len(document)):
        # Get the page
        page = document.load_page(page_num)
        # Extract the text from the page
        text += page.get_text()
    
    return text