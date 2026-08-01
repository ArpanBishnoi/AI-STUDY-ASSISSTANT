import chromadb
client = chromadb.PersistentClient(path="./chroma_db")
chunks_collection = client.get_or_create_collection(name="CHUNKS")
