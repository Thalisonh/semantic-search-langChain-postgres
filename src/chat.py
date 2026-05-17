import os
from search import search_prompt

def main():
    try:
        question = input("Faça sua pergunta: ")
        response = search_prompt(question)

        print(f"\nRESPOSTA: {response}")

    except Exception as e:
        print(f"Erro ao buscar: {e}")
        return
    
    pass

if __name__ == "__main__":
    main()