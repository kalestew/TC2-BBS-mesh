import os
import sys
import sqlite3
import threading
import datetime

from db_operations import (
    initialize_database,
    add_bulletin,
    get_bulletins,
    get_bulletin_content,
    add_mail,
    get_mail,
    get_mail_content,
)

from utils import (
    get_db_connection,
    send_message,
)

import configparser

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

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
    recipient_id = input("Enter the recipient's node ID: ")
    sender_id = input("Enter your node ID: ")
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
