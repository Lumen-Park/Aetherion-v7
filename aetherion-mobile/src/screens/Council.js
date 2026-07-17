import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { councilAPI } from '../api/client';

export default function Council() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    councilAPI.stats().then((res) => setStats(res.data));
  }, []);

  if (!stats) return <Text>Loading...</Text>;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Council Statistics</Text>
      <Text>Total Verdicts: {stats.total}</Text>
      <Text>Approval Rate: {(stats.approval_rate * 100).toFixed(1)}%</Text>
      <Text>Average Score: {stats.avg_score?.toFixed(2)}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  title: { fontSize: 20, fontWeight: 'bold', marginBottom: 15 },
});
