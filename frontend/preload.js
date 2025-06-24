const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electron', {
  getActiveWindow: () => ipcRenderer.invoke('get-active-window'),
}); 