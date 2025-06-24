import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Progress } from "./ui/progress"
import { TrendingUp, Clock, Zap, AlertTriangle } from "lucide-react"

export function TodaysSummary({ trackingData }) {
  // Use real data if available, otherwise fall back to mock data
  const apps = trackingData?.apps || [
    { name: "VS Code", bundleId: "com.microsoft.vscode", time: "3h 24m", category: "productive", duration: 12240 },
    { name: "Chrome", bundleId: "com.google.chrome", time: "2h 15m", category: "neutral", duration: 8100 },
    { name: "Slack", bundleId: "com.slack.slack", time: "1h 42m", category: "productive", duration: 6120 },
    { name: "YouTube", bundleId: "com.youtube.app", time: "1h 18m", category: "distracting", duration: 4680 },
    { name: "Figma", bundleId: "com.figma.desktop", time: "58m", category: "productive", duration: 3480 },
  ]

  // Calculate time distribution from real data
  const totalTime = apps.reduce((sum, app) => sum + app.duration, 0)
  const productiveTime = apps.filter((app) => app.category === "productive").reduce((sum, app) => sum + app.duration, 0)
  const neutralTime = apps.filter((app) => app.category === "neutral").reduce((sum, app) => sum + app.duration, 0)
  const distractingTime = apps
    .filter((app) => app.category === "distracting")
    .reduce((sum, app) => sum + app.duration, 0)

  const productivePercent = totalTime > 0 ? Math.round((productiveTime / totalTime) * 100) : 67
  const neutralPercent = totalTime > 0 ? Math.round((neutralTime / totalTime) * 100) : 28
  const distractingPercent = totalTime > 0 ? Math.round((distractingTime / totalTime) * 100) : 5

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return hours > 0 ? `${hours}h ${minutes}m` : `${minutes}m`
  }

  // Get top 5 apps by duration
  const topApps = apps
    .sort((a, b) => b.duration - a.duration)
    .slice(0, 5)
    .map((app, index) => ({
      name: app.name,
      time: formatDuration(app.duration),
      category: app.category,
    }))

  const getCategoryColor = (category) => {
    switch (category) {
      case "productive":
        return "bg-green-500"
      case "neutral":
        return "bg-yellow-500"
      case "distracting":
        return "bg-red-500"
      default:
        return "bg-gray-500"
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case "productive":
        return <TrendingUp className="h-4 w-4" />
      case "neutral":
        return <Clock className="h-4 w-4" />
      case "distracting":
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <Clock className="h-4 w-4" />
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Time Distribution Chart */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Time Distribution
            {trackingData && <span className="text-sm font-normal text-muted-foreground">(Live Data)</span>}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Productive Time</span>
              <span className="text-sm text-muted-foreground">
                {formatDuration(productiveTime)} ({productivePercent}%)
              </span>
            </div>
            <Progress value={productivePercent} className="h-3" />

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Neutral Time</span>
              <span className="text-sm text-muted-foreground">
                {formatDuration(neutralTime)} ({neutralPercent}%)
              </span>
            </div>
            <Progress value={neutralPercent} className="h-3" />

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Distracting Time</span>
              <span className="text-sm text-muted-foreground">
                {formatDuration(distractingTime)} ({distractingPercent}%)
              </span>
            </div>
            <Progress value={distractingPercent} className="h-3" />
          </div>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Zap className="h-4 w-4 text-blue-500" />
              <span className="font-medium">AI Insight</span>
            </div>
            <p className="text-sm text-muted-foreground">
              {productivePercent >= 60
                ? `Great focus today! You spent ${productivePercent}% of your time on productive tasks. Consider taking a short break every hour to maintain this momentum.`
                : `Your productivity could be improved. Try using Focus Mode to reduce distractions and increase your productive time.`}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Top 5 Apps */}
      <Card>
        <CardHeader>
          <CardTitle>Top 5 Apps</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {topApps.map((app, index) => (
              <div key={app.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-muted-foreground">{index + 1}</span>
                    {getCategoryIcon(app.category)}
                  </div>
                  <span className="font-medium">{app.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">{app.time}</span>
                  <div className={`w-2 h-2 rounded-full ${getCategoryColor(app.category)}`} />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
