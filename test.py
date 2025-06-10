import tweepy
from dotenv import load_dotenv
import os
import random
import json
from datetime import datetime, timedelta
import hashlib
import logging
from filelock import FileLock
from groq import Groq  # Updated import for groq==0.9.0

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

# Tweet history tracking
TWEET_HISTORY_FILE = "tweet_history.json"
COOLDOWN_DAYS = 30
LOCK_FILE = "tweet_history.json.lock"

def load_tweet_history():
    """Load previously posted tweets with file locking"""
    with FileLock(LOCK_FILE):
        try:
            with open(TWEET_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"posted_tweets": [], "last_cleanup": str(datetime.now())}

def save_tweet_history(history):
    """Save tweet history to file with file locking"""
    with FileLock(LOCK_FILE):
        with open(TWEET_HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=2)

def clean_old_history(history):
    """Remove tweets older than cooldown period"""
    cutoff_date = datetime.now() - timedelta(days=COOLDOWN_DAYS)
    history["posted_tweets"] = [
        tweet for tweet in history["posted_tweets"]
        if datetime.fromisoformat(tweet["date"]) > cutoff_date
    ]
    history["last_cleanup"] = str(datetime.now())
    return history

def get_tweet_hash(tweet_content):
    """Generate SHA-256 hash for tweet to check duplicates"""
    clean_tweet = ' '.join(tweet_content.split()).replace('#', '').lower()
    return hashlib.sha256(clean_tweet.encode()).hexdigest()

def is_tweet_recent(tweet_content, history):
    """Check if similar tweet was posted recently"""
    tweet_hash = get_tweet_hash(tweet_content)
    return any(posted_tweet["hash"] == tweet_hash for posted_tweet in history["posted_tweets"])

def add_tweet_to_history(tweet_content, history):
    """Add posted tweet to history"""
    tweet_hash = get_tweet_hash(tweet_content)
    history["posted_tweets"].append({
        "hash": tweet_hash,
        "content": tweet_content[:100] + "..." if len(tweet_content) > 100 else tweet_content,
        "date": str(datetime.now())
    })
    return history

def generate_tweet_with_groq():
    """Generate a high-engagement tweet using Groq"""
    styles = [
        "Surprising fact + insight + question",
        "Contrarian opinion + example + challenge",
        "Mini story + lesson + question",
        "Bold prediction + why + CTA",
        "Metaphor or analogy + insight + takeaway",
        "Frustration + insight + mini-solution",
        "Common developer mistake + how to avoid it",
        "Unpopular opinion + short explanation + invitation to discuss",
        "Real-world example + micro-lesson",
        "Better alternative to common tools + quick use-case",
        "Quick fix for a dev error + why it works",
        "Relatable dev struggle + emotional hook"
    ]

    topics = [
        "AI and its real-world use cases",
        "how AI is transforming daily life or work",
        "common misconceptions in tech or startups",
        "how developers can grow faster",
        "what most people miss about innovation",
        "what the future of work with AI could look like",
        "how to build in public or share progress",
        "problems developers face while building side projects",
        "frameworks or stacks that simplify product building",
        "common tech errors devs face (e.g., CORS, env config, dependency hell)",
        "which tools are overrated in dev workflow",
        "how small teams can ship faster without overengineering",
        "real reasons why most MVPs fail",
        "self-hosted vs SaaS solutions: pros and cons",
        "productive habits or shortcuts developers actually use",
        "tech stacks that feel simple but scale well",
        "when to ditch your current stack for something better"
    ]

    selected_style = random.choice(styles)
    selected_topic = random.choice(topics)

    system_prompt = (
        "You're a tech thought leader writing engaging tweets. Your tone is clear, clever, and thought-provoking. "
        "Structure tweets in this format:\n"
        "- Hook (question, stat, bold statement)\n"
        "- Insight or example\n"
        "- End with a question or reflective CTA\n"
        "Keep tweets under 200 characters. No hashtags. Avoid generic or robotic phrasing. Use natural, casual tone."
    )

    user_prompt = f"Write a tweet in the style of: {selected_style}, about: {selected_topic}."

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.8,
            max_tokens=120,
            top_p=0.95
        )

        generated_tweet = response.choices[0].message.content.strip()

        # Basic cleanup
        generated_tweet = generated_tweet.replace('"', '').strip()

        # Truncate if needed
        if len(generated_tweet) > 200:
            sentences = generated_tweet.split('. ')
            for s in sentences:
                if len(s) < 200:
                    generated_tweet = s.strip()
                    break
            else:
                generated_tweet = generated_tweet[:200]

        return generated_tweet

    except Exception as e:
        logging.error(f"Error generating tweet with Groq: {e}")
        return None


def enhance_tweet(base_tweet):
    """Add appropriate hashtags and ensure quality"""
    if not base_tweet:
        return None
        
    hashtag_groups = {
        'ai': ['#AI', '#MachineLearning', '#TechInnovation'],
        'programming': ['#Programming', '#SoftwareDev', '#Coding'],
        'future': ['#FutureTech', '#Innovation', '#TechTrends'],
        'business': ['#Startup', '#TechBusiness', '#Entrepreneurship'],
        'ethics': ['#TechEthics', '#DigitalEthics', '#TechImpact']
    }
    
    hashtags = set()
    base_tweet_lower = base_tweet.lower()
    
    # Select hashtags based on content
    if any(word in base_tweet_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 'neural', 'model']):
        hashtags.update(hashtag_groups['ai'])
    if any(word in base_tweet_lower for word in ['code', 'programming', 'developer', 'software', 'debug', 'algorithm']):
        hashtags.update(hashtag_groups['programming'])
    if any(word in base_tweet_lower for word in ['future', 'innovation', 'breakthrough', 'disrupt', 'transform']):
        hashtags.update(hashtag_groups['future'])
    if any(word in base_tweet_lower for word in ['startup', 'entrepreneur', 'business', 'market', 'industry']):
        hashtags.update(hashtag_groups['business'])
    if any(word in base_tweet_lower for word in ['ethics', 'privacy', 'security', 'society', 'impact']):
        hashtags.update(hashtag_groups['ethics'])
    
    # Default hashtags if none matched
    if not hashtags:
        hashtags = {'#Tech', '#Innovation', '#Future'}
    
    # Limit to 3 hashtags
    hashtags = list(hashtags)[:3]
    hashtag_string = ' '.join(hashtags)
    
    # Construct final tweet
    final_tweet = f"{base_tweet} {hashtag_string}"
    
    # Ensure under 280 characters
    if len(final_tweet) > 280:
        available_chars = 280 - len(hashtag_string) - 1
        final_tweet = f"{base_tweet[:available_chars].rstrip('.')} {hashtag_string}"
    
    return final_tweet

def main():
    """Main function to generate and post a tweet"""
    logging.info("Starting tweet bot")
    
    # Load and clean tweet history
    history = load_tweet_history()
    history = clean_old_history(history)
    
    max_attempts = 3
    attempts = 0
    
    while attempts < max_attempts:
        base_tweet = generate_tweet_with_groq()
        if not base_tweet:
            logging.warning(f"Attempt {attempts + 1}: Failed to generate tweet")
            attempts += 1
            continue
            
        final_tweet = enhance_tweet(base_tweet)
        if not final_tweet:
            logging.warning(f"Attempt {attempts + 1}: Failed to enhance tweet")
            attempts += 1
            continue
        
        # Check if final tweet is too similar to recent tweets
        if not is_tweet_recent(final_tweet, history):
            break
        
        logging.warning(f"Attempt {attempts + 1}: Generated tweet too similar to recent post")
        attempts += 1
    
    if attempts == max_attempts:
        logging.error("Could not generate a unique tweet after maximum attempts")
        return
    
    # Post the tweet
    try:
        client.create_tweet(text=final_tweet)
        logging.info(f"Tweet posted successfully: {final_tweet}")
        
        # Add to history after successful post
        history = add_tweet_to_history(final_tweet, history)
        save_tweet_history(history)
        logging.info(f"Total tweets in history: {len(history['posted_tweets'])}")
        
    except tweepy.TweepyException as e:
        logging.error(f"Error posting tweet: {e}")
        logging.error(f"Attempted tweet: {final_tweet}")

if __name__ == "__main__":
    main()