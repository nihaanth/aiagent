import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Button, Divider } from 'react-native-paper';

const TranscriptionDisplay = ({ transcription, agentResponse, onClear }) => {
  return (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.header}>
          <Text style={styles.title}>Live Conversation</Text>
          <Button 
            mode="outlined" 
            onPress={onClear}
            compact
            style={styles.clearButton}
          >
            Clear
          </Button>
        </View>
        
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          {transcription ? (
            <View style={styles.messageContainer}>
              <Text style={styles.label}>👤 You:</Text>
              <Text style={styles.userText}>{transcription}</Text>
            </View>
          ) : (
            <Text style={styles.placeholderText}>
              🎤 Start speaking to Dr. Claude AI...
            </Text>
          )}
          
          {agentResponse && (
            <>
              <Divider style={styles.divider} />
              <View style={styles.messageContainer}>
                <Text style={styles.label}>🩺 Dr. Claude:</Text>
                <Text style={styles.agentText}>{agentResponse}</Text>
              </View>
            </>
          )}
        </ScrollView>
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginVertical: 8,
    elevation: 2,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  clearButton: {
    borderColor: '#2E7D32',
  },
  scrollView: {
    maxHeight: 200,
  },
  messageContainer: {
    marginVertical: 8,
  },
  label: {
    fontSize: 14,
    fontWeight: 'bold',
    marginBottom: 4,
    color: '#555',
  },
  userText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    backgroundColor: '#F0F0F0',
    padding: 12,
    borderRadius: 8,
  },
  agentText: {
    fontSize: 16,
    lineHeight: 24,
    color: '#333',
    backgroundColor: '#E8F5E8',
    padding: 12,
    borderRadius: 8,
  },
  placeholderText: {
    fontSize: 14,
    color: '#999',
    fontStyle: 'italic',
    textAlign: 'center',
    padding: 20,
  },
  divider: {
    marginVertical: 8,
    backgroundColor: '#E0E0E0',
  },
});

export default TranscriptionDisplay;