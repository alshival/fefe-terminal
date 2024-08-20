from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src import functions

spec = {
    "type": "function",
    "function": {
        "name": "search_youtube",
        "description": "Search for videos on YouTube using the Data API.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query. Description of video requested by the user."
                }
            }
        }
    }
}

# Function to search for YouTube videos
def search_youtube(query, max_results=6):
    
    google_api_key = functions.get_google_api_key()

    try:
        # Create a resource object for interacting with the YouTube API
        youtube = build('youtube', 'v3', developerKey=google_api_key)

        # Make an API request to search for videos
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results
        )
        response = request.execute()

        # Process and return the results
        results = []
        for item in response['items']:
            results.append({
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
            })

        return results

    except HttpError as e:
        # # Handle specific HTTP error, e.g., invalid API key
        # error_message = e.content.decode('utf-8')
        #print(f"An error occurred: {error_message}")
        return "Google API key is not valid. Set it using `fefe-setup api-key`."

    except Exception as e:
        # Handle other unexpected errors
        return f"An unexpected error occurred: {str(e)}"
