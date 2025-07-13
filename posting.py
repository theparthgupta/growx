import logging
import tweepy
from config import client
from history import load_tweet_history, save_tweet_history, clean_old_history, is_tweet_recent, add_tweet_to_history
from generation import generate_tweet_with_groq, enhance_tweet

def post_tweet(tweet_content):
    """Post a tweet to X/Twitter"""
    try:
        client.create_tweet(text=tweet_content)
        logging.info(f"Tweet posted successfully: {tweet_content}")
        return True
    except tweepy.TweepyException as e:
        logging.error(f"Error posting tweet: {e}")
        logging.error(f"Attempted tweet: {tweet_content}")
        return False

def generate_and_post_tweet():
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
        return False
    
    # Post the tweet
    if post_tweet(final_tweet):
        # Add to history after successful post
        history = add_tweet_to_history(final_tweet, history)
        save_tweet_history(history)
        logging.info(f"Total tweets in history: {len(history['posted_tweets'])}")
        return True
    
    return False 