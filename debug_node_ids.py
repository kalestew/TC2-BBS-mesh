import sqlite3

def print_node_ids():
    # Connect to the SQLite database
    conn = sqlite3.connect('bulletins.db')
    cursor = conn.cursor()
    
    # Fetch distinct sender and recipient IDs from the mail table
    cursor.execute("SELECT DISTINCT sender, recipient FROM mail")
    mail_node_ids = cursor.fetchall()
    print("📬 **Mail Table Node IDs:**")
    for sender, recipient in mail_node_ids:
        print(f"👉 Sender ID: {sender}, Recipient ID: {recipient}")
    
    print("\n📰 **Bulletins Table Sender Short Names:**")
    # Fetch distinct sender_short_name from the bulletins table
    cursor.execute("SELECT DISTINCT sender_short_name FROM bulletins")
    bulletin_node_ids = cursor.fetchall()
    for (sender_short_name,) in bulletin_node_ids:
        print(f"👉 Sender Short Name: {sender_short_name}")
    
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    print_node_ids()