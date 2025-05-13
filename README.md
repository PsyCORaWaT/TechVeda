# TechVeda

**TechVeda** is a collaborative note sharing platform designed to empower students by making knowledge accessible and easy to share. Upload, organize, and discover study materials with a modern, responsive interface.

---

## Features

- 📤 **Upload & Share:** Easily upload notes and files by subject.
- 📁 **Organized Library:** Browse and search files by subject, type, or uploader.
- 🔍 **Search & Filter:** Quickly find what you need with advanced filters.
- 👤 **User Profiles:** Manage your profile, bio, and social links.
- 🌙 **Light/Dark Mode:** Toggle between light and dark themes.
- 🔔 **Flash Alerts:** Get instant feedback on your actions.
- 🤝 **Community Links:** Join our Discord and GitHub to contribute and connect.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Flask
- Google Drive API credentials (for file storage)
- See `requirements.txt` for all dependencies

### Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/TechVeda.git
    cd TechVeda
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up Google Drive API:**
    - Place your `credentials.json` in the project root.

4. **Run the app:**
    ```bash
    python app.py
    ```
    The app will be available at [http://localhost:5000](http://localhost:5000).

---

## Folder Structure

```
TechVeda/
│
├── app.py
├── config.py
├── db.py
├── users.json
├── metadata.json
├── static/
│   ├── style.css
│   ├── script.js
│   └── dash.css
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── login.html
│   ├── register.html
│   └── edit_profile.html
└── ...
```

---

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

- Join our [Discord](https://discord.gg/your-discord-link)
- Star us on [GitHub](https://github.com/your-github-link)

---

## License

[MIT](LICENSE)

---

**Empowering students with shared knowledge.**
