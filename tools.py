from langchain_community.tools import wikipedia, DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper 
from langchain.tools import Tool
from datetime import datetime

import json
from datetime import datetime
from langchain.tools import Tool

def save_to_txt_from_json(json_str: str):
    """Expects a JSON string with 'content' and 'topic' fields."""
    try:
        data = json.loads(json_str)
        content = data["content"]
        topic = data["topic"]

        # Sanitize the topic to be a safe filename
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (" ", "_", "-")).rstrip()
        filename = f"{safe_topic}.txt"

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_text = f"---GPT Chat---\nTimestamp: {timestamp}\n\nTopic: {topic}\n\n{content}\n\n"

        with open(filename, "a", encoding="utf-8") as f:
            f.write(formatted_text)

        return f"Data successfully saved to {filename}"

    except Exception as e:
        return f"Error saving chat: {str(e)}"

save_tool = Tool(
    name="save_chat",
    func=save_to_txt_from_json,
    description="Save chat content to a file named after the topic. Input should be a JSON string with 'topic' and 'content'."
)



search = DuckDuckGoSearchRun()
search_tool = Tool(
    name = "search",
    func = search.run,
    description = "Search wikipedia for information",
)

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)
wiki_tool = WikipediaQueryRun(api_wrapper = api_wrapper)
