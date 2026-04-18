# Manual YouTube Token Update (No Python Needed)

Since Python isn't properly installed on your system, here's an alternative method:

## Option 1: Install Python First (Recommended)

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.12.x"
   - Run the installer
   - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation!

2. **After installation:**
   - Close and reopen Command Prompt
   - Run: `python refresh_youtube_token.py`

---

## Option 2: Use Online Python (Quick Method)

If you don't want to install Python, you can use an online Python environment:

### Step 1: Go to Replit
Visit: https://replit.com/

### Step 2: Create New Repl
1. Click "Create Repl"
2. Select "Python"
3. Name it: "YouTube Token Generator"

### Step 3: Upload Files
Upload these two files to Replit:
- `client_secret.json`
- `refresh_youtube_token.py`

### Step 4: Run
Click the "Run" button and follow the authentication prompts.

---

## Option 3: Manual Method (Most Complex)

If you can't run Python at all, you can manually authenticate:

### Step 1: Install Required Libraries Locally

You'll need to install Python first (see Option 1).

### Step 2: Run Authentication Manually

Open Command Prompt and run these commands one by one:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
python refresh_youtube_token.py
```

---

## Option 4: Ask Someone to Help

If you have a friend or colleague with Python installed, they can:
1. Run the script on their computer
2. Send you the encoded values
3. You paste them in Railway

⚠️ **Security Note:** Only do this with someone you trust, as they'll have access to your YouTube credentials temporarily.

---

## Easiest Solution: Install Python

**I strongly recommend Option 1** - installing Python properly. It takes 5 minutes and will make everything work smoothly.

### Quick Python Installation:

1. Go to: https://www.python.org/downloads/
2. Download and run installer
3. ✅ Check "Add Python to PATH"
4. Click "Install Now"
5. Close and reopen Command Prompt
6. Run: `python refresh_youtube_token.py`

---

## After You Get the Token

Once you have the encoded values (from any method above), update Railway:

1. Go to: https://railway.app/
2. Select your project → service
3. Go to Variables tab
4. Update:
   - `YOUTUBE_CLIENT_SECRET_B64`
   - `YOUTUBE_TOKEN_JSON`
5. Save and redeploy

---

## Need Help?

Let me know which option you'd like to try and I can provide more detailed instructions!
