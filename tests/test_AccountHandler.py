from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat
from telegram.ext import CallbackContext
from AccountHandler import AccountHandler
import pytest

@pytest.mark.asyncio
async def test_callback():
    allowed_users = ["valid_user"]
    handler = AccountHandler(allowed_users)

    # Mock Update
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = MagicMock(spec=User)
    mock_update.effective_user.username = "unauthorized_user"

    # Mock Message
    mock_update.effective_message = MagicMock(spec=Message)
    mock_update.effective_message.reply_text = AsyncMock()

    # Mock Chat
    mock_update.effective_chat = MagicMock(spec=Chat)
    mock_update.effective_chat.send_message = AsyncMock()

    # Mock Callback Query
    mock_update.callback_query = MagicMock()
    mock_update.callback_query.answer = AsyncMock()

    # Mock Context
    mock_context = MagicMock(spec=CallbackContext)

    # Run callback
    await handler.callback(mock_update, mock_context)

    # Assert reply_text was called
    mock_update.effective_message.reply_text.assert_called_once_with("You do not have access")

    # Ensure fallback to effective_chat.send_message in case reply_text fails
    mock_update.effective_chat.send_message.assert_not_called()

@pytest.mark.parametrize(
    "username, expected",
    [
        ("valid_user", False),  # Should return False because the user is allowed
        ("unauthorized_user", True),  # Should return True because the user is not in allowed_usernames
    ],
)
def test_check_update(username, expected):
    allowed_users = ["valid_user"]
    handler = AccountHandler(allowed_users)

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = MagicMock(spec=User)
    mock_update.effective_user.username = username

    assert handler.check_update(mock_update) == expected
