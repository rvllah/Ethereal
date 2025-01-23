import subprocess
import sys
import json
import os
import platform
import discord
from discord.ext import commands
from tqdm import tqdm  # for colored progress bars

# File to store bot tokens
TOKEN_FILE = "tokens.json"

def clear_screen():
    """Clear the terminal screen for better visual appeal."""
    os.system("cls" if platform.system() == "Windows" else "clear")

def install_packages():
    """Check if required packages are installed. If not, install them."""
    required_packages = ['discord.py', 'tqdm']
    
    for package in required_packages:
        try:
            # Try importing the package. If it is installed, no action is taken.
            __import__(package.split('==')[0])
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"{package} installed successfully.")

def load_data(file):
    """Load data from a JSON file, or return an empty dictionary if the file does not exist or is corrupt."""
    if os.path.exists(file):
        try:
            with open(file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading {file}. File is empty or corrupt.")
            return {}
    return {}

def save_data(file, data):
    """Save data to a JSON file."""
    try:
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {file}: {e}")

def save_bot_token():
    """Save the bot token to a JSON file."""
    clear_screen()

    token = input("Enter bot token to save> ").strip()
    tokens = load_data(TOKEN_FILE)
    
    # Saving the token
    token_name = input("Enter a name for this token: ").strip()
    tokens[token_name] = token
    save_data(TOKEN_FILE, tokens)
    print(f"Token saved successfully as {token_name}.")

class CleanupBot(discord.Client):
    def __init__(self, token, guild_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = token
        self.guild_id = guild_id
    
    async def on_ready(self):
        clear_screen()
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("Starting cleanup process...")

        # Fetch the guild (server) by ID
        guild = self.get_guild(self.guild_id)
        if not guild:
            print(f"Could not find a guild with ID {self.guild_id}. Ensure the bot is in the server.")
            await self.close()
            return
        
        print(f"Cleaning up server: {guild.name} (ID: {guild.id})")
        
        # Create a tqdm progress bar for channel deletion
        channels_to_delete = [channel for channel in guild.channels]
        roles_to_delete = [role for role in guild.roles if role.name != "@everyone"]

        # Deleting channels with progress bar
        print(f"Deleting {len(channels_to_delete)} channels...")
        for _ in tqdm(channels_to_delete, desc="Channels", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} channels deleted", colour="green"):
            try:
                await guild.get_channel(_.id).delete()
            except Exception as e:
                print(f"Failed to delete channel {_.name}: {e}")

        # Deleting roles with progress bar
        print(f"Deleting {len(roles_to_delete)} roles...")
        for _ in tqdm(roles_to_delete, desc="Roles", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} roles deleted", colour="blue"):
            try:
                await guild.get_role(_.id).delete()
            except Exception as e:
                print(f"Failed to delete role {_.name}: {e}")
        
        print("Cleanup process completed.")
        await self.close()
        main_menu()  # Go back to the main menu after completion

def main_menu():
    """Main menu for user interaction."""
    clear_screen()

    menu_options = [
        "1. Save Bot Token", "2. Load Bot Token", "3. Cleanup Server", "4. Exit"
    ]
    
    for option in menu_options:
        print(option)
    
    choice = input("> ").strip()

    if choice == "1":
        save_bot_token()
    elif choice == "2":
        load_bot_token()
    elif choice == "3":
        server_cleanup()
    elif choice == "4":
        exit()
    else:
        print("Invalid choice. Please try again.")
        main_menu()

def load_bot_token():
    """Load and display saved bot tokens."""
    clear_screen()

    tokens = load_data(TOKEN_FILE)
    if tokens:
        print("Saved Bot Tokens:")
        for token_name in tokens:
            print(f" - {token_name}")
    else:
        print("No saved tokens found.")
    input("Press Enter to continue...")

def server_cleanup():
    """Cleanup the Discord server based on a bot token."""
    clear_screen()

    tokens = load_data(TOKEN_FILE)
    if tokens:
        print("Saved Bot Tokens:")
        for token_name in tokens:
            print(f" - {token_name}")
        
        print("\nAlternatively, you can enter a new bot token manually.")
        choice = input("Enter the name of the saved token or type 'new' to enter a new token: ").strip()

        if choice == 'new':
            token = input("Enter your bot token: ").strip()
        elif choice in tokens:
            token = tokens[choice]
        else:
            print("Invalid token name. Please try again.")
            server_cleanup()
            return
    else:
        token = input("No saved tokens found. Enter your bot token: ").strip()

    guild_id = int(input("Enter the guild (server) ID: ").strip())
    
    intents = discord.Intents.default()
    intents.guilds = True
    
    client = CleanupBot(token, guild_id, intents=intents)
    client.run(token)

if __name__ == "__main__":
    # Check if the packages are installed before continuing
    install_packages()
    
    # Proceed to the main menu after ensuring the packages are installed
    main_menu()
