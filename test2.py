import os
import anthropic
from dotenv import load_dotenv
from rag import test_rag
from db import SEARCH

# Load .env variables
# load_dotenv()

def context(user_prompt):
    def handle_get_RAG(key_words):
        res = []
        for x in key_words:
            res.append(str(test_rag(x)).replace("\n", ""))
        return res

    def handle_get_Database(yr, ticker, form_type, form_sec):
        print(f"Searching database for {ticker} {form_type} forms from {yr}")
        res = SEARCH("combined_data.json", form_type, ticker, yr, form_sec) 
        res = str(res).replace("\n", "")
        return res


    tools = [
        {
            "name": "get_RAG",
            "description": '''Search the RAG Database for specific keywords or semantic meaning based on context. 
                Use this whenever the query requires understanding the meaning of words, synonyms, 
                or context beyond exact matches, OR when some database parameters are missing 
                or unclear.''',
            "input_schema": {
                "type": "object",
                "properties": {
                    "key_words": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Only Two relevant keywords as individual elements"
                    }
                },
                "required": ["key_words"]
            }
        },
        {
            "name": "get_Database",
            "description": "Search the database to retrieve based on the following parameters",
            "input_schema": {
                "type": "object",
                "properties": {
                    "year": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of all Years to retrieve the document as individual elements"
                    },
                    "ticker": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Ticker symbol of the company",
                        "enum": ["AAPL", "NVDA", "GOOGL", "AMZN", "META", "MSFT"]
                    },
                    "form_type": {
                        "type": "array",
                        "items": {"type": "string"},
                        "enum": ["10-K", "10-Q", "8-K", "Form3", "Form4", "Form5"],
                        "description": "SEC Filing form type"
                    },
                    "10-K_and_10-Q_section": {
                        "type": "array",
                        "items": {"type": "string"},
                        "enum": ["1", "1A", "1B", "1C", "2", "3", "4", "5", "6", "7", "7A", "8", "9", "9A", "9B", "10", "11", "12", "13", "14", "15",
                                 "part1item1", "part1item2", "part1item3", "part1item4", "part2item1", "part2item1a", "part2item2", "part2item3", 
                                 "part2item4", "part2item5", "part2item6"],
                        "description": "Sections of 10-K and 10-Q to retrieve from"
                    }
                },
                "required": ["ticker", "form_type"]
            }
        }
    ]

    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"You are a data retrieval agent. Based on the user's request, decide whether to search the RAG database or the main Database. User prompt: {user_prompt}"
                }
            ],
            tools=tools
        )

        if response.stop_reason == "tool_use":
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input

                    if tool_name == "get_RAG":
                        return handle_get_RAG(tool_input["key_words"])
                    elif tool_name == "get_Database":
                        year = tool_input.get("year", [])
                        ticker = tool_input["ticker"]
                        form_type = tool_input["form_type"]
                        form_sec = tool_input.get("10-K_and_10-Q_section", [])
                        return handle_get_Database(year, ticker, form_type, form_sec)
                    else:
                        return f"Unknown tool: {tool_name}"
        else:
            return "No tool use detected"

    except Exception as e:
        return f"Error: {e}"