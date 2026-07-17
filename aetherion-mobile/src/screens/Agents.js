import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { agentsAPI } from '../api/client';

export default function Agents() {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    agentsAPI.list().then((res) => setAgents(res.data.agents));
  }, []);

  return (
    <FlatList
      data={agents}
      keyExtractor={(item) => item.name}
      renderItem={({ item }) => (
        <View style={styles.item}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.college}>{item.college}</Text>
          <Text>{item.expertise}</Text>
        </View>
      )}
    />
  );
}

const styles = StyleSheet.create({
  item: { padding: 15, borderBottomWidth: 1, borderColor: '#ddd' },
  name: { fontWeight: 'bold', fontSize: 16 },
  college: { color: '#666' },
});
