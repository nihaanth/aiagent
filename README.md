# AI Medical Agent

A medical assistant AI agent with voice capabilities, built with Python backend and React Native/Expo frontend.

## Project Structure

```
agent/
├── main.py                 # Main Python backend server
├── medical_functions.py    # Medical function implementations
├── pharma_functions.py     # Pharmacy-related functions
├── mobile_bridge.py        # Mobile app bridge
├── config.json            # Agent configuration
├── requirements.txt       # Python dependencies
├── pharmacy-app/          # React Native/Expo frontend
│   ├── App.js
│   ├── package.json
│   └── components/        # React Native components
└── README.md
```

## Prerequisites

- Python 3.8+
- Node.js 20.19.4+ (as specified in package.json volta config)
- npm 10.9.3+
- Expo CLI
- ngrok account
- Twilio account
- Deepgram API key
- OpenAI API key

## Setup Instructions

### 1. Python Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment variables:**
   Create a `.env` file in the root directory:
   ```env
   DEEPGRAM_API_KEY=your_deepgram_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   ```

3. **Start the Python server:**
   ```bash
   python main.py
   ```

### 2. React Native/Expo App Setup

1. **Navigate to the app directory:**
   ```bash
   cd pharmacy-app
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the Expo development server:**
   ```bash
   npm start
   # or
   expo start
   ```

4. **Run on specific platforms:**
   ```bash
   # For iOS simulator
   npm run ios
   
   # For Android emulator
   npm run android
   
   # For web browser
   npm run web
   ```

### 3. Twilio Phone Number Verification Setup

1. **Log into your Twilio Console:**
   - Go to [console.twilio.com](https://console.twilio.com)

2. **Get a Twilio phone number:**
   - Navigate to Phone Numbers → Manage → Buy a number
   - Choose a number that supports voice capabilities
   - Purchase the number

3. **Configure webhook URL:**
   - In Phone Numbers → Manage → Active numbers
   - Click on your purchased number
   - Set the webhook URL to your ngrok tunnel (see ngrok setup below)
   - Set HTTP method to POST

4. **Add phone number to Twilio Verify:**
   - Go to Verify → Services in Twilio Console
   - Create a new Verify service or use existing
   - Add your phone number to the service for testing

### 4. ngrok Setup

1. **Install ngrok:**
   ```bash
   # Using npm
   npm install -g ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Authenticate ngrok:**
   ```bash
   ngrok authtoken YOUR_NGROK_AUTH_TOKEN
   ```

3. **Start ngrok tunnel:**
   ```bash
   # Expose local Python server (assuming it runs on port 8000)
   ngrok http 8000
   ```

4. **Copy the HTTPS URL:**
   - ngrok will provide URLs like `https://abc123.ngrok.io`
   - Use this URL in your Twilio webhook configuration
   - Update any hardcoded URLs in your code to use this ngrok URL

### 5. Environment Configuration

Ensure your `.env` file contains all required variables:

```env
# Deepgram (for speech-to-text and text-to-speech)
DEEPGRAM_API_KEY=your_deepgram_api_key

# OpenAI (for AI responses)
OPENAI_API_KEY=your_openai_api_key

# Twilio (for phone integration)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# Server configuration
SERVER_PORT=8000
NGROK_URL=https://your-ngrok-url.ngrok.io
```

## Running the Complete System

1. **Start the Python backend:**
   ```bash
   python main.py
   ```

2. **Start ngrok tunnel (in a separate terminal):**
   ```bash
   ngrok http 8000
   ```

3. **Start the React Native app (in a separate terminal):**
   ```bash
   cd pharmacy-app
   npm start
   ```

4. **Update Twilio webhook:**
   - Copy the ngrok HTTPS URL
   - Update your Twilio phone number webhook configuration

## Testing

1. **Test the mobile app:**
   - Scan the QR code with Expo Go app on your phone
   - Or run in iOS/Android simulator

2. **Test phone integration:**
   - Call your Twilio phone number
   - The AI agent should answer and interact with you

3. **Test medical functions:**
   - Try asking about symptoms, medications, or scheduling appointments
   - The AI should use the configured medical functions

## Troubleshooting

### Common Issues

1. **ngrok tunnel disconnected:**
   - Restart ngrok and update Twilio webhook URL

2. **Python dependencies issues:**
   - Ensure you're using Python 3.8+
   - Try creating a virtual environment: `python -m venv venv && source venv/bin/activate`

3. **React Native Metro bundler issues:**
   - Clear cache: `expo start --clear`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

4. **Audio not working:**
   - Check device permissions for microphone
   - Ensure WebRTC is properly configured

### Logs and Debugging

- Python backend logs: Check terminal where `python main.py` is running
- React Native logs: Check Metro bundler terminal and device console
- Twilio logs: Check Twilio Console → Monitor → Logs
- ngrok logs: Check ngrok terminal for request logs

## Features

- **Voice AI Agent:** Real-time voice conversation with medical AI
- **Medical Functions:** Symptom assessment, medication info, appointment scheduling
- **Pharmacy Integration:** Pharmacy-specific functions and workflows
- **Mobile App:** Cross-platform React Native app with Expo
- **Twilio Integration:** Phone call support for voice interactions
- **Real-time Communication:** WebSocket-based real-time audio streaming

## API Keys Required

1. **Deepgram API Key:** For speech-to-text and text-to-speech
2. **OpenAI API Key:** For AI conversation capabilities
3. **Twilio Account:** For phone number and voice capabilities
4. **ngrok Account:** For secure tunneling (free tier available)
