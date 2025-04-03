import operator
from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    score: dict
    comment: dict
    sender: str
    company_name: str
    user_query: str
    checklist: dict