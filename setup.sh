#!/bin/bash

# IT Support Bot Setup Script

echo "🛠️  Setting up IT Support Bot..."

# Check if conda environment exists
if conda env list | grep -q "it-support-bot"; then
    echo "✅ Conda environment 'it-support-bot' found"
    source activate it-support-bot
else
    echo "❌ Conda environment 'it-support-bot' not found"
    echo "Please create it first with: conda create -n it-support-bot python=3.9"
    exit 1
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your email configuration"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "1. Edit the .env file with your email settings"
echo "2. Run: python app.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "For production deployment, consider:"
echo "- Using a proper WSGI server like Gunicorn"
echo "- Setting up HTTPS"
echo "- Using environment variables for secrets"
echo "- Deploying to Azure App Service or similar"
