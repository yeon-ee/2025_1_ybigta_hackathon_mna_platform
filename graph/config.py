import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm_a = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4o',
    temperature=0.01,
    max_tokens=2000,
)
llm_b = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4o',
    temperature=0.01,
    max_tokens=2000,
)
llm_c = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4o',
    temperature=0.01,
    max_tokens=2000,
) 