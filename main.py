import hashlib
import json
import os
import subprocess
import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext


class TelegramBot:
    SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)

    def __init__(self, auth_file, links_file, password_file, whitelist_file):
        # Load token and links from JSON files
        with open(auth_file, 'r') as f:
            self.token = json.load(f)["TOKEN"]
        with open(links_file, 'r') as f:
            self.links = json.load(f)

        self.password_file = password_file
        self.whitelist_file = whitelist_file
        self.whitelist = self.load_whitelist()

        self.authenticated_users = {}  # Store authenticated users with timestamps
        self.pending_auth = {}  # Store pending authentication states

        self.ensure_password()  # Ensure the password is set

        self.application = Application.builder().token(self.token).read_timeout(10).connect_timeout(
            10).build()

        self.active_processes = {}
        self.add_handlers()

    def ensure_password(self):
        if not os.path.exists(self.password_file):
            password = input("Set a password for the bot: ")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with open(self.password_file, 'w') as f:
                f.write(hashed_password)

    def load_whitelist(self):
        if os.path.exists(self.whitelist_file):
            with open(self.whitelist_file, 'r') as f:
                return set(json.load(f))
        return set()

    def add_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("record", self.show_links))
        self.application.add_handler(CommandHandler("status", self.check_status))
        self.application.add_handler(CallbackQueryHandler(self.record))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_password))

    def is_authenticated(self, username):
        if username in self.authenticated_users:
            last_active = self.authenticated_users[username]
            if time.time() - last_active < self.SESSION_TIMEOUT:
                self.authenticated_users[username] = time.time()  # Refresh session timestamp
                return True
            else:
                self.authenticated_users.pop(username)  # Remove expired session
        return False

    def request_authentication(self, update: Update):
        username = update.message.from_user.username
        if username not in self.whitelist:
            update.message.reply_text("You are not whitelisted to use this bot.")
            return False

        update.message.reply_text("Please enter the bot password to proceed.")
        self.pending_auth[username] = True
        return False

    async def handle_password(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username
        if username not in self.pending_auth:
            return

        password = update.message.text
        with open(self.password_file, 'r') as f:
            stored_password = f.read().strip()

        if hashlib.sha256(password.encode()).hexdigest() == stored_password:
            self.authenticated_users[username] = time.time()  # Save authentication time
            self.pending_auth.pop(username, None)
            await update.message.reply_text("Authentication successful! Please retry your command.")
        else:
            await update.message.reply_text("Invalid password. Try again.")

    async def start(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "Welcome! Please authenticate before using the bot's features."
        )

    async def show_links(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username

        if not self.is_authenticated(username):
            self.request_authentication(update)
            return

        # Create a list of buttons for each link
        buttons = [
            [InlineKeyboardButton(name, callback_data=name)] for name in self.links.keys()
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Select a stream to record:", reply_markup=reply_markup)

    async def record(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        name = query.data
        url = self.links.get(name)

        if not url:
            await query.edit_message_text(f"No link found for {name}.")
            return

        # Define the yt-dlp command
        command = [
            "yt-dlp",
            url,
            "--output",
            f"{name}-%(timestamp)s.%(ext)s"
        ]

        try:
            # Run the command
            process = subprocess.Popen(["a.bat", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.active_processes[name] = process
            await query.edit_message_text(f"Recording started for {name}. File will be saved.")
        except Exception as e:
            await query.edit_message_text(f"An error occurred: {e}")

    async def check_status(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username

        if not self.is_authenticated(username):
            self.request_authentication(update)
            return

        if not self.active_processes:
            await update.message.reply_text("No active recordings.")
            return

        status_messages = []
        for name, process in self.active_processes.items():
            if process.poll() is None:
                status_messages.append(f"{name}: Recording in progress.")
            else:
                status_messages.append(f"{name}: Recording completed.")

        await update.message.reply_text("\n".join(status_messages))

    def run(self):
        self.application.run_polling()


if __name__ == "__main__":
    # Specify the paths to the auth, links, password, and whitelist JSON files
    AUTH_FILE = "auth.json"
    LINKS_FILE = "links.json"
    PASSWORD_FILE = "password.txt"
    WHITELIST_FILE = "whitelist.json"

    bot = TelegramBot(AUTH_FILE, LINKS_FILE, PASSWORD_FILE, WHITELIST_FILE)
    bot.run()
