import subprocess
import sys
import os
import platform
import json
import shutil
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

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

# Utility functions for JSON operations
def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(file, data):
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file}: {e}")

# Display options in a grid format
def display_grid(items, title="Features"):
    print(f"\n{title}:")
    term_width = shutil.get_terminal_size().columns
    max_length = max(len(item) for item in items) + 4
    columns = max(1, term_width // max_length)

    for i in range(0, len(items), columns):
        row = items[i:i + columns]
        print("".join(f"{item:<{max_length}}" for item in row))
    print()

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
    except discord.Forbidden:
        print("Error: Bot lacks the required permissions to create roles.")
    except Exception as e:
        print(f"Error creating roles: {e}")

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
            "Exit"
        ]

        display_grid(options, "Main Menu")
        choice = input("Enter your choice number> ").strip()

        if choice == "1":
            token_name = input("Enter a name for this token: ").strip()
            token = input("Enter bot token: ").strip()
            tokens = load_data(TOKEN_FILE)
            tokens[token_name] = token
            save_data(TOKEN_FILE, tokens)
            print("Token saved successfully.")

        elif choice == "2":
            tokens = load_data(TOKEN_FILE)
            if tokens:
                display_grid(tokens.keys(), "Saved Tokens")
            else:
                print("No tokens saved.")

        elif choice == "3":
            token_name = input("Enter bot token name to use: ").strip()
            guild_id = input("Enter guild ID: ").strip()
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
            else:
                print("Token not found.")

        elif choice == "4":
            print("Exiting...")
            sys.exit(0)

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(menu())
