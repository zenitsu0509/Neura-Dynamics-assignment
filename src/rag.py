import os
import glob
from typing import List, Dict
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    def __init__(self, data_dir: str = "data", collection_name: str = "policy_docs"):
        self.data_dir = data_dir
        self.collection_name = collection_name
        
        # Initialize Groq Client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Allow model to be overridden by env var, but default to user request
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self._resolved_model: str | None = None

        # Initialize ChromaDB
        self.chroma_client = chromadb.Client()
        
        # Use Sentence Transformers for embeddings
        # We use a local embedding model to avoid extra API costs and for speed
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_fn
        )

    def _resolve_model(self) -> str:
        """Resolve a usable Groq model id.

        We validate the requested model against `models.list()` so we don't
        accidentally call some other default model.
        """
        if self._resolved_model:
            return self._resolved_model

        requested = (self.model or "").strip()
        fallback = "openai/gpt-oss-120b"

        try:
            available = {m.id for m in self.groq_client.models.list().data}
        except Exception:
            # If model listing fails, still try the requested model.
            self._resolved_model = requested or fallback
            return self._resolved_model

        if requested and requested in available:
            self._resolved_model = requested
            return self._resolved_model

        if fallback in available:
            self._resolved_model = fallback
            return self._resolved_model

        # Last resort: pick any available model to avoid hard failure,
        # but keep the choice deterministic.
        self._resolved_model = sorted(available)[0] if available else (requested or fallback)
        return self._resolved_model

    def load_documents(self) -> List[Dict[str, str]]:
        """
        Loads text files from the data directory.
        """
        documents = []
        file_paths = glob.glob(os.path.join(self.data_dir, "*.txt"))
        
        for file_path in file_paths:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "content": content,
                    "source": os.path.basename(file_path)
                })
        return documents

    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Splits text into chunks.
        
        Strategy: Fixed-size chunking with overlap.
        Reason: 
        - Chunk Size (500): Policy documents often contain short, distinct sections (e.g., "Refund Process"). 
          500 characters is typically enough to capture a full rule or paragraph without being too fragmented.
        - Overlap (50): Ensures that context is preserved across chunk boundaries, preventing sentences 
          from being cut in a way that loses meaning.
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start += chunk_size - overlap
            
        return chunks

    def ingest_data(self):
        """
        Loads data, chunks it, and adds it to the vector store.
        """
        print("Loading documents...")
        docs = self.load_documents()
        
        ids = []
        documents = []
        metadatas = []
        
        doc_id_counter = 0
        
        print(f"Found {len(docs)} documents. Processing...")
        
        for doc in docs:
            chunks = self.chunk_text(doc["content"])
            for i, chunk in enumerate(chunks):
                ids.append(f"{doc['source']}_{i}")
                documents.append(chunk)
                metadatas.append({"source": doc["source"]})
                doc_id_counter += 1
        
        if documents:
            print(f"Adding {len(documents)} chunks to vector store...")
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            print("Data ingestion complete.")
        else:
            print("No documents found to ingest.")

    def retrieve(self, query: str, n_results: int = 3) -> List[str]:
        """
        Retrieves the most relevant chunks for a given query.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Flatten the list of documents (results['documents'] is a list of lists)
        return results['documents'][0] if results['documents'] else []

    def generate_answer(self, query: str, context_chunks: List[str], prompt_template: str) -> str:
        """
        Generates an answer using the Groq LLM.
        """
        context = "\n\n".join(context_chunks)
        
        # Format the prompt
        prompt = prompt_template.format(context=context, question=query)
        
        model_to_use = self._resolve_model()

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model_to_use,
            )

            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error generating answer (model={model_to_use}): {e}"

    def query(self, question: str, prompt_template: str) -> Dict[str, any]:
        """
        End-to-end RAG pipeline: Retrieve -> Generate
        """
        retrieved_chunks = self.retrieve(question)
        answer = self.generate_answer(question, retrieved_chunks, prompt_template)
        
        return {
            "question": question,
            "answer": answer,
            "context": retrieved_chunks
        }
