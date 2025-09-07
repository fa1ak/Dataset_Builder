#!/bin/bash

# OpenAI Setup Script for Dataset Processor
echo "🤖 Setting up OpenAI integration for Dataset Processor..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created!"
else
    echo "⚠️  .env file already exists. Backing up to .env.backup..."
    cp .env .env.backup
fi

echo ""
echo "🔑 **Next Steps:**"
echo "1. Get your OpenAI API key from: https://platform.openai.com/api-keys"
echo "2. Edit the .env file and replace 'your_openai_api_key_here' with your actual API key"
echo "3. Install the new dependencies: pip install -r requirements.txt"
echo "4. Restart the application"
echo ""
echo "📝 **To edit .env file:**"
echo "   nano .env"
echo ""
echo "🔧 **To install dependencies:**"
echo "   pip install openai python-dotenv"
echo ""
echo "🚀 **To test the setup:**"
echo "   python -c \"from openai_client import openai_client; print('OpenAI available:', openai_client.is_available())\""
echo ""
echo "✅ Setup script completed!"
