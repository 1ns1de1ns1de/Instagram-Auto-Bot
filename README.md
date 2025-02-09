# 🤖 Instagram Auto Bot

## 📝 Overview

Instagram Auto Bot is a powerful Python script that automates various Instagram interactions using Selenium WebDriver. This tool provides a range of features to streamline your Instagram activities, including:

- Automated Direct Messaging (DM)
- Liking Latest Posts
- Commenting on Posts
- Following Users
- Cookie Management

⚠️ **Disclaimer**: Use this tool responsibly and in compliance with Instagram's terms of service.

## 🌟 Features

- **Automated DM Sending**: Send personalized messages to multiple users
- **Post Interaction**: 
  - Like latest posts
  - Comment on latest posts
- **User Management**: 
  - Follow users automatically
  - Manage multiple Instagram accounts
- **Smart Delay Mechanism**: Randomized delays to mimic human behavior
- **Robust Cookie Management**: Save and load session cookies
- **Detailed Logging**: CSV logs for all interactions

## 🛠 Prerequisites

### Software Requirements
- Python 3.8+
- Google Chrome
- ChromeDriver

### Required Python Packages
- selenium
- chromedriver_autoinstaller
- tqdm
- colorama
- pickle

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/1ns1de1ns1de/instagram-auto-bot.git
cd instagram-auto-bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## 📋 Preparation

### Create Necessary Files
1. `data.txt`: List of usernames to interact with
2. `message.txt`: Messages for DM (can use `{username}` as placeholder)
3. `comment.txt`: Comments for posts

### Folder Structure
```
instagram-auto-bot/
│
├── cookies/             # Stores session cookies
├── data.txt             # List of target usernames
├── message.txt          # DM message templates
├── comment.txt          # Comment templates
├── dm_log.csv           # DM interaction logs
├── follow_log.csv       # Follow interaction logs
└── like_comment_log.csv # Like & Comment logs
```

## 🎮 Usage

### Menu Options
1. **Start Selenium**: Initialize and save cookies for manual login
2. **Update Delay Settings**: Customize interaction delays
3. **Auto DM**: Send automated direct messages
4. **Like & Comment**: Automatically like and comment on latest posts
5. **Follow Users**: Automatically follow listed users

### Running the Script
```bash
python bot.py
```

## ⚙️ Configuration

### Delay Settings
- Customize interaction delays between actions
- Helps avoid detection by Instagram's anti-spam mechanisms
- Default range: 20-50 seconds

### Customization
- Modify `default_delay_range` to adjust interaction speed
- Add more robust selectors for different Instagram page structures

## 🔒 Security & Ethics

- **Always respect Instagram's Terms of Service**
- Use the bot responsibly
- Be aware of potential account restrictions
- Do not spam or engage in harmful activities

## 🐛 Troubleshooting

- Ensure Chrome and ChromeDriver are up to date
- Check internet connection
- Verify target usernames and message templates
- Instagram may change page structures, so update selectors if needed

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚠️ Legal Notice

This script is for educational purposes only. The user assumes full responsibility for any consequences of using this tool.

## 📧 Contact

Project Link: [https://github.com/1ns1de1ns1de/instagram-auto-bot](https://github.com/1ns1de1ns1de/instagram-auto-bot)

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Happy Automating!** 🚀📱
