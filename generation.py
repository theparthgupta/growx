import random
import logging
from config import groq_client

def generate_tweet_with_groq():
    """Generate a tweet that sounds personal and human."""
    styles = [
        "Bold hot take + a follow-up punch",
        "Relatable dev L + ironic twist",
        "Random rant + actual insight",
        "Curious founder thought + subtle sarcasm",
        "Midnight shower thought + code pain",
        "Petty tech gripe + overreaction"
    ]

    topics = [
        "frameworks that waste time",
        "when AI tools gaslight devs",
        "tech that looks cool but solves nothing",
        "shipping MVPs just to feel productive",
        "writing code that works but feels cursed",
        "the lies in job descriptions vs reality",
        "building in public with no audience yet",
        "why CORS exists just to hurt us",
        "startups naming bugs as features",
        "self-hosted tools that ruin your weekend"
    ]

    tone_prefixes = [
        "Not to sound bitter, but ",
        "Can we talk about how ",
        "Unpopular opinion: ",
        "I might delete this later but ",
        "Tell me I'm wrong: ",
        "Dev confession: ",
        "Been thinking about this — ",
    ]

    selected_style = random.choice(styles)
    selected_topic = random.choice(topics)
    selected_prefix = random.choice(tone_prefixes)

    system_prompt = (
        "You're a sarcastic yet insightful software engineer tweeting as a real person, not a brand. "
        "Style: short, edgy, human, not polished, not corporate. Be smart but not preachy. Swear mildly if it feels natural. "
        "Make the reader chuckle, nod or argue. Under 160 characters max."
        "You're a sarcastic dev/founder tweeting brutally honest, sometimes spicy takes on coding, AI, side projects, and building in public. "
        "Your tweets feel like: hot takes, coding pain, dumb ideas that worked, dev chaos, and late-night builds. "
        "Use informal tone, dev slang, unfinished thoughts if needed, lowercase is okay. Aim for <150 characters. "
        "Write like you're talking to other devs, founders, and internet friends. Don't explain too much. Be punchy."
    )

    user_prompt = (
        f"Write a tweet in the style of: {selected_style}, about: {selected_topic}. "
        f"Start with: '{selected_prefix}'"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.95,
            max_tokens=120,
            top_p=0.95
        )

        generated_tweet = response.choices[0].message.content.strip()

        # Basic cleanup
        generated_tweet = generated_tweet.replace('"', '').strip()

        # Truncate if too long
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
        'ai': ['#buildinpublic', '#AIhumor', '#AIMemes', '#LLMthings'],
        'programming': ['#devhumor', '#techtwitter', '#100DaysOfCode', '#showerthoughts'],
        'future': ['#indiehacker', '#web3ishard', '#startuplife'],
        'business': ['#founderlife', '#nocode', '#bootstrap'],
        'ethics': ['#techethics', '#AIethics', '#digitalrights']
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