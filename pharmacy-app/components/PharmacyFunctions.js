import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Card, Text, Chip, List, Button, Divider } from 'react-native-paper';

const PharmacyFunctions = ({ functionCalls }) => {
  const [expandedItems, setExpandedItems] = useState({});

  const toggleExpanded = (id) => {
    setExpandedItems(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const getFunctionIcon = (functionName) => {
    switch (functionName) {
      case 'assess_symptoms':
        return '';
      case 'get_medication_info':
        return '';
      case 'schedule_appointment':
        return '';
      case 'check_appointment':
        return '';
      case 'get_health_tips':
        return '';
      case 'emergency_guidance':
        return '';
      default:
        return '';
    }
  };

  const getFunctionColor = (functionName) => {
    switch (functionName) {
      case 'assess_symptoms':
        return '#2196F3';
      case 'get_medication_info':
        return '#4CAF50';
      case 'schedule_appointment':
        return '#FF9800';
      case 'check_appointment':
        return '#9C27B0';
      case 'get_health_tips':
        return '#607D8B';
      case 'emergency_guidance':
        return '#F44336';
      default:
        return '#757575';
    }
  };

  const formatResult = (result) => {
    if (typeof result === 'object') {
      return JSON.stringify(result, null, 2);
    }
    return String(result);
  };

  if (functionCalls.length === 0) {
    return (
      <Card style={styles.card}>
        <Card.Content>
          <Text style={styles.title}>Function Calls</Text>
          <Text style={styles.placeholderText}>
            Medical functions will appear here when Dr Tips processes your requests...
          </Text>
        </Card.Content>
      </Card>
    );
  }

  return (
    <Card style={styles.card}>
      <Card.Content>
        <View style={styles.header}>
          <Text style={styles.title}>Function Calls</Text>
          <Chip style={styles.countChip}>
            {functionCalls.length}
          </Chip>
        </View>
        
        <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
          {functionCalls.map((call, index) => (
            <View key={call.id} style={styles.functionCallContainer}>
              <List.Item
                title={
                  <View style={styles.functionHeader}>
                    <Text style={styles.functionIcon}>
                      {getFunctionIcon(call.name)}
                    </Text>
                    <Text style={styles.functionName}>{call.name}</Text>
                  </View>
                }
                description={`Called at ${call.timestamp}`}
                right={() => (
                  <Button
                    mode="outlined"
                    compact
                    onPress={() => toggleExpanded(call.id)}
                    style={[
                      styles.expandButton,
                      { borderColor: getFunctionColor(call.name) }
                    ]}
                  >
                    {expandedItems[call.id] ? 'Hide' : 'Details'}
                  </Button>
                )}
                style={[
                  styles.listItem,
                  { borderLeftColor: getFunctionColor(call.name) }
                ]}
              />
              
              {expandedItems[call.id] && (
                <View style={styles.expandedContent}>
                  <Text style={styles.sectionTitle}>Parameters:</Text>
                  <View style={styles.codeBlock}>
                    <Text style={styles.codeText}>
                      {JSON.stringify(call.parameters, null, 2)}
                    </Text>
                  </View>
                  
                  <Text style={styles.sectionTitle}>Result:</Text>
                  <View style={styles.codeBlock}>
                    <Text style={styles.codeText}>
                      {formatResult(call.result)}
                    </Text>
                  </View>
                </View>
              )}
              
              {index < functionCalls.length - 1 && <Divider style={styles.divider} />}
            </View>
          ))}
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
  countChip: {
    backgroundColor: '#E8F5E8',
  },
  scrollView: {
    maxHeight: 300,
  },
  functionCallContainer: {
    marginVertical: 4,
  },
  listItem: {
    backgroundColor: '#FAFAFA',
    borderRadius: 8,
    borderLeftWidth: 4,
    paddingLeft: 12,
  },
  functionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  functionIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  functionName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  expandButton: {
    alignSelf: 'center',
  },
  expandedContent: {
    padding: 12,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#555',
    marginBottom: 8,
    marginTop: 8,
  },
  codeBlock: {
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#E0E0E0',
  },
  codeText: {
    fontFamily: 'monospace',
    fontSize: 12,
    color: '#333',
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

export default PharmacyFunctions;
