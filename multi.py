import subprocess
import sys
import os
import platform
import json
import asyncio
from tqdm import tqdm

# Ensure required modules are installed
def install_package(package_name):
    try:
        __import__(package_name)
    except ImportError:
        print(f"{package_name} is not installed.")
        choice = input(f"Do you want to install {package_name}? (yes/no): ").strip().lower()
        if choice in ['yes', 'y']:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"{package_name} installed successfully.")
            except Exception as e:
                print(f"Failed to install {package_name}: {e}")
                sys.exit(1)
        else:
            print(f"Cannot proceed without {package_name}. Exiting...")
            sys.exit(1)

# Install required packages
install_package("discord")
install_package("tqdm")

# Import after installation
import discord
from discord.ext import commands

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

# Utility functions
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

def load_data(file):
    """Load JSON data from a file or return an empty dictionary if the file is missing or corrupt."""
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(file, data):
    """Save JSON data to a file."""
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file}: {e}")

async def create_roles(bot, guild_id):
    """Create starter roles in a guild."""
    guild = bot.get_guild(int(guild_id))
    if not guild:
        print(f"Error: Bot is not in the specified guild (ID: {guild_id}).")
        return

    roles = {
        "Owner": discord.Permissions(administrator=True),
        "Admin": discord.Permissions(administrator=True),
        "Moderator": discord.Permissions(manage_messages=True, kick_members=True),
        "Member": discord.Permissions(read_messages=True, send_messages=True),
    }

    try:
        for role_name, permissions in roles.items():
            if discord.utils.get(guild.roles, name=role_name):
                print(f"Role {role_name} already exists.")
                continue
            await guild.create_role(name=role_name, permissions=permissions)
            print(f"Role {role_name} created.")
    except Exception as e:
        print(f"Error creating roles: {e}")

async def create_channels(bot, guild_id):
    """Create starter channels in a guild."""
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
        for category_name, channel_names in categories.items():
            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                category = await guild.create_category(category_name)

            for channel_name in channel_names:
                if discord.utils.get(category.channels, name=channel_name):
                    print(f"Channel {channel_name} already exists.")
                    continue
                await guild.create_text_channel(channel_name, category=category)
                print(f"Channel {channel_name} created in {category_name}.")
    except Exception as e:
        print(f"Error creating channels: {e}")

async def menu():
    """Main menu to interact with the bot."""
    while True:
        clear_screen()
        print(ASCII_ART)
        print("Welcome to the Discord Bot Setup Tool!")

        print("\nOptions:")
        print("1. Save Bot Token")
        print("2. Load Bot Tokens")
        print("3. Create Starter Roles")
        print("4. Create Starter Channels")
        print("5. Exit")
        choice = input("\nEnter your choice: ").strip()

        if choice == "1":
            clear_screen()
            token_name = input("Enter a name for the token: ").strip()
            token = input("Enter the bot token: ").strip()
            data = load_data(TOKEN_FILE)
            data[token_name] = token
            save_data(TOKEN_FILE, data)
            print("Token saved successfully.")
            input("\nPress Enter to return to the main menu.")

        elif choice == "2":
            clear_screen()
            tokens = load_data(TOKEN_FILE)
            if tokens:
                print("\nSaved Tokens:")
                for name in tokens:
                    print(f"- {name}")
            else:
                print("No tokens found.")
            input("\nPress Enter to return to the main menu.")

        elif choice in ["3", "4"]:
            clear_screen()
            use_saved = input("Use a saved token? (yes/no): ").strip().lower()
            if use_saved in ["yes", "y"]:
                tokens = load_data(TOKEN_FILE)
                if not tokens:
                    print("No saved tokens found. Please save one first.")
                    input("\nPress Enter to return to the main menu.")
                    continue

                print("\nAvailable Tokens:")
                for name in tokens:
                    print(f"- {name}")
                token_name = input("Enter the name of the saved token: ").strip()
                bot_token = tokens.get(token_name)
            else:
                bot_token = input("Enter the bot token: ").strip()

            guild_id = input("Enter the Guild ID: ").strip()

            if not bot_token:
                print("Invalid or missing bot token. Please try again.")
                input("\nPress Enter to return to the main menu.")
                continue

            intents = discord.Intents.default()
            intents.members = True
            bot = commands.Bot(command_prefix="!", intents=intents)

            @bot.event
            async def on_ready():
                print(f"Bot logged in as {bot.user}")
                if choice == "3":
                    await create_roles(bot, guild_id)
                elif choice == "4":
                    await create_channels(bot, guild_id)
                await bot.close()

            try:
                await bot.start(bot_token)
            except discord.LoginFailure:
                print("Invalid bot token.")
            input("\nPress Enter to return to the main menu.")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Try again.")
            input("\nPress Enter to return to the main menu.")

if __name__ == "__main__":
    asyncio.run(menu())
