```jsx
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import LoginScreen from './src/screens/Login';
import DashboardScreen from './src/screens/Dashboard';
import TaskScreen from './src/screens/Task';
import AgentsScreen from './src/screens/Agents';
import CouncilScreen from './src/screens/Council';
import OverrideScreen from './src/screens/Override';

const Stack = createNativeStackNavigator();

export default function App() {
  const [isAuth, setIsAuth] = useState(false);

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!isAuth ? (
          <Stack.Screen name="Login" options={{ headerShown: false }}>
            {(props) => <LoginScreen {...props} onLogin={() => setIsAuth(true)} />}
          </Stack.Screen>
        ) : (
          <>
            <Stack.Screen name="Dashboard" component={DashboardScreen} />
            <Stack.Screen name="Task" component={TaskScreen} />
            <Stack.Screen name="Agents" component={AgentsScreen} />
            <Stack.Screen name="Council" component={CouncilScreen} />
            <Stack.Screen name="Override" component={OverrideScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
