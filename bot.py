import discord
from discord.ext import commands, tasks
import instaloader
import random
from collections import defaultdict
import os

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



# Initialize the bot with the command prefix
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!sr ", intents=intents)

# A simple loop that runs every 5 minutes to keep the bot alive
@tasks.loop(minutes=5)
async def keep_alive():
    print("Bot is alive!")

@bot.event
async def on_ready():
    keep_alive.start()  # Start the loop when the bot is ready
    print(f'Bot connected as {bot.user}')

# Other bot code here...

@bot.command()
async def of(ctx, *, username: str):
    """Analyze an Instagram profile and provide a report."""
    initial_message = await ctx.send(f"🔍 Analyzing profile: {username}. Please wait...")

    # Get profile info and analyze
    profile_info = await get_public_instagram_info(username)
    if profile_info:
        reports_to_file = analyze_profile(profile_info)

        result_text = f"**Public Information for {username}:\n\n"
        result_text += f"Username: {profile_info.get('username', 'N/A')}\n"
        result_text += f"Full Name: {profile_info.get('full_name', 'N/A')}\n"
        result_text += f"Biography: {profile_info.get('biography', 'N/A')}\n"
        result_text += f"Followers: {profile_info.get('follower_count', 'N/A')}\n"
        result_text += f"Following: {profile_info.get('following_count', 'N/A')}\n"
        result_text += f"Private Account: {'Yes' if profile_info.get('is_private') else 'No'}\n"
        result_text += f"Posts: {profile_info.get('post_count', 'N/A')}\n"
        result_text += f"External URL: {profile_info.get('external_url', 'N/A')}\n\n"

        result_text += "Suggested Reports to File:\n"
        for report in reports_to_file.values():
            result_text += f"• {report}\n"

        # Add credits and disclaimer
        result_text += "\n*Note: This analysis is based on available data and may not be fully accurate. Suggestions are generated randomly if no specific issues are found.*\n"
        result_text += "Credits: Developed by @69mog ."

        # Create an embed to display the result
        embed = discord.Embed(description=result_text, color=discord.Color.blue())

        # Add a button that redirects to your website
        button = discord.ui.Button(label="Visit My Portal", url="https://atomix-rehan.blogspot.com/p/portal_15.html?m=1")
        view = discord.ui.View()
        view.add_item(button)

        # Send the embed with the button
        await ctx.send(embed=embed, view=view)

    else:
        await initial_message.edit(content=f"❌ Profile {username} not found or an error occurred.")

async def get_public_instagram_info(username):
    L = instaloader.Instaloader()

    try:
        profile = instaloader.Profile.from_username(L.context, username)
        info = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "follower_count": profile.followers,
            "following_count": profile.followees,
            "is_private": profile.is_private,
            "post_count": profile.mediacount,
            "external_url": profile.external_url,
        }
        return info
    except instaloader.exceptions.ProfileNotExistsException:
        return None
    except instaloader.exceptions.InstaloaderException as e:
        print(f"An error occurred: {e}")
        return None

def check_keywords(text, keywords):
    return any(keyword in text.lower() for keyword in keywords)

def analyze_profile(profile_info):
    # Special case for the username 'test.1234100'
    if profile_info.get("username", "") == "test.1234100":
        return {
            "SELF": "3x - Self",
            "NUDITY": "2x - Nude"
        }

    reports = defaultdict(int)

    # Profile attributes to check
    profile_texts = [
        profile_info.get("username", ""),
        profile_info.get("biography", ""),
        " ".join(["Example post about selling stuff", "Another post mentioning @someone", "Nude picture..."])  # Example posts
    ]

    for text in profile_texts:
        for category, keywords in report_keywords.items():
            if check_keywords(text, keywords):
                reports[category] += 1

    # Generate suggestions based on found issues
    if reports:
        num_categories = min(len(reports), random.randint(2, 5))
        selected_categories = random.sample(list(reports.keys()), num_categories)
    else:
        # Use random suggestions if no specific issues are found
        all_categories = list(report_keywords.keys())
        num_categories = random.randint(2, 5)
        selected_categories = random.sample(all_categories, num_categories)

    unique_counts = random.sample(range(1, 6), len(selected_categories))
    formatted_reports = {
        category: f"{count}x - {category}" for category, count in zip(selected_categories, unique_counts)
    }

    return formatted_reports

# Start the bot
bot.run(os.getenv("TOKEN"))
