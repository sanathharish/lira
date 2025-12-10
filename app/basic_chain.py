# app/basic_chain.py

import os
from dotenv import load_dotenv

# from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


# def get_llm():
#     return ChatOpenAI(
#         model="gpt-4.1-mini",
#         temperature=0.3
#     )

def get_llm():
    return ChatOllama(
        model="llama3.2",
        temperature=0.3,
    )



def build_basic_chain():

    prompt = ChatPromptTemplate.from_messages([
        # ONE SINGLE STRING for system message
        (
            "system",
            "You are a helpful research assistant. Explain everything clearly using simple language."
        ),
        (
            "user",
            "Briefly explain the topic: {topic}"
        )
    ])

    llm = get_llm()
    parser = StrOutputParser()

    chain = prompt | llm | parser
    return chain


def demo():
    chain = build_basic_chain()

    test_topics = [
        "Quantum computing",
        "Why LangChain is used"
    ]

    for t in test_topics:
        print(f"\n=== TOPIC: {t} ===")
        print(chain.invoke({"topic": t}))


if __name__ == "__main__":
    demo()
