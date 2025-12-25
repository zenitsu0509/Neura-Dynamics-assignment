import time
from rag import RAGSystem
from prompts import IMPROVED_PROMPT

TEST_QUESTIONS = [
    {
        "question": "What is the time limit for refunds?",
        "type": "Answerable",
        "expected_key_info": "30 days"
    },
    {
        "question": "Can I cancel my order if it has already shipped?",
        "type": "Answerable",
        "expected_key_info": "No, must wait to receive item and follow Refund Policy"
    },
    {
        "question": "Do you ship to France?",
        "type": "Answerable (Negative)",
        "expected_key_info": "No, only Canada, UK, and Australia"
    },
    {
        "question": "What is the restocking fee for late cancellations?",
        "type": "Answerable",
        "expected_key_info": "10%"
    },
    {
        "question": "How do I contact support for a missing refund?",
        "type": "Answerable",
        "expected_key_info": "support@example.com"
    },
    {
        "question": "Can I return a gift card?",
        "type": "Answerable",
        "expected_key_info": "No, non-refundable"
    },
    {
        "question": "What is the company's policy on remote work?",
        "type": "Unanswerable",
        "expected_key_info": "I cannot find the answer / Not in policy"
    },
    {
        "question": "Can I get a refund if I bought the item 35 days ago?",
        "type": "Answerable (Inference)",
        "expected_key_info": "No, limit is 30 days"
    }
]

def evaluate():
    print("Initializing RAG System for Evaluation...")
    rag = RAGSystem()
    rag.ingest_data()
    
    print("\n--- Starting Evaluation ---")
    print(f"Model: {rag.model}")
    print(f"Prompt: Improved Prompt")
    
    results = []
    
    for i, item in enumerate(TEST_QUESTIONS):
        print(f"\nQuestion {i+1}: {item['question']}")
        print(f"Type: {item['type']}")
        print(f"Expected Info: {item['expected_key_info']}")
        
        start_time = time.time()
        response = rag.query(item['question'], IMPROVED_PROMPT)
        elapsed = time.time() - start_time
        
        print(f"Answer:\n{response['answer']}")
        print(f"Time: {elapsed:.2f}s")
        
        # Simple manual scoring prompt
        score = input("Score (1=Bad, 2=OK, 3=Good): ")
        results.append({
            "question": item['question'],
            "answer": response['answer'],
            "score": score
        })

    print("\n--- Evaluation Summary ---")
    total_score = 0
    for res in results:
        print(f"Q: {res['question']}")
        print(f"Score: {res['score']}")
        try:
            total_score += int(res['score'])
        except:
            pass
            
    print(f"\nTotal Score: {total_score}/{len(TEST_QUESTIONS)*3}")

if __name__ == "__main__":
    evaluate()
