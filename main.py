from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

load_dotenv() #load enviroment variable

# llm = ChatOpenAI(model = "gpt-4o-mini")
# llm2 = ChatAnthropic(model = "claude-3-5-sonnet-20241022")

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    model="openrouter/gpt-3.5-turbo"
)

response = llm.invoke("What is the meaning of life?")
print(response)