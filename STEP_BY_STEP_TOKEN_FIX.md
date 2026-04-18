# Step-by-Step: Fix YouTube Token (EASY METHOD)

Your YouTube token has expired. Here's the EASIEST way to fix it:

## 🎯 What You Need:

1. Your Google account that has access to the YouTube channel
2. 10 minutes of time
3. Access to Google Cloud Console

---

## 📝 Step 1: Get OAuth Credentials (If you don't have client_secret.json)

### 1.1 Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

### 1.2 Create OAuth Client ID
1. Click **"+ CREATE CREDENTIALS"**
2. Select **"OAuth client ID"**
3. Application type: **"Desktop app"** (IMPORTANT!)
4. Name: "TikTok to YouTube Bot"
5. Click **"CREATE"**

### 1.3 Download the JSON file
1. Click the download icon next to your new credential
2. Save it to this folder
3. Rename it to: **`client_secret.json`**

---

## 📝 Step 2: Run the Token Refresh Script

### Option A: Double-click method (Easiest)
1. Find `refresh_token.bat` in this folder
2. **Double-click** it
3. Press ENTER when prompted
4. Your browser will open

### Option B: Command line method
1. Open Command Prompt in this folder
2. Type: `py refresh_youtube_token.py`
3. Press ENTER
4. Your browser will open

---

## 📝 Step 3: Authenticate in Browser

1. Browser opens automatically
2. **Select your Google account** (the one with YouTube access)
3. Click **"Continue"** when asked for permissions
4. Grant **YouTube upload** permission
5. You'll see: **"The authentication flow has completed"**
6. Close the browser tab

---

## 📝 Step 4: Copy the Encoded Values

Back in the Command Prompt, you'll see:

```
COPY THESE TO RAILWAY ENVIRONMENT VARIABLES
============================================================

Variable Name: YOUTUBE_CLIENT_SECRET_B64
Value:
eyJpbnN0YWxsZWQiOnsiY2xpZW50X2lkIjoiMTIzNC... (long string)

------------------------------------------------------------

Variable Name: YOUTUBE_TOKEN_JSON
Value:
eyJ0b2tlbiI6InlhMjkuYTBBZlc... (long string)
```

**Copy both values!** They're also saved in `railway_credentials.txt`

---

## 📝 Step 5: Update Railway

### 5.1 Go to Railway Dashboard
Visit: https://railway.app/

### 5.2 Find Your Service
1. Click on your project
2. Click on your service (the one running the TikTok bot)

### 5.3 Update Variables
1. Click **"Variables"** tab
2. Find **`YOUTUBE_CLIENT_SECRET_B64`**
   - Click to edit
   - Paste the first long value
   - Save
3. Find **`YOUTUBE_TOKEN_JSON`**
   - Click to edit
   - Paste the second long value
   - Save

### 5.4 Redeploy
Railway will automatically redeploy with the new token.

---

## ✅ Verify It's Working

After Railway redeploys (takes 2-3 minutes), check the logs:

**Before (broken):**
```
Saved YouTube token could not be refreshed: invalid_grant
```

**After (working):**
```
✓ YouTube API authenticated successfully!
```

---

## 🆘 Troubleshooting

### "Python was not found"
Try these commands instead:
- `py refresh_youtube_token.py`
- `python3 refresh_youtube_token.py`
- Or install Python from: https://www.python.org/downloads/

### "client_secret.json not found"
You need to download it from Google Cloud Console first (see Step 1)

### "redirect_uri_mismatch"
You created **Web app** instead of **Desktop app**. Delete it and create Desktop app.

### "Access blocked: This app's request is invalid"
Your OAuth consent screen needs to be configured in Google Cloud Console.

---

## 🎉 Done!

Once you update Railway with the new token:
- ✅ Videos will download automatically
- ✅ Videos will split into 38-second parts
- ✅ Watermark will be added (centered, black text)
- ✅ Videos will upload to YouTube automatically
- ✅ All parts will have the same title (no part numbers)

---

## 📞 Need Help?

If you're stuck, the encoded values are saved in:
- `railway_credentials.txt` (you can open this file and copy from there)

The token is valid for a long time and will auto-refresh, so you won't need to do this often!
