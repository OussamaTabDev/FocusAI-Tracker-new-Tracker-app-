"use client"

import { useState } from "react"
import { TopBar } from "./components/TopBar"
import { Dashboard } from "./components/Dashboard"
import { SettingsWindow } from "./components/SettingsWindow"
import { ThemeProvider } from "./components/ThemeProvider"
import { useSystemTracker } from "./hooks/useSystemTracker"
import { Alert, AlertDescription } from "./components/ui/alert"
import { AlertTriangle } from "lucide-react"

function App() {
  const [currentMode, setCurrentMode] = useState("Standard")
  const [showSettings, setShowSettings] = useState(false)
  const [activeWindow, setActiveWindow] = useState(null)

  const { isTracking, currentData, systemInfo, error, startTracking, stopTracking } = useSystemTracker()

  const handleTrackingToggle = async () => {
    if (isTracking) {
      await stopTracking()
    } else {
      await startTracking()
    }
  }

  const fetchActiveWindow = async () => {
    if (window.electron && window.electron.getActiveWindow) {
      const win = await window.electron.getActiveWindow()
      setActiveWindow(win)
    } else {
      alert('Not running in Electron')
    }
  }

  return (
    <ThemeProvider defaultTheme="light">
      <div className="min-h-screen bg-background text-foreground">
        <div className="flex flex-col h-screen">
          <TopBar
            currentMode={currentMode}
            onModeChange={setCurrentMode}
            onSettingsClick={() => setShowSettings(true)}
            isTracking={isTracking}
            onTrackingToggle={handleTrackingToggle}
          />

          {error && (
            <Alert className="mx-6 mt-4 border-yellow-200 bg-yellow-50">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Dashboard
            currentMode={currentMode}
            isTracking={isTracking}
            trackingData={currentData}
            systemInfo={systemInfo}
          />

          <button onClick={fetchActiveWindow}>Get Active Window</button>
          {activeWindow && (
            <pre style={{ textAlign: 'left', background: '#eee', padding: '1em' }}>
              {JSON.stringify(activeWindow, null, 2)}
            </pre>
          )}
        </div>

        {showSettings && <SettingsWindow onClose={() => setShowSettings(false)} />}
      </div>
    </ThemeProvider>
  )
}

export default App

async function fetchActiveWindow() {
  if (window.electron && window.electron.getActiveWindow) {
    const win = await window.electron.getActiveWindow();
    console.log(win);
  } else {
    console.log('Not running in Electron');
  }
}