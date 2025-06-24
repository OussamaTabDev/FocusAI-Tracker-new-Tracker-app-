"use client"

import { Button } from "./ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "./ui/avatar"
import { Badge } from "./ui/badge"
import { Settings, User, Play, Square } from "lucide-react"
import { ThemeToggle } from "./ThemeToggle"

export function TopBar({ currentMode, onModeChange, onSettingsClick, isTracking, onTrackingToggle }) {
  return (
    <div className="flex items-center justify-between px-6 py-4 border-b bg-card">
      <div className="flex items-center gap-4">
        <h1 className="text-xl font-semibold">ProductivityTracker</h1>
        <div className="flex items-center gap-2">
          <Button
            variant={currentMode === "Standard" ? "default" : "outline"}
            size="sm"
            onClick={() => onModeChange("Standard")}
            className="h-8"
          >
            Standard
          </Button>
          <Button
            variant={currentMode === "Kids" ? "default" : "outline"}
            size="sm"
            onClick={() => onModeChange("Kids")}
            className="h-8"
          >
            Kids
          </Button>
        </div>
        <Badge variant={currentMode === "Kids" ? "destructive" : "secondary"}>{currentMode} Mode</Badge>
        <div className="flex items-center gap-2 ml-4">
          <Button
            variant={isTracking ? "destructive" : "default"}
            size="sm"
            onClick={onTrackingToggle}
            className="h-8 flex items-center gap-2"
          >
            {isTracking ? (
              <>
                <Square className="h-3 w-3" />
                Stop Tracking
              </>
            ) : (
              <>
                <Play className="h-3 w-3" />
                Start Tracking
              </>
            )}
          </Button>
          {isTracking && (
            <div className="flex items-center gap-1 text-sm">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-muted-foreground">Recording</span>
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <ThemeToggle />
        <Button variant="ghost" size="icon" onClick={onSettingsClick}>
          <Settings className="h-4 w-4" />
        </Button>
        <Avatar className="h-8 w-8">
          <AvatarImage src="/placeholder.svg?height=32&width=32" />
          <AvatarFallback>
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      </div>
    </div>
  )
}
