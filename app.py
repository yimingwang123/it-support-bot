from flask import Flask, render_template, request, jsonify, session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import uuid
import logging

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, will use system environment variables
    pass

# Import Azure OpenAI service
from azure_openai_service import AzureOpenAIService

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Azure OpenAI service
azure_ai_service = AzureOpenAIService()

# IT Support knowledge base with common issues and solutions in German
IT_KNOWLEDGE_BASE = {
    'password': {
        'keywords': ['passwort', 'kennwort', 'reset', 'vergessen', 'anmeldung', 'konto', 'gesperrt', 'password', 'login'],
        'title': 'Passwort zurücksetzen',
        'steps': [
            "1. Gehen Sie zur Unternehmens-Anmeldeseite",
            "2. Klicken Sie auf den Link 'Passwort vergessen'",
            "3. Geben Sie Ihre E-Mail-Adresse ein",
            "4. Überprüfen Sie Ihre E-Mails für Anweisungen zum Zurücksetzen",
            "5. Folgen Sie dem Link in der E-Mail und erstellen Sie ein neues Passwort",
            "6. Ihr neues Passwort sollte mindestens 8 Zeichen mit Groß-, Kleinbuchstaben, Zahlen und Symbolen enthalten",
            "Falls Sie weiterhin nicht auf Ihr Konto zugreifen können, kontaktieren Sie die IT unter Durchwahl 1234"
        ]
    },
    'vpn': {
        'keywords': ['vpn', 'verbindung', 'remote', 'fernzugriff', 'netzwerk', 'verbinden', 'connection'],
        'title': 'VPN-Verbindungsprobleme',
        'steps': [
            "1. Überprüfen Sie zuerst Ihre Internetverbindung",
            "2. Stellen Sie sicher, dass der VPN-Client installiert und aktualisiert ist",
            "3. Überprüfen Sie, ob Ihre VPN-Anmeldedaten korrekt sind",
            "4. Versuchen Sie, die Verbindung zu trennen und erneut zu verbinden",
            "5. Löschen Sie den VPN-Cache und starten Sie die Anwendung neu",
            "6. Überprüfen Sie, ob Ihre Firewall oder Antivirus das VPN blockiert",
            "7. Versuchen Sie, sich mit einem anderen VPN-Server zu verbinden",
            "Falls Probleme bestehen bleiben, kontaktieren Sie die IT mit Fehlercodes"
        ]
    },
    'email': {
        'keywords': ['email', 'e-mail', 'outlook', 'mail', 'senden', 'empfangen', 'synchronisierung', 'sync'],
        'title': 'E-Mail-Probleme',
        'steps': [
            "1. Überprüfen Sie Ihre Internetverbindung",
            "2. Starten Sie Ihren E-Mail-Client (Outlook, etc.) neu",
            "3. Überprüfen Sie, ob Sie innerhalb des Speicherkontingents sind",
            "4. Überprüfen Sie die E-Mail-Server-Einstellungen",
            "5. Versuchen Sie, auf E-Mails über den Webbrowser zuzugreifen",
            "6. Löschen Sie den E-Mail-Cache und Offline-Dateien",
            "7. Aktualisieren Sie Ihren E-Mail-Client auf die neueste Version",
            "Kontaktieren Sie die IT, wenn Sie Server-Konfigurationsdetails benötigen"
        ]
    },
    'printer': {
        'keywords': ['drucker', 'drucken', 'papier', 'stau', 'toner', 'printer', 'print'],
        'title': 'Drucker-Probleme',
        'steps': [
            "1. Überprüfen Sie, ob der Drucker eingeschaltet und verbunden ist",
            "2. Überprüfen Sie, ob das Papier korrekt eingelegt ist",
            "3. Suchen Sie nach Papierstaus und beseitigen Sie diese",
            "4. Stellen Sie sicher, dass der Toner-/Tintenstand ausreichend ist",
            "5. Starten Sie sowohl Computer als auch Drucker neu",
            "6. Aktualisieren oder installieren Sie die Druckertreiber neu",
            "7. Überprüfen Sie die Druckwarteschlange und löschen Sie hängende Aufträge",
            "Bei Hardware-Problemen kontaktieren Sie die Gebäudeverwaltung"
        ]
    },
    'software': {
        'keywords': ['software', 'anwendung', 'programm', 'installieren', 'aktualisieren', 'absturz', 'application'],
        'title': 'Software-Probleme',
        'steps': [
            "1. Schließen und starten Sie die Anwendung neu",
            "2. Überprüfen Sie auf verfügbare Software-Updates",
            "3. Starten Sie Ihren Computer neu",
            "4. Führen Sie das Programm als Administrator aus",
            "5. Überprüfen Sie Systemanforderungen und Kompatibilität",
            "6. Deaktivieren Sie temporär das Antivirus und versuchen Sie es erneut",
            "7. Installieren Sie die Software bei Bedarf neu",
            "Kontaktieren Sie die IT für Software-Lizenzierung oder Installationshilfe"
        ]
    },
    'computer': {
        'keywords': ['langsam', 'leistung', 'einfrieren', 'absturz', 'start', 'boot', 'slow', 'performance'],
        'title': 'Computer-Leistungsprobleme',
        'steps': [
            "1. Starten Sie Ihren Computer neu",
            "2. Überprüfen Sie den verfügbaren Festplattenspeicher (sollte mindestens 15% frei haben)",
            "3. Führen Sie eine Festplattenbereinigung aus, um temporäre Dateien zu entfernen",
            "4. Überprüfen Sie mit Antivirus-Software auf Malware",
            "5. Aktualisieren Sie Ihr Betriebssystem",
            "6. Schließen Sie unnötige Programme im Hintergrund",
            "7. Überprüfen Sie den Task-Manager auf hohe CPU-/Speichernutzung",
            "Falls Probleme bestehen bleiben, könnte eine Hardware-Diagnose erforderlich sein"
        ]
    }
}

def find_relevant_solution(message):
    """Find the most relevant IT solution based on user message"""
    message_lower = message.lower()
    
    for category, info in IT_KNOWLEDGE_BASE.items():
        for keyword in info['keywords']:
            if keyword in message_lower:
                return info
    
    return {
        'title': 'Allgemeine IT-Unterstützung',
        'steps': [
            "Ich verstehe, dass Sie ein IT-Problem haben. Hier sind einige allgemeine Schritte zur Fehlerbehebung:",
            "1. Versuchen Sie, Ihr Gerät neu zu starten",
            "2. Überprüfen Sie alle Kabelverbindungen",
            "3. Aktualisieren Sie Ihre Software/Treiber",
            "4. Kontaktieren Sie die IT-Unterstützung unter Durchwahl 1234 für spezielle Hilfe",
            "Bitte geben Sie weitere Details zu Ihrem spezifischen Problem für bessere Hilfe an."
        ]
    }

def send_email_summary(user_name, user_email, chat_history, main_issue):
    """Send email summary to IT support"""
    try:
        # Email configuration - in production, use environment variables
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        sender_email = os.environ.get('SENDER_EMAIL', 'your-email@company.com')
        sender_password = os.environ.get('SENDER_PASSWORD', 'your-app-password')
        
        # Debug credential validation
        logger.info(f"🔍 DEBUG - Checking credentials:")
        logger.info(f"sender_email: '{sender_email}'")
        logger.info(f"sender_password: '{sender_password}'")
        logger.info(f"Email in placeholder list: {sender_email in ['test@example.com', 'your-gmail@gmail.com', 'your-email@company.com']}")
        logger.info(f"Password in placeholder list: {sender_password in ['test-password', 'your-app-password', 'your-16-digit-app-password']}")
        logger.info(f"'your-' in email: {'your-' in sender_email}")
        logger.info(f"'your-' in password: {'your-' in sender_password}")
        
        # Check if using test/placeholder credentials
        if (sender_email in ['test@example.com', 'your-gmail@gmail.com', 'your-email@company.com'] or 
            sender_password in ['test-password', 'your-app-password', 'your-16-digit-app-password'] or
            'your-' in sender_email or 'your-' in sender_password):
            logger.info(f"DEVELOPMENT MODE: Email summary would be sent for session with {user_email}")
            logger.info(f"Subject: IT-Support Sitzung Zusammenfassung: {main_issue}")
            
            # Log the full email content for testing
            email_content = f"""
IT-Support Chat-Sitzung Zusammenfassung

Benutzerinformationen:
- Name: {user_name}
- E-Mail: {user_email}
- Sitzungsdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hauptproblem: {main_issue}

Chat-Verlauf:
"""
            for entry in chat_history:
                email_content += f"\n{entry['timestamp']} - {entry['sender']}: {entry['message']}\n"
            
            email_content += f"""

Nächste Schritte:
- Nachverfolgung mit Benutzer, falls Problem weiterhin besteht
- Wissensdatenbank aktualisieren, falls neue Lösung gefunden wurde
- Auf ähnliche Probleme von anderen Benutzern achten

Dies ist eine automatische E-Mail vom IT-Support Chatbot System.
"""
            logger.info("EMAIL CONTENT PREVIEW:")
            logger.info(email_content)
            logger.warning("⚠️  To send real emails, update SENDER_EMAIL and SENDER_PASSWORD in .env file")
            return True
        
        # PRODUCTION: Send real email
        logger.info(f"📧 Sending real email from {sender_email} to yimiwang@microsoft.com")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'yimiwang@microsoft.com'
        msg['Subject'] = f'IT-Support Sitzung Zusammenfassung: {main_issue}'
        
        # Create email body
        body = f"""
IT-Support Chat-Sitzung Zusammenfassung

Benutzerinformationen:
- Name: {user_name}
- E-Mail: {user_email}
- Sitzungsdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hauptproblem: {main_issue}

Chat-Verlauf:
"""
        
        for entry in chat_history:
            body += f"\n{entry['timestamp']} - {entry['sender']}: {entry['message']}\n"
        
        body += f"""

Nächste Schritte:
- Nachverfolgung mit Benutzer, falls Problem weiterhin besteht
- Wissensdatenbank aktualisieren, falls neue Lösung gefunden wurde
- Auf ähnliche Probleme von anderen Benutzern achten

Dies ist eine automatische E-Mail vom IT-Support Chatbot System.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        logger.info(f"🔄 Connecting to SMTP server {smtp_server}:{smtp_port}")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        logger.info("🔐 Authenticating...")
        server.login(sender_email, sender_password)
        
        logger.info("📨 Sending email...")
        text = msg.as_string()
        server.sendmail(sender_email, 'yimiwang@microsoft.com', text)
        server.quit()
        
        logger.info(f"✅ Email summary sent successfully to yimiwang@microsoft.com")
        return True
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = 'yimiwang@microsoft.com'
        msg['Subject'] = f'IT-Support Sitzung Zusammenfassung: {main_issue}'
        
        # Create email body
        body = f"""
IT-Support Chat-Sitzung Zusammenfassung

Benutzerinformationen:
- Name: {user_name}
- E-Mail: {user_email}
- Sitzungsdatum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Hauptproblem: {main_issue}

Chat-Verlauf:
"""
        
        for entry in chat_history:
            body += f"\n{entry['timestamp']} - {entry['sender']}: {entry['message']}\n"
        
        body += f"""

Nächste Schritte:
- Nachverfolgung mit Benutzer, falls Problem weiterhin besteht
- Wissensdatenbank aktualisieren, falls neue Lösung gefunden wurde
- Auf ähnliche Probleme von anderen Benutzern achten

Dies ist eine automatische E-Mail vom IT-Support Chatbot System.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, 'yimiwang@microsoft.com', text)
        server.quit()
        
        logger.info(f"Email summary sent successfully for session with {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email summary: {str(e)}")
        return False

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('index.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    """Initialize a new chat session"""
    data = request.get_json()
    
    # Store user info in session
    session['user_name'] = data.get('name')
    session['user_email'] = data.get('email')
    session['session_id'] = str(uuid.uuid4())
    session['chat_history'] = []
    session['main_issue'] = None
    
    logger.info(f"New session started for {session['user_email']}")
    
    return jsonify({
        'status': 'success',
        'message': f"Hallo {session['user_name']}! Ich bin Ihr IT-Support-Assistent. Wie kann ich Ihnen heute helfen?"
    })

@app.route('/send_message', methods=['POST'])
def send_message():
    """Process user message and return bot response"""
    data = request.get_json()
    user_message = data.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400
    
    # Check if user wants to end session
    if user_message.lower() in ['end', 'finished', 'done', 'quit', 'exit', 'ende', 'fertig', 'beenden', 'schluss']:
        return end_session()
    
    # Add user message to chat history
    timestamp = datetime.now().strftime('%H:%M:%S')
    session['chat_history'].append({
        'timestamp': timestamp,
        'sender': 'User',
        'message': user_message
    })
    
    # Set main issue if this is the first question
    if session.get('main_issue') is None:
        session['main_issue'] = user_message
    
    # Get AI-powered response using Azure OpenAI
    try:
        # Prepare conversation context for AI
        conversation_context = []
        for entry in session.get('chat_history', [])[-5:]:  # Last 5 messages for context
            if entry['sender'] == 'User':
                conversation_context.append(f"Benutzer: {entry['message']}")
            else:
                conversation_context.append(f"Assistent: {entry['message']}")
        
        # Get AI response
        bot_response = azure_ai_service.get_it_support_response(
            user_message, 
            context="\n".join(conversation_context[:-1])  # Exclude current message
        )
        
        logger.info(f"✅ AI response generated successfully")
        
    except Exception as e:
        logger.error(f"❌ Error getting AI response: {str(e)}")
        # Fallback to keyword-based response
        solution = find_relevant_solution(user_message)
        bot_response = f"Ich kann Ihnen bei {solution['title']} helfen. Hier sind die empfohlenen Schritte:\n\n"
        bot_response += "\n".join(solution['steps'])
    
    # Add standard ending to response
    bot_response += "\n\nGibt es noch etwas anderes, womit ich Ihnen helfen kann? Schreiben Sie 'ende', wenn Sie fertig sind."
    
    # Add bot response to chat history
    session['chat_history'].append({
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'sender': 'Bot',
        'message': bot_response
    })
    
    return jsonify({
        'status': 'success',
        'message': bot_response
    })

@app.route('/end_session', methods=['POST'])
def end_session():
    """End the chat session and send email summary"""
    if not session.get('user_name'):
        return jsonify({'error': 'Keine aktive Sitzung'}), 400
    
    # Send email summary
    email_sent = send_email_summary(
        session['user_name'],
        session['user_email'],
        session['chat_history'],
        session.get('main_issue', 'General IT Support')
    )
    
    # Clear session
    user_name = session['user_name']
    session.clear()
    
    response_message = f"Vielen Dank {user_name}! Ihre Sitzung wurde beendet."
    if email_sent:
        response_message += " Eine Zusammenfassung wurde an unser IT-Team gesendet."
    else:
        response_message += " Hinweis: Es gab ein Problem beim Senden der Zusammenfassungs-E-Mail."
    
    return jsonify({
        'status': 'success',
        'message': response_message,
        'session_ended': True
    })

@app.route('/get_chat_history')
def get_chat_history():
    """Get current chat history"""
    return jsonify({
        'chat_history': session.get('chat_history', []),
        'user_name': session.get('user_name'),
        'session_active': bool(session.get('user_name'))
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
