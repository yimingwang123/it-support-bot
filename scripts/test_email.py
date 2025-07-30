#!/usr/bin/env python3
"""
Email Test Utility for IT Support Chatbot

This script helps test email functionality without running the full application.
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv('../.env')
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables.")

def test_email_configuration():
    """Test email configuration and send a test email"""
    
    # Get configuration
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    sender_email = os.environ.get('SENDER_EMAIL', '')
    sender_password = os.environ.get('SENDER_PASSWORD', '')
    
    if not sender_email or not sender_password:
        print("❌ Email configuration not found!")
        print("Please update your .env file with:")
        print("SENDER_EMAIL=your-email@example.com")
        print("SENDER_PASSWORD=your-password")
        return False
    
    if sender_email == 'test@example.com' or sender_password == 'test-password':
        print("❌ Using test credentials. Please update .env with real email credentials.")
        return False
    
    print(f"📧 Testing email configuration...")
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"Sender: {sender_email}")
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'yimiwang@microsoft.com'
        msg['Subject'] = 'IT-Support Chatbot - Test E-Mail'
        
        body = f"""
Dies ist eine Test-E-Mail vom IT-Support Chatbot System.

Konfiguration:
- SMTP Server: {smtp_server}
- Port: {smtp_port}
- Absender: {sender_email}
- Testzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Falls Sie diese E-Mail erhalten, funktioniert die E-Mail-Konfiguration korrekt!

---
IT-Support Chatbot System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("🔄 Verbinde mit SMTP Server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        print("🔐 Authentifizierung...")
        server.login(sender_email, sender_password)
        
        print("📨 Sende Test-E-Mail...")
        text = msg.as_string()
        server.sendmail(sender_email, 'yimiwang@microsoft.com', text)
        server.quit()
        
        print("✅ Test-E-Mail erfolgreich gesendet!")
        print("📬 Überprüfen Sie yimiwang@microsoft.com für die Test-Nachricht.")
        return True
        
    except Exception as e:
        print(f"❌ E-Mail-Test fehlgeschlagen: {str(e)}")
        print("\n🔧 Häufige Lösungen:")
        print("1. Überprüfen Sie Benutzername und Passwort")
        print("2. Für Gmail: Verwenden Sie ein App-Passwort (nicht Ihr normales Passwort)")
        print("3. Überprüfen Sie Firewall-Einstellungen")
        print("4. Stellen Sie sicher, dass weniger sichere Apps aktiviert sind (falls erforderlich)")
        return False

if __name__ == "__main__":
    print("🛠️ IT-Support Chatbot - E-Mail-Test")
    print("=" * 50)
    
    success = test_email_configuration()
    
    if success:
        print("\n🎉 E-Mail-Konfiguration ist bereit!")
        print("Der Chatbot kann jetzt E-Mail-Zusammenfassungen senden.")
    else:
        print("\n❗ E-Mail-Konfiguration muss korrigiert werden.")
        print("Siehe EMAIL_SETUP.md für detaillierte Anweisungen.")
