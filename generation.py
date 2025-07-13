import random
import logging
from config import groq_client

def generate_tweet_with_groq():
    """Generate a tweet that is natural, human, under 100 characters, and interesting/useful about tech."""
    # List of interesting, non-generic, useful tech topics
    topics = [
        "A shortcut or trick in a popular programming language",
        "A surprising use of a common tool (like git, VSCode, Docker, etc.)",
        "A real-world lesson learned from debugging",
        "A productivity hack for devs that isn't widely known",
        "A myth about software development that wastes time",
        "A small but powerful open-source tool",
        "A counterintuitive fact about databases or APIs",
        "A quick tip for making code more readable",
        "A security gotcha that most devs miss",
        "A way to automate a boring dev task"
    ]
    selected_topic = random.choice(topics)

    system_prompt = (
        "You are a real, human software engineer. "
        "Write a tweet that is NOT generic, does NOT use any template or repeated prefix, and sounds like a quick, natural thought. "
        "Keep it under 100 characters. "
        "Use double spaces between sentences for readability and don't use dashes or em dashes between words. "
        "Share something interesting, useful, or surprising about tech, programming, or dev life. "
        "No cliches, no corporate speak, no hashtags, no intros like 'Pro tip:' or 'Did you know'. "
        "Just a punchy, human, useful or surprising insight."
    )

    user_prompt = (
        f"Write a tweet about: {selected_topic}"
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.95,
            max_tokens=80,
            top_p=0.95
        )

        generated_tweet = response.choices[0].message.content.strip()

        # Remove quotes and trim
        generated_tweet = generated_tweet.replace('"', '').strip()

        # Add double spaces between sentences
        generated_tweet = generated_tweet.replace('. ', '.  ')

        # Truncate to 100 characters
        if len(generated_tweet) > 100:
            generated_tweet = generated_tweet[:100].rstrip('. ')

        return generated_tweet

    except Exception as e:
        logging.error(f"Error generating tweet with Groq: {e}")
        return None

def enhance_tweet(base_tweet):
    """No hashtags or generic enhancement, just return the tweet as is (per new requirements)."""
    if not base_tweet:
        return None
    return base_tweet 