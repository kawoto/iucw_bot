# 📚 Telegram Exam Results Bot

A Telegram bot that allows students to log in and retrieve their exam results from their college portal.

## 🚀 Features
- Secure login with username and password
- Fetches grades and GPA summary from the student portal
- Inline buttons for login and retry options
- Formatted and structured results display
- Implements retries and timeouts for better performance

## 🛠️ Technologies Used
- **Python** (Backend Logic)
- **logging**(Login verification)
- **Telegram Bot API** (User Interaction)
- **Requests** (HTTP Requests Handling)
- **BeautifulSoup & LXML** (Web Scraping)
- **Tenacity** (Retry Mechanism)
- **Telegram.ext** (Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext)

---

## 📌 Setup & Installation
### Prerequisites
Ensure you have Python 3.x installed along with the required dependencies.

### Installation Steps
1. **Clone the repository**
   ```sh
   git clone https://github.com/kawoto/iucw_bot.git
   cd iucw_bot
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set up the Telegram Bot**
   - Create a bot on [BotFather](https://t.me/BotFather) and get the `BOT_TOKEN`
   - Replace `BOT_TOKEN` in the script with your actual bot token

4. **Run the bot**
   ```sh
   python bot.py
   ```

---

## 📝 Usage
1. Start the bot by sending `/start`
2. Click **Login** and enter your credentials
3. If login is successful, your grades will be displayed
4. Use **Retry** to check for updated results

---

## 🛡 Security & Best Practices
- Avoid hardcoding sensitive credentials
- Use **environment variables** for the bot token
- Implement **rate limiting** to prevent abuse

---

## 🔧 Configuration
- Modify `LOGIN_URL` and `RESULT_PAGE_URL` to match your college portal
- Adjust `HEADERS` if the portal requires specific user-agent headers

---

## 📌 Example Output
```
📖 Your Grades:
-------------------------------------------------
| Course                          | Grade | Mark |
-------------------------------------------------
| Prepare and Implement Human Res | B+    | 87   |
| Perform Human Resource activiti | B+    | 87   |
| Organize Office Records         | C+    | 79   |
-------------------------------------------------

📊 GPA Summary:
   - Grade Point: 3.5
   - Credit Hour: 15
   - GPA: 3.6
```
---
## 🤝 Contributions
Feel free to fork this repository and submit pull requests!
---
## 📜 License
This project is licensed under the MIT License.
---
## 📬 Contact
For questions or feedback, reach out via [Telegram](https://t.me/kawoto) or open an issue.

