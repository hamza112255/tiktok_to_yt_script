# YouTube API Quota Rotation System

## 🚀 Quick Start

### You Have 3 Projects? Follow These Steps:

#### 1️⃣ Authenticate Locally
```bash
python authenticate_all_projects.py
```

#### 2️⃣ For Railway Deployment
```bash
python encode_for_railway_rotation.py
```
Then add the variables from `railway_rotation_credentials.txt` to Railway.

#### 3️⃣ Push to GitHub
```bash
git add .
git commit -m "Add YouTube quota rotation"
git push origin main
```

Done! 🎉

---

## 📊 What This Does

- **3x More Quota**: 30,000 units/day instead of 10,000
- **~150 Uploads/Day**: Instead of ~50
- **Automatic Rotation**: Based on day of month
- **Same Channel**: All uploads to your YouTube channel

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `authenticate_all_projects.py` | Authenticate all projects |
| `encode_for_railway_rotation.py` | Encode for Railway |
| `check_rotation_status.py` | Check current status |
| `RAILWAY_DEPLOYMENT_CHECKLIST.md` | Step-by-step guide |
| `COMPLETE_SETUP_SUMMARY.md` | Full overview |

---

## 🔄 How Rotation Works

```
Day 1, 4, 7, 10... → Project 1
Day 2, 5, 8, 11... → Project 2
Day 3, 6, 9, 12... → Project 3
```

Automatic. No manual switching needed.

---

## ✅ Checklist

- [ ] Created 3 Google Cloud projects
- [ ] Downloaded `client_secret_1.json`, `2.json`, `3.json`
- [ ] Run `python authenticate_all_projects.py`
- [ ] Run `python encode_for_railway_rotation.py`
- [ ] Added 6 variables to Railway
- [ ] Pushed to GitHub

---

## 📚 Full Documentation

- **Local Setup**: `YOUTUBE_QUOTA_ROTATION_GUIDE.md`
- **Railway Setup**: `RAILWAY_ROTATION_DEPLOYMENT.md`
- **Quick Reference**: `QUICK_START_ROTATION.txt`
- **Visual Guide**: `ROTATION_DIAGRAM.txt`

---

## 🆘 Need Help?

1. Check `COMPLETE_SETUP_SUMMARY.md` for overview
2. Follow `RAILWAY_DEPLOYMENT_CHECKLIST.md` step-by-step
3. Run `python check_rotation_status.py` to verify setup

---

**Ready?** Start with: `python authenticate_all_projects.py`
