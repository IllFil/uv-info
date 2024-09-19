import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
# Kaunas coordinates
latitude = 54.9024914
longitude = 23.9609016

# API URL
url = f"https://currentuvindex.com/api/v1/uvi?latitude={latitude}&longitude={longitude}"

# Email configuration
smtp_server = 'smtp.gmail.com'
smtp_port = 587
email_address = os.environ['email_address']
email_password = os.environ['email_password']
recipient_email = os.environ['recipient_email']


def fetch_uv_data():
    # Make a GET request to the API
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None


def analyze_uv_data(data):
    forecast_data = data.get('forecast', [])
    uv_exceeds_threshold = False
    uv_data = {"over_threshold": [], "below_threshold": []}

    # Get today's date in UTC format (YYYY-MM-DD)
    today_date = datetime.now().strftime('%Y-%m-%d')

    for entry in forecast_data:
        # Extract date from the timestamp
        timestamp = entry['time']
        entry_date = timestamp.split('T')[0]

        # Check if the entry is for today
        if entry_date == today_date:
            uv_index = entry['uvi']
            if uv_index >= 2.5:
                uv_exceeds_threshold = True
                uv_data["over_threshold"].append(entry)
            else:
                uv_data["below_threshold"].append(entry)
        if entry_date != today_date:
            return uv_exceeds_threshold, uv_data

def send_email(uv_exceeds_threshold, uv_data):

    subject = "UV Index Daily Report"
    over_threshold_str = "\n".join([f"{entry['time']}: {entry['uvi']}" for entry in uv_data["over_threshold"]])
    below_threshold_str = "\n".join([f"{entry['time']}: {entry['uvi']}" for entry in uv_data["below_threshold"]])
    if uv_exceeds_threshold:
        body = f"UV Index is above or equal to 2.5 at the following times:\n\n{over_threshold_str}"
    else:
        body = f"UV Index is below 2.5 at the following times:\n\n{below_threshold_str}"


    # Set up the email
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    data = fetch_uv_data()
    if data:
        uv_exceeds_threshold, uv_data = analyze_uv_data(data)
        send_email(uv_exceeds_threshold, uv_data)


if __name__ == "__main__":
    main()