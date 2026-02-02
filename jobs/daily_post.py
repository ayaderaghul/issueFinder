import os
import requests
from datetime import datetime, timedelta

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID")

GITHUB_SEARCH_URL = "https://api.github.com/search/issues"
DISCORD_API_URL = "https://discord.com/api/v10"


def search_issues(query):
    params = {
        "q": query,
        "sort": "created",
        "order": "desc",
        "per_page": 10,
    }
    res = requests.get(GITHUB_SEARCH_URL, params=params)
    res.raise_for_status()
    return res.json()["items"]


def format_issues(title, issues):
    if not issues:
        return f"**{title}**\nNo issues found today.\n"

    lines = [f"**{title}**"]
    for issue in issues:
        lines.append(f"- [{issue['title']}]({issue['html_url']})")
    return "\n".join(lines) + "\n"


def post_to_discord(message):
    url = f"{DISCORD_API_URL}/channels/{DISCORD_CHANNEL_ID}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {"content": message}
    
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()


def main():
    since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

    python_issues = search_issues(f'python created:>={since} label:"good first issue" no:assignee state:open')
    js_issues = search_issues(f'javascript created:>={since} label:"good first issue" no:assignee state:open')

    message = (
        "📌 **Daily Issue Finder**\n\n"
        + format_issues("🐍 Python Issues", python_issues)
        + "\n"
        + format_issues("🟨 JavaScript Issues", js_issues)
    )

    print("MESSAGE LENGTH:", len(message))
    print(message)
    post_to_discord(message)


if __name__ == "__main__":
    main()
