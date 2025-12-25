# Prompt Engineering

This document details the iteration process for designing the prompts used in the RAG system.

## 1. Initial Prompt

The initial prompt was a simple, generic instruction to the LLM.

```python
INITIAL_PROMPT = """
You are a helpful assistant. Answer the user's question based on the following context:

Context:
{context}

Question:
{question}

Answer:
"""
```

### Issues with Initial Prompt

- **Lack of Persona:** It didn't specify a role, leading to generic responses.
- **Hallucination Risk:** It didn't explicitly forbid using outside knowledge or making things up if the context was missing.
- **Formatting:** It didn't request any specific structure, leading to dense paragraphs.
- **Tone:** It didn't specify a professional tone.

## 2. Improved Prompt

The improved prompt addresses the issues identified above.

```python
IMPROVED_PROMPT = """
You are a specialized Policy Assistant for a company. Your task is to answer employee or customer questions strictly based on the provided policy documents.

Instructions:
1.  **Source of Truth:** Answer ONLY using the information provided in the "Context" section below. Do not use outside knowledge or make assumptions.
2.  **Missing Information:** If the answer is not explicitly found in the context, state: "I cannot find the answer to this question in the provided policy documents." Do not try to make up an answer.
3.  **Structure:** Use bullet points or numbered lists for clarity if the answer involves multiple steps or items.
4.  **Tone:** Maintain a professional, clear, and helpful tone.
5.  **Citations:** If possible, mention which policy section the information comes from (e.g., "According to the Refund Policy...").

Context:
{context}

Question:
{question}

Answer:
"""
```

### Improvements

- **Persona:** Defined as "Specialized Policy Assistant".
- **Constraints:** Added "strictly based on provided policy documents" and "Answer ONLY using...".
- **Edge Case Handling:** Explicit instruction for missing information ("I cannot find the answer...").
- **Structure:** Requested bullet points for readability.
- **Citations:** Encouraged citing the source policy.

## 3. Evaluation of Improvements

When testing with the question "What is the company's policy on remote work?" (which is not in the docs):

- **Initial Prompt:** Might try to hallucinate a generic remote work policy or say "I don't know" without much grace.
- **Improved Prompt:** Correctly responds with "I cannot find the answer to this question in the provided policy documents."

When testing with "How do I get a refund?":

- **Initial Prompt:** Provides the steps but maybe in a block of text.
- **Improved Prompt:** Provides a bulleted list, cites the "Refund Policy", and mentions the 30-day limit clearly.
