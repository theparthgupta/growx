# Tweet Bot

A modular, human-like tweet bot that posts concise, insightful, and readable tech tweets using the X (Twitter) API and Groq LLM. Designed for clarity, maintainability, and easy automation.

---

## Features

- **Human-like, non-generic tweets** about tech, coding, and dev life
- **Short, punchy, multi-line tweets** (no dashes/em dashes, line breaks for readability)
- **No duplicate/recent tweets** (history tracking)
- **Automated posting** via GitHub Actions (or manual run)
- **Modular codebase** for easy maintenance and extension

---

## Project Structure

```
growx/
│
├── config.py         # Loads env vars, sets up API clients, constants, logging
├── history.py        # Tweet history: load, save, deduplication, cleanup
├── generation.py     # Tweet generation & formatting (Groq LLM, line breaks, no dashes)
├── posting.py        # Orchestrates tweet generation, deduplication, posting
├── main.py           # Entry point: runs the bot
├── requirements.txt  # Python dependencies
├── tweet_history.json # (auto-generated) Tracks posted tweets
└── .github/
    └── workflows/
        └── tweet-bot.yml  # GitHub Actions workflow for scheduled/auto posting
```

---

## Setup

1. **Clone the repo**
   ```sh
   git clone <your-repo-url>
   cd growx
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file or set these in your environment:
   ```
   API_KEY=your_x_api_key
   API_SECRET=your_x_api_secret
   ACCESS_TOKEN=your_x_access_token
   ACCESS_TOKEN_SECRET=your_x_access_token_secret
   GROQ_API_KEY=your_groq_api_key
   ```

---

## Usage

**Manual run:**
```sh
python main.py
```

**What happens:**  
- Generates a short, human, multi-line tweet about tech (no dashes/em dashes)
- Checks for recent duplicates
- Posts to X (Twitter)
- Updates `tweet_history.json`

---

## Automation (GitHub Actions)

- The workflow in `.github/workflows/tweet-bot.yml` will:
  - Run every 10 minutes (or manually)
  - Install dependencies
  - Run the bot (`python main.py`)
  - Commit and push updated `tweet_history.json` to avoid repeats

**To enable:**
- Add your API keys as GitHub repository secrets:
  - `API_KEY`, `API_SECRET`, `ACCESS_TOKEN`, `ACCESS_TOKEN_SECRET`, `GROQ_API_KEY`
- Push to GitHub. The workflow will run as scheduled.

---

## Customization

- **Tweet style/logic:** Edit `generation.py` (prompt, formatting, topics)
- **History/cooldown:** Edit constants in `config.py` and logic in `history.py`
- **Workflow schedule:** Edit the `cron` line in `.github/workflows/tweet-bot.yml`

---

## License

MIT (or your preferred license)

---

## Credits

- [Tweepy](https://www.tweepy.org/) for X API
- [Groq](https://groq.com/) for LLM
- [filelock](https://pypi.org/project/filelock/) for safe file access

---

**Questions or improvements?**  
Open an issue or PR! 
