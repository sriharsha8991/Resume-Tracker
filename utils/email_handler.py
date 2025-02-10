import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailHandler:
    def __init__(self):
        self.smtp_config = {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': "your-email@gmail.com",  # Replace with your email
            'password': "your-app-password",     # Replace with your app password
            'sender_email': "your-email@gmail.com"
        }
    
    def send_email(self, recipient_email, subject, body):
        message = MIMEMultipart()
        message['From'] = self.smtp_config['sender_email']
        message['To'] = recipient_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port']) as server:
                server.starttls()
                server.login(self.smtp_config['username'], self.smtp_config['password'])
                server.send_message(message)
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    def send_acceptance_email(self, email, name):
        subject = "Congratulations! Your Application Has Been Shortlisted"
        body = f"""Dear {name},
        
We are pleased to inform you that your application has been shortlisted for further consideration.
We will contact you shortly to schedule an interview.

Best regards,
HR Team"""
        return self.send_email(email, subject, body)
    
    def send_rejection_email(self, email, name):
        subject = "Update Regarding Your Application"
        body = f"""Dear {name},
        
Thank you for your interest in our organization. After careful consideration, 
we regret to inform you that we will not be moving forward with your application at this time.

We wish you the best in your future endeavors.

Best regards,
HR Team"""
        return self.send_email(email, subject, body)
