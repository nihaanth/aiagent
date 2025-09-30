import React, { useState } from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, TextInput as PaperTextInput, Button } from 'react-native-paper';

const TextInput = ({ isConnected, onSendMessage }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && isConnected) {
      onSendMessage(message);
      setMessage(''); // Clear input after sending
    }
  };

  const handleKeyPress = (event) => {
    if (event.nativeEvent.key === 'Enter') {
      handleSend();
    }
  };

  return (
    <Card style={styles.card}>
      <Card.Content style={styles.content}>
        <View style={styles.inputContainer}>
          <PaperTextInput
            mode="outlined"
            placeholder={isConnected ? "Type your message to Dr Tips..." : "Connecting..."}
            value={message}
            onChangeText={setMessage}
            onSubmitEditing={handleSend}
            disabled={!isConnected}
            style={styles.textInput}
            multiline={false}
            right={
              <PaperTextInput.Icon
                icon="send"
                onPress={handleSend}
                disabled={!message.trim() || !isConnected}
              />
            }
          />
        </View>
        
        <Button
          mode="contained"
          onPress={handleSend}
          disabled={!message.trim() || !isConnected}
          style={[
            styles.sendButton,
            (!message.trim() || !isConnected) && styles.disabledButton
          ]}
          contentStyle={styles.buttonContent}
        >
          Send Message
        </Button>
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    margin: 16,
    elevation: 4,
    backgroundColor: '#FFFFFF',
  },
  content: {
    paddingVertical: 16,
  },
  inputContainer: {
    marginBottom: 12,
  },
  textInput: {
    backgroundColor: '#FAFAFA',
  },
  sendButton: {
    backgroundColor: '#2E7D32',
  },
  disabledButton: {
    backgroundColor: '#BDBDBD',
  },
  buttonContent: {
    paddingVertical: 8,
  },
});

export default TextInput;
