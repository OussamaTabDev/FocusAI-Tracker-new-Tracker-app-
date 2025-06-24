class SystemTracker {
  constructor() {
    this.isTracking = false
    this.trackingInterval = null
    this.currentSession = null
    this.listeners = []
    this.initializeTracker()
  }

  async initializeTracker() {
    // Check if we're in an Electron environment
    if (typeof window !== "undefined" && window.electronAPI) {
      console.log("Electron environment detected")
      await this.setupElectronTracking()
    } else {
      console.log("Web environment - using mock data")
      this.setupWebTracking()
    }
  }

  async setupElectronTracking() {
    const electronAPI = window.electronAPI

    try {
      // Request permissions for system monitoring
      const hasPermission = await electronAPI.requestPermissions()
      if (!hasPermission) {
        console.warn("System monitoring permissions not granted")
        this.setupWebTracking()
        return
      }

      // Set up real system tracking
      electronAPI.onAppUsageUpdate((data) => {
        this.currentSession = data
        this.notifyListeners(data)
      })
    } catch (error) {
      console.error("Failed to setup Electron tracking:", error)
      this.setupWebTracking()
    }
  }

  setupWebTracking() {
    // Fallback to web-based tracking with mock data and limited real data
    this.currentSession = {
      totalScreenTime: 0,
      activeTime: 0,
      idleTime: 0,
      apps: this.generateMockApps(),
      timestamp: new Date(),
    }
  }

  generateMockApps() {
    const mockApps = [
      { name: "Visual Studio Code", bundleId: "com.microsoft.vscode", category: "productive" },
      { name: "Google Chrome", bundleId: "com.google.chrome", category: "neutral" },
      { name: "Slack", bundleId: "com.slack.slack", category: "productive" },
      { name: "YouTube", bundleId: "com.youtube.app", category: "distracting" },
      { name: "Figma", bundleId: "com.figma.desktop", category: "productive" },
      { name: "Discord", bundleId: "com.discord.app", category: "distracting" },
      { name: "Notion", bundleId: "com.notion.app", category: "productive" },
      { name: "Spotify", bundleId: "com.spotify.app", category: "neutral" },
    ]

    return mockApps.map((app) => ({
      ...app,
      duration: Math.floor(Math.random() * 7200) + 300, // 5 minutes to 2 hours
      lastUsed: new Date(Date.now() - Math.random() * 86400000), // Within last 24 hours
      icon: `/placeholder.svg?height=32&width=32`,
    }))
  }

  async startTracking() {
    if (this.isTracking) return true

    try {
      if (typeof window !== "undefined" && window.electronAPI) {
        const success = await window.electronAPI.startTracking()
        if (success) {
          this.isTracking = true
          this.startWebTracking() // Also start web-based tracking for additional data
          return true
        }
      } else {
        this.startWebTracking()
        return true
      }
    } catch (error) {
      console.error("Failed to start tracking:", error)
    }

    return false
  }

  startWebTracking() {
    this.isTracking = true

    // Track page visibility and focus
    this.setupPageVisibilityTracking()

    // Update tracking data every 30 seconds
    this.trackingInterval = setInterval(() => {
      this.updateTrackingData()
    }, 30000)

    // Initial update
    this.updateTrackingData()
  }

  setupPageVisibilityTracking() {
    if (typeof document === "undefined") return

    let startTime = Date.now()
    let isActive = !document.hidden

    const handleVisibilityChange = () => {
      const now = Date.now()
      const duration = now - startTime

      if (this.currentSession) {
        if (isActive) {
          this.currentSession.activeTime += duration / 1000
        } else {
          this.currentSession.idleTime += duration / 1000
        }
        this.currentSession.totalScreenTime = this.currentSession.activeTime + this.currentSession.idleTime
      }

      isActive = !document.hidden
      startTime = now
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    window.addEventListener("focus", handleVisibilityChange)
    window.addEventListener("blur", handleVisibilityChange)
  }

  updateTrackingData() {
    if (!this.currentSession) return

    // Simulate app usage updates
    this.currentSession.apps = this.currentSession.apps.map((app) => ({
      ...app,
      duration: app.duration + Math.floor(Math.random() * 60), // Add 0-60 seconds
      lastUsed: Math.random() > 0.7 ? new Date() : app.lastUsed, // 30% chance of recent use
    }))

    this.currentSession.timestamp = new Date()
    this.notifyListeners(this.currentSession)
  }

  async stopTracking() {
    if (!this.isTracking) return true

    try {
      if (typeof window !== "undefined" && window.electronAPI) {
        await window.electronAPI.stopTracking()
      }

      if (this.trackingInterval) {
        clearInterval(this.trackingInterval)
        this.trackingInterval = null
      }

      this.isTracking = false
      return true
    } catch (error) {
      console.error("Failed to stop tracking:", error)
      return false
    }
  }

  isCurrentlyTracking() {
    return this.isTracking
  }

  getCurrentSession() {
    return this.currentSession
  }

  onDataUpdate(callback) {
    this.listeners.push(callback)

    // Return unsubscribe function
    return () => {
      this.listeners = this.listeners.filter((listener) => listener !== callback)
    }
  }

  notifyListeners(data) {
    this.listeners.forEach((listener) => {
      try {
        listener(data)
      } catch (error) {
        console.error("Error in tracking listener:", error)
      }
    })
  }

  async getSystemInfo() {
    if (typeof window !== "undefined" && window.electronAPI) {
      try {
        return await window.electronAPI.getSystemInfo()
      } catch (error) {
        console.error("Failed to get system info:", error)
      }
    }

    // Fallback system info
    return {
      platform: this.detectPlatform(),
      version: "Unknown",
      totalMemory: 0,
      freeMemory: 0,
    }
  }

  detectPlatform() {
    if (typeof navigator === "undefined") return "unknown"

    const userAgent = navigator.userAgent.toLowerCase()
    if (userAgent.includes("win")) return "windows"
    if (userAgent.includes("mac")) return "macos"
    if (userAgent.includes("linux")) return "linux"
    return "unknown"
  }

  async getInstalledApps() {
    if (typeof window !== "undefined" && window.electronAPI) {
      try {
        return await window.electronAPI.getInstalledApps()
      } catch (error) {
        console.error("Failed to get installed apps:", error)
      }
    }

    return this.generateMockApps()
  }

  async takeScreenshot() {
    if (typeof window !== "undefined" && window.electronAPI) {
      try {
        return await window.electronAPI.takeScreenshot()
      } catch (error) {
        console.error("Failed to take screenshot:", error)
      }
    }

    // Web fallback - cannot take actual screenshots due to security restrictions
    return null
  }

  async blockApplication(bundleId) {
    if (typeof window !== "undefined" && window.electronAPI) {
      try {
        return await window.electronAPI.blockApplication(bundleId)
      } catch (error) {
        console.error("Failed to block application:", error)
      }
    }

    console.log(`Would block application: ${bundleId}`)
    return false
  }

  async unblockApplication(bundleId) {
    if (typeof window !== "undefined" && window.electronAPI) {
      try {
        return await window.electronAPI.unblockApplication(bundleId)
      } catch (error) {
        console.error("Failed to unblock application:", error)
      }
    }

    console.log(`Would unblock application: ${bundleId}`)
    return false
  }
}

// Singleton instance
export const systemTracker = new SystemTracker()
