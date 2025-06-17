# 🧠 AI Research Assistant using LangChain & OpenRouter

This project implements a simple AI-powered research assistant using [LangChain](https://www.langchain.com/), [OpenRouter](https://openrouter.ai/), and [Pydantic](https://docs.pydantic.dev/).  
It generates structured research responses in JSON format using a Pydantic schema and supports future integration with LangChain tools.

---

## 📚 Features

- 🔑 Uses OpenRouter's `gpt-3.5-turbo` model
- 🧱 Structured output using Pydantic
- 🛠️ Extendable tool-calling agent setup
- 🧾 JSON-formatted responses with topic, summary, sources, and tools used

---

## 🛠️ Installation

### 📥 Clone the repository

```bash
git clone https://github.com/yourusername/ai-research-assistant.git
cd ai-research-assistant
🧪 Create a virtual environment

python -m venv venv
Activate the virtual environment
On macOS/Linux:


source venv/bin/activate
On Windows:

venv\Scripts\activate
📦 Install dependencies

pip install -r requirements.txt
🔐 Set up environment variables
Create a .env file in the root directory and add your OpenRouter API key:


OPENROUTER_API_KEY=your_openrouter_api_key_here
📁 Project Structure

.
├── main.py               # Main script to run the assistant
├── .env                  # Contains OpenRouter API Key
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
▶️ How to Use
Run the main script:

python main.py
Example query:


What is the capital of Nepal?
Example output:

{
  "topic": "Capital of Nepal",
  "summary": "Kathmandu is the capital and largest city of Nepal...",
  "sources": ["https://en.wikipedia.org/wiki/Kathmandu"],
  "tool_used": []
}

🧰 Tools
Currently, no tools are integrated.

To add tools:

Define them using LangChain’s Tool interface

Add them to the tools list

Pass the list into both the agent and executor

Example:


tools = [your_custom_tool]
✅ Requirements
Python 3.8 or higher

OpenRouter API Key

If you are not using requirements.txt, install manually:

pip install langchain langchain-openai python-dotenv pydantic
```
