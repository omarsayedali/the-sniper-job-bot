# 🤖 The Sniper V2.0 - AI-Powered Job Hunter

> **"While I sleep, it hunts."**

A next-generation automation bot that monitors freelance platforms (Mostaql, RemoteOK), filters out noise, and uses **Google Gemini AI** to draft winning proposals automatically.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![Gemini](https://img.shields.io/badge/AI-Gemini_Pro-orange?style=for-the-badge&logo=google)
![Telegram](https://img.shields.io/badge/Alerts-Telegram-blue?style=for-the-badge&logo=telegram)

---
## 📸 Screenshots

### Telegram Alerts
![Telegram Alerts](https://github.com/user-attachments/assets/52fec0d5-3a4e-4ba5-ba84-cfbc9e212510)

### Telegram Profile
![Telegram Profile](https://github.com/user-attachments/assets/278d2213-8b20-4ebc-a6d6-93a9e57610f2)

### Bot Running Status
![Bot Running](https://github.com/user-attachments/assets/eab758ce-6681-446c-b335-a01d2f1842fd)

### Version 2
![Version 2](https://github.com/user-attachments/assets/d5de5bd0-0306-4cf6-85fe-f4c7e2a0a91e)
---

### 🚀 New in V2.0 (The AI Upgrade)
*   **🧠 AI Auto-Drafting:** Integrated `google.generativeai`. The bot reads the job description and writes a custom cover letter tailored to the client's problem.
*   **🛡️ Smart Filters:** No more "WordPress" spam. The bot only alerts on specific keywords (e.g., `Python`, `Flask`, `Scraping`, `Bot`).
*   **⚡ Instant Delivery:** Sends the Job Link + The AI Proposal directly to Telegram.

---

### 🛠️ Tech Stack
*   **Core:** Python 3.x
*   **AI:** Google Gemini API
*   **Data:** Feedparser (RSS), SQLite (Deduplication)
*   **Notifications:** Telegram Bot API
*   **Security:** `.env` for credential management

### 📸 How it Works
1.  **Scan:** Checks RSS feeds every 10 minutes.
2.  **Filter:** Discards 95% of irrelevant jobs.
3.  **Analyze:** Sends valid jobs to Gemini AI.
4.  **Draft:** Generates a persuasive proposal.
5.  **Alert:** Buzzes my phone with the ready-to-send text.

---
*Built by Omar Sayed Ali*
