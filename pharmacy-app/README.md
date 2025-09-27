# Pharmacy Assistant Mobile App

A React Native app that connects to your pharmacy assistant agent with live transcription and real-time function calls display.

## Features

- **Live Transcription**: Real-time speech-to-text display
- **Agent Responses**: See pharmacy assistant responses in real-time
- **Function Calls**: Monitor all pharmacy functions being executed
- **Professional UI**: Clean, medical-themed interface
- **Real-time Connection**: WebSocket connection to pharmacy agent

## Setup Instructions

### Prerequisites

1. Node.js (v16 or higher)
2. Expo CLI
3. Your pharmacy agent running on localhost:5000

### Installation

1. Install dependencies:
```bash
cd pharmacy-app
npm install
```

2. Install Expo CLI globally (if not already installed):
```bash
npm install -g @expo/cli
```

3. Start the development server:
```bash
npx expo start
```

### Running the App

1. **Start your pharmacy agent first**:
```bash
cd ..
python main.py
```

2. **Start the React Native app**:
```bash
npx expo start
```

3. **Choose your platform**:
   - Press `i` for iOS Simulator
   - Press `a` for Android Emulator  
   - Scan QR code with Expo Go app on your phone

## App Components

### Main Features

- **Header**: Pharmacy Assistant branding
- **Connection Status**: Shows connection state to backend
- **Transcription Display**: Live conversation with user and assistant
- **Function Calls**: Real-time display of pharmacy functions being executed
- **Audio Controls**: Record button with visual feedback

### Pharmacy Functions Supported

- 💊 **get_drug_info**: Get comprehensive drug information
- 📋 **place_order**: Place medication orders
- 🔍 **lookup_order**: Check order status
- ⚠️ **check_drug_interactions**: Drug interaction checking
- 🔄 **get_drug_alternatives**: Find alternative medications
- 📄 **check_prescription_status**: Track prescription status

## Architecture

```
Mobile App (Port 8080) ←→ Mobile Bridge ←→ Pharmacy Agent (Port 5000) ←→ Twilio/Deepgram
```

The app connects to a mobile bridge server that relays real-time data from your pharmacy agent:
- Live transcriptions from Deepgram
- Agent responses 
- Function call executions with parameters and results

## Demo Features

Perfect for demonstrating:
- Real-time voice interaction with pharmacy assistant
- Live transcription display
- Function call monitoring
- Professional pharmacy UI
- Cross-platform mobile experience

## Troubleshooting

1. **Connection Issues**: Ensure pharmacy agent is running on localhost:5000
2. **Audio Permissions**: Grant microphone permissions when prompted
3. **Network**: Ensure both servers are accessible on localhost

## File Structure

```
pharmacy-app/
├── App.js                 # Main app component
├── components/
│   ├── Header.js          # App header
│   ├── ConnectionStatus.js # Connection indicator
│   ├── TranscriptionDisplay.js # Live transcription
│   ├── PharmacyFunctions.js # Function calls display
│   └── AudioControls.js   # Recording controls
├── package.json
└── app.json
```