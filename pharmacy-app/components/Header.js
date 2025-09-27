import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Appbar, Title } from 'react-native-paper';

const Header = () => {
  return (
    <Appbar.Header style={styles.header}>
      <View style={styles.headerContent}>
        <Appbar.Content 
          title="🩺 Dr. Claude AI" 
          titleStyle={styles.title}
        />
      </View>
    </Appbar.Header>
  );
};

const styles = StyleSheet.create({
  header: {
    backgroundColor: '#2E7D32',
    elevation: 4,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  headerContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#FFFFFF',
  },
});

export default Header;