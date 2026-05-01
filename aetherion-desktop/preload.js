```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  getServerUrl: () => process.env.AETHERION_SERVER || 'http://localhost:8000',
  setServerUrl: (url) => ipcRenderer.invoke('set-server-url', url),
});
