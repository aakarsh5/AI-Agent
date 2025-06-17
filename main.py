from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor

# Load environment variables
load_dotenv()

class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tool_used: list[str]

# Initialize LLM
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
llm = ChatOpenAI(
    openai_api_key=openrouter_api_key,
    openai_api_base="https://openrouter.ai/api/v1",
    model="gpt-3.5-turbo"
)

# Output parser
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a research assistant that helps write research papers.\n"
            "Use tools when needed.\n"
            "Respond to the user query with a well-researched answer, formatted using the following JSON schema:\n{format_instructions}\nReturn real data in this format, not the schema itself."

        ),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}")
    ]
).partial(format_instructions=parser.get_format_instructions())

# Dummy tool list
tools = []  # Add actual tools here later

# Create the agent
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

# Run the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
raw_response = agent_executor.invoke({"input": "What is the capital of Nepal?"})
print(raw_response)
