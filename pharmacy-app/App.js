// Import minimal polyfills for iOS compatibility
import './polyfills-minimal';

import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, View, ScrollView } from 'react-native';
import { Provider as PaperProvider, DefaultTheme } from 'react-native-paper';
import { StatusBar } from 'expo-status-bar';

import Header from './components/Header';
import ConversationDisplay from './components/ConversationDisplay';
import TextInput from './components/TextInput';
import ConnectionStatus from './components/ConnectionStatus';
import AuthModal from './components/AuthModal';
import HistoryViewer from './components/HistoryViewer';

const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#2E7D32',
    accent: '#4CAF50',
    background: '#F8F9FA',
    surface: '#FFFFFF',
    error: '#F44336',
  },
};

export default function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [userMessage, setUserMessage] = useState('');
  const [agentResponse, setAgentResponse] = useState('');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [conversationHistory, setConversationHistory] = useState(null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  const wsRef = useRef(null);

  useEffect(() => {
    connectToAgent();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Auto-load recent conversation for testing
  const autoLoadRecentConversation = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log('Auto-loading recent conversations from database...');

      // Request recent conversations instead of using hardcoded credentials
      setIsLoadingHistory(true);
      wsRef.current.send(JSON.stringify({
        command: 'get_recent_conversations'
      }));
    }
  };

  // Auto-load conversation when connected
  useEffect(() => {
    if (isConnected && !conversationHistory) {
      // Wait a moment for connection to stabilize, then auto-load
      const timer = setTimeout(autoLoadRecentConversation, 1000);
      return () => clearTimeout(timer);
    }
  }, [isConnected, conversationHistory]);

  const sendMessage = (message) => {
    if (!message.trim() || !isConnected) return;
    
    console.log(`Sending message: "${message}"`);
    setUserMessage(message);
    
    // Send message to backend
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        event: 'user_message',
        message: message.trim(),
        timestamp: new Date().toISOString()
      }));
    }
  };

  const connectToAgent = () => {
    // Don't create multiple connections
    if (wsRef.current && wsRef.current.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket already connecting, skipping...');
      return;
    }

    try {
      console.log('Attempting to connect to Dr. Claude AI at ws://localhost:9004');
      // Connect to the mobile bridge server
      const ws = new WebSocket('ws://localhost:9004');
      
      ws.onopen = () => {
        console.log('Connected to Dr. Claude AI');
        setIsConnected(true);
        
        // Send a ping to keep connection alive
        const pingInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            console.log('Sending ping to backend');
            ws.send(JSON.stringify({ command: 'ping' }));
          } else {
            clearInterval(pingInterval);
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received from backend:', data);
          handleAgentMessage(data);
        } catch (error) {
          console.error('Error parsing message:', error);
          console.error('Raw message:', event.data);
        }
      };

      ws.onclose = (event) => {
        console.log('Disconnected from Dr. Claude AI', event.code, event.reason);
        setIsConnected(false);
        
        // Only reconnect if it wasn't a clean close and we're not already connecting
        if (event.code !== 1000 && (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED)) {
          console.log('Reconnecting in 3 seconds...');
          setTimeout(connectToAgent, 3000);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect to agent:', error);
      setIsConnected(false);
      // Retry connection after delay
      setTimeout(connectToAgent, 5000);
    }
  };

  const handleAgentMessage = (data) => {
    switch (data.event) {
      case 'agent_response':
        console.log(`Agent response: "${data.text}"`);
        setAgentResponse(data.text);
        break;
      case 'function_call':
        console.log(`Function call: ${data.function_name}`, data.parameters);
        // Function calls are processed but not displayed in UI
        break;
      case 'connection_established':
        console.log('Connection established:', data.message);
        break;
      case 'pong':
        console.log('Pong received from backend');
        break;
      case 'history':
        console.log('Received conversation history:', data.history);
        setConversationHistory(data.history);
        setIsLoadingHistory(false);
        setShowHistory(true);
        setShowAuthModal(false);
        // Auto-display conversation history without requiring user to click
        break;
      case 'history_error':
        console.log('History error:', data.message);
        setIsLoadingHistory(false);
        alert(`Error retrieving history: ${data.message}`);
        break;
      case 'recent_conversations':
        console.log('Received recent conversations:', data.conversations);
        if (data.conversations && data.conversations.length > 0) {
          // Display the most recent conversation
          const mostRecent = data.conversations[0];
          setConversationHistory(mostRecent);
          setIsLoadingHistory(false);
          setShowHistory(true);
          setShowAuthModal(false);
        }
        break;
      case 'recent_conversations_error':
        console.log('Recent conversations error:', data.message);
        setIsLoadingHistory(false);
        // Don't show alert for this - just log it
        break;
      default:
        console.log('Unknown message type:', data);
    }
  };

  const clearConversation = () => {
    setUserMessage('');
    setAgentResponse('');
  };

  const handleAuthentication = (phoneNumber, passcode) => {
    setIsLoadingHistory(true);

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log(`Requesting history for ${phoneNumber} with passcode ${passcode}`);
      wsRef.current.send(JSON.stringify({
        command: 'fetch_history',
        phone_number: phoneNumber,
        passcode: passcode,
      }));
    } else {
      setIsLoadingHistory(false);
      alert('Not connected to server. Please try again.');
    }
  };

  const showHistoryModal = () => {
    setShowAuthModal(true);
  };

  const closeAuthModal = () => {
    setShowAuthModal(false);
    setIsLoadingHistory(false);
  };

  const closeHistoryViewer = () => {
    setShowHistory(false);
    setConversationHistory(null);
  };

  if (showHistory) {
    return (
      <PaperProvider theme={theme}>
        <View style={styles.container}>
          <StatusBar style="dark" />
          <HistoryViewer
            history={conversationHistory}
            onClose={closeHistoryViewer}
            isLoading={isLoadingHistory}
          />
        </View>
      </PaperProvider>
    );
  }

  return (
    <PaperProvider theme={theme}>
      <View style={styles.container}>
        <StatusBar style="dark" />

        <Header onViewHistory={showHistoryModal} />

        <ConnectionStatus isConnected={isConnected} />

        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          <ConversationDisplay
            userMessage={userMessage}
            agentResponse={agentResponse}
            onClear={clearConversation}
          />
        </ScrollView>

        <TextInput
          isConnected={isConnected}
          onSendMessage={sendMessage}
        />

        <AuthModal
          visible={showAuthModal}
          onDismiss={closeAuthModal}
          onAuthenticate={handleAuthentication}
          isLoading={isLoadingHistory}
        />
      </View>
    </PaperProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
});
