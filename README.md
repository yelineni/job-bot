# Job Bot - Automated Job Search & Email Notifications

An automated job search bot that runs on GitHub Actions, scrapes job postings from multiple job boards, filters by keywords and companies, and sends you email notifications every hour.

## Features

✅ **Automated Hourly Searches** - Runs every hour via GitHub Actions  
✅ **Multi-Source Scraping** - LinkedIn, Indeed, Google Jobs, Dice, ZipRecruiter  
✅ **Smart Filtering** - Priority companies, roles, and keywords  
✅ **Deduplication** - Tracks sent jobs (by URL + company combo) to avoid duplicates  
✅ **Error Alerts** - Sends full traceback on failures  
✅ **Time-Based Filtering** - Only searches between 9 AM - 8 PM EST  

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yelineni/job-bot.git
cd job-bot
```

### 2. Add GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions**

Add these secrets:
- `EMAIL_USER`: Your Gmail address
- `EMAIL_PASS`: Gmail App Password (not your regular password)
- `RECIPIENT_EMAIL`: Where to send job notifications
- `ERROR_NOTIFICATION_EMAIL`: Where to send error alerts

### 3. Create Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Factor Authentication
3. Go to **App passwords** → Select Mail & Windows Computer
4. Copy the generated 16-char password
5. Use this as `EMAIL_PASS` secret (not your regular Gmail password)

### 4. Customize Search Parameters

Edit `src/searchjobs.py`:
- **PRIORITY_COMPANIES**: List of companies to search
- **ROLES**: Job titles to search for
- **CORE_KEYWORDS**: Required keywords in job postings
- **USER_TZ**: Your timezone

### 5. Run Workflow

The workflow runs automatically every hour. To manually trigger:
- Go to **Actions** tab → **Job Bot Workflow** → **Run workflow**

## File Structure

```
job-bot/
├── .github/
│   └── workflows/
│       └── jobbot.yml          # GitHub Actions workflow
├── src/
│   └── searchjobs.py           # Main bot logic
├── sent_jobs.json              # Tracks sent jobs (auto-generated)
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
└── README.md                  # This file
```

## How It Works

1. **Runs every hour** (9 AM - 8 PM EST)
2. **Searches priority companies first** for matching roles
3. **Falls back to general search** if fewer than 10 jobs found
4. **Filters out duplicates** using `sent_jobs.json` (URL + company combo)
5. **Sends top 10 jobs** via email if new listings found
6. **Commits changes** to `sent_jobs.json` back to repo

## Deduplication Logic

Jobs are considered duplicates if they have the **same URL AND same company**, even if the role differs. This prevents:
- Resending the exact same job posting
- Multiple roles from same company at same URL are deduplicated

## Troubleshooting

### Emails not sending?
- Verify Gmail App Password (not regular password)
- Check 2-Factor Authentication is enabled
- Ensure secrets are added correctly in GitHub

### No jobs found?
- Check if current time is between 9 AM - 8 PM EST
- Verify keywords are specific enough
- Check job boards aren't blocking requests

### Workflow failing?
- Check **Actions** tab for error logs
- Look for error notification emails
- Verify `requirements.txt` packages install correctly

## License

MIT License - Feel free to fork and customize!