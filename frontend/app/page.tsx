"use client"

import { useState } from "react"
import { TopBar } from "@/src/components/top-bar"
import { Dashboard } from "@/src/components/dashboard"
import { SettingsWindow } from "@/src/components/settings-window"
import { ThemeProvider } from "@/src/components/theme-provider"
import { useSystemTracker } from "@/src/hooks/use-system-tracker"
import { Alert, AlertDescription } from "@/src/components/ui/alert"
import { AlertTriangle } from "lucide-react"

export default function Home() {
  const [currentMode, setCurrentMode] = useState<"Standard" | "Kids">("Standard")
  const [showSettings, setShowSettings] = useState(false)

  const { isTracking, currentData, systemInfo, error, startTracking, stopTracking } = useSystemTracker()

  const handleTrackingToggle = async () => {
    if (isTracking) {
      await stopTracking()
    } else {
      await startTracking()
    }
  }

  return (
    <ThemeProvider attribute="class" defaultTheme="light">
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
        </div>

        {showSettings && <SettingsWindow onClose={() => setShowSettings(false)} />}
      </div>
    </ThemeProvider>
  )
}
