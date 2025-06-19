# SnipIt-App
This Python-based application allows users to get summaries from Wikipedia or the latest news articles on any topic using either **typed** or **voice input**. It stores the summaries in a **MySQL database** and sends **SMS alerts** upon successful entries. If Wikipedia fails, it uses **Gemini AI** to generate summaries as a fallback.

## Features

✅ **Voice & Text Input Support**  
✅ **Wikipedia Summary** with fallback to **Gemini AI**  
✅ **Latest News Fetching** via News API  
✅ **Avoids Duplicates** (checks if topic already stored)  
✅ **Stores Data in MySQL Database**  
✅ **SMS Alerts via Twilio** for new entries  
✅ **Text-to-Speech Output**

---

## Technologies Used

- Python 3.x  
- [Wikipedia API](https://pypi.org/project/wikipedia/)  
- [Google Gemini AI (GenerativeAI)](https://ai.google.dev/)  
- [NewsAPI.org](https://newsapi.org/)  
- [Twilio API](https://www.twilio.com/) for SMS  
- SpeechRecognition (voice input)  
- pyttsx3 (voice output)  
- MySQL Database  

---

## Prerequisites

- Python 3.8+
- MySQL Server
- API keys:
  - OpenAI/Google Gemini API Key
  - Twilio Account SID, Auth Token, and Phone Number
  - NewsAPI Key

---

## API Setup

### 1. Wikipedia — No setup needed  
### 2. [Gemini API](https://ai.google.dev/)
Replace:
```python
genai.configure(api_key="YOUR_GEMINI_API_KEY")
```

### 3. Twilio API
```python
account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"
twilio_phone = "YOUR_TWILIO_PHONE"
your_phone = "YOUR_RECEIVER_PHONE"
```

### 4. News API
```python
NEWS_API_KEY = "YOUR_NEWS_API_KEY"
```

## Database Setup
### 1. Create database and tables:
```sql
CREATE DATABASE wikipedia_db;
USE wikipedia_db;

CREATE TABLE wiki_summary (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(255),
    summary TEXT
);

CREATE TABLE news_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(255),
    title TEXT,
    description TEXT,
    source VARCHAR(255),
    url TEXT,
    published_at DATETIME
);
```

### 2. Install dependencies
```bash
pip install wikipedia mysql-connector-python google-generativeai twilio inflect requests speechrecognition pyttsx3
```

## How to Run 
```python
python filename.py
```

## App Flow
### 1. Choose between:
  #### 1 → Wikipedia Summary
  #### 2 → Latest News

### 2. Choose if you want to use voice input or type
App checks for duplicates in the database

If new:
Summary/news is fetched

### 3. Stored in database

### 4. SMS sent via Twilio

### 5. Text-to-speech reads out summary


## Created By-
## Raima Deb
### 2nd-Year Computer Science Student
### With ❤️ and curiosity for AI, APIs, and Automation


