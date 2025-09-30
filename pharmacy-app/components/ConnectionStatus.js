import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Banner, Text } from 'react-native-paper';

const ConnectionStatus = ({ isConnected }) => {
  if (isConnected) {
    return (
      <Banner
        visible={true}
        style={styles.connectedBanner}
        icon="check-circle"
      >
        <Text style={styles.connectedText}>Connected to Dr Tips</Text>
      </Banner>
    );
  }

  return (
    <Banner
      visible={true}
      style={styles.disconnectedBanner}
      icon="alert-circle"
    >
      <Text style={styles.disconnectedText}>
        Connecting to Dr Tips...
      </Text>
    </Banner>
  );
};

const styles = StyleSheet.create({
  connectedBanner: {
    backgroundColor: '#E8F5E8',
    borderBottomWidth: 1,
    borderBottomColor: '#4CAF50',
  },
  disconnectedBanner: {
    backgroundColor: '#FFEBEE',
    borderBottomWidth: 1,
    borderBottomColor: '#F44336',
  },
  connectedText: {
    color: '#2E7D32',
    fontWeight: '500',
  },
  disconnectedText: {
    color: '#C62828',
    fontWeight: '500',
  },
});

export default ConnectionStatus;
