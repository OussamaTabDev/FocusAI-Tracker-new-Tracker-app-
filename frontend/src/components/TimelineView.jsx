import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Badge } from "./ui/badge"
import { Clock, ImageIcon } from "lucide-react"

export function TimelineView({ trackingData }) {
  const timelineData = trackingData?.timeline || [
    { time: "09:00", duration: "2h 30m", app: "VS Code", category: "productive", screenshot: true },
    { time: "11:30", duration: "45m", app: "Chrome", category: "neutral", screenshot: true },
    { time: "12:15", duration: "1h", app: "Lunch Break", category: "break", screenshot: false },
    { time: "13:15", duration: "1h 45m", app: "Figma", category: "productive", screenshot: true },
    { time: "15:00", duration: "30m", app: "Slack", category: "productive", screenshot: false },
    { time: "15:30", duration: "25m", app: "YouTube", category: "distracting", screenshot: true },
    { time: "16:00", duration: "2h", app: "VS Code", category: "productive", screenshot: true },
  ]

  const getCategoryColor = (category) => {
    switch (category) {
      case "productive":
        return "border-l-green-500 bg-green-50 dark:bg-green-950"
      case "neutral":
        return "border-l-yellow-500 bg-yellow-50 dark:bg-yellow-950"
      case "distracting":
        return "border-l-red-500 bg-red-50 dark:bg-red-950"
      case "break":
        return "border-l-blue-500 bg-blue-50 dark:bg-blue-950"
      default:
        return "border-l-gray-500 bg-gray-50 dark:bg-gray-950"
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Today's Timeline
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {timelineData.map((item, index) => (
            <div key={index} className={`p-4 border-l-4 rounded-r-lg ${getCategoryColor(item.category)}`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <span className="font-mono text-sm font-medium">{item.time}</span>
                  <div>
                    <span className="font-medium">{item.app}</span>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm text-muted-foreground">{item.duration}</span>
                      <Badge variant="outline" className="text-xs">
                        {item.category}
                      </Badge>
                    </div>
                  </div>
                </div>
                {item.screenshot && (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <ImageIcon className="h-4 w-4" />
                    <span className="text-xs">Screenshot</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
