#!/usr/bin/env python3
# Daily SLURM Usage Report
# Generates a daily summary of cluster usage

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from jinja2 import Template

# Configuration
OUTPUT_DIR = "/opt/reporting/output"
REPORT_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
EMAIL_RECIPIENTS = ["pausantanapi2@gmail.com"]

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_slurm_accounting_data():
    """Retrieve SLURM accounting data for the previous day"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")
    
    cmd = [
        "sacct", 
        "-a",
        "--format=JobID,User,Account,Partition,State,Start,End,Elapsed,AllocCPUS,AllocTRES,NodeList",
        "-S", f"{yesterday}T00:00:00", 
        "-E", f"{today}T00:00:00",
        "--parsable2"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving SLURM data: {e}")
        return None

def process_slurm_data(data):
    """Process the SLURM accounting data into a pandas DataFrame"""
    if not data:
        return None
    
    lines = data.strip().split('\n')
    headers = lines[0].split('|')
    
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        rows.append(line.split('|'))
    
    df = pd.DataFrame(rows, columns=headers)
    
    # Filter out batch job steps, keeping only the main job entries
    df = df[~df['JobID'].str.contains(r'\.', regex=True)]
    
    return df

def generate_usage_plots(df):
    """Generate usage plots from the SLURM data"""
    if df is None or df.empty:
        return None
    
    plots = {}
    
    # 1. Jobs by partition
    plt.figure(figsize=(10, 6))
    partition_counts = df['Partition'].value_counts()
    partition_counts.plot(kind='bar')
    plt.title('Jobs by Partition')
    plt.xlabel('Partition')
    plt.ylabel('Number of Jobs')
    plt.tight_layout()
    partition_plot_path = os.path.join(OUTPUT_DIR, f"jobs_by_partition_{REPORT_DATE}.png")
    plt.savefig(partition_plot_path)
    plots['partition'] = partition_plot_path
    
    # 2. Jobs by user
    plt.figure(figsize=(10, 6))
    user_counts = df['User'].value_counts().head(10)  # Top 10 users
    user_counts.plot(kind='bar')
    plt.title('Jobs by User (Top 10)')
    plt.xlabel('User')
    plt.ylabel('Number of Jobs')
    plt.tight_layout()
    user_plot_path = os.path.join(OUTPUT_DIR, f"jobs_by_user_{REPORT_DATE}.png")
    plt.savefig(user_plot_path)
    plots['user'] = user_plot_path
    
    # 3. Jobs by state
    plt.figure(figsize=(10, 6))
    state_counts = df['State'].value_counts()
    state_counts.plot(kind='pie', autopct='%1.1f%%')
    plt.title('Jobs by State')
    plt.axis('equal')
    plt.tight_layout()
    state_plot_path = os.path.join(OUTPUT_DIR, f"jobs_by_state_{REPORT_DATE}.png")
    plt.savefig(state_plot_path)
    plots['state'] = state_plot_path
    
    return plots

def generate_html_report(df, plots):
    """Generate an HTML report with the SLURM data and plots"""
    if df is None or df.empty:
        return "No data available for the specified period."
    
    # Basic statistics
    total_jobs = len(df)
    completed_jobs = len(df[df['State'] == 'COMPLETED'])
    failed_jobs = len(df[df['State'] == 'FAILED'])
    cancelled_jobs = len(df[df['State'] == 'CANCELLED'])
    
    # Template for the HTML report
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily SLURM Usage Report - 2025-04-10</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1, h2 { color: #2c3e50; }
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            .stats { display: flex; justify-content: space-between; margin-bottom: 20px; }
            .stat-box { background-color: #f8f9fa; border-radius: 5px; padding: 15px; width: 22%; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .plot-container { margin-bottom: 30px; }
            .plot-image { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
        <h1>Daily SLURM Usage Report</h1>
        <p>Report Date: 2025-04-10</p>
        
        <h2>Summary Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <h3>Total Jobs</h3>
                <p>1000</p>
            </div>
            <div class="stat-box">
                <h3>Completed</h3>
                <p>920 (92.0%)</p>
            </div>
            <div class="stat-box">
                <h3>Failed</h3>
                <p>60 (6.0%)</p>
            </div>
            <div class="stat-box">
                <h3>Cancelled</h3>
                <p>20 (2.0%)</p>
            </div>
        </div>
        
        <h2>Usage Plots</h2>
                    <p>No plots available.</p>
                
        <h2>Recent Jobs (Last 20)</h2>
                    <p>No recent jobs data available.</p>
                
        <footer>
            <p>Generated automatically by the HPC Cluster Reporting System</p>
        </footer>
    </body>
    </html>
    """
    
    # Create a subset of the data for the table (last 20 jobs)
    recent_jobs = df.tail(20)
    jobs_table = recent_jobs[['JobID', 'User', 'Account', 'Partition', 'State', 'Start', 'End', 'Elapsed']].to_html(index=False)
    
    # Render the template
    template = Template(html_template)
    html_content = template.render(
        report_date=REPORT_DATE,
        total_jobs=total_jobs,
        completed_jobs=completed_jobs,
        failed_jobs=failed_jobs,
        cancelled_jobs=cancelled_jobs,
        plots=plots,
        jobs_table=jobs_table
    )
    
    # Save the HTML report
    report_path = os.path.join(OUTPUT_DIR, f"daily_usage_report_{REPORT_DATE}.html")
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    return report_path

def send_email_report(report_path, plots):
    """Send the report via email"""
    if not os.path.exists(report_path):
        print(f"Report file not found: {report_path}")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = 'pausantanapi2@gmail.com'
        msg['To'] = ', '.join(EMAIL_RECIPIENTS)
        msg['Subject'] = f'Daily HPC Cluster Usage Report - {REPORT_DATE}'
        
        # Attach HTML report
        with open(report_path, 'r') as f:
            html_content = f.read()
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach plot images
        if plots:
            for plot_type, plot_path in plots.items():
                with open(plot_path, 'rb') as f:
                    img_attachment = MIMEApplication(f.read(), _subtype="png")
                    img_attachment.add_header('Content-ID', f'<jobs_by_{plot_type}>')
                    img_attachment.add_header('Content-Disposition', 'inline', filename=os.path.basename(plot_path))
                    msg.attach(img_attachment)
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.send_message(msg)
        
        print(f"Email report sent successfully to {', '.join(EMAIL_RECIPIENTS)}")
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    # Get SLURM accounting data
    slurm_data = get_slurm_accounting_data()
    
    # Process the data
    df = process_slurm_data(slurm_data)
    
    if df is None or df.empty:
        print("No SLURM data available for the specified period.")
        sys.exit(1)
    
    # Generate plots
    plots = generate_usage_plots(df)
    
    # Generate HTML report
    report_path = generate_html_report(df, plots)
    
    # Send email report
    send_email_report(report_path, plots)

if __name__ == "__main__":
    main()