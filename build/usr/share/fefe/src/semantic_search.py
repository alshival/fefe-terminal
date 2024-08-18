# This is in development. Still in the brainstorming phase. Commenting out for now.

# file_index_CREATE = '''CREATE TABLE IF NOT EXISTS file_index (
#                     filepath TEXT PRIMARY KEY,
#                     last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#               );'''

# directory_index_CREATE = '''CREATE TABLE IF NOT EXISTS directory_index (
#                     path TEXT PRIMARY KEY,
#                     last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#               );'''

# from src import documentReader
# from src import functions
# import chromadb 
# from langchain_experimental.text_splitter import SemanticChunker
# from langchain_openai.embeddings import OpenAIEmbeddings
# import re 
# import os 
# import time
# from datetime import datetime
# supported_filetypes = [
#     '.pdf',   # PDF Documents
#     '.txt',   # Plain Text Files
#     '.md',    # Markdown Files
#     '.docx',  # Word Documents
#     '.html',  # HTML Files
#     '.rtf',   # Rich Text Format Files
#     '.xml',   # XML Files
#     '.yaml',  # YAML Files
#     # '.log'    # Log Files. Probably want to include these eventually for developers.
# ]

# def vectordb_connect():
#     # Initialize Chroma client with persistent storage
#     client = chromadb.PersistentClient(path=os.path.join(functions.get_home_path(),".fefe-semantic.db"))

#     # Create a new collection or connect to an existing one
#     collection = client.get_or_create_collection(
#         name="semantic_search",
#         metadata={"hnsw:space": "cosine"}  # Set the distance function to cosine similarity
#     )
#     return client, collection 

# def get_filetype(filename):
#     # Regular expression to match the file extension
#     match = re.search(r'\.\w+$', filename)
#     if match:
#         return match.group(0)
#     else:
#         return None
    
# def get_file_info(filepath):
#     # Get file creation time
#     try:
#         creation_time = os.path.getctime(filepath)
#     except AttributeError:
#         # If the OS doesn't support creation time, we fallback to metadata change time (Unix/Linux)
#         creation_time = os.path.getmtime(filepath)
    
#     # Convert the timestamp to a readable format
#     creation_time_readable = time.ctime(creation_time)

#     # Get last modification time
#     modification_time = os.path.getmtime(filepath)
#     modification_time_readable = time.ctime(modification_time)

#     # Get file size
#     file_size = os.path.getsize(filepath)

#     return {
#         "creation_time": creation_time,
#         "creation_time_readable": creation_time_readable,
#         "modification_time": modification_time,
#         "modification_time_readable": modification_time_readable,
#         "file_size": file_size
#     }


# def add_to_chroma(documents):
#     client,collection = vectordb_connect()
#     for doc in documents:
#         collection.add(
#             documents=[doc.page_content],
#             metadatas=[doc.metadata],
#             ids=[doc.metadata['file'] + str(hash(doc.page_content))]  # Creating a unique ID
#         )

# def query_chroma(query_text, top_k=5, where=None, where_document=None):
#     client,collection = vectordb_connect()
#     # Initialize the parameters dictionary with required fields
#     parameters = {
#         "query_texts": [query_text],
#         "n_results": top_k
#     }

#     # Add optional parameters if they are provided
#     if where is not None:
#         parameters["where"] = where
    
#     if where_document is not None:
#         parameters["where_document"] = where_document

#     # Query the Chroma collection with the dynamic parameters
#     results = collection.query(**parameters)

#     return results


# def split_document(filepath):
#     # Get file creation time
#     file_info = get_file_info(filepath)
#     metadata = {
#         'directory': os.path.dirname(filepath),
#         'filepath':filepath,
#         'file': os.path.basename(filepath),
#         'filetype': get_filetype(filepath),
#         'created': file_info['creation_time'],
#         'modified': file_info['modification_time'],
#         'file_size': file_info['file_size']
#     }

#     file_text = documentReader.documentReader(filepath)
#     # Using openAi embeddings
#     text_splitter = SemanticChunker(OpenAIEmbeddings(openai_api_key='API_KEY'))
#     texts = text_splitter.create_documents([file_text],[metadata])
#     return texts

# def index_file(filepath):
#     texts = split_document(filepath)
#     add_to_chroma(texts)
#     upsert_file_index(filepath)

# def index_directory(path):
#     files = os.listdir(path)
#     for file in files:
#         filetype = get_filetype(file)
#         if filetype in supported_filetypes:
#             filepath = os.path.join(path,file)
#             texts = split_document(filepath)
#             add_to_chroma(texts)
#         upsert_file_index(filepath)
#     upsert_directory_index(path)

# def get_file_vectordb_metadatas(filepath):
#     client,collection = vectordb_connect()
#     metadatas = collection.get(include=['metadatas'])
#     return [{'id':metadatas['ids'][i],'metadata':metadatas['metadatas'][i]} for i in range(len(metadatas)) if metadatas['metadatas'][i]['filepath']=='/home/samuel/Documents/Github/fefe-terminal/dev/usr/dummy/Localization_Is_All_You_Need.pdf']

# #-------------------------------------------------------------------------------
# # We use the SQLite database to keep track of when a directory was last indexed.
# #-------------------------------------------------------------------------------
# def upsert_file_index(filepath):
#     db = functions.db_connect()
#     cursor = db.cursor()

#     # Check if the path already exists
#     cursor.execute("""
#     SELECT COUNT(*)
#     FROM file_index
#     WHERE filepath = ?
#     """, (filepath,))
#     count = cursor.fetchone()[0]

#     if count == 0:
#         # If path does not exist, insert it
#         cursor.execute("""
#         INSERT INTO file_index (filepath)
#         VALUES (?)
#         """, (filepath,))
#     else:
#         # If path exists, update the last_indexed timestamp
#         cursor.execute("""
#         UPDATE file_index
#         SET last_indexed = CURRENT_TIMESTAMP
#         WHERE filepath = ?
#         """, (filepath,))

#     db.commit()
#     db.close()

# def upsert_directory_index(path):
#     db = functions.db_connect()
#     cursor = db.cursor()

#     # Check if the path already exists
#     cursor.execute("""
#     SELECT COUNT(*)
#     FROM directory_index
#     WHERE path = ?
#     """, (path,))
#     count = cursor.fetchone()[0]

#     if count == 0:
#         # If path does not exist, insert it
#         cursor.execute("""
#         INSERT INTO directory_index (path)
#         VALUES (?)
#         """, (path,))
#     else:
#         # If path exists, update the last_indexed timestamp
#         cursor.execute("""
#         UPDATE directory_index
#         SET last_indexed = CURRENT_TIMESTAMP
#         WHERE path = ?
#         """, (path,))

#     db.commit()
#     db.close()

# def get_file_last_indexed(filepath):
#     db = functions.db_connect()
#     cursor = db.cursor()
#     cursor.execute("""
#     SELECT 
#         last_indexed 
#     FROM file_index
#     WHERE filepath = ?
#     """, (filepath,))

#     result = cursor.fetchone()
#     db.close()
    
#     if result:
#         # Assuming last_indexed is a string in the format 'YYYY-MM-DD HH:MM:SS'
#         return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
#     else:
#         return None
    
# def get_directory_last_index(path):
#     db = functions.db_connect()
#     cursor = db.cursor()
#     cursor.execute("""
#     SELECT 
#         last_indexed 
#     FROM directory_index
#     WHERE path = ?
#     """, (path,))

#     result = cursor.fetchone()
#     db.close()
    
#     if result:
#         # Assuming last_indexed is a string in the format 'YYYY-MM-DD HH:MM:SS'
#         return datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
#     else:
#         return None
            
# def update_vectordb_file(filepath):
#     # Check if indexed
#     file_last_indexed = get_file_last_indexed(filepath)
#     # If not indexed, then index
#     if file_last_indexed is None:
#         index_file(filepath)
#     # If already indexed, then reindex
#     else:
#         client,collection = vectordb_connect()
#         vector_documents = get_file_vectordb_metadatas(filepath)
#         if len(vector_documents) > 0:
#             collection.delete(ids=[x['id'] for x in vector_documents])
#             index_file(filepath)
#         else:
#             index_file(filepath)

# # def semantic_search(query,metadatas={}):
