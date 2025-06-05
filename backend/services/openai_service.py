from dotenv import load_dotenv
import os
import openai
from backend.services.weather_service import get_weather
from backend.services.db_service import get_flights, save_booking, connect
from backend.utils import read_faq
from backend.utils import web_search
import string

load_dotenv()

def clean_param(param):
    return param.translate(str.maketrans('', '', string.punctuation)).strip()


api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Missing OPENAI_API_KEY environment variable")

openai.api_key = api_key

def extract_city(prompt: str) -> str:
    words = prompt.lower().split()
    for i, word in enumerate(words):
        if word in ["in", "at"] and i + 1 < len(words):
            return words[i + 1].capitalize()
    return ""

def extract_flight_details(prompt: str):
    words = prompt.lower().split()
    try:
        from_index = words.index("from")
        to_index = words.index("to")
        date_index = words.index("on")
        departure = words[from_index + 1].upper()
        destination = words[to_index + 1].upper()
        date = words[date_index + 1]
        return departure, destination, date
    except Exception:
        return None, None, None

def extract_name_email(prompt: str):
    try:
        lower_prompt = prompt.lower()
        name_start = lower_prompt.index("my name is") + len("my name is")
        email_start = lower_prompt.index("email is")
        name = prompt[name_start:email_start].replace("and", "").strip()
        email = prompt[email_start + len("email is"):].strip()
        return name, email
    except Exception:
        return None, None

def ask_openai(prompt: str) -> str:
    prompt_lower = prompt.lower()

    # Handle weather queries
    if "weather" in prompt_lower:
        city = clean_param(extract_city(prompt))
        if city:
            return get_weather(city)
        return "Please specify a city like 'weather in Paris'."

    # Handle flight booking
    if all(k in prompt_lower for k in ["book", "flight", "from", "to", "on"]):
        print("Booking intent detected!")
        departure, destination, date = clean_param(extract_flight_details(prompt))

        if not all([departure, destination, date]):
            return "Please provide booking details in this format: 'Book flight from LK to LA on 2025-06-10'"
        results = get_flights(departure, destination, date)
        if not results:
            return f"No available flights from {departure} to {destination} on {date} to book."
        flight = results[0]
        return (
            f"Found flight {flight[4]} on {date} at {flight[5]}.\n"
            "Please provide your **name** and **email** to complete the booking."
        )

    # Handle general flight search
    if all(k in prompt_lower for k in ["flight", "from", "to", "on"]):
        departure, destination, date = extract_flight_details(prompt)
        if not all([departure, destination, date]):
            return "Please use the format: 'flight from XXX to YYY on YYYY-MM-DD'."
        results = get_flights(departure, destination, date)
        if not results:
            return f"No flights found from {departure} to {destination} on {date}."
        flights_info = "\n".join([f"{r[4]} at {r[5]}" for r in results])
        return f"Flights from {departure} to {destination} on {date}:\n{flights_info}"

    # Handle name and email for booking
    if "my name is" in prompt_lower and "email is" in prompt_lower:
        name, email = extract_name_email(prompt)
        if not name or not email:
            return "Please provide name and email clearly like: 'My name is Prarthana and my email is prarthana@example.com'."
        try:
            conn = connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM flights ORDER BY id DESC LIMIT 1")
            flight_id = cursor.fetchone()[0]
            save_booking(name, email, flight_id)
            return f"Booking confirmed for {name} ({email}) on flight ID {flight_id}."
        except Exception as e:
            print(f"Booking final step error: {e}")
            return "Booking failed. Please try again later."

    # Handle airline FAQs
    if any(k in prompt_lower for k in ["baggage", "cancellation", "check-in"]):
        faq = read_faq()
        messages = [
            {"role": "system", "content": "You are a helpful assistant answering airline FAQs from a document."},
            {"role": "user", "content": f"Based on this document:\n{faq}\n\nAnswer this question:\n{prompt}"}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message['content']

    #handle web search for attractions
    if "attractions" in prompt.lower() or "things to do" in prompt.lower() or "places to visit" in prompt.lower():
        search_results = web_search(prompt)
        return f"Here are the top results I found online:\n\n{search_results}"


    # Fallback to ChatGPT
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful airline assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response['choices'][0]['message']['content'].strip()
