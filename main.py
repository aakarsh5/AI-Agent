from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent

from langchain_community.llms import Ollama


load_dotenv() #load enviroment variable

# llm = ChatOpenAI(model = "gpt-4o-mini")
llm = Ollama(model="llama3")

# llm2 = ChatAnthropic(model = "claude-3-5-sonnet-20241022")

# class ResearchResponse(BaseModel):
#     topic:str
#     summary:str
#     sources:list[str]
#     tool_used:list[str]


# openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# llm = ChatOpenAI(
#     openai_api_key=openrouter_api_key,
#     openai_api_base="https://openrouter.ai/api/v1",
#     model="gpt-3.5-turbo"
# )
# parser = PydanticOutputParser(pydantic_object=ResearchResponse)

response = llm.invoke("What is the meaning of life?")
print(response)
