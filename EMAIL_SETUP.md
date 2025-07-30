# Email Configuration Guide

This guide explains how to configure email functionality for the IT Support Chatbot.

## Option 1: Gmail (Recommended for Testing)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"
3. **Update .env file**:
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SENDER_EMAIL=your-gmail@gmail.com
   SENDER_PASSWORD=your-16-digit-app-password
   ```

## Option 2: Outlook/Office 365

1. **Update .env file**:
   ```env
   SMTP_SERVER=smtp-mail.outlook.com
   SMTP_PORT=587
   SENDER_EMAIL=your-email@outlook.com
   SENDER_PASSWORD=your-password
   ```

## Option 3: Azure Communication Services (Production)

For production deployments, consider using Azure Communication Services:

1. **Create an Azure Communication Services resource**
2. **Get connection string from Azure portal**
3. **Update code to use Azure Communication Services SDK**

## Option 4: SendGrid (Production Alternative)

1. **Create SendGrid account**
2. **Get API key**
3. **Update .env file**:
   ```env
   SENDGRID_API_KEY=your-sendgrid-api-key
   SENDER_EMAIL=verified-sender@yourdomain.com
   ```

## Testing Email Functionality

1. Update the `.env` file with real credentials
2. Restart the Flask application
3. Complete a chat session and end it
4. Check the target email address for the summary

## Security Notes

- Never commit real credentials to version control
- Use environment variables in production
- Consider using Azure Key Vault for secrets
- Implement rate limiting for email sending
- Validate email addresses before sending

## Troubleshooting

### Common Issues:
1. **Authentication failed**: Check credentials and app passwords
2. **Connection timeout**: Check firewall and network settings
3. **TLS errors**: Ensure correct SMTP port (587 for TLS, 465 for SSL)

### Development Mode:
- The application logs email content instead of sending real emails
- Look for "EMAIL CONTENT PREVIEW" in the console logs
- This prevents accidental spam during development
