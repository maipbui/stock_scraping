import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yaml

with open("src/resources.yml", "r") as f:
    cfg = yaml.load(f.read(), Loader=yaml.FullLoader)
email = cfg["email"]["from_address"]
password = cfg["email"]["from_address_password"]
send_to_email = cfg["email"]["to_address"]


def send_notification(subject, message):

    subject = "Stock News: " + subject
    msg = MIMEMultipart()
    msg["From"] = email
    msg["To"] = send_to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email, password)
    text = msg.as_string()
    server.sendmail(email, send_to_email, text)
    server.quit()
