import React from 'react';
import { View, StyleSheet, Animated } from 'react-native';
import { FAB, Text, Card } from 'react-native-paper';

const AudioControls = ({ 
  isRecording, 
  isConnected, 
  onStartRecording, 
  onStopRecording 
}) => {
  const pulseAnim = React.useRef(new Animated.Value(1)).current;

  React.useEffect(() => {
    if (isRecording) {
      const pulse = Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 600,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 600,
            useNativeDriver: true,
          }),
        ]),
      );
      pulse.start();
      return () => pulse.stop();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isRecording, pulseAnim]);

  const handlePress = () => {
    if (!isConnected) return;
    
    if (isRecording) {
      onStopRecording();
    } else {
      onStartRecording();
    }
  };

  const getStatusText = () => {
    if (!isConnected) return 'Connecting...';
    if (isRecording) return 'Recording... Tap to stop';
    return 'Tap to start recording';
  };

  const getIcon = () => {
    if (isRecording) return 'stop';
    return 'microphone';
  };

  const getFabColor = () => {
    if (!isConnected) return '#BDBDBD';
    if (isRecording) return '#F44336';
    return '#2E7D32';
  };

  return (
    <Card style={styles.card}>
      <Card.Content style={styles.content}>
        <Text style={styles.statusText}>{getStatusText()}</Text>
        
        <View style={styles.fabContainer}>
          <Animated.View
            style={[
              styles.fabWrapper,
              {
                transform: [{ scale: pulseAnim }],
              },
            ]}
          >
            <FAB
              icon={getIcon()}
              onPress={handlePress}
              disabled={!isConnected}
              style={[
                styles.fab,
                { backgroundColor: getFabColor() }
              ]}
              color="#FFFFFF"
              size="large"
            />
          </Animated.View>
        </View>
        
        {isRecording && (
          <View style={styles.recordingIndicator}>
            <View style={styles.recordingDot} />
            <Text style={styles.recordingText}>Recording</Text>
          </View>
        )}
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
    alignItems: 'center',
    paddingVertical: 20,
  },
  statusText: {
    fontSize: 16,
    color: '#555',
    marginBottom: 20,
    textAlign: 'center',
  },
  fabContainer: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  fabWrapper: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  fab: {
    elevation: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
  },
  recordingIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 16,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#FFEBEE',
    borderRadius: 20,
  },
  recordingDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#F44336',
    marginRight: 8,
  },
  recordingText: {
    fontSize: 14,
    color: '#C62828',
    fontWeight: '500',
  },
});

export default AudioControls;