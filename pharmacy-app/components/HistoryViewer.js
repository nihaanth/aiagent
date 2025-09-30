import React from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Surface,
  Text,
  Title,
  Chip,
  Card,
  Badge,
  Divider,
  IconButton,
  Button,
} from 'react-native-paper';

const MessageBubble = ({ message, isUser = false }) => {
  const displayText = message?.text ?? message?.content ?? '';
  const timestamp = message?.timestamp ? new Date(message.timestamp) : null;
  const hasValidTimestamp = timestamp && !Number.isNaN(timestamp.getTime());

  return (
    <View style={[styles.messageContainer, isUser ? styles.userMessage : styles.agentMessage]}>
      <Surface style={[styles.messageBubble, isUser ? styles.userBubble : styles.agentBubble]}>
        <Text style={[styles.messageText, isUser ? styles.userText : styles.agentText]}>
          {displayText}
        </Text>
        {hasValidTimestamp && (
          <Text style={styles.timestamp}>
            {timestamp.toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit'
            })}
          </Text>
        )}
      </Surface>
    </View>
  );
};

const FunctionCallCard = ({ functionCall }) => (
  <Card style={styles.functionCard}>
    <Card.Content>
      <View style={styles.functionHeader}>
        <Text style={styles.functionName}>📋 {functionCall.name}</Text>
        <Text style={styles.functionTime}>
          {new Date(functionCall.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })}
        </Text>
      </View>

      {functionCall.parameters && Object.keys(functionCall.parameters).length > 0 && (
        <View style={styles.parametersContainer}>
          <Text style={styles.sectionTitle}>Parameters:</Text>
          {Object.entries(functionCall.parameters).map(([key, value]) => (
            <Text key={key} style={styles.parameterText}>
              • {key}: {JSON.stringify(value)}
            </Text>
          ))}
        </View>
      )}

      {functionCall.result && (
        <View style={styles.resultContainer}>
          <Text style={styles.sectionTitle}>Result:</Text>
          <Text style={styles.resultText}>
            {typeof functionCall.result === 'object'
              ? JSON.stringify(functionCall.result, null, 2)
              : functionCall.result}
          </Text>
        </View>
      )}
    </Card.Content>
  </Card>
);

const HistoryViewer = ({ history, onClose, isLoading }) => {
  if (isLoading) {
    return (
      <Surface style={styles.container}>
        <View style={styles.loadingContainer}>
          <Text>Loading conversation history...</Text>
        </View>
      </Surface>
    );
  }

  if (!history) {
    return (
      <Surface style={styles.container}>
        <View style={styles.emptyContainer}>
          <Text style={styles.emptyText}>No conversation history found</Text>
          <Button mode="outlined" onPress={onClose} style={styles.closeButton}>
            Close
          </Button>
        </View>
      </Surface>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString([], {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4CAF50';
      case 'in_progress': return '#FF9800';
      default: return '#757575';
    }
  };

  return (
    <Surface style={styles.container}>
      <View style={styles.header}>
        <Title style={styles.title}>Call History</Title>
        <IconButton icon="close" onPress={onClose} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Session Info */}
        <Card style={styles.sessionCard}>
          <Card.Content>
            <View style={styles.sessionHeader}>
              <Text style={styles.sessionTitle}>Session Details</Text>
              <Badge
                style={[styles.statusBadge, { backgroundColor: getStatusColor(history.status) }]}
              >
                {history.status}
              </Badge>
            </View>

            <View style={styles.sessionDetails}>
              <Text style={styles.detailRow}>
                📞 Phone: {history.phoneNumber}
              </Text>
              <Text style={styles.detailRow}>
                👤 User: {history.username}
              </Text>
              <Text style={styles.detailRow}>
                📅 Date: {formatDate(history.createdAt)}
              </Text>
              {history.endedAt && (
                <Text style={styles.detailRow}>
                  ⏰ Ended: {formatDate(history.endedAt)}
                </Text>
              )}
            </View>
          </Card.Content>
        </Card>

        {/* Messages */}
        {history.messages && history.messages.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>💬 Conversation</Text>
            {history.messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message}
                isUser={message.role === 'user'}
              />
            ))}
          </View>
        )}

        {/* Function Calls */}
        {history.functionCalls && history.functionCalls.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>🔧 Medical Functions Used</Text>
            {history.functionCalls.map((functionCall, index) => (
              <FunctionCallCard key={index} functionCall={functionCall} />
            ))}
          </View>
        )}

        {/* Empty state for messages */}
        {(!history.messages || history.messages.length === 0) &&
         (!history.functionCalls || history.functionCalls.length === 0) && (
          <View style={styles.emptySection}>
            <Text style={styles.emptyText}>No conversation data available</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.footer}>
        <Button mode="contained" onPress={onClose} style={styles.closeButton}>
          Close History
        </Button>
      </View>
    </Surface>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#2E7D32',
    flex: 1,
  },
  content: {
    flex: 1,
    padding: 16,
  },
  sessionCard: {
    marginBottom: 16,
    elevation: 2,
  },
  sessionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  sessionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  statusBadge: {
    color: 'white',
    fontSize: 12,
  },
  sessionDetails: {
    marginTop: 8,
  },
  detailRow: {
    fontSize: 14,
    marginBottom: 4,
    color: '#666',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
    color: '#2E7D32',
  },
  messageContainer: {
    marginBottom: 12,
  },
  userMessage: {
    alignItems: 'flex-end',
  },
  agentMessage: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 12,
    elevation: 1,
  },
  userBubble: {
    backgroundColor: '#2E7D32',
    borderBottomRightRadius: 4,
  },
  agentBubble: {
    backgroundColor: '#FFFFFF',
    borderBottomLeftRadius: 4,
  },
  messageText: {
    fontSize: 14,
    lineHeight: 20,
  },
  userText: {
    color: 'white',
  },
  agentText: {
    color: '#333',
  },
  timestamp: {
    fontSize: 10,
    color: '#999',
    marginTop: 4,
    alignSelf: 'flex-end',
  },
  functionCard: {
    marginBottom: 12,
    elevation: 1,
  },
  functionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  functionName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
  },
  functionTime: {
    fontSize: 12,
    color: '#666',
  },
  parametersContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#F0F0F0',
    borderRadius: 6,
  },
  parameterText: {
    fontSize: 12,
    color: '#333',
    marginBottom: 2,
  },
  resultContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#E8F5E8',
    borderRadius: 6,
  },
  resultText: {
    fontSize: 12,
    color: '#2E7D32',
    fontFamily: 'monospace',
  },
  emptySection: {
    padding: 32,
    alignItems: 'center',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
  },
  closeButton: {
    backgroundColor: '#2E7D32',
  },
});

export default HistoryViewer;
