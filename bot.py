import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

# ================== EDIT THESE ==================
BOT_TOKEN = "8585116374:AAFJGHDW1riRSEMEwvouWYeRL6TDTINPYcc"
USERNAME = "24L31A4608"
PASSWORD = "Bhuvan@123"

LOGIN_URL = "https://webprosindia.com/vignanit/"
ATTENDANCE_URL = "https://webprosindia.com/vignanit/StudentMaster.aspx"
# ================================================

# AES encryption (same as website JS)
def encrypt_password(password):
    key = b'8701661282118308'
    iv = b'8701661282118308'
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(password.encode(), AES.block_size))
    return base64.b64encode(encrypted).decode()

async def show_attendance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() != "show":
        return

    try:
        session = requests.Session()

        # Step 1: Get login page to extract VIEWSTATE
        response = session.get(LOGIN_URL)
        soup = BeautifulSoup(response.text, "html.parser")

        viewstate = soup.find(id="__VIEWSTATE")["value"]
        eventvalidation = soup.find(id="__EVENTVALIDATION")["value"]

        encrypted_pwd = encrypt_password(PASSWORD)

        # Step 2: Login
        payload = {
            "__VIEWSTATE": viewstate,
            "__EVENTVALIDATION": eventvalidation,
            "txtId2": USERNAME,
            "txtPwd2": PASSWORD,
            "hdnpwd2": encrypted_pwd,
            "imgBtn2.x": "0",
            "imgBtn2.y": "0"
        }

        session.post(LOGIN_URL, data=payload)

        # Step 3: Get attendance page
        attendance_page = session.get(ATTENDANCE_URL)
        soup = BeautifulSoup(attendance_page.text, "html.parser")

        tables = soup.find_all("table")

        if not tables:
            await update.message.reply_text("Unable to fetch attendance.")
            return

        # -------- SIMPLE PARSING (Basic Version) --------
        text_output = ""

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = [col.text.strip() for col in row.find_all(["td", "th"])]
                if cols:
                    text_output += " | ".join(cols) + "\n"

        if not text_output:
            text_output = "Attendance data not found."

        await update.message.reply_text(text_output[:4000])

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), show_attendance))

print("Bot Running...")
app.run_polling()