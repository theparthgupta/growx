import os
import tweepy
from dotenv import load_dotenv
from groq import Groq
import logging

# Configure logging
logging.basicConfig(filename='tweet_bot.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# X API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Validate environment variables
required_vars = [API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, GROQ_API_KEY]
if not all(required_vars):
    logging.error("Missing required environment variables")
    raise ValueError("Missing required environment variables")

# Initialize X API client
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Constants
TWEET_HISTORY_FILE = "tweet_history.json"
COOLDOWN_DAYS = 30
LOCK_FILE = "tweet_history.json.lock" 