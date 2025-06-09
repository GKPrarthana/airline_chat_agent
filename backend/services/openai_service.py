from dotenv import load_dotenv
import os
import openai
import re
import json
 
from backend.services.weather_service import get_weather as actual_get_weather
from backend.services.db_service import get_flights as actual_get_flights, save_booking as actual_save_booking
from backend.utils import read_faq as actual_search_policy_document # Renaming for clarity if tool name differs
from backend.utils import web_search as actual_web_search
 
# --- Constants ---
OPENAI_MODEL = "gpt-4o-mini"

# --- Main Application ---

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")
openai.api_key = api_key

# 1. Define the tools (functions) available to the model
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather forecast for a specific city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string", "description": "The city name, e.g., 'New York'"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_flights",
            "description": "Get available flights for a given route and date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "departure": {"type": "string", "description": "The departure city code, e.g., 'LK'"},
                    "destination": {"type": "string", "description": "The destination city code, e.g., 'LA'"},
                    "date": {"type": "string", "description": "The departure date in YYYY-MM-DD format."},
                },
                "required": ["departure", "destination", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_booking",
            "description": "Save a flight booking after getting passenger details.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The full name of the passenger."},
                    "email": {"type": "string", "description": "The email address of the passenger."},
                    "flight_id": {"type": "string", "description": "The ID of the flight to book."},
                },
                "required": ["name", "email", "flight_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_policy_document",
            "description": "Search the airline's policy document for information on topics like baggage or cancellations.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The user's question about airline policy."}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for information about tourist attractions or activities at a destination.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The user's search query."}},
                "required": ["query"],
            },
        },
    },
]

# 2. Map function names to the actual Python functions
function_map = {
    "get_weather": actual_get_weather,
    "get_flights": actual_get_flights,
    "save_booking": actual_save_booking,
    "search_policy_document": actual_search_policy_document,
    "web_search": actual_web_search,
}

# 3. Main function to handle the conversation
def ask_agent(prompt: str, conversation_history: list = None):
    """
    Handles a user's prompt, maintains conversation history, and calls tools as needed.
    """
    if conversation_history is None:
        conversation_history = [
            {"role": "system", "content": "You are a friendly and helpful airline customer service agent. You must use the provided tools to answer user questions about weather, flights, policies, and destinations. When a user expresses intent to book a specific flight, first confirm the flight details with them. If the user confirms and provides their name and email (or if you need to ask for these details and they subsequently provide them), you must then use the 'save_booking' tool. Ensure you use the passenger's name, their email, and the correct flight_id (this is usually the flight number discussed earlier in the conversation) when calling 'save_booking'. You need to remember the flight_id from the earlier parts of the conversation to complete the booking."},
        ]

    conversation_history.append({"role": "user", "content": prompt})

    try:
        # First API call to determine if a tool should be used
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=conversation_history,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response["choices"][0]["message"]

        # Check if the model wants to call one or more tools
        if response_message.get("tool_calls"):
            tool_calls = response_message["tool_calls"]
            conversation_history.append(response_message)  # Add model's turn to history

            # Execute all tool calls
            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                function_to_call = function_map.get(function_name)
                
                if function_to_call:
                    function_args = json.loads(tool_call["function"]["arguments"])
                    function_response = function_to_call(**function_args)
                    
                    # Add the tool's response to the conversation history
                    conversation_history.append({
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    })
            
            # Second API call to generate a natural language response based on the tool's output
            final_response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=conversation_history,
            )
            final_message = final_response["choices"][0]["message"]["content"]
            conversation_history.append({"role": "assistant", "content": final_message})
            return final_message, conversation_history

        # If no tool is called, return the model's direct response
        else:
            direct_response = response_message["content"]
            conversation_history.append({"role": "assistant", "content": direct_response})
            return direct_response, conversation_history

    except Exception as e:
        print(f"An error occurred: {e}")
        return "Sorry, I encountered an error. Please try again.", conversation_history

# --- Example Usage ---
if __name__ == "__main__":
    # --- Example 1: Weather Query ---
    print("--- 1. Weather Query ---")
    response, history = ask_agent("What's the weather like in New York tomorrow?")
    print(f"Agent: {response}\n")

    # --- Example 2: Flight Search ---
    print("--- 2. Flight Search ---")
    response, history = ask_agent("What flights are available from LK to LA on June 10, 2025?")
    print(f"Agent: {response}\n")
    
    # --- Example 3: Multi-turn Booking ---
    print("--- 3. Multi-turn Booking ---")
    # The user first asks to book a flight without providing details
    response, history = ask_agent("Great, please book flight LKLA001 for me.", conversation_history=history)
    print(f"Agent: {response}\n")
    # The user provides the details in the next turn
    response, history = ask_agent("My name is John Doe and my email is john.doe@example.com", conversation_history=history)
    print(f"Agent: {response}\n")

    # --- Example 4: Policy Question ---
    print("--- 4. Policy Question ---")
    response, history = ask_agent("What is the baggage limit for international flights?")
    print(f"Agent: {response}\n")

    # --- Example 5: Web Search ---
    print("--- 5. Web Search ---")
    response, history = ask_agent("What are some tourist attractions in LA?")
    print(f"Agent: {response}\n")