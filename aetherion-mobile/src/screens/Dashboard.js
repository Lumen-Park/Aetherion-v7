```jsx
import React, { useState } from 'react';
import { View, TextInput, Button, StyleSheet, Alert } from 'react-native';
import { tasksAPI } from '../api/client';

export default function Dashboard({ navigation }) {
  const [goal, setGoal] = useState('');

  const submitTask = async () => {
    const key = `${Date.now()}-${Math.random().toString(36)}`;
    try {
      const res = await tasksAPI.runPipeline(goal, key);
      navigation.navigate('Task', { taskId: res.data.task_id });
    } catch (e) {
      Alert.alert('Error', e.message);
    }
  };

  return (
    <View style={styles.container}>
      <TextInput
        placeholder="Enter research goal..."
        value={goal}
        onChangeText={setGoal}
        multiline
        style={styles.input}
      />
      <Button title="Run Pipeline" onPress={submitTask} />
      <View style={{ marginVertical: 10 }} />
      <Button
        title="Experiment Mode"
        onPress={() => navigation.navigate('Task', { taskId: null, mode: 'lab' })}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  input: { borderWidth: 1, padding: 10, marginVertical: 10, borderRadius: 5, height: 100 },
});
