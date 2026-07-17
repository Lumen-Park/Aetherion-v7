import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, Alert } from 'react-native';
import * as SecureStore from 'expo-secure-store';
import { authAPI } from '../api/client';

export default function LoginScreen({ onLogin }) {
  const [apiKey, setApiKey] = useState('');

  const handleLogin = async () => {
    try {
      const res = await authAPI.login(apiKey);
      await SecureStore.setItemAsync('aetherion_token', res.data.access_token);
      onLogin();
    } catch (e) {
      Alert.alert('Error', 'Invalid API key or server unreachable');
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Enter API Key"
        value={apiKey}
        onChangeText={setApiKey}
        secureTextEntry
        style={styles.input}
      />
      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  input: { borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5 },
});
