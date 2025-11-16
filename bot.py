# bot.py
import os
import json
import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

# ENV vars
TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
SHEET_KEY = os.getenv("SHEET_KEY")
TEST_CHAT_ID = os.getenv("TEST_CHAT_ID")

if not TOKEN:
    raise Exception("BOT_TOKEN env var missing")
if not GOOGLE_CREDS:
    raise Exception("GOOGLE_CREDS env var missing")
if not SHEET_KEY:
    raise Exception("SHEET_KEY env var missing")

# Google auth
creds_dict = json.loads(GOOGLE_CREDS)
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SHEET_KEY).sheet1

bot = Bot(token=TOKEN)


async def send_test_message():
    if not TEST_CHAT_ID:
        print("TEST_CHAT_ID not set — skipping test message.")
        return
    try:
        await bot.send_message(
            chat_id=TEST_CHAT_ID,
            text=f"✅ Bot started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.HTML,
        )
        print("Test message sent.")
    except Exception as e:
        print("Failed to send test message:", e)


async def watch_sheet_loop():
    last_len = 0
    while True:
        print("Bot alive:", datetime.now())   # 🔥 heartbeat za Render

        try:
            rows = sheet.get_all_values()
            if len(rows) > last_len:
                new_rows = rows[last_len:]
                for r in new_rows:
                    msg = "🆕 Nova prijava:\n" + "\n".join(r)
                    if TEST_CHAT_ID:
                        await bot.send_message(chat_id=TEST_CHAT_ID, text=msg)
                last_len = len(rows)
        except Exception as e:
            print("Sheet watch error:", e)

        await asyncio.sleep(10)


async def main():
    print("Bot starting...")
    await send_test_message()
    await watch_sheet_loop()


if __name__ == "__main__":
    asyncio.run(main())
