import os
import sys
from rag import RAGSystem
from prompts import INITIAL_PROMPT, IMPROVED_PROMPT

def main():
    print("Initializing RAG System...")
    rag = RAGSystem()
    
    # Ingest data on startup
    rag.ingest_data()
    
    print("\n--- Policy Assistant Ready ---")
    print("Type 'exit' to quit.")
    print("Type 'switch' to toggle between Initial and Improved prompts.")
    
    current_prompt = IMPROVED_PROMPT
    prompt_name = "Improved"
    
    while True:
        try:
            query = input(f"\n({prompt_name} Prompt) Enter your question: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            if query.lower() == 'switch':
                if current_prompt == IMPROVED_PROMPT:
                    current_prompt = INITIAL_PROMPT
                    prompt_name = "Initial"
                else:
                    current_prompt = IMPROVED_PROMPT
                    prompt_name = "Improved"
                print(f"Switched to {prompt_name} Prompt.")
                continue
            
            if not query.strip():
                continue
                
            print("\nThinking...")
            result = rag.query(query, current_prompt)
            
            print("\n--- Answer ---")
            print(result['answer'])
            print("\n--- Retrieved Context Sources ---")
            for i, chunk in enumerate(result['context']):
                print(f"[{i+1}] ...{chunk[:100].replace(chr(10), ' ')}...")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
