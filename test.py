import tweepy
from transformers import pipeline
from dotenv import load_dotenv
import os
import random
import json
from datetime import datetime, timedelta
import hashlib

# Load environment variables
load_dotenv()

# X API credentials
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

# Initialize X API client
client = tweepy.Client(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

# Initialize a better model for tweet generation (consider upgrading to GPT-3.5 or Claude)
generator = pipeline(
    "text-generation",
    model="gpt2-medium",  # Better model than base gpt2
    framework="pt",
    max_length=100,
    num_return_sequences=3,  # Generate multiple options
    do_sample=True,
    top_k=40,
    top_p=0.9,
    temperature=0.7,
    pad_token_id=50256
)

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
    # Remove hashtags and extra spaces for comparison
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

# Expanded curated high-quality tweet templates and prompts
tweet_categories = {
    "philosophical_tech": [
        "The real question isn't whether AI will replace humans, but whether we'll lose our humanity trying to compete with it.",
        "Every algorithm reflects the biases of its creator. The question is: are we ready to face our own reflection?",
        "We're building the future with yesterday's ethics. Time to upgrade our moral operating system.",
        "The most powerful code isn't the one that runs fastest, but the one that serves humanity best.",
        "We're not just building software; we're architecting the future of human interaction.",
        "Technology amplifies human nature—both the good and the ugly. Choose which side you're amplifying.",
        "The scariest part about AI isn't that it might think like us, but that it might think better than us.",
        "We're teaching machines to optimize everything except the things that make life worth living.",
        "Every 'smart' device makes us a little less smart. Convenience has a hidden cost.",
        "The digital divide isn't about access to technology—it's about wisdom to use it well.",
        "We're solving problems with code that we created with code. Maybe we need less code, not more.",
        "The most advanced AI still can't understand why humans cry at movies. That's our superpower.",
        "Technology is neutral, but the systems we build with it are not. Design with intention.",
        "We're creating tools to make decisions for us, then wondering why we feel powerless.",
        "The future belongs to those who can think critically about the tools they use.",
        "Every notification is a vote for distraction over deep work. Vote wisely.",
        "We measure everything that's easy to measure and ignore everything that matters.",
        "The internet promised infinite knowledge but delivered infinite distraction.",
        "AI will master pattern recognition, but humans will always own pattern breaking.",
        "We're not digital natives—we're digital immigrants learning a foreign language."
    ],
    
    "tech_insights": [
        "The best developers I know spend 80% of their time thinking and 20% coding. Debugging starts in the mind.",
        "Clean code isn't about impressing other developers. It's about respecting future you.",
        "The hardest problems in tech aren't technical—they're human. Psychology > Algorithms.",
        "Every 'revolutionary' technology is just yesterday's science fiction with better marketing.",
        "The most valuable skill in tech isn't coding—it's knowing when NOT to code.",
        "Good code is written for humans, not computers. Compilers don't need comments.",
        "The best architecture is the one you can delete without crying.",
        "Premature optimization is the root of all evil, but so is premature generalization.",
        "Your code will be read 10x more than it's written. Write for the reader.",
        "The senior developer's secret: they've made more mistakes than you've written lines of code.",
        "Documentation is love letters to your future self (and your teammates).",
        "The best debugging tool is still careful thought, not fancy software.",
        "Every abstraction has a cost. Make sure you're paying for value, not complexity.",
        "Ship early, ship often, but never ship broken. Speed without quality is just chaos.",
        "The most expensive code isn't the code you write—it's the code you maintain.",
        "Great developers don't memorize syntax; they understand principles.",
        "Your first solution is rarely your best solution. Iterate, don't stagnate.",
        "The best code is boring code. Excitement belongs in the product, not the implementation.",
        "Testing isn't about finding bugs—it's about designing better systems.",
        "Refactoring is like cleaning your room: painful but necessary."
    ],
    
    "ai_observations": [
        "AI doesn't think like humans. It optimizes like humans wish they could—without emotion, bias, or second-guessing.",
        "The Turing Test is outdated. The real test: can AI help humans become more human?",
        "We're teaching machines to be intelligent, but forgot to teach them wisdom.",
        "AI will automate jobs, but it will also create problems we never knew we had.",
        "The singularity isn't when AI surpasses humans—it's when we can't tell where one ends and the other begins."
    ],
    
    "startup_wisdom": [
        "You don't need a revolutionary idea. You need revolutionary execution of an obvious idea.",
        "The best startups solve problems so obvious that everyone wonders why no one solved them before.",
        "Product-market fit isn't finding customers for your product—it's finding the product your customers desperately need.",
        "Your first hire determines your company culture more than your mission statement ever will.",
        "Most startups fail not because they built the wrong thing, but because they built it for the wrong people."
    ],
    
    "tech_philosophy": [
        "Every line of code is a decision about how the world should work. Choose wisely.",
        "We're not just users of technology—we're inhabitants of digital worlds we collectively create.",
        "The internet promised to connect humanity. Instead, it revealed how disconnected we already were.",
        "Privacy isn't about having something to hide—it's about having something to protect.",
        "The most dangerous code isn't malicious—it's the code that works exactly as intended."
    ]
}

# Dynamic tweet templates that can be customized
dynamic_templates = {
    "tech_opinions": [
        "Hot take: {topic} is {adjective} because {reason}.",
        "Unpopular opinion: The {tech_term} trend is {judgment}, and here's why: {explanation}.",
        "Reality check: {common_belief} is actually {contrarian_view}.",
        "Plot twist: {technology} won't {common_prediction}, it will {alternative_outcome}.",
        "Controversial take: {popular_thing} is {negative_adjective} for {industry}."
    ],
    "learning_insights": [
        "After {time_period} in tech, I've learned that {insight}.",
        "The {skill} you think you need isn't {obvious_skill}—it's {unexpected_skill}.",
        "Mistake I made early in my career: {mistake}. What I do now: {solution}.",
        "If I could teach {target_audience} one thing about {topic}, it would be: {lesson}.",
        "The hardest lesson in {field}: {lesson_learned}."
    ],
    "future_predictions": [
        "In {timeframe}, {technology} will {prediction}, but we're not ready for {consequence}.",
        "The next big thing in {field} isn't {obvious_trend}—it's {surprising_trend}.",
        "By {year}, {current_process} will be replaced by {new_process}, changing {impact_area}.",
        "Everyone thinks {popular_belief}, but actually {contrarian_prediction} will happen first.",
        "The {technology} revolution will start in {unexpected_place}, not {expected_place}."
    ]
}

# Variables to fill templates
template_variables = {
    "topics": ["AI", "blockchain", "cloud computing", "remote work", "automation", "cybersecurity"],
    "adjectives": ["overrated", "underrated", "misunderstood", "revolutionary", "dangerous", "inevitable"],
    "tech_terms": ["microservices", "serverless", "low-code", "web3", "metaverse", "edge computing"],
    "judgments": ["overhyped", "undervalued", "perfectly timed", "premature", "necessary"],
    "time_periods": ["5 years", "a decade", "15 years", "my entire career"],
    "technologies": ["AI", "VR", "blockchain", "quantum computing", "IoT", "5G"],
    "fields": ["programming", "data science", "cybersecurity", "UX design", "DevOps"],
    "years": ["2025", "2026", "2027", "2030"],
    "timeframes": ["5 years", "a decade", "the next few years"]
}

def generate_dynamic_tweet(history):
    """Generate a tweet from dynamic templates"""
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        category = random.choice(list(dynamic_templates.keys()))
        template = random.choice(dynamic_templates[category])
        
        # Fill template with random variables
        filled_template = template
        for var_type, options in template_variables.items():
            if f"{{{var_type}}}" in template:
                filled_template = filled_template.replace(f"{{{var_type}}}", random.choice(options))
        
        # Handle remaining generic placeholders
        generic_replacements = {
            "{reason}": random.choice(["it solves the wrong problem", "it creates more problems than it solves", "nobody asked for it", "the timing is perfect"]),
            "{explanation}": random.choice(["we're solving yesterday's problems", "we're ignoring the human element", "the fundamentals still matter"]),
            "{common_belief}": random.choice(["coding bootcamps guarantee jobs", "AI will replace all developers", "remote work kills innovation"]),
            "{contrarian_view}": random.choice(["more nuanced than that", "completely backwards", "missing the point"]),
            "{common_prediction}": random.choice(["replace humans", "solve everything", "be adopted quickly"]),
            "{alternative_outcome}": random.choice(["augment human creativity", "create new problems", "take decades to mature"]),
            "{popular_thing}": random.choice(["React", "Python", "Agile", "TypeScript", "Docker"]),
            "{negative_adjective}": random.choice(["overused", "misapplied", "cargo-culted"]),
            "{industry}": random.choice(["startups", "enterprise", "education", "healthcare"]),
            "{insight}": random.choice(["simple solutions beat clever ones", "communication matters more than code", "users don't care about your tech stack"]),
            "{skill}": random.choice(["most important skill", "key ability", "crucial talent"]),
            "{obvious_skill}": random.choice(["coding", "algorithms", "frameworks"]),
            "{unexpected_skill}": random.choice(["listening", "saying no", "admitting ignorance"]),
            "{mistake}": random.choice(["chasing the latest framework", "not asking enough questions", "trying to build everything myself"]),
            "{solution}": random.choice(["focus on fundamentals", "ask 'why' three times", "collaborate more"]),
            "{target_audience}": random.choice(["new developers", "founders", "students"]),
            "{topic}": random.choice(["programming", "startups", "AI", "career growth"]),
            "{lesson}": random.choice(["it's not about the code", "users come first", "simple is better"]),
            "{field}": random.choice(["tech", "programming", "startups", "AI"]),
            "{lesson_learned}": random.choice(["perfection is the enemy of progress", "premature optimization kills projects", "users define success, not developers"]),
            "{prediction}": random.choice(["democratize development", "change how we work", "reshape entire industries"]),
            "{consequence}": random.choice(["the ethical implications", "the job displacement", "the security risks"]),
            "{obvious_trend}": random.choice(["more automation", "faster computers", "better frameworks"]),
            "{surprising_trend}": random.choice(["human-centered design", "simplification", "energy efficiency"]),
            "{current_process}": random.choice(["manual testing", "traditional databases", "centralized systems"]),
            "{new_process}": random.choice(["AI-assisted development", "edge computing", "decentralized networks"]),
            "{impact_area}": random.choice(["how we work", "what we build", "who can participate"]),
            "{popular_belief}": random.choice(["AI will replace developers", "remote work is the future", "blockchain solves everything"]),
            "{contrarian_prediction}": random.choice(["human creativity becomes more valuable", "in-person collaboration makes a comeback", "simple solutions win"]),
            "{unexpected_place}": random.choice(["education", "healthcare", "agriculture"]),
            "{expected_place}": random.choice(["Silicon Valley", "big tech companies", "startups"])
        }
        
        for placeholder, replacement in generic_replacements.items():
            if placeholder in filled_template:
                filled_template = filled_template.replace(placeholder, replacement)
        
        # Check if this tweet is too similar to recent ones
        if not is_tweet_recent(filled_template, history):
            return filled_template
        
        attempts += 1
    
    # If all attempts failed, fall back to curated content
    return generate_curated_tweet(history)

# Question-based engaging tweets (expanded)
engaging_questions = [
    "What's the one programming concept you wish you'd learned earlier?",
    "If you could uninvent one technology, what would it be and why?",
    "What's the most overrated trend in tech right now?",
    "Which sci-fi prediction about technology do you think will never happen?",
    "What's one piece of advice you'd give to your past self starting in tech?",
    "If AI could solve one global problem, which would you choose?",
    "What's the most beautiful piece of code you've ever seen?",
    "Which technology breakthrough genuinely surprised you?",
    "What's the biggest misconception people have about working in tech?",
    "If you had to explain the internet to someone from 1950, how would you do it?",
    "What's the worst code you've ever had to maintain?",
    "Which programming language do you think is most misunderstood?",
    "What's the most valuable debugging technique you've learned?",
    "If you could only use one development tool for the rest of your career, what would it be?",
    "What's the biggest lesson you've learned from a failed project?",
    "Which technology do you think peaked and is now declining?",
    "What's the most counterintuitive thing about software development?",
    "If you could add one feature to any programming language, what would it be?",
    "What's the most important skill for a developer that isn't coding?",
    "Which tech prediction from 10 years ago aged the worst?",
    "What's the most elegant solution to a complex problem you've seen?",
    "If you could automate one part of your development workflow, what would it be?",
    "What's the biggest trade-off in software architecture you've had to make?",
    "Which open-source project has had the biggest impact on your career?",
    "What's the most important thing to consider when choosing a tech stack?"
]

# Counter-intuitive insights
contrarian_takes = [
    "Unpopular opinion: The best programmers are lazy. They automate everything because they hate repetitive work.",
    "Hot take: We don't have an AI problem. We have a human problem that we're trying to solve with AI.",
    "Controversial: Most 'disruptive' technologies just make existing inefficiencies more efficient.",
    "Counterpoint: The best code is the code you don't write. Simplicity > Complexity.",
    "Reality check: Your app doesn't need AI. It needs better UX."
]

def generate_curated_tweet(history):
    """Generate a high-quality tweet from curated content, avoiding recent posts"""
    max_attempts = 50  # Prevent infinite loops
    attempts = 0
    
    while attempts < max_attempts:
        category = random.choice(list(tweet_categories.keys()))
        tweet = random.choice(tweet_categories[category])
        
        if not is_tweet_recent(tweet, history):
            return tweet
        
        attempts += 1
    
    # If all curated tweets are recent, generate a dynamic one
    return generate_dynamic_tweet(history)

def generate_question_tweet(history):
    """Generate an engaging question tweet, avoiding recent posts"""
    max_attempts = 30
    attempts = 0
    
    while attempts < max_attempts:
        tweet = random.choice(engaging_questions)
        
        if not is_tweet_recent(tweet, history):
            return tweet
        
        attempts += 1
    
    # Fallback to dynamic generation
    return generate_dynamic_tweet(history)

def generate_contrarian_tweet(history):
    """Generate a thought-provoking contrarian take, avoiding recent posts"""
    max_attempts = 20
    attempts = 0
    
    while attempts < max_attempts:
        tweet = random.choice(contrarian_takes)
        
        if not is_tweet_recent(tweet, history):
            return tweet
        
        attempts += 1
    
    # Fallback to dynamic generation
    return generate_dynamic_tweet(history)

def generate_gpt2_tweet(history):
    """Generate tweet using GPT-2 with better prompts"""
    sophisticated_prompts = [
        "The intersection of technology and philosophy reveals that",
        "Most people don't realize that artificial intelligence",
        "The future of programming isn't about writing more code, it's about",
        "Silicon Valley's biggest blind spot is",
        "The most profound impact of technology isn't technical—it's"
    ]
    
    prompt = random.choice(sophisticated_prompts)
    
    try:
        responses = generator(prompt, max_length=80, num_return_sequences=3)
        
        # Select the best response (you can add more sophisticated selection logic)
        best_response = None
        for response in responses:
            generated_text = response["generated_text"].replace(prompt, "").strip()
            
            # Filter out poor quality responses
            if (len(generated_text.split()) > 8 and 
                len(generated_text.split()) < 25 and
                not any(word in generated_text.lower() for word in ['http', 'www', '@', '#']) and
                generated_text.count('.') <= 2):
                best_response = prompt + " " + generated_text
                break
        
        if best_response:
            return best_response
        else:
            # Fallback to curated content if GPT-2 fails
            return generate_curated_tweet(history)
            
    except Exception as e:
        print(f"GPT-2 generation failed: {e}")
        return generate_curated_tweet(history)

def select_tweet_type():
    """Select which type of tweet to generate"""
    tweet_types = {
        'curated': 0.3,      # 30% curated high-quality content
        'question': 0.25,    # 25% engaging questions
        'contrarian': 0.2,   # 20% thought-provoking takes
        'dynamic': 0.15,     # 15% dynamic template tweets
        'gpt2': 0.1         # 10% GPT-2 generated (with fallback)
    }
    
    rand = random.random()
    cumulative = 0
    
    for tweet_type, probability in tweet_types.items():
        cumulative += probability
        if rand <= cumulative:
            return tweet_type
    
    return 'curated'  # Default fallback

def enhance_tweet(base_tweet):
    """Add appropriate hashtags and ensure quality"""
    
    # Smart hashtag selection based on content
    hashtags = []
    
    if any(word in base_tweet.lower() for word in ['ai', 'artificial intelligence', 'machine learning', 'algorithm']):
        hashtags.extend(['#AI', '#MachineLearning'])
    
    if any(word in base_tweet.lower() for word in ['code', 'programming', 'developer', 'software']):
        hashtags.extend(['#Programming', '#SoftwareDevelopment'])
    
    if any(word in base_tweet.lower() for word in ['startup', 'entrepreneur', 'business']):
        hashtags.extend(['#Startup', '#Tech'])
    
    if any(word in base_tweet.lower() for word in ['philosophy', 'ethics', 'human', 'society']):
        hashtags.extend(['#TechPhilosophy', '#DigitalEthics'])
    
    # Default hashtags if none matched
    if not hashtags:
        hashtags = ['#Tech', '#Innovation']
    
    # Limit hashtags to avoid spam appearance
    hashtags = hashtags[:3]
    
    # Construct final tweet
    hashtag_string = ' '.join(set(hashtags))  # Remove duplicates
    final_tweet = f"{base_tweet} {hashtag_string}"
    
    # Ensure under 280 characters
    if len(final_tweet) > 280:
        # Trim the base tweet to fit
        available_chars = 280 - len(hashtag_string) - 1
        final_tweet = f"{base_tweet[:available_chars].strip()} {hashtag_string}"
    
    return final_tweet

# Main execution
def main():
    # Load and clean tweet history
    history = load_tweet_history()
    history = clean_old_history(history)
    
    tweet_type = select_tweet_type()
    max_attempts = 3  # Maximum number of attempts to generate a unique tweet
    attempts = 0
    
    while attempts < max_attempts:
        if tweet_type == 'curated':
            base_tweet = generate_curated_tweet(history)
        elif tweet_type == 'question':
            base_tweet = generate_question_tweet(history)
        elif tweet_type == 'contrarian':
            base_tweet = generate_contrarian_tweet(history)
        elif tweet_type == 'dynamic':
            base_tweet = generate_dynamic_tweet(history)
        else:  # gpt2
            base_tweet = generate_gpt2_tweet(history)
        
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
        print(f"Tweet type: {tweet_type}")
        print(f"Total tweets in history: {len(history['posted_tweets'])}")
        
    except Exception as e:
        print(f"Error posting tweet: {e}")
        print(f"Attempted tweet: {final_tweet}")

if __name__ == "__main__":
    main()