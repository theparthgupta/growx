import random
import logging
import re
from config import groq_client

def generate_tweet_with_groq():
    """Generate a tweet that is natural, human, short, uses line breaks, and never contains dashes or em dashes."""
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
        "Keep it short, ideally around 100 characters, but never long. "
        "Use line breaks for readability, especially after code, tips, or sentences. "
        "Never use dashes or em dashes anywhere in the tweet. "
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
            max_tokens=120,
            top_p=0.95
        )

        generated_tweet = response.choices[0].message.content.strip()

        # Remove quotes and trim
        generated_tweet = generated_tweet.replace('"', '').strip()

        # Remove all dashes and em dashes
        generated_tweet = generated_tweet.replace('—', '').replace('-', '')

        # Add line breaks after code blocks, semicolons, and punctuation for readability
        generated_tweet = re.sub(r'(;|\.|!|\?)\s*', r'\1\n', generated_tweet)
        # Remove extra blank lines
        generated_tweet = re.sub(r'\n+', r'\n', generated_tweet).strip()

        # Only truncate if over 280 chars (Twitter/X hard limit), and do so at a word boundary
        if len(generated_tweet) > 280:
            cutoff = generated_tweet[:280].rstrip()
            if ' ' in cutoff:
                generated_tweet = cutoff[:cutoff.rfind(' ')]
            else:
                generated_tweet = cutoff

        return generated_tweet

    except Exception as e:
        logging.error(f"Error generating tweet with Groq: {e}")
        return None

def enhance_tweet(base_tweet):
    """No hashtags or generic enhancement, just return the tweet as is (per new requirements)."""
    if not base_tweet:
        return None
    return base_tweet 