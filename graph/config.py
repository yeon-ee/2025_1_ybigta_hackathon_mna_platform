import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm_a = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4',
    temperature=0.01,
    max_tokens=2000,
)
llm_b = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4',
    temperature=0.01,
    max_tokens=2000,
)
llm_c = ChatOpenAI(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model='gpt-4',
    temperature=0.01,
    max_tokens=2000,
) 

# from langchain_upstage import ChatUpstage
# llm_a = ChatUpstage(api_key=os.getenv("SOLAR_API_KEY"), model='solar-pro', temperature=0.7)
# llm_b = ChatUpstage(api_key=os.getenv("SOLAR_API_KEY"), model='solar-pro', temperature=0.7)
# llm_c = ChatUpstage(api_key=os.getenv("SOLAR_API_KEY"), model='solar-pro', temperature=0.7)