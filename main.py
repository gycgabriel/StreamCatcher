import hashlib
import json
import os
import re
import signal
import subprocess
import time

import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

from handlers import AccountHandler


class TelegramBot:
    SESSION_TIMEOUT = 3600  # Session timeout in seconds (1 hour)

    def __init__(self, auth_file, links_file, password_file):
        # Load token and links from JSON files
        with open(os.path.join(os.path.dirname(__file__), auth_file), 'r') as f:
            auth_file_obj = json.load(f)
            self.token = auth_file_obj["BOT_TOKEN"]
            self.admin_chat_id = auth_file_obj["CHAT_ID"]
            self.allowed_users = auth_file_obj["ALLOWED_USERNAMES"]
        with open(os.path.join(os.path.dirname(__file__), links_file), 'r') as f:
            link_file_obj = json.load(f)
            self.links = link_file_obj["LINK_MAP"]
            self.target_script_path = os.path.join(os.path.dirname(__file__), link_file_obj["TARGET_SCRIPT_PATH"])
            self.target_script_dir = os.path.dirname(self.target_script_path)

        self.password_file = password_file

        self.authenticated_users = {}  # Store authenticated users with timestamps
        self.pending_auth = {}  # Store pending authentication states

        self.ensure_password()  # Ensure the password is set

        self.application = Application.builder().token(self.token)\
            .read_timeout(10).connect_timeout(10).post_init(self.send_init_message).build()

        self.active_processes = {}
        self.add_handlers()

    async def send_init_message(self, application):
        print("[*] Bot is running")
        await application.bot.send_message(chat_id=self.admin_chat_id, text="─=≡Σ((( つ•̀ω•́)つ [Online]")

    def ensure_password(self):
        if not os.path.exists(self.password_file):
            password = input("Set a password for the bot: ")
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            with open(os.path.join(os.path.dirname(__file__), self.password_file), 'w') as f:
                f.write(hashed_password)

    def add_handlers(self):
        self.application.add_handler(AccountHandler(self.allowed_users))
        self.application.add_handler(CommandHandler("start", self.handle_start_command))
        self.application.add_handler(CommandHandler("record", self.handle_record_command))
        self.application.add_handler(CommandHandler("status", self.handle_status_command))
        self.application.add_handler(CommandHandler("stop", self.handle_status_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        # all other text, assume is password
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_password))

    def is_authenticated(self, username):
        return True
        if username in self.authenticated_users:
            last_active = self.authenticated_users[username]
            if time.time() - last_active < self.SESSION_TIMEOUT:
                self.authenticated_users[username] = time.time()  # Refresh session timestamp
                return True
            else:
                self.authenticated_users.pop(username)  # Remove expired session
        return False

    async def request_authentication(self, update: Update):
        username = update.message.from_user.username

        await update.message.reply_text("Please enter the bot password to proceed.")
        self.pending_auth[username] = True
        return False

    async def handle_password(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username
        if username not in self.pending_auth:  # Typed without /start
            return

        password = update.message.text
        with open(self.password_file, 'r') as f:
            stored_password = f.read().strip()

        if hashlib.sha256(password.encode()).hexdigest() == stored_password:
            self.authenticated_users[username] = time.time()  # Save authentication time
            self.pending_auth.pop(username, None)
            await update.message.reply_text("Authentication successful! Please retry your command.")
        else:
            await update.message.reply_text("Invalid password. Please try again:")

    async def handle_start_command(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username

        buttons = [[KeyboardButton("/start")], [KeyboardButton("/record")], [KeyboardButton("/status")], [KeyboardButton("/stop")]]

        if self.is_authenticated(username):
            await update.message.reply_text(
                f"Welcome back, {username}\\! 👋\n\n"
                "Available commands:\n"
                "• /start \\- Show this message\n"
                "• /record \\- Choose a stream to record\n"
                "• /status \\- Check or stop active recordings\n"
                "• /stop \\- Check or stop active recordings\n",
                reply_markup=ReplyKeyboardMarkup(buttons),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        self.pending_auth[username] = True
        await update.message.reply_text(
            "Welcome to StreamCatcher Bot\! 🎥\n\n"
            "This Telegram bot allows you to remotely record livestreams using *yt\-dlp* and manage your recordings\.  "
            "To get started, you need to authenticate using the bot's password\.\n\n"
            "*How to Use the Bot:*\n"
            "1\. Authenticate with the bot password\.\n"
            "2\. Use /record to choose a stream to record\.\n"
            "3\. Use /status to check or stop active recordings\.\n\n"
            "*Please enter the bot password to proceed\.*",
            parse_mode=ParseMode.MARKDOWN_V2
        )

    async def handle_record_command(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username

        if not self.is_authenticated(username):
            await self.request_authentication(update)
            return

        # Create a list of buttons for each link
        buttons = [
            [InlineKeyboardButton(name, callback_data=f"record|{name}")] for name in self.links.keys()
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text("Select a stream to record:", reply_markup=reply_markup)

    async def handle_callback(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()

        data = query.data
        action, name = data.split('|', 1)

        if action == "record":
            await self.handle_record(query, name)
        elif action == "kill":
            await self.handle_kill(query, name)

    async def handle_record(self, query, name):
        url = self.links.get(name)

        if not url:
            await query.edit_message_text(f"No link found for {name}.")
            return

        if name in self.active_processes and self.active_processes[name].poll() is None:
            await query.edit_message_text(f"Recording for {name} is already in progress.")
            return

        try:
            process = subprocess.Popen([self.target_script_path, url],
                                       cwd=self.target_script_dir,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       text=True,
                                       encoding='utf-8',
                                       errors='ignore',
                                       creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.active_processes[name] = process
            await query.edit_message_text(f"Recording started for {name}. File will be saved.")
        except Exception as e:
            await query.edit_message_text(f"An error occurred: {e}")

    @staticmethod
    def kill_child_processes(parent_pid):
        parent_process = psutil.Process(parent_pid)

        for child in parent_process.children(recursive=True):
            try:
                if "ffmpeg" in child.name().lower():
                    print(f"Found ffmpeg process with PID {child.pid}")
                    child.send_signal(signal.CTRL_C_EVENT)
                    child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                print(f"Timeout waiting for child process {child.pid} to terminate.")
                child.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        for child in parent_process.children(recursive=True):
            print(f"Killing child process {child.pid}")
            child.send_signal(signal.CTRL_BREAK_EVENT)
            child.send_signal(signal.CTRL_C_EVENT)

        for child in parent_process.children(recursive=True):
            child.terminate()

        psutil.wait_procs(parent_process.children(recursive=True))

    async def handle_kill(self, query, name):
        process = self.active_processes.get(name)
        if process and process.poll() is None:
            try:
                self.kill_child_processes(process.pid)
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print(f"After few seconds, forcing termination.")
                process.kill()
                process.wait()
                print(f"Process '{name}' has been killed.")
            except Exception as e:
                print(f"Error during termination: {e}")
            finally:
                self.active_processes.pop(name, None)
            await query.edit_message_text(f"Recording for {name} has been stopped.")
        else:
            await query.edit_message_text(f"No active recording found for {name}.")

    async def handle_status_command(self, update: Update, context: CallbackContext):
        username = update.message.from_user.username

        if not self.is_authenticated(username):
            await self.request_authentication(update)
            return

        if not self.active_processes:
            await update.message.reply_text("No active recordings.")
            return

        buttons = []
        active_processes_info = []
        ## Note: yt-dlp calls ffmpeg
        # ffmpeg output captured in stderr (actual recording details)
        # yt-dlp output captured in stdout (the starting media info)
        for name, process in self.active_processes.items():
            if process.poll() is None:
                # Capture the output and search for the 'time=' field to get the duration
                duration = None
                match = False
                while not match:
                    line = process.stderr.readline()
                    print(line)
                    if not line:
                        continue

                    match = re.search(r"time=(\d+:\d{2}:\d{2})", line)
                    if match:
                        duration = match.group(1)  # Extracted duration
                        print(f"Duration: {duration}")

                process_info = f"Recording {name} - Duration: {duration}" if duration else f"Recording {name} - Duration info unavailable"
                active_processes_info.append(process_info)

                buttons.append([InlineKeyboardButton(f"Stop {name}", callback_data=f"kill|{name}")])

        if active_processes_info:
            message = "Active recordings:\n" + "\n".join(active_processes_info)
        else:
            message = "No active recordings."

        reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

        await update.message.reply_text(message, reply_markup=reply_markup)

    def run(self):
        print("[*] Bot is starting")
        self.application.run_polling()


if __name__ == "__main__":
    AUTH_FILE = "config/auth.json"
    LINKS_FILE = "config/links.json"
    PASSWORD_FILE = "config/password.txt"

    bot = TelegramBot(AUTH_FILE, LINKS_FILE, PASSWORD_FILE)
    bot.run()
