import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { tasksAPI } from '../api/client';

export default function Task({ route }) {
  const { taskId, mode } = route.params || {};
  const [status, setStatus] = useState(null);

  useEffect(() => {
    if (!taskId) return;
    const interval = setInterval(async () => {
      try {
        const res = await tasksAPI.getStatus(taskId);
        setStatus(res.data);
        if (res.data.status === 'completed' || res.data.status === 'failed') {
          clearInterval(interval);
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [taskId]);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Task: {taskId || mode || 'N/A'}</Text>
      {status ? (
        <>
          <Text>Status: {status.status}</Text>
          {status.council_verdict && (
            <Text style={styles.verdict}>
              Council: {status.council_verdict.verdict} (Score: {status.council_verdict.score})
            </Text>
          )}
          {status.result && <Text style={styles.result}>{status.result}</Text>}
        </>
      ) : (
        <Text>Loading...</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 18, fontWeight: 'bold', marginBottom: 10 },
  verdict: { fontSize: 16, marginVertical: 5 },
  result: { backgroundColor: '#f0f0f0', padding: 10, marginTop: 10 },
});
