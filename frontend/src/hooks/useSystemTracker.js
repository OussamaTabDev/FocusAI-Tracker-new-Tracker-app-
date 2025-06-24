"use client"

import { useState, useEffect, useCallback } from "react"
import { systemTracker } from "../lib/systemTracker"

export function useSystemTracker() {
  const [isTracking, setIsTracking] = useState(false)
  const [currentData, setCurrentData] = useState(null)
  const [systemInfo, setSystemInfo] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Initialize tracking state
    setIsTracking(systemTracker.isCurrentlyTracking())
    setCurrentData(systemTracker.getCurrentSession())

    // Set up data listener
    const unsubscribe = systemTracker.onDataUpdate((data) => {
      setCurrentData(data)
      setError(null)
    })

    // Get system info
    systemTracker.getSystemInfo().then(setSystemInfo).catch(console.error)

    return unsubscribe
  }, [])

  const startTracking = useCallback(async () => {
    try {
      setError(null)
      const success = await systemTracker.startTracking()
      if (success) {
        setIsTracking(true)
      } else {
        setError("Failed to start tracking. Please check permissions.")
      }
      return success
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      return false
    }
  }, [])

  const stopTracking = useCallback(async () => {
    try {
      setError(null)
      const success = await systemTracker.stopTracking()
      if (success) {
        setIsTracking(false)
      } else {
        setError("Failed to stop tracking")
      }
      return success
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Unknown error occurred"
      setError(errorMessage)
      return false
    }
  }, [])

  const takeScreenshot = useCallback(async () => {
    try {
      return await systemTracker.takeScreenshot()
    } catch (err) {
      console.error("Failed to take screenshot:", err)
      return null
    }
  }, [])

  const blockApp = useCallback(async (bundleId) => {
    try {
      return await systemTracker.blockApplication(bundleId)
    } catch (err) {
      console.error("Failed to block app:", err)
      return false
    }
  }, [])

  const unblockApp = useCallback(async (bundleId) => {
    try {
      return await systemTracker.unblockApplication(bundleId)
    } catch (err) {
      console.error("Failed to unblock app:", err)
      return false
    }
  }, [])

  const getInstalledApps = useCallback(async () => {
    try {
      return await systemTracker.getInstalledApps()
    } catch (err) {
      console.error("Failed to get installed apps:", err)
      return []
    }
  }, [])

  return {
    isTracking,
    currentData,
    systemInfo,
    error,
    startTracking,
    stopTracking,
    takeScreenshot,
    blockApp,
    unblockApp,
    getInstalledApps,
  }
}
