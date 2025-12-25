# RAG Policy Assistant

This project is a Retrieval-Augmented Generation (RAG) system designed to answer questions based on company policy documents. It uses the Groq API for LLM generation and ChromaDB for vector storage.

## Setup

1.  **Clone the repository**
2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup:**
    - Copy `.env.example` to `.env`
    - Add your Groq API key to `.env`
    - (Optional) Set `GROQ_MODEL` in `.env` if you want to use a specific model (default: `openai/gpt-oss-120b`).

## Usage

### Interactive Mode

Run the main script to interact with the assistant:

```bash
python src/main.py
```

- Type your question to get an answer.
- Type `switch` to toggle between the **Initial** and **Improved** prompts to see the difference.
- Type `exit` to quit.

### Evaluation

Run the evaluation script to test the system against a set of predefined questions:

```bash
python src/evaluate.py
```

This will run 8 test questions (answerable, unanswerable, and edge cases) and allow you to manually score the responses.

## Architecture

-   **Data Loading:** Reads text files from the `data/` directory.
-   **Chunking:** Splits text into 500-character chunks with 50-character overlap.
    -   *Reasoning:* 500 characters captures enough context (approx. 1 paragraph) to be meaningful, while overlap prevents cutting sentences in half at boundaries.
-   **Embeddings:** Uses `sentence-transformers/all-MiniLM-L6-v2` locally.
    -   *Reasoning:* Fast, free, and effective for semantic search on English text.
-   **Vector Store:** Stores embeddings in ChromaDB for fast retrieval.
-   **Retrieval:** Finds the top 3 most relevant chunks for a user query.
-   **Generation:** Uses Groq API (defaulting to `openai/gpt-oss-120b` as requested) to generate answers based on retrieved context.

## Prompts

See [prompts.md](prompts.md) for a detailed breakdown of the prompt engineering process, including the initial vs. improved prompts and the rationale behind the changes.

## Evaluation Results

--- Evaluation Summary ---
Q: What is the time limit for refunds?
Score: 3
Q: Can I cancel my order if it has already shipped?
Score: 2
Q: Do you ship to France?
Score: 3
Q: What is the restocking fee for late cancellations?
Score: 3
Q: How do I contact support for a missing refund?
Score: 3
Q: Can I return a gift card?
Score: 3
Q: What is the company's policy on remote work?
Score: 3
Q: Can I get a refund if I bought the item 35 days ago?
Score: 3

Total Score: 23/24
## Key Trade-offs & Improvements

-   **Chunking:** Fixed-size chunking is simple but might split semantic units. **Improvement:** Semantic chunking or recursive character splitting.
-   **Retrieval:** Basic top-k retrieval. **Improvement:** Hybrid search (keyword + semantic) or a reranking step (e.g., using a Cross-Encoder) to improve relevance.
-   **Evaluation:** Manual scoring is subjective. **Improvement:** Use an "LLM-as-a-Judge" approach to automatically score answers against a ground truth dataset.
