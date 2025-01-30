from telegram import Update
from telegram.ext import BaseHandler, CallbackContext


class AccountHandler(BaseHandler):
    def __init__(self, allowed_usernames):
        super().__init__(callback=self.callback)
        self.allowed_usernames = allowed_usernames

    async def callback(self, update: Update, context: CallbackContext):
        try:
            await update.callback_query.answer()
        except:
            pass

        try:
            await update.effective_message.reply_text('You do not have access')
        except:
            await update.effective_chat.send_message('Unauthorized access')

    def check_update(self, update: Update):
        if update.effective_user.username not in self.allowed_usernames:
            return True

        return False