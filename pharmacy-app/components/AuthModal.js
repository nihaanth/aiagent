import React, { useState } from 'react';
import { View, StyleSheet, Alert } from 'react-native';
import {
  Modal,
  Portal,
  Text,
  TextInput,
  Button,
  Surface,
  Title,
  HelperText,
  IconButton,
} from 'react-native-paper';

const AuthModal = ({ visible, onDismiss, onAuthenticate, isLoading }) => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [passcode, setPasscode] = useState('');
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    const newErrors = {};

    // Phone number validation
    const phoneRegex = /^\+?1?[2-9]\d{2}[2-9]\d{2}\d{4}$/;
    if (!phoneNumber) {
      newErrors.phoneNumber = 'Phone number is required';
    } else if (!phoneRegex.test(phoneNumber.replace(/\D/g, ''))) {
      newErrors.phoneNumber = 'Please enter a valid phone number';
    }

    // Passcode validation
    if (!passcode) {
      newErrors.passcode = 'Passcode is required';
    } else if (!/^\d{6}$/.test(passcode)) {
      newErrors.passcode = 'Passcode must be 6 digits';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      // Format phone number
      const formattedPhone = phoneNumber.startsWith('+')
        ? phoneNumber
        : `+1${phoneNumber.replace(/\D/g, '')}`;

      onAuthenticate(formattedPhone, passcode);
    }
  };

  const formatPhoneNumber = (text) => {
    // Remove all non-digits
    const digits = text.replace(/\D/g, '');

    // Format as (XXX) XXX-XXXX
    if (digits.length >= 6) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6, 10)}`;
    } else if (digits.length >= 3) {
      return `(${digits.slice(0, 3)}) ${digits.slice(3)}`;
    } else {
      return digits;
    }
  };

  const handlePhoneChange = (text) => {
    const formatted = formatPhoneNumber(text);
    setPhoneNumber(formatted);
    if (errors.phoneNumber) {
      setErrors({ ...errors, phoneNumber: null });
    }
  };

  const handlePasscodeChange = (text) => {
    // Only allow digits and limit to 6 characters
    const digits = text.replace(/\D/g, '').slice(0, 6);
    setPasscode(digits);
    if (errors.passcode) {
      setErrors({ ...errors, passcode: null });
    }
  };

  const clearForm = () => {
    setPhoneNumber('');
    setPasscode('');
    setErrors({});
  };

  const handleDismiss = () => {
    clearForm();
    onDismiss();
  };

  return (
    <Portal>
      <Modal
        visible={visible}
        onDismiss={handleDismiss}
        contentContainerStyle={styles.modalContainer}
      >
        <Surface style={styles.surface}>
          <View style={styles.header}>
            <Title style={styles.title}>Retrieve Call History</Title>
            <IconButton icon="close" onPress={handleDismiss} />
          </View>

          <Text style={styles.description}>
            Enter your phone number and the 6-digit passcode provided during your call to access your conversation history.
          </Text>

          <View style={styles.inputContainer}>
            <TextInput
              label="Phone Number"
              value={phoneNumber}
              onChangeText={handlePhoneChange}
              mode="outlined"
              keyboardType="phone-pad"
              placeholder="(555) 123-4567"
              error={!!errors.phoneNumber}
              disabled={isLoading}
              left={<TextInput.Icon icon="phone" />}
            />
            <HelperText type="error" visible={!!errors.phoneNumber}>
              {errors.phoneNumber}
            </HelperText>
          </View>

          <View style={styles.inputContainer}>
            <TextInput
              label="6-Digit Passcode"
              value={passcode}
              onChangeText={handlePasscodeChange}
              mode="outlined"
              keyboardType="numeric"
              placeholder="123456"
              error={!!errors.passcode}
              disabled={isLoading}
              maxLength={6}
              secureTextEntry
              left={<TextInput.Icon icon="lock" />}
            />
            <HelperText type="error" visible={!!errors.passcode}>
              {errors.passcode}
            </HelperText>
          </View>

          <View style={styles.buttonContainer}>
            <Button
              mode="outlined"
              onPress={handleDismiss}
              style={[styles.button, styles.cancelButton]}
              disabled={isLoading}
            >
              Cancel
            </Button>
            <Button
              mode="contained"
              onPress={handleSubmit}
              style={[styles.button, styles.submitButton]}
              loading={isLoading}
              disabled={isLoading}
            >
              Retrieve History
            </Button>
          </View>

          <Text style={styles.helpText}>
            💡 Your passcode was provided at the beginning of your call. Contact support if you need assistance.
          </Text>
        </Surface>
      </Modal>
    </Portal>
  );
};

const styles = StyleSheet.create({
  modalContainer: {
    margin: 20,
    maxHeight: '80%',
  },
  surface: {
    padding: 20,
    borderRadius: 12,
    elevation: 4,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2E7D32',
    flex: 1,
  },
  description: {
    fontSize: 14,
    color: '#666',
    marginBottom: 24,
    lineHeight: 20,
  },
  inputContainer: {
    marginBottom: 16,
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 24,
    marginBottom: 16,
  },
  button: {
    flex: 1,
    marginHorizontal: 8,
  },
  cancelButton: {
    borderColor: '#666',
  },
  submitButton: {
    backgroundColor: '#2E7D32',
  },
  helpText: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

export default AuthModal;