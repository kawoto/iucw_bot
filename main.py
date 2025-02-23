import os
import logging
import requests
from lxml import html
from grade_extractor import GradeExtractor
from tenacity import retry, stop_after_attempt, wait_exponential
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Telegram Bot Token
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN)
if not BOT_TOKEN:
    raise ValueError("BOT TOKEN NOT FOUND! please set it in GitHub secrets.")

# Login URLs
LOGIN_URL = "https://196.191.244.97/Account/Login"
RESULT_PAGE_URL = "https://196.191.244.97/Students/Grades"

# Headers for HTTP requests
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": LOGIN_URL
}

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Store user sessions {user_id: {"username": username, "password": password}}
user_sessions = {}

async def start(update: Update, context: CallbackContext) -> None:
    """Send a welcome message with login button."""
    keyboard = [[InlineKeyboardButton("Login", callback_data="login")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Welcome! Please log in to continue.", reply_markup=reply_markup)

async def handle_button_click(update: Update, context: CallbackContext) -> None:
    """Handle inline button clicks."""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "login":
        await query.message.reply_text("Please enter your username:")
        context.user_data["awaiting_username"] = True
    elif query.data == "retry":
        if user_id in user_sessions:
            username = user_sessions[user_id]["username"]
            password = user_sessions[user_id]["password"]
            result = login_and_fetch_result(username, password)
            await query.message.reply_text(result)
        else:
            await query.message.reply_text("⚠️ Please log in first using /start.")

async def handle_text(update: Update, context: CallbackContext) -> None:
    """Handle user input for login or fetching grades."""
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if context.user_data.get("awaiting_username"):
        context.user_data["username"] = text
        context.user_data["awaiting_username"] = False
        context.user_data["awaiting_password"] = True
        await update.message.reply_text("Now enter your password:")
        return
    
    if context.user_data.get("awaiting_password"):
        username = context.user_data.get("username")
        password = text
        context.user_data["awaiting_password"] = False
        
        session = requests.Session()
        login_successful = login(session, username, password)
        
        if login_successful:
            user_sessions[user_id] = {"username": username, "password": password}
            result = fetch_grades(session)
            await update.message.reply_text("✅ Login successful! Click retry anytime to check for new results.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Retry", callback_data="retry")]]))
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("❌ Login failed. Please try again.")
            login(session, username, password)
        return

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def fetch_page_with_retry(url, session):
    response = session.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def login(session, username, password):
    """Logs in the user and returns True if successful."""
    try:
        response = fetch_page_with_retry(LOGIN_URL, session)
        tree = html.fromstring(response.content)
        
        csrf_token = tree.xpath("//input[@name='__RequestVerificationToken']/@value")
        if not csrf_token:
            return False
        
        payload = {
            "Email": username,
            "Password": password,
            "__RequestVerificationToken": csrf_token[0],
        }
        
        response = session.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=15)
        return response.url != LOGIN_URL
    except requests.exceptions.RequestException as e:
        logging.error(f"Login request failed: {e}")
        return False

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=2, min=5, max=30))
def format_grades(grades):
    """Formats grades into a neat table."""
    if not grades:
        return "No grades found."

    formatted_grades = "📖 *Your Grades:*\n"
    formatted_grades += "-------------------------------------------------\n"
    formatted_grades += "| Course                          | Grade | Mark |\n"
    formatted_grades += "-------------------------------------------------\n"

    for grade in grades:
        course = grade["Course"][:30] + "..." if len(grade["Course"]) > 30 else grade["Course"]
        formatted_grades += f"| {course:<30} | {grade['Grade']:<5} | {grade['Mark']:<4} |\n"

    formatted_grades += "-------------------------------------------------\n"
    return formatted_grades


def fetch_grades(session):
    """Fetch grades for a logged-in session with formatted output."""
    try:
        result_page = fetch_page_with_retry(RESULT_PAGE_URL, session)
        extractor = GradeExtractor(result_page.text)
        grades = extractor.extract_grades()
        gpa_summary = extractor.extract_gpa_summary()

        formatted_grades = format_grades(grades)
        formatted_gpa = f"📊 *GPA Summary:*\n" \
                        f"   - Grade Point: {gpa_summary.get('Grade Point', 'N/A')}\n" \
                        f"   - Credit Hour: {gpa_summary.get('Credit Hour', 'N/A')}\n" \
                        f"   - GPA: {gpa_summary.get('GPA', 'N/A')}"

        return f"{formatted_grades}\n{formatted_gpa}"

    except requests.exceptions.RequestException as e:
        return f"❌ Error fetching grades: {e}"

def login_and_fetch_result(username, password):
    """Logs in and fetches student results."""
    session = requests.Session()
    if login(session, username, password):
        return fetch_grades(session)
    return "❌ Login failed. Please try again."

def main():
    app = Application.builder().token(BOT_TOKEN).connect_timeout(15).read_timeout(30).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("Bot is running...")
    app.run_polling(timeout=50)

if __name__ == "__main__":
    main()
