import os
import requests
from pytrends.request import TrendReq
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID   = os.environ["TELEGRAM_CHAT_ID"]

# Keywords to track — edit these to match your vibe
FASHION_KEYWORDS = [
    "streetwear 2026",
    "y2k fashion",
    "gorpcore",
    "quiet luxury",
    "oversized fits",
]

REDDIT_SUBREDDITS = ["malefashionadvice", "femalefashionadvice", "streetwear"]

def get_google_trends():
    pytrends = TrendReq(hl='en-US', tz=300)
    lines = ["📈 *Google Trends This Week:*"]
    for keyword in FASHION_KEYWORDS:
        try:
            pytrends.build_payload([keyword], timeframe='now 7-d')
            data = pytrends.interest_over_time()
            if not data.empty:
                avg = int(data[keyword].mean())
                peak = int(data[keyword].max())
                lines.append(f"• *{keyword}*: avg interest {avg}/100, peak {peak}/100")
        except Exception as e:
            lines.append(f"• {keyword}: unavailable")
    return "\n".join(lines)

def get_reddit_trends():
    headers = {"User-Agent": "trend-agent/1.0"}
    lines = ["🔥 *Hot on Reddit Right Now:*"]
    for sub in REDDIT_SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=3"
            res = requests.get(url, headers=headers)
            posts = res.json()["data"]["children"]
            lines.append(f"\nr/{sub}:")
            for post in posts:
                title = post["data"]["title"]
                ups = post["data"]["ups"]
                lines.append(f"  • {title} ({ups} upvotes)")
        except Exception as e:
            lines.append(f"  • r/{sub}: unavailable")
    return "\n".join(lines)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    })

def run():
    today = datetime.now().strftime("%B %d, %Y")
    msg = f"🧵 *Weekly Fashion Trend Report — {today}*\n\n"
    msg += get_google_trends()
    msg += "\n\n"
    msg += get_reddit_trends()
    send_telegram(msg)

if __name__ == "__main__":
    run()
