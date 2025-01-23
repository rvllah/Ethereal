import subprocess
import sys
import json
import os
import platform
import shutil
import discord
from discord.ext import commands
import asyncio
from tqdm import tqdm

# File to store bot tokens and guild IDs
TOKEN_FILE = "tokens.json"

ASCII_ART = r"""
  ___________ __  .__                                .__   
  \_   _____//  |_|  |__   ___________   ____ _____  |  |  
   |    __)_\   __\  |  \_/ __ \_  __ \_/ __ \\\__  \ |  |  
   |        \|  | |   Y  \  ___/|  | \/\  ___/ / __ \|  |__
  /_______  /|__| |___|  /\___  >__|    \___  >____  /____/
          \/           \/     \/            \/     \/      
"""

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def load_data(file):
    """Load data from a JSON file, or return an empty dictionary if the file does not exist or is corrupt."""
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(file, data):
    """Save data to a JSON file."""
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file}: {e}")

def display_grid(items, title="Features"):
    """Display the items in a grid format."""
    print(f"\n{title}:")
    term_width = shutil.get_terminal_size().columns
    max_length = max(len(item) for item in items) + 4  # Padding
    columns = max(1, term_width // max_length)

    for i in range(0, len(items), columns):
        row = items[i:i + columns]
        print("".join(f"{item:<{max_length}}" for item in row))
    print()

def get_input(prompt="> "):
    """Get input from the user."""
    try:
        return input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nInput interrupted.")
        return ""

def show_progress_bar(task, total_steps=100):
    """Show a colored progress bar for tasks."""
    for _ in tqdm(range(total_steps), desc=task, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", colour="green"):
        asyncio.sleep(0.01)

async def create_roles(bot, guild_id):
    """Create starter roles in the specified guild."""
    guild = bot.get_guild(int(guild_id))
    if not guild:
        print(f"Error: Bot is not in the specified guild (ID: {guild_id}).")
        return

    role_data = {
        "Owner": discord.Permissions(administrator=True),
        "Admin": discord.Permissions(administrator=True),
        "Moderator": discord.Permissions(manage_messages=True, kick_members=True),
        "Member": discord.Permissions(read_messages=True, send_messages=True),
    }

    try:
        for role_name, permissions in role_data.items():
            existing_role = discord.utils.get(guild.roles, name=role_name)
            if existing_role:
                print(f"Role {role_name} already exists, skipping.")
                continue

            await guild.create_role(
                name=role_name,
                permissions=permissions,
                reason="Setting up starter roles."
            )
            print(f"Created role: {role_name}")

        show_progress_bar("Creating roles")
        print("Finished creating roles.")
    except discord.Forbidden:
        print("Error: Bot lacks the required permissions to create roles.")
    except Exception as e:
        print(f"Error creating roles: {e}")

async def create_channels(bot, guild_id):
    """Create starter channels in the specified guild."""
    guild = bot.get_guild(int(guild_id))
    if not guild:
        print(f"Error: Bot is not in the specified guild (ID: {guild_id}).")
        return

    categories = {
        "Important": ["rules", "announcements", "roles"],
        "Main": ["chat", "media", "bot-cmds"],
        "Staff": ["staff-chat", "logs", "cmds"],
    }

    try:
        for category_name, channels in categories.items():
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)

            for channel_name in channels:
                existing_channel = discord.utils.get(category.channels, name=channel_name)
                if existing_channel:
                    print(f"Channel {channel_name} already exists, skipping.")
                    continue

                await guild.create_text_channel(channel_name, category=category)
            print(f"Created category: {category_name}")

        show_progress_bar("Creating channels")
        print("Finished creating channels.")
    except discord.Forbidden:
        print("Error: Bot lacks the required permissions to create channels.")
    except Exception as e:
        print(f"Error creating channels: {e}")

async def menu():
    """Display the menu and handle user choices."""
    while True:
        clear_screen()
        print(ASCII_ART)
        print("Welcome to the Discord Bot Setup Tool!\n")
        options = [
            "Save Bot Token",
            "Load Bot Token",
            "Create Starter Roles",
            "Create Starter Channels",
            "Exit"
        ]

        display_grid(options, "Main Menu")
        choice = get_input("Enter your choice number> ")

        if choice == "1":
            token_name = get_input("Enter a name for this token: ")
            token = get_input("Enter bot token: ")
            tokens = load_data(TOKEN_FILE)
            tokens[token_name] = token
            save_data(TOKEN_FILE, tokens)
            show_progress_bar("Saving Token")
            clear_screen()
            print("Token saved successfully.")

        elif choice == "2":
            tokens = load_data(TOKEN_FILE)
            if tokens:
                display_grid(tokens.keys(), "Saved Tokens")
            else:
                print("No tokens saved.")

        elif choice == "3":
            token_name = get_input("Enter bot token name to use: ")
            guild_id = get_input("Enter guild ID: ")
            tokens = load_data(TOKEN_FILE)
            bot_token = tokens.get(token_name)

            if bot_token:
                intents = discord.Intents.default()
                intents.members = True
                bot = commands.Bot(command_prefix="!", intents=intents)

                @bot.event
                async def on_ready():
                    await create_roles(bot, guild_id)
                    await bot.close()

                try:
                    await bot.start(bot_token)
                except discord.LoginFailure:
                    print("Invalid bot token.")
                clear_screen()

            else:
                print("Token not found.")

        elif choice == "4":
            token_name = get_input("Enter bot token name to use: ")
            guild_id = get_input("Enter guild ID: ")
            tokens = load_data(TOKEN_FILE)
            bot_token = tokens.get(token_name)

            if bot_token:
                intents = discord.Intents.default()
                intents.members = True
                bot = commands.Bot(command_prefix="!", intents=intents)

                @bot.event
                async def on_ready():
                    await create_channels(bot, guild_id)
                    await bot.close()

                try:
                    await bot.start(bot_token)
                except discord.LoginFailure:
                    print("Invalid bot token.")
                clear_screen()

            else:
                print("Token not found.")

        elif choice == "5":
            print("Exiting...")
            sys.exit(0)

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(menu())
