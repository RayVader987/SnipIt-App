import wikipedia
import mysql.connector
from mysql.connector import Error
import google.generativeai as genai
from twilio.rest import Client
import inflect
import requests
from datetime import datetime
import speech_recognition as sr
import pyttsx3

# === CONFIGURE GEMINI ===
genai.configure(api_key="enter your gemini api key here")    ##Replace with GEMINI API here
model = genai.GenerativeModel("gemini-2.5-flash")

# === CONFIGURE TWILIO ===
account_sid = "enter your twilio account_sid"
auth_token = "enter the auth toke"
twilio_client = Client(account_sid, auth_token)
twilio_phone = "enter the twilio phone number generated here"
your_phone = "enter your number where you want to receive the notification here"

# === CONFIGURE NEWS API ===
NEWS_API_KEY = "enter api generated from new api website"    ##Replace with api generated from newsapi website

# === CONNECT TO MYSQL ===
try:
    db = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="enter your MySQL password here",
        database="wikipedia_db"
    )
except Error as err:
    print("Database connection failed:", err)
    exit()

cursor = db.cursor()
p = inflect.engine()

# === INIT TEXT-TO-SPEECH ENGINE ===
engine = pyttsx3.init()
engine.setProperty('rate', 170)

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return ""
        except sr.RequestError:
            print("Could not request results; check your internet.")
            return ""

def normalize_topic_strict(text):
    text = text.lower().replace(" ", "")
    singular = p.singular_noun(text)
    return singular if singular else text

def send_sms_notification(message_text):
    try:
        message = twilio_client.messages.create(
            body=message_text,
            from_=twilio_phone,
            to=your_phone
        )
        print("SMS notification sent.")
    except Exception as sms_error:
        print("Failed to send SMS:", sms_error)

def store_news_to_db(topic, title, description, source, url, published_at):
    insert_query = """
        INSERT INTO news_log (topic, title, description, source, url, published_at)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (topic, title, description, source, url, published_at))
    db.commit()
    send_sms_notification(f"News on '{topic}' inserted into the news database.")

def get_latest_news(topic):
    normalized_topic = normalize_topic_strict(topic)
    cursor.execute("SELECT topic FROM news_log")
    existing = [normalize_topic_strict(row[0]) for row in cursor.fetchall()]
    if normalized_topic in existing:
        print("\nThis news topic already exists in the database. Skipping insert.")
        return

    url = "https://newsapi.org/v2/everything"
    params = {
        'q': topic,
        'sortBy': 'publishedAt',
        'pageSize': 1,
        'apiKey': NEWS_API_KEY
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        if data.get("status") == "ok" and data["articles"]:
            article = data["articles"][0]
            title = article["title"]
            desc = article["description"]
            source = article["source"]["name"]
            url_link = article["url"]
            published = article["publishedAt"]

            print("\n[Latest News]")
            print("Title      :", title)
            print("Source     :", source)
            print("Published  :", published)
            print("Summary    :", desc)
            print("URL        :", url_link)

            speak(f"Here's the latest news on {topic}. Title: {title}. Summary: {desc}.")

            published_dt = datetime.strptime(published, "%Y-%m-%dT%H:%M:%SZ")
            store_news_to_db(normalized_topic, title, desc, source, url_link, published_dt)
            print("News saved to database.")
        else:
            print("No recent news found for this topic.")
    except Exception as e:
        print("Failed to fetch news:", e)

# === USER INTERFACE ===
print("\nWhat would you like to do?")
print("1. Wikipedia-style Summary")
print("2. Latest News")
choice = input("Enter your choice (1 or 2): ").strip()

use_audio = input("Do you want to speak the topic instead of typing? (yes/no): ").strip().lower() == "yes"

if choice == "1":
    topic = listen() if use_audio else input("Enter a topic to search: ")
    normalized_input = normalize_topic_strict(topic)

    cursor.execute("SELECT topic FROM wiki_summary")
    existing_topics = cursor.fetchall()
    duplicate_found = any(normalize_topic_strict(row[0]) == normalized_input for row in existing_topics)

    if duplicate_found:
        print("\nTopic already exists in the database. Skipping insert.")
    else:
        try:
            summary = wikipedia.summary(topic, sentences=3)
            print("\n[Wikipedia]")
        except Exception:
            try:
                prompt = f"Give me a short and informative summary of the topic '{topic}'."
                response = model.generate_content(prompt)
                summary = response.text.strip()
                print("\n[Gemini AI]")
            except Exception as e:
                print("Gemini API failed:", e)
                summary = "Summary not available."

        print("Topic  :", topic)
        print("Summary:", summary)

        speak(f"Here's the summary for {topic}. {summary}")

        if summary.strip().lower() != "summary not available.":
            insert_query = "INSERT INTO wiki_summary (topic, summary) VALUES (%s, %s)"
            cursor.execute(insert_query, (normalized_input, summary))
            db.commit()
            send_sms_notification(f"New summary for '{topic}' added to database.")

elif choice == "2":
    news_topic = listen() if use_audio else input("Enter the news topic: ")
    get_latest_news(news_topic)

else:
    print("Invalid choice. Exiting.")

cursor.close()
db.close()
