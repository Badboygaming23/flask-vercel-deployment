import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_otp_email(email, otp):
    """
    Send OTP email to the user.
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f'"Leirad Noznag" <{Config.EMAIL_USER}>'
        msg['To'] = email
        msg['Subject'] = 'Your OTP for Registration'
        
        # Email body
        body = f'Your One-Time Password (OTP) is: {otp}. It is valid for 5 minutes. Do not share this with anyone.'
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
        server.starttls()  # Enable security
        server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
        
        # Send email
        text = msg.as_string()
        server.sendmail(Config.EMAIL_USER, email, text)
        server.quit()
        
        logger.info(f"OTP email sent successfully to: {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending OTP email to {email}: {str(e)}")
        return False

def send_password_reset_email(email, otp):
    """
    Send password reset OTP email to the user.
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f'"Leirad Noznag" <{Config.EMAIL_USER}>'
        msg['To'] = email
        msg['Subject'] = 'Password Reset OTP'
        
        # Email body
        body = f'Your One-Time Password (OTP) for password reset is: {otp}. It is valid for 5 minutes. Do not share this with anyone.'
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP(Config.EMAIL_HOST, Config.EMAIL_PORT)
        server.starttls()  # Enable security
        server.login(Config.EMAIL_USER, Config.EMAIL_PASS)
        
        # Send email
        text = msg.as_string()
        server.sendmail(Config.EMAIL_USER, email, text)
        server.quit()
        
        logger.info(f"Password reset email sent successfully to: {email}")
        return True
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {str(e)}")
        return False