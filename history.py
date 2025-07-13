import json
import hashlib
import logging
from datetime import datetime, timedelta
from filelock import FileLock
from config import TWEET_HISTORY_FILE, COOLDOWN_DAYS, LOCK_FILE

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