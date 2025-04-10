#!/usr/bin/env python3
# Test version of Daily SLURM Usage Report
# Uses mock data instead of real SLURM data

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
OUTPUT_DIR = "/tmp/reporting/output"  # Changed to /tmp for testing
REPORT_DATE = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
# Use environment variable for email recipients too
EMAIL_RECIPIENTS = os.environ.get('EMAIL_RECIPIENTS', 'admin@example.com').split(',')

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_mock_slurm_data():
    """Generate mock SLURM accounting data for testing"""
    # Header row
    header = "JobID|User|Account|Partition|State|Start|End|Elapsed|AllocCPUS|AllocTRES|NodeList"
    
    # Generate some mock job data
    jobs = []
    users = ["user1", "user2", "user3", "user4", "user5"]
    accounts = ["account1", "account2", "account3"]
    partitions = ["compute", "gpu", "highmem"]
    states = ["COMPLETED", "FAILED", "CANCELLED", "TIMEOUT", "COMPLETED", "COMPLETED"]
    
    # Generate 50 mock jobs
    for i in range(1, 51):
        user = users[i % len(users)]
        account = accounts[i % len(accounts)]
        partition = partitions[i % len(partitions)]
        state = states[i % len(states)]
        
        # Generate timestamps
        start_time = (datetime.now() - timedelta(days=1, hours=i % 24)).strftime("%Y-%m-%dT%H:%M:%S")
        end_time = (datetime.now() - timedelta(days=1, hours=(i % 24) - 2)).strftime("%Y-%m-%dT%H:%M:%S")
        elapsed = "02:00:00"
        
        # Generate job entry
        job = f"{i}|{user}|{account}|{partition}|{state}|{start_time}|{end_time}|{elapsed}|{i % 16 + 1}|cpu={i % 16 + 1}|node{i % 5 + 1}"
        jobs.append(job)
    
    # Combine header and jobs
    return header + "\n" + "\n".join(jobs)

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
        <title>Daily SLURM Usage Report - {{ report_date }}</title>
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
        <h1>Daily SLURM Usage Report (TEST)</h1>
        <p>Report Date: {{ report_date }}</p>
        
        <h2>Summary Statistics</h2>
        <div class="stats">
            <div class="stat-box">
                <h3>Total Jobs</h3>
                <p>{{ total_jobs }}</p>
            </div>
            <div class="stat-box">
                <h3>Completed</h3>
                <p>{{ completed_jobs }} ({{ (completed_jobs/total_jobs*100)|round(1) if total_jobs else 0 }}%)</p>
            </div>
            <div class="stat-box">
                <h3>Failed</h3>
                <p>{{ failed_jobs }} ({{ (failed_jobs/total_jobs*100)|round(1) if total_jobs else 0 }}%)</p>
            </div>
            <div class="stat-box">
                <h3>Cancelled</h3>
                <p>{{ cancelled_jobs }} ({{ (cancelled_jobs/total_jobs*100)|round(1) if total_jobs else 0 }}%)</p>
            </div>
        </div>
        
        <h2>Usage Plots</h2>
        {% if plots %}
            {% if 'partition' in plots %}
            <div class="plot-container">
                <h3>Jobs by Partition</h3>
                <img src="{{ plots.partition }}" class="plot-image" />
            </div>
            {% endif %}
            
            {% if 'user' in plots %}
            <div class="plot-container">
                <h3>Jobs by User (Top 10)</h3>
                <img src="{{ plots.user }}" class="plot-image" />
            </div>
            {% endif %}
            
            {% if 'state' in plots %}
            <div class="plot-container">
                <h3>Jobs by State</h3>
                <img src="{{ plots.state }}" class="plot-image" />
            </div>
            {% endif %}
        {% else %}
            <p>No plots available.</p>
        {% endif %}
        
        <h2>Recent Jobs (Last 20)</h2>
        {% if jobs_table %}
            {{ jobs_table|safe }}
        {% else %}
            <p>No recent jobs data available.</p>
        {% endif %}
        
        <footer>
            <p>Generated automatically by the HPC Cluster Reporting System (TEST VERSION)</p>
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
    
    print(f"HTML report generated: {report_path}")
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
        
        # Get Gmail app password from environment variable
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD')
        if not gmail_password:
            print("Warning: GMAIL_APP_PASSWORD environment variable not set")
            print("Email authentication will fail without a password")
        
        # Send email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            # Use the app password from environment variable
            if gmail_password:
                server.login('pausantanapi2@gmail.com', gmail_password)
            server.send_message(msg)
        
        print(f"Email report sent successfully to {', '.join(EMAIL_RECIPIENTS)}")
        return True
    
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def main():
    print("Starting test SLURM report generation...")
    
    # Get mock SLURM accounting data
    slurm_data = get_mock_slurm_data()
    
    # Process the data
    df = process_slurm_data(slurm_data)
    
    if df is None or df.empty:
        print("No SLURM data available for the specified period.")
        sys.exit(1)
    
    print(f"Processed {len(df)} mock SLURM jobs")
    
    # Generate plots
    plots = generate_usage_plots(df)
    
    # Generate HTML report
    report_path = generate_html_report(df, plots)
    
    # Send email report (mock)
    send_email_report(report_path, plots)
    
    print("Test report generation completed successfully!")

if __name__ == "__main__":
    main()