import React, { useState } from 'react';
import { View, TextInput, Button, Alert, StyleSheet } from 'react-native';
import apiClient from '../api/client';

export default function Override() {
  const [taskId, setTaskId] = useState('');
  const [reason, setReason] = useState('');

  const handleOverride = async () => {
    try {
      const res = await apiClient.post(`/tasks/override/${taskId}`, null, { params: { reason } });
      Alert.alert('Success', res.data.status);
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput placeholder="Task ID" value={taskId} onChangeText={setTaskId} style={styles.input} />
      <TextInput placeholder="Reason" value={reason} onChangeText={setReason} style={styles.input} />
      <Button title="Apply Override" onPress={handleOverride} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  input: { borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5 },
});
