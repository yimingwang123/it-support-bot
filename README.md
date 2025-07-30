# 🛠️ IT Support Chatbot

A Python Flask web ap4. **Start the application**:
```bash
python app.py
```

5. **Open your browser** to `http://localhost:5000`

## Email Configuration

To enable email summaries, you need to configure SMTP settings:

### Quick Test
```bash
python test_email.py
```

### Gmail Setup (Recommended for testing)
1. Enable 2-factor authentication on Gmail
2. Generate an App Password
3. Update `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-16-digit-app-password
```

### For detailed email setup instructions, see [EMAIL_SETUP.md](EMAIL_SETUP.md)ion that provides an intelligent IT support chatbot to help users with common IT issues.

## Features

- **Modern UI**: Beautiful, glassmorphic design with smooth animations and gradients
- **User Session Management**: Collects user name and email at the start of each session
- **Intelligent Issue Detection**: Automatically identifies common IT issues and provides step-by-step solutions
- **German Language Support**: Complete German localization for UI and responses
- **Knowledge Base**: Built-in solutions for common problems like:
  - Password resets (Passwort zurücksetzen)
  - VPN connection issues (VPN-Verbindungsprobleme)
  - Email problems (E-Mail-Probleme)
  - Printer troubles (Drucker-Probleme)
  - Software issues (Software-Probleme)
  - Computer performance problems (Computer-Leistungsprobleme)
- **Email Summaries**: Automatically sends session summaries to IT support team
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Session Persistence**: Maintains chat history during active sessions
- **Smooth Animations**: Modern micro-interactions and transitions

## Quick Start

### Prerequisites
- Python 3.9+
- Conda environment named `it-support-bot`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yimingwang123/it-support-bot.git
cd it-support-bot
```

2. Run the setup script:
```bash
./setup.sh
```

3. Configure email settings:
```bash
cp .env.example .env
# Edit .env with your email configuration
```

4. Start the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Configuration

### Email Setup

The bot sends session summaries via email. Configure your email settings in the `.env` file:

#### For Gmail:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```

**Note**: For Gmail, you need to:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password instead of your regular password

#### For Outlook/Office 365:
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your-email@outlook.com
SENDER_PASSWORD=your-password
```

### Security Settings

```env
SECRET_KEY=your-random-secret-key-here
```

## Usage

1. **Start a Session**: Enter your name and email address
2. **Ask Questions**: Describe your IT issue in natural language
3. **Get Solutions**: Receive step-by-step troubleshooting instructions
4. **End Session**: Type "end", "finished", or click the "End Session" button
5. **Email Summary**: A summary is automatically sent to the IT team

### Example Interactions (German)

- "Ich kann mich nicht mit dem VPN verbinden"
- "Mein Passwort funktioniert nicht"
- "Der Drucker hat einen Papierstau"
- "Mein Computer läuft sehr langsam"
- "Outlook synchronisiert meine E-Mails nicht"
- "Die Software stürzt immer ab"

## API Endpoints

- `GET /` - Main chat interface
- `POST /start_session` - Initialize a new chat session
- `POST /send_message` - Send a message and get bot response
- `POST /end_session` - End the current session
- `GET /get_chat_history` - Retrieve chat history

## File Structure

```
it-support-bot/
├── app.py                 # Main Flask application
├── templates/
│   └── index.html        # Web interface
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── setup.sh            # Setup script
└── README.md           # This file
```

## Customization

### Adding New IT Solutions

Edit the `IT_KNOWLEDGE_BASE` dictionary in `app.py`:

```python
IT_KNOWLEDGE_BASE = {
    'new_issue': {
        'keywords': ['keyword1', 'keyword2'],
        'title': 'Issue Title',
        'steps': [
            "1. First step",
            "2. Second step",
            "3. Final step"
        ]
    }
}
```

### UI Features

The modern interface includes:
- **Glassmorphic Design**: Translucent panels with backdrop blur effects
- **Smooth Animations**: Slide-in messages, button hover effects, and transitions
- **Custom Scrollbars**: Styled scrollbars matching the theme
- **Responsive Layout**: Adapts perfectly to all screen sizes
- **Loading Indicators**: Modern spinning loaders during operations
- **Status Messages**: Animated success/error notifications
- **Gradient Themes**: Beautiful color gradients throughout the interface

## Production Deployment

### Azure App Service

1. Create an Azure App Service
2. Configure environment variables in the Azure portal
3. Deploy using Git or Azure DevOps

### Environment Variables for Production

Set these in your production environment:
- `SECRET_KEY`: Strong random secret key
- `SMTP_SERVER`: Your email server
- `SMTP_PORT`: Email server port
- `SENDER_EMAIL`: Sender email address
- `SENDER_PASSWORD`: Email password/app password

### Security Considerations

- Use HTTPS in production
- Store secrets in environment variables
- Implement rate limiting
- Add input validation and sanitization
- Consider using Azure Key Vault for secrets

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Testing Email Functionality

For testing without sending real emails, you can modify the `send_email_summary` function to log instead of sending emails.

## Troubleshooting

### Common Issues

1. **Email not sending**: Check SMTP settings and firewall rules
2. **Session not persisting**: Ensure SECRET_KEY is set
3. **Dependencies not found**: Run `pip install -r requirements.txt`

### Logs

The application logs important events. Check the console output for debugging information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section above