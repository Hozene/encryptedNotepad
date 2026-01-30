# Encrypted Notepad

A secure, web-based notepad app designed with a **Zero-Knowledge** architecture. All notes are encrypted on the client side.

1. **Clone the repository**
```
git clone Hozene/encryptedNotepad
cd encryptedNotepad
```

2. **Install dependencies**
```
pip install -r requirements.txt
```

3. **Configure env variables**
- Create a .env file in root directory
```
SECRET_KEY=your_secret_key
```

4. **Run the application**

The database will be created automatically on the first run.
```
python app.py
```
