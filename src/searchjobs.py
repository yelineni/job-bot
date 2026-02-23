import os
import smtplib
import json
from datetime import datetime
import pytz
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jobspy import scrape_jobs
import pandas as pd
import traceback

# --- CONFIGURATION ---
USER_TZ = "America/New_York"
SENT_JOBS_FILE = "sent_jobs.json"

PRIORITY_COMPANIES = ["7-ELEVEN", "ABN", "ACCENTURE", "ADOBE", "ADP", "ADVITHRI", "AECOM", "AKAMAI", "ALLIANCE", "ALTEN", "ALTIMETRIK", "AMAZON", "AMAZON.COM", "AMGEN", "ANSYS", "ANTRA", "APTIV", "ARIBA", "ARISTA", "ARYADIT", "ASANA", "ASCENDION", "ASRA", "AT&T", "ATT", "ATLASSIAN", "ATOS", "ATRIX", "AUDIBLE", "AUTODESK", "AVCO", "AXTRIA", "BAHWAN", "BAIN", "BATTELLE", "BCT", "BDO", "BEAN", "BEST", "BIRLASOFT", "BITWISE", "BLACK ROCK", "BLIZZARD", "BLOCK", "BLOOMBERG", "BOSTON", "BRILLIO", "BROOKHAVEN", "BRUHAT", "BURNS", "BYTEDANCE", "C3", "CAPGEMINI", "CAREMARK", "CARESOFT", "CGI", "CHARTER", "CHEWY", "CIGNITI", "CITIUSTECH", "CLOUDBERG", "CLOUDFLARE", "COFORGE", "COGNIER", "COGNIZANT", "COLLABERA", "COLLABORATE", "COMCAST", "COMPREHENSIVE", "COMPUNNEL", "CONFLUENT", "CONFLUX", "CORNERSTONE", "CORTEVA", "COSTCO", "COTIVITI", "COUPANG", "CROWE", "CRUISE", "CSC", "CVS", "DANA-FARBER", "DATABRICKS", "DELOITTE", "DENKEN", "DEVOIR", "DIGITALTREE", "DOCUSIGN", "DOORDASH", "DROPBOX", "DXC", "EBAY", "ECLINICALWORKS", "EFICENS", "ELECTRONIC", "ENVIRONMENTAL", "EPAM", "EPSILON", "EPSOFT", "EQUINIX", "ERNST", "EVIDEN", "EXLSERVICE", "EXPEDIA", "EXPERIAN", "EXPERIS", "F5", "FEDEX", "FIS", "FORGE", "FORTHRIGHT", "FORTINET", "FUJITSU", "GAP", "GENENTECH", "GENPACT", "GILEAD", "GLOBALLOGIC", "GOOGLE", "GRANT", "HCL", "HDR", "HEWLETT", "HEXAWARE", "HITACHI", "HOME", "HONEYWELL", "HOWARD", "HTC", "HUBSPOT", "IBM", "INCEDO", "INDEED", "INDU", "INFINITE", "INFOCONS", "INFOGAIN", "INFORMATICA", "INNOVA", "INSIGHT", "INTELLECTT", "INTONE", "INTRAEDGE", "INTUIT", "IQVIA", "IRIS", "ITC", "ITECHMATICS", "JOSH", "KAAR", "KFORCE", "KPIT", "KPMG", "LANDT", "LATENTVIEW", "LATHAM", "LAWRENCE", "LER", "LINKEDIN", "LOWES", "LT", "LTIMINDTREE", "LYFT", "MACYS", "MAHAUGHA", "MANHATTAN", "MAPLEBEAR", "MARVELOUS", "MASTECH", "MATHWORKS", "MAVEN", "MAVERIC", "MCKESSON", "MCKINSEY", "MEGHAZ", "MEJENTA", "MERCK", "META", "MICROSOFT", "MIRACLE", "MITCHELL", "MODERNATX", "MOURI", "MPHASIS", "NAGARRO", "NATIONAL", "NATSOFT", "NEO", "NETAPP", "NETFLIX", "NISUM", "NOKIA", "NORDSTROM", "NTT", "NUTANIX", "NUTECH", "OKTA", "OMA4", "OPTUM", "ORACLE", "PALANTIR", "PALO", "PAYCOM", "PERFICIENT", "PERSISTENT", "PHOTON", "PINTEREST", "PIONEER", "PPD", "PRICEWATERHOUSECOOPERS", "PRIMITIVE", "PRISTEN", "PROBPM", "PRODAPT", "PURE", "PWC", "PYRAMID", "QUADRANT", "QUEST", "RANDSTAD", "RAVIN", "RED", "REGENERON", "ROBLOX", "ROKU", "RUBRIK", "SAFE", "SAFEWAY", "SAGE", "SAI", "SALESFORCE", "SAP", "SAPIENT", "SAPPHIRE", "SAVIENCE", "SAXON", "SERVICENOW", "SHARPLINK", "SHILSOFT", "SIARAA", "SIDLEY", "SIEMENS", "SIRIUS", "SLALOM", "SLK", "SNAP", "SNOWFLAKE", "SOFTWARE", "SONY", "SPERIDIAN", "SPHERE", "SPLUNK", "SPOTIFY", "STANTEC", "STAPLES", "STRATEGIC", "SYNECHRON", "SYNOPSYS", "SYSTEM", "TARGET", "TATA", "TAVANT", "TECH MAHINDRA", "TERBIUM", "TEXAS", "THERMO", "TIGER", "TIKTOK", "TK-CHAIN", "T-MOBILE", "TREDENCE", "TRIAD", "TWILIO", "UBER", "UCHICAGO", "UST", "UT-BATTELLE", "VALUEMOMENTUM", "VASTEK", "VENTOIS", "VERIDIC", "VERIZON", "VERTEX", "VIRTUSA", "VISTA", "VISUAL", "VISYS", "VMWARE", "V-SOFT", "WALMART", "WAL-MART", "WAYFAIR", "WAYMO", "WIPRO", "WORKDAY", "WSP", "YAHOO", "YASH", "YERRALPHA", "ZENSAR", "ZIFO", "ZOOM", "ZS", "ZSCALER", "Robert Half"]

ROLES = ['"Data Analyst"', '"Business Analyst"']
CORE_KEYWORDS = '"SQL" "Power BI" "Excel" "Product" "CSPO" "Agile" -Labr -Secret -TS/SCI'

def load_sent_jobs():
    """Load previously sent jobs from JSON file."""
    if os.path.exists(SENT_JOBS_FILE):
        try:
            with open(SENT_JOBS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading sent jobs: {e}")
            return {}
    return {}

def save_sent_jobs(sent_jobs):
    """Save sent jobs to JSON file."""
    try:
        with open(SENT_JOBS_FILE, 'w') as f:
            json.dump(sent_jobs, f, indent=2)
    except Exception as e:
        print(f"Error saving sent jobs: {e}")

def is_job_sent(job_url, company, sent_jobs):
    """Check if job has already been sent."""
    job_key = f"{company}||{job_url}"
    return job_key in sent_jobs

def mark_job_sent(job_url, company, sent_jobs):
    """Mark a job as sent."""
    job_key = f"{company}||{job_url}"
    sent_jobs[job_key] = datetime.now().isoformat()

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def run_job_search():
    try:
        tz = pytz.timezone(USER_TZ)
        sent_jobs = load_sent_jobs()
        collected = []
        stop_search = False

        def collected_count():
            if not collected:
                return 0
            return pd.concat(collected).drop_duplicates(subset=['job_url']).shape[0]

        # 1. SEARCH PRIORITY COMPANIES
        print("Searching priority companies...")
        for chunk in chunk_list(PRIORITY_COMPANIES, 20):
            if stop_search:
                break
            company_filter = "(" + " OR ".join(chunk) + ")"
            for role in ROLES:
                try:
                    if collected_count() >= 10:
                        stop_search = True
                        break
                    remaining = 10 - collected_count()
                    priority_query = f"{role} {company_filter} {CORE_KEYWORDS}"
                    jobs = scrape_jobs(
                        site_name=["linkedin", "indeed", "google"],
                        search_term=priority_query,
                        location="USA",
                        results_wanted=remaining,
                        hours_old=3,
                        country_indeed='USA'
                    )
                    if not jobs.empty:
                        def _not_sent(r):
                            comp = r['company'] if 'company' in r and r['company'] else "Unknown"
                            return not is_job_sent(r['job_url'], comp, sent_jobs)
                        not_sent_df = jobs[jobs.apply(_not_sent, axis=1)]
                        if not not_sent_df.empty:
                            collected.append(not_sent_df)
                except Exception as e:
                    print(f"Chunk search error: {e}")

        # 2. GENERAL SEARCH FALLBACK
        if collected_count() < 10:
            print(f"Filling with general results...")
            for role in ROLES:
                try:
                    if collected_count() >= 10:
                        break
                    remaining = 10 - collected_count()
                    general_query = f"{role} {CORE_KEYWORDS}"
                    general_jobs = scrape_jobs(
                        site_name=["linkedin", "indeed", "google", "zip_recruiter"],
                        search_term=general_query,
                        location="USA",
                        results_wanted=remaining,
                        hours_old=3,
                        country_indeed='USA'
                    )
                    if not general_jobs.empty:
                        def _not_sent(r):
                            comp = r['company'] if 'company' in r and r['company'] else "Unknown"
                            return not is_job_sent(r['job_url'], comp, sent_jobs)
                        not_sent_df = general_jobs[general_jobs.apply(_not_sent, axis=1)]
                        if not not_sent_df.empty:
                            collected.append(not_sent_df)
                except Exception as e:
                    print(f"General search error: {e}")

        # 3. FINAL FILTER & SEND
        if collected:
            final_df = pd.concat(collected).drop_duplicates(subset=['job_url'])
            new_rows = []
            for _, row in final_df.iterrows():
                comp = row['company'] if 'company' in row and row['company'] else "Unknown"
                if not is_job_sent(row['job_url'], comp, sent_jobs):
                    new_rows.append(row)
            
            final_top_10 = pd.DataFrame(new_rows).head(10)

            if not final_top_10.empty:
                send_email(final_top_10, sent_jobs)
                save_sent_jobs(sent_jobs)
            else:
                print("Zero new jobs found.")
        else:
            print("No jobs found.")
            
    except Exception as e:
        print(f"Critical error: {e}")
        send_error_email(str(e), traceback.format_exc())

def send_email(df, sent_jobs):
    """Send job listings email via Outlook."""
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("RECIPIENT_EMAIL")

    msg = MIMEMultipart()
    msg['Subject'] = f"Top 10 Analyst Jobs - {datetime.now().strftime('%I %p')}"
    msg['From'] = sender
    msg['To'] = recipient

    html = f"<h3>New Postings (Past 3 Hours)</h3><p>Found {len(df)} matching roles:</p><ol>"
    for _, row in df.iterrows():
        company = row['company'] if row['company'] else "Unknown Company"
        site = row['site_name'] if 'site_name' in row else "Job Board"
        html += f"<li><b>[{site.upper()}] {row['title']}</b> at <i>{company}</i><br><a href='{row['job_url']}'>View Posting</a></li><br>"
        mark_job_sent(row['job_url'], company, sent_jobs)
    html += "</ol>"
    
    msg.attach(MIMEText(html, 'html'))
    try:
        # Outlook STARTTLS configuration
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Email sent successfully.")
    except Exception as e:
        print(f"Email error: {e}")
        send_error_email(f"Failed to send job email: {e}", traceback.format_exc())

def send_error_email(error_msg, full_traceback):
    """Send error notification email via Outlook."""
    sender = os.environ.get("EMAIL_USER")
    password = os.environ.get("EMAIL_PASS")
    recipient = os.environ.get("ERROR_NOTIFICATION_EMAIL")

    msg = MIMEMultipart()
    msg['Subject'] = f"🚨 Job Bot Error - {datetime.now().strftime('%I %p')}"
    msg['From'] = sender
    msg['To'] = recipient

    html = f"<h3>Job Bot Error</h3><p><b>Error:</b> {error_msg}</p><pre>{full_traceback}</pre>"
    msg.attach(MIMEText(html, 'html'))
    try:
        with smtplib.SMTP('smtp.office365.com', 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, recipient, msg.as_string())
        print("Error notification sent.")
    except Exception as e:
        print(f"Failed to send error email: {e}")

if __name__ == "__main__":
    run_job_search()
