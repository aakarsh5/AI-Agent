from langchain_community.tools import wikipedia, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper 
from langchain.tools import Tool
from datetime import datetime

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name = "search",
    func = search.run,
    description = "Search wikipedia for information",
)
