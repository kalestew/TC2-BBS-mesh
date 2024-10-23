import os
import sys
import sqlite3
import threading
import datetime
import requests

from db_operations import (
    initialize_database,
    add_bulletin,
    get_bulletins,
    get_bulletin_content,
    add_mail,
    get_mail,
    get_mail_content,
    get_db_connection  # Correctly import from db_operations
)

from utils import (
    send_message,
)

import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Verify required sections
required_sections = ['sync', 'user']
for section in required_sections:
    if not config.has_section(section):
        print(f"Configuration error: Missing [{section}] section in config.ini.")
        sys.exit(1)

bbs_nodes = config['sync'].get('bbs_nodes', '').split(',')

# Ensure bbs_nodes is a list of node IDs
bbs_nodes = [node.strip() for node in bbs_nodes if node.strip()]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    banner = """
████████╗ ██████╗██████╗       ██████╗ ██████╗ ███████╗
╚══██╔══╝██╔════╝╚════██╗      ██╔══██╗██╔══██╗██╔════╝
   ██║   ██║      █████╔╝█████╗██████╔╝██████╔╝███████╗
   ██║   ██║     ██╔═══╝ ╚════╝██╔══██╗██╔══██╗╚════██║
   ██║   ╚██████╗███████╗      ██████╔╝██████╔╝███████║
   ╚═╝    ╚═════╝╚══════╝      ╚═════╝ ╚═════╝ ╚══════╝
Admin Tool
"""
    print(banner)

def pause():
    input("Press Enter to continue...")

def list_bulletins():
    boards = ['General', 'Info', 'News', 'Urgent']
    for board in boards:
        bulletins = get_bulletins(board)
        print(f"\nBoard: {board} ({len(bulletins)} bulletins)")
        for bulletin in bulletins:
            bulletin_id, subject, sender_short_name, date, unique_id = bulletin
            print(f"ID: {bulletin_id}, Subject: {subject}, From: {sender_short_name}, Date: {date}")
    pause()

def post_bulletin():
    boards = ['General', 'Info', 'News', 'Urgent']
    print("Select the board to post the bulletin:")
    for idx, board in enumerate(boards):
        print(f"{idx + 1}. {board}")
    choice = input("Enter the number of the board: ")
    try:
        board = boards[int(choice) - 1]
    except (IndexError, ValueError):
        print("Invalid choice.")
        return
    sender_short_name = input("Enter your short name: ")
    subject = input("Enter the subject of the bulletin: ")
    print("Enter the content of the bulletin. Type 'END' on a new line to finish.")
    content_lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        content_lines.append(line)
    content = '\n'.join(content_lines)
    unique_id = add_bulletin(board, sender_short_name, subject, content, bbs_nodes, None)
    print(f"Bulletin posted with ID: {unique_id}")
    pause()

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT sender FROM mail")
    users = cursor.fetchall()
    if users:
        print("Potential Recipients:")
        for user in users:
            print(f"- {user[0]}")
    else:
        print("No users found.")
    pause()

def send_mail():
    recipient_short_name = input("Enter the recipient's short name: ")
    sender_short_name = input("Enter your short name: ")
    subject = input("Enter the subject of the mail: ")
    print("Enter the content of the mail. Type 'END' on a new line to finish.")
    content_lines = []
    while True:
        line = input()
        if line.strip().upper() == 'END':
            break
        content_lines.append(line)
    content = '\n'.join(content_lines)

    # Find the recipient's node ID using the short name
    recipient_id = get_node_id_by_short_name(recipient_short_name)
    if recipient_id is None:
        print(f"Recipient with short name '{recipient_short_name}' not found.")
        return

    # Safely get sender_id
    sender_id = config['user'].get('node_id', None)
    if not sender_id:
        print("Configuration error: 'node_id' not found in [user] section.")
        return

    unique_id = add_mail(sender_id, sender_short_name, recipient_id, subject, content, bbs_nodes, None)
    print(f"Mail sent with ID: {unique_id}")
    pause()

def view_mail():
    mails = get_mail(None)  # Fetch all mail messages
    if mails:
        print("Mail Messages:")
        for mail in mails:
            mail_id, sender_short_name, subject, date, unique_id = mail
            print(f"ID: {mail_id}, Subject: {subject}, From: {sender_short_name}, Date: {date}")
    else:
        print("No mail messages found.")
    pause()

def get_node_id_by_short_name(short_name):
    response = requests.get('http://localhost:5000/nodes')
    if response.status_code == 200:
        nodes = response.json()
        for node in nodes:
            if node['short_name'].lower() == short_name.lower():
                return node['num']
    print(f"Recipient with short name '{short_name}' not found.")
    return None

def main_menu():
    while True:
        clear_screen()
        display_banner()
        print("Admin Tool Main Menu")
        print("1. List Bulletins")
        print("2. Post Bulletin")
        print("3. List Potential Recipients")
        print("4. Send Mail Message")
        print("5. View Mail Messages")
        print("6. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            list_bulletins()
        elif choice == '2':
            post_bulletin()
        elif choice == '3':
            list_users()
        elif choice == '4':
            send_mail()
        elif choice == '5':
            view_mail()
        elif choice == '6':
            print("Exiting admin tool.")
            sys.exit(0)
        else:
            print("Invalid choice.")
            pause()

if __name__ == "__main__":
    initialize_database()
    main_menu()
