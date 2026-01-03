# AI Customer Support Bot 🤖

Multi-platform AI-powered customer support chatbot for **Telegram & WhatsApp**, built with **Python FastAPI** and powered by **OpenAI / Gemini**.

Designed for small and medium businesses to automate customer replies, FAQs, order status, and booking inquiries.

---

## 🚀 Features

- ✅ Telegram Bot (Webhook based)
- ✅ WhatsApp Cloud API (structure ready)
- ✅ Multi-AI support (OpenAI / Gemini)
- ✅ Auto-reply to customer messages
- ✅ FAQ handling
- ✅ Order status & booking info (API / mock)
- ✅ Message & response logging
- ✅ Clean, scalable architecture

---

## 🧠 Tech Stack

- Python 3.10+
- FastAPI
- Telegram Bot API
- WhatsApp Cloud API
- OpenAI API
- Google Gemini API
- SQLite
- Webhooks

---

## 📂 Project Structure

ai-customer-support-bot/
├── app/
│ ├── main.py
│ ├── config.py
│ ├── bots/
│ ├── ai/
│ ├── services/
│ ├── admin/
│ └── models/
├── database/
├── .env.example
├── requirements.txt
└── README.md


---

## ⚙️ Setup & Installation

```bash
git clone https://github.com/yourusername/ai-customer-support-bot.git
cd ai-customer-support-bot

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux / Mac

pip install -r requirements.txt
