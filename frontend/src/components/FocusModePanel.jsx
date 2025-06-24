"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { Play, Pause, Square, Focus, Shield } from "lucide-react"

export function FocusModePanel({ trackingData }) {
  const [isActive, setIsActive] = useState(false)
  const [timeRemaining, setTimeRemaining] = useState(25 * 60) // 25 minutes in seconds
  const [selectedRule, setSelectedRule] = useState("deep-work")

  const focusRules = [
    { id: "deep-work", name: "Deep Work", duration: "25 min", description: "Block all distracting apps and websites" },
    { id: "light-focus", name: "Light Focus", duration: "15 min", description: "Block social media and entertainment" },
    { id: "meeting-mode", name: "Meeting Mode", duration: "60 min", description: "Allow communication apps only" },
    { id: "custom", name: "Custom", duration: "Custom", description: "Use your custom rules" },
  ]

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  const progress = ((25 * 60 - timeRemaining) / (25 * 60)) * 100

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Focus className="h-5 w-5" />
            Focus Session
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center">
            <div className="text-6xl font-mono font-bold mb-2">{formatTime(timeRemaining)}</div>
            <Progress value={progress} className="h-2 mb-4" />
            <Badge variant={isActive ? "default" : "secondary"} className="mb-4">
              {isActive ? "Active" : "Inactive"}
            </Badge>
          </div>

          <div className="flex justify-center gap-2">
            <Button onClick={() => setIsActive(!isActive)} className="flex items-center gap-2" size="lg">
              {isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {isActive ? "Pause" : "Start"}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setIsActive(false)
                setTimeRemaining(25 * 60)
              }}
              size="lg"
            >
              <Square className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Focus Rules
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Select Focus Rule</label>
            <Select value={selectedRule} onValueChange={setSelectedRule}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {focusRules.map((rule) => (
                  <SelectItem key={rule.id} value={rule.id}>
                    <div className="flex items-center justify-between w-full">
                      <span>{rule.name}</span>
                      <Badge variant="outline" className="ml-2">
                        {rule.duration}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="p-3 bg-muted rounded-lg">
            <p className="text-sm">{focusRules.find((rule) => rule.id === selectedRule)?.description}</p>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Currently Blocked:</h4>
            <div className="flex flex-wrap gap-2">
              <Badge variant="destructive">YouTube</Badge>
              <Badge variant="destructive">Twitter</Badge>
              <Badge variant="destructive">Instagram</Badge>
              <Badge variant="destructive">Reddit</Badge>
              <Badge variant="destructive">TikTok</Badge>
            </div>
          </div>

          <div className="space-y-2">
            <h4 className="font-medium">Session Stats:</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Today's Sessions:</span>
                <div className="font-medium">6</div>
              </div>
              <div>
                <span className="text-muted-foreground">Total Focus Time:</span>
                <div className="font-medium">3h 45m</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
