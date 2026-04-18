# How to Get client_secret.json from Google Cloud Console

## Step-by-Step with Screenshots Guide

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/apis/credentials

**Make sure you're signed in with the Google account that has access to your YouTube channel!**

---

### 2. Enable YouTube Data API v3 (if not already enabled)

1. Click on **"+ ENABLE APIS AND SERVICES"** at the top
2. Search for: **"YouTube Data API v3"**
3. Click on it
4. Click **"ENABLE"**
5. Go back to Credentials page

---

### 3. Configure OAuth Consent Screen (if not done)

1. Click **"OAuth consent screen"** in the left sidebar
2. Select **"External"** (unless you have a Google Workspace)
3. Click **"CREATE"**
4. Fill in:
   - App name: "TikTok to YouTube Bot"
   - User support email: Your email
   - Developer contact: Your email
5. Click **"SAVE AND CONTINUE"**
6. Click **"SAVE AND CONTINUE"** on Scopes page (no changes needed)
7. Click **"SAVE AND CONTINUE"** on Test users page
8. Click **"BACK TO DASHBOARD"**

---

### 4. Create OAuth Client ID

1. Click **"Credentials"** in the left sidebar
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"OAuth client ID"**

---

### 5. Configure the OAuth Client

**⚠️ IMPORTANT: Choose the correct application type!**

1. Application type: **"Desktop app"** (NOT Web application!)
2. Name: "TikTok to YouTube Bot" (or any name you like)
3. Click **"CREATE"**

---

### 6. Download the Credentials

1. You'll see a popup with your Client ID and Client Secret
2. Click **"DOWNLOAD JSON"** button
3. Save the file to your computer

---

### 7. Rename and Move the File

1. Find the downloaded file (usually in Downloads folder)
2. It will be named something like: `client_secret_123456789-abc.apps.googleusercontent.com.json`
3. **Rename it to:** `client_secret.json`
4. **Move it to:** `F:\Flutter Projects\New folder\tiktok_to_yt_script\`

---

### 8. Verify the File

The file should look like this when you open it:

```json
{
  "installed": {
    "client_id": "123456789-abcdefg.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-abcdefghijklmnop",
    "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
  }
}
```

**Key things to check:**
- It should have `"installed"` at the top (not `"web"`)
- If it says `"web"` instead, you created the wrong type - delete it and create a **Desktop app** instead

---

## ✅ Done!

Once you have `client_secret.json` in the correct folder, you can proceed to run the token refresh script.

---

## 🆘 Troubleshooting

### "I don't see the CREATE CREDENTIALS button"
- Make sure you're on the Credentials page
- URL should be: https://console.cloud.google.com/apis/credentials

### "I created Web app instead of Desktop app"
1. Go back to Credentials page
2. Find your OAuth client in the list
3. Click the trash icon to delete it
4. Create a new one as **Desktop app**

### "The file has 'web' instead of 'installed'"
You downloaded the wrong type. Delete the credential and create a **Desktop app** instead.

### "I can't find the downloaded file"
- Check your Downloads folder
- Look for files starting with `client_secret_`
- The file extension is `.json`

---

## 📞 Still Need Help?

If you're stuck, you can:
1. Share a screenshot of what you're seeing (hide any sensitive info)
2. Describe which step you're stuck on
3. Check if you're signed in with the correct Google account
