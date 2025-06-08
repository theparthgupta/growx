import tweepy
from dotenv import load_dotenv
import os
import random
import json
from datetime import datetime, timedelta
import hashlib
import groq

# Load environment variables
load_dotenv()

# X API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize X API client
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Initialize Groq client
groq_client = groq.Client(api_key=GROQ_API_KEY)

# Tweet history tracking
TWEET_HISTORY_FILE = "tweet_history.json"
COOLDOWN_DAYS = 30  # Don't repeat tweets for 30 days

def load_tweet_history():
    """Load previously posted tweets"""
    try:
        with open(TWEET_HISTORY_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"posted_tweets": [], "last_cleanup": str(datetime.now())}

def save_tweet_history(history):
    """Save tweet history to file"""
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
    """Generate hash for tweet to check duplicates"""
    clean_tweet = ' '.join(tweet_content.split()).replace('#', '').lower()
    return hashlib.md5(clean_tweet.encode()).hexdigest()

def is_tweet_recent(tweet_content, history):
    """Check if similar tweet was posted recently"""
    tweet_hash = get_tweet_hash(tweet_content)
    
    for posted_tweet in history["posted_tweets"]:
        if posted_tweet["hash"] == tweet_hash:
            return True
    return False

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
    """Generate a tweet using Groq API"""
    prompts = [
        "Write a concise, insightful tweet about a breakthrough in AI or technology. Include a surprising fact or statistic. Keep it under 200 characters to leave room for hashtags.",
        "Create an engaging tweet about the future of technology that includes a thought-provoking question. Keep it under 200 characters to leave room for hashtags.",
        "Write a tweet about a recent tech innovation that could change our lives. Include one specific example. Keep it under 200 characters to leave room for hashtags.",
        "Create a tweet about programming or software development that shares a valuable insight or tip. Keep it under 200 characters to leave room for hashtags.",
        "Write a tweet about the intersection of technology and society that makes people think. Include a compelling observation. Keep it under 200 characters to leave room for hashtags."
    ]
    
    prompt = random.choice(prompts)
    
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": """You are a tech thought leader who writes engaging, insightful tweets. Follow these rules:
1. Keep tweets under 200 characters to leave room for hashtags
2. Include specific facts, statistics, or examples
3. Make content informative and valuable
4. Use clear, concise language
5. End with a thought-provoking point or question
6. Do not include hashtags in the main tweet text"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=100,
            top_p=0.9
        )
        
        generated_tweet = completion.choices[0].message.content.strip()
        
        # Clean up the tweet
        generated_tweet = generated_tweet.replace('"', '').replace('"', '')
        if generated_tweet.startswith('"') and generated_tweet.endswith('"'):
            generated_tweet = generated_tweet[1:-1]
            
        # Ensure the tweet is not too long
        if len(generated_tweet) > 200:
            # Try to cut at a sentence boundary
            sentences = generated_tweet.split('. ')
            shortened_tweet = sentences[0]
            if len(shortened_tweet) > 200:
                # If still too long, cut at word boundary
                words = shortened_tweet.split()
                shortened_tweet = ' '.join(words[:30])  # Approximate 200 chars
            generated_tweet = shortened_tweet.strip()
        
        return generated_tweet
        
    except Exception as e:
        print(f"Error generating tweet with Groq: {e}")
        return None

def enhance_tweet(base_tweet):
    """Add appropriate hashtags and ensure quality"""
    if not base_tweet:
        return None
        
    # Smart hashtag selection based on content
    hashtags = []
    
    # Tech and AI related
    if any(word in base_tweet.lower() for word in ['ai', 'artificial intelligence', 'machine learning', 'algorithm', 'neural', 'model']):
        hashtags.extend(['#AI', '#MachineLearning', '#TechInnovation'])
    
    # Programming related
    if any(word in base_tweet.lower() for word in ['code', 'programming', 'developer', 'software', 'debug', 'algorithm']):
        hashtags.extend(['#Programming', '#SoftwareDev', '#Coding'])
    
    # Future and innovation
    if any(word in base_tweet.lower() for word in ['future', 'innovation', 'breakthrough', 'disrupt', 'transform']):
        hashtags.extend(['#FutureTech', '#Innovation', '#TechTrends'])
    
    # Business and startup
    if any(word in base_tweet.lower() for word in ['startup', 'entrepreneur', 'business', 'market', 'industry']):
        hashtags.extend(['#Startup', '#TechBusiness', '#Entrepreneurship'])
    
    # Ethics and society
    if any(word in base_tweet.lower() for word in ['ethics', 'privacy', 'security', 'society', 'impact']):
        hashtags.extend(['#TechEthics', '#DigitalEthics', '#TechImpact'])
    
    # Default hashtags if none matched
    if not hashtags:
        hashtags = ['#Tech', '#Innovation', '#Future']
    
    # Limit hashtags to avoid spam appearance
    hashtags = hashtags[:3]
    
    # Construct final tweet
    hashtag_string = ' '.join(set(hashtags))  # Remove duplicates
    final_tweet = f"{base_tweet} {hashtag_string}"
    
    # Ensure under 280 characters
    if len(final_tweet) > 280:
        available_chars = 280 - len(hashtag_string) - 1
        final_tweet = f"{base_tweet[:available_chars].strip()} {hashtag_string}"
    
    return final_tweet

def main():
    # Load and clean tweet history
    history = load_tweet_history()
    history = clean_old_history(history)
    
    max_attempts = 3  # Maximum number of attempts to generate a unique tweet
    attempts = 0
    
    while attempts < max_attempts:
        base_tweet = generate_tweet_with_groq()
        if not base_tweet:
            print("Failed to generate tweet, trying again...")
            attempts += 1
            continue
            
        final_tweet = enhance_tweet(base_tweet)
        
        # Check if final tweet is too similar to recent tweets
        if not is_tweet_recent(final_tweet, history):
            break
        
        print(f"Attempt {attempts + 1}: Generated tweet too similar to recent post, trying again...")
        attempts += 1
    
    if attempts == max_attempts:
        print("Warning: Could not generate a unique tweet after maximum attempts")
        return
    
    # Post the tweet
    try:
        client.create_tweet(text=final_tweet)
        
        # Add to history after successful post
        history = add_tweet_to_history(final_tweet, history)
        save_tweet_history(history)
        
        print(f"Tweet posted successfully: {final_tweet}")
        print(f"Total tweets in history: {len(history['posted_tweets'])}")
        
    except Exception as e:
        print(f"Error posting tweet: {e}")
        print(f"Attempted tweet: {final_tweet}")

if __name__ == "__main__":
    main()
