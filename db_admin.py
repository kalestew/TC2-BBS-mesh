import os
import sqlite3
import threading

thread_local = threading.local()

def get_db_connection():
    if not hasattr(thread_local, 'connection'):
        thread_local.connection = sqlite3.connect('bulletins.db')
    return thread_local.connection

def initialize_database():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bulletins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    board TEXT NOT NULL,
                    sender_short_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    unique_id TEXT NOT NULL
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS mail (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender TEXT NOT NULL,
                    sender_short_name TEXT NOT NULL,
                    recipient TEXT NOT NULL,
                    date TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    content TEXT NOT NULL,
                    unique_id TEXT NOT NULL
                );''')
    c.execute('''CREATE TABLE IF NOT EXISTS channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL
                );''')
    conn.commit()
    print("📄 **Database schema initialized.**")

def list_bulletins():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, board, sender_short_name, date, subject, unique_id FROM bulletins")
    bulletins = c.fetchall()
    if bulletins:
        print("📰 **Bulletins:**")
        for bulletin in bulletins:
            print(f"👉 (ID: {bulletin[0]}, Board: {bulletin[1]}, Poster: {bulletin[2]}, Subject: {bulletin[4]})")
    else:
        print("❌ **No bulletins found.**")
    print_separator()
    return bulletins

def list_mail():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, sender, sender_short_name, recipient, date, subject, unique_id FROM mail")
    mail = c.fetchall()
    if mail:
        print("📬 **Mail:**")
        for msg in mail:
            print(f"👉 (ID: {msg[0]}, Sender: {msg[2]}, Recipient: {msg[3]}, Subject: {msg[5]})")
    else:
        print("❌ **No mail found.**")
    print_separator()
    return mail

def list_channels():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, url FROM channels")
    channels = c.fetchall()
    if channels:
        print("📺 **Channels:**")
        for channel in channels:
            print(f"👉 (ID: {channel[0]}, Name: {channel[1]}, URL: {channel[2]})")
    else:
        print("❌ **No channels found.**")
    print_separator()
    return channels

def list_node_ids():
    conn = get_db_connection()
    c = conn.cursor()
    
    # List distinct sender and recipient IDs from the mail table
    c.execute("SELECT DISTINCT sender, recipient FROM mail")
    mail_node_ids = c.fetchall()
    print("📬 **Mail Table Node IDs:**")
    for sender, recipient in mail_node_ids:
        print(f"👉 Sender ID: {sender}, Recipient ID: {recipient}")
    
    # List distinct sender_short_name from the bulletins table
    c.execute("SELECT DISTINCT sender_short_name FROM bulletins")
    bulletin_node_ids = c.fetchall()
    print("\n📰 **Bulletins Table Sender Short Names:**")
    for (sender_short_name,) in bulletin_node_ids:
        print(f"👉 Sender Short Name: {sender_short_name}")
    
    print_separator()
    conn.close()

def delete_bulletin():
    bulletins = list_bulletins()
    if bulletins:
        bulletin_ids = input_bold("🔪 Enter the bulletin ID(s) to delete (comma-separated) or 'X' to cancel: ").split(',')
        if 'X' in [id.strip().upper() for id in bulletin_ids]:
            print_bold("❌ **Deletion cancelled.**")
            print_separator()
            return
        conn = get_db_connection()
        c = conn.cursor()
        for bulletin_id in bulletin_ids:
            c.execute("DELETE FROM bulletins WHERE id = ?", (bulletin_id.strip(),))
        conn.commit()
        print_bold(f"✅ **Bulletin(s) with ID(s) {', '.join(bulletin_ids)} deleted.**")
        print_separator()

def delete_mail():
    mail = list_mail()
    if mail:
        mail_ids = input_bold("🔪 Enter the mail ID(s) to delete (comma-separated) or 'X' to cancel: ").split(',')
        if 'X' in [id.strip().upper() for id in mail_ids]:
            print_bold("❌ **Deletion cancelled.**")
            print_separator()
            return
        conn = get_db_connection()
        c = conn.cursor()
        for mail_id in mail_ids:
            c.execute("DELETE FROM mail WHERE id = ?", (mail_id.strip(),))
        conn.commit()
        print_bold(f"✅ **Mail with ID(s) {', '.join(mail_ids)} deleted.**")
        print_separator()

def delete_channel():
    channels = list_channels()
    if channels:
        channel_ids = input_bold("🔪 Enter the channel ID(s) to delete (comma-separated) or 'X' to cancel: ").split(',')
        if 'X' in [id.strip().upper() for id in channel_ids]:
            print_bold("❌ **Deletion cancelled.**")
            print_separator()
            return
        conn = get_db_connection()
        c = conn.cursor()
        for channel_id in channel_ids:
            c.execute("DELETE FROM channels WHERE id = ?", (channel_id.strip(),))
        conn.commit()
        print_bold(f"✅ **Channel(s) with ID(s) {', '.join(channel_ids)} deleted.**")
        print_separator()

def input_bold(prompt):
    print("\033[1m", end='')  # ANSI escape code for bold text
    response = input(prompt)
    print("\033[0m", end='')  # ANSI escape code to reset text
    return response

def print_bold(message):
    print("\033[1m" + message + "\033[0m")  # Bold text

def print_separator():
    print_bold("========================")

def main():
    initialize_database()
    while True:
        print_separator()
        print_bold("🛠️ **DB Admin Tool** 🛠️")
        print("1. List Bulletins")
        print("2. List Mail")
        print("3. List Channels")
        print("4. List Node IDs")
        print("5. Delete Bulletin")
        print("6. Delete Mail")
        print("7. Delete Channel")
        print("8. Exit")
        choice = input_bold("🔢 Enter your choice: ")
        print_separator()
        if choice == '1':
            list_bulletins()
        elif choice == '2':
            list_mail()
        elif choice == '3':
            list_channels()
        elif choice == '4':
            list_node_ids()
        elif choice == '5':
            delete_bulletin()
        elif choice == '6':
            delete_mail()
        elif choice == '7':
            delete_channel()
        elif choice == '8':
            print_bold("👋 **Exiting DB Admin Tool.**")
            break
        else:
            print_bold("❌ **Invalid choice. Please try again.**")
            print_separator()

if __name__ == "__main__":
    main()
