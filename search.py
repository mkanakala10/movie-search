import uvicorn
import torch
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Semantic Movie Search API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Hardware Optimization for macOS (Apple Silicon MPS)
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(f"Loading PyTorch model on hardware: {device.upper()}")

# 2. Initialize the embedding model
model = SentenceTransformer("BAAI/bge-small-en-v1.5", device=device)
VECTOR_SIZE = model.get_embedding_dimension() # 384 dimensions

# 3. Initialize Qdrant Vector Database (running in-memory)
qdrant = QdrantClient(":memory:")

# 4. Create a collection with Cosine Similarity
qdrant.create_collection(
    collection_name="movies",
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)

# 5. Our database of movies with semantic plots
movie_catalog = [
    {"id": 1, "name": "Inception", "plot": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O."},
    {"id": 2, "name": "Interstellar", "plot": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival."},
    {"id": 3, "name": "The Matrix", "plot": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers."},
    {"id": 4, "name": "Toy Story", "plot": "A cowboy doll is profoundly threatened and jealous when a new spaceman action figure supplants him as top toy in a boy's room."},
    {"id": 5, "name": "Finding Nemo", "plot": "After his son is captured in the Great Barrier Reef and taken to Sydney, a timid clownfish sets out on a journey to bring him home."}
]

# 6. Embed and index the catalog on startup
print("Embedding movie catalog...")
points = []
for movie in movie_catalog:
    # We embed the PLOT so the AI understands the story
    vector = model.encode(movie["plot"]).tolist() 
    points.append(
        PointStruct(id=movie["id"], vector=vector, payload=movie)
    )

# Insert into the vector database
qdrant.upsert(collection_name="movies", points=points)
print("Database ready!")

# 7. The API Endpoint
@app.get("/search")
async def semantic_search(q: str, limit: int = 2):
    # Convert the user's search query into a vector
    query_vector = model.encode(q).tolist()

    # Search the vector DB for the closest vectors
    search_results = qdrant.query_points(
        collection_name="movies",
        query=query_vector,
        limit=limit
    )

    # Format and return the results
    return [
        {"title": hit.payload["name"], "overview": hit.payload["plot"]}
        for hit in search_results.points
    ]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)