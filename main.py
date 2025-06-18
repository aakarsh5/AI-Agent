from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool,wiki_tool,save_tool

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
tools = [search_tool,wiki_tool,save_tool]  # Add actual tools here later

# Create the agent
agent = create_tool_calling_agent(
    llm=llm,
    prompt=prompt,
    tools=tools
)

# Run the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
query = input("What can I help you with ? ")
raw_response = agent_executor.invoke({"input":query})
# print(raw_response)

try:
    output_text = raw_response.get("output", "")
    structured_response = parser.parse(output_text)
    print(structured_response)
except Exception as e:
    print("❌ Error parsing response:", e)
    print("🧾 Raw response:", raw_response)

