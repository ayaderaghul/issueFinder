import discord
from discord.ext import commands
import requests

# --- CONFIGURATION ---
DISCORD_TOKEN = ''
# Optional: Add GitHub Token if you hit rate limits
GITHUB_TOKEN = None 

# Set up the bot with the prefix '!' (e.g., !find python)
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_github_issues(language):
    """
    Fetches issues from GitHub API. 
    Returns a list of dictionaries.
    """
    url = "https://api.github.com/search/issues"
    query = f'label:"good first issue" state:open no:assignee language:{language}'
    
    params = {
        "q": query,
        "sort": "updated",
        "order": "desc",
        "per_page": 5 # Limit to top 5 to avoid spamming chat
    }
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except Exception as e:
        print(f"GitHub API Error: {e}")
        return []

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='find')
async def find_issues(ctx, language="python"):
    """
    Usage: !find <language>
    Example: !find javascript
    """
    await ctx.send(f"🔎 Searching for 'good first issues' in **{language}**...")
    
    issues = get_github_issues(language)
    
    if not issues:
        await ctx.send("No issues found (or API limit reached). Try again later.")
        return

    # Create a pretty Discord Embed
    embed = discord.Embed(
        title=f"Good First Issues: {language.capitalize()}",
        description="Here are the latest unassigned issues:",
        color=0x00ff00 # Green color
    )

    for issue in issues:
        repo_name = issue['repository_url'].split('repos/')[-1]
        title = issue['title']
        url = issue['html_url']
        
        # Add a field for each issue
        embed.add_field(
            name=f"📂 {repo_name}",
            value=f"[{title}]({url})",
            inline=False
        )

    await ctx.send(embed=embed)

# Run the bot
bot.run(DISCORD_TOKEN)