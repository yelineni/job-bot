import os
import json
import traceback
import smtplib
import pandas as pd
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jobspy import scrape_jobs
from dotenv import load_dotenv

load_dotenv()

def load_sent_jobs():
    """Load previously sent jobs from JSON file."""
    if os.path.exists("sent_jobs.json"):
        with open("sent_jobs.json", "r") as f:
            return json.load(f)
    return {}

def save_sent_jobs(sent_jobs):
    """Save updated sent jobs to JSON file."""
    with open("sent_jobs.json", "w") as f:
        json.dump(sent_jobs, f, indent=4)

def mark_job_sent(job_url, company, sent_jobs):
    """Mark a job as sent with a timestamp."""
    sent_jobs[job_url] = {
        "company": company,
        "sent_at": datetime.now().isoformat()
    }

def clean_old_jobs(sent_jobs, days=7):
    """Remove jobs older than 'days' from the tracking dictionary."""
    cutoff = datetime.now() - timedelta(days=days)
    to_remove = [
        url for url, data in sent_jobs.items() 
        if datetime.fromisoformat(data["sent_at"]) < cutoff
    ]
    for url in to_remove:
        del sent_jobs[url]

def send_email(df, sent_jobs):
    """Send job listings email via Gmail."""
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")  # 16-character App Password
    recipient = os.environ.get("RECIPIENT_EMAIL")

    msg = MIMEMultipart()
    msg['Subject'] = f"Top 10 Analyst Jobs - {datetime.now().strftime('%I %p')}"
    msg['From'] = sender
    msg['To'] = recipient

    # Build the HTML content
    html = f"<h3>New Postings (Past 3 Hours)</h3><p>Found {len(df)} matching roles:</p><ol>"
    for _, row in df.iterrows():
        company = row['company'] if row['company'] else "Unknown Company"
        site = row['site_name'] if 'site_name' in row else "Job Board"
        html += f"<li><b>[{site.upper()}] {row['title']}</b> at <i>{company}</i><br><a href='{row['job_url']}'>View Posting</a></li><br>"
        mark_job_sent(row['job_url'], company, sent_jobs)
    html += "</ol>"
    
    msg.attach(MIMEText(html, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Secure the connection for Gmail
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully via Gmail.")
    except Exception as e:
        print(f"Email error: {e}")
        send_error_email(f"Failed to send job email: {e}", traceback.format_exc())

def send_error_email(error_msg, full_traceback):
    """Send error notification email via Gmail."""
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("ERROR_NOTIFICATION_EMAIL")

    msg = MIMEMultipart()
    msg['Subject'] = f"🚨 Job Bot Error - {datetime.now().strftime('%I %p')}"
    msg['From'] = sender
    msg['To'] = recipient

    error_html = f"<h2>An error occurred</h2><p><b>Error:</b> {error_msg}</p><pre>{full_traceback}</pre>"
    msg.attach(MIMEText(error_html, 'html'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls() 
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Error notification sent.")
    except Exception as e:
        print(f"Failed to send error email: {e}")

def run_job_search():
    """Main function to scrape and process jobs with bot-detection bypass."""
    sent_jobs = load_sent_jobs()
    clean_old_jobs(sent_jobs)

    try:
        # We add more specific parameters to look like a real browser
        jobs = scrape_jobs(
            site_name=["linkedin", "indeed", "glassdoor"],
            search_term="Data Analyst",
            location="United States",
            results_wanted=30,
            hours_old=3, # Increased slightly to ensure we find enough data
            country_indeed='USA',
            # Adding a delay helps avoid the 'Example Domain' bot-block
            enforce_desktop=True 
        )

        if not jobs.empty:
            # 1. REMOVE any jobs that point to 'example.com'
            jobs = jobs[~jobs['job_url'].str.contains("example.com", na=False)]
            
            # 2. Filter out jobs already sent
            new_jobs = jobs[~jobs['job_url'].isin(sent_jobs.keys())]
            
            if not new_jobs.empty:
                # Get top 10 relevant jobs
                final_top_10 = new_jobs.head(10)
                send_email(final_top_10, sent_jobs)
                save_sent_jobs(sent_jobs)
            else:
                print("Zero new jobs found.")
        else:
            print("No jobs found.")

    except Exception as e:
        print(f"Critical error: {e}")
        send_error_email(str(e), traceback.format_exc())
