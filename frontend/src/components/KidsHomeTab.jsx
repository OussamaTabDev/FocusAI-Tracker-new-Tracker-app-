import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Progress } from "./ui/progress"
import { Badge } from "./ui/badge"
import { Clock, Star, Heart, Zap, BookOpen, Gamepad2 } from "lucide-react"

export function KidsHomeTab({ isTracking }) {
  const timeRemaining = 2 * 60 + 30 // 2h 30m in minutes
  const totalTime = 4 * 60 // 4h total allowed
  const progress = ((totalTime - timeRemaining) / totalTime) * 100

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="text-center p-6 bg-gradient-to-r from-blue-400 to-purple-500 rounded-2xl text-white">
        <h1 className="text-4xl font-bold mb-2">Welcome Back, Alex! 👋</h1>
        <p className="text-xl opacity-90">Ready for another awesome day?</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Screen Time Card */}
        <Card className="border-4 border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl text-blue-700 dark:text-blue-300">
              <Clock className="h-8 w-8" />
              Screen Time Today
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-6xl font-bold text-blue-600 mb-2">{formatTime(timeRemaining)}</div>
              <p className="text-lg text-blue-600 mb-4">Time Left to Play!</p>
              <Progress value={progress} className="h-4 mb-4 bg-blue-200" />
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/50 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">1h 30m</div>
                  <div className="text-sm text-blue-600">Used Today</div>
                </div>
                <div className="bg-white/50 p-3 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">4h</div>
                  <div className="text-sm text-green-600">Daily Limit</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Daily Goals */}
        <Card className="border-4 border-green-200 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl text-green-700 dark:text-green-300">
              <Star className="h-8 w-8" />
              Today's Goals
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-blue-500" />
                  <span className="font-medium">Read for 30 minutes</span>
                </div>
                <Badge className="bg-green-500 text-white">✓ Done!</Badge>
              </div>

              <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-yellow-500" />
                  <span className="font-medium">Complete homework</span>
                </div>
                <Badge className="bg-green-500 text-white">✓ Done!</Badge>
              </div>

              <div className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Heart className="h-5 w-5 text-red-500" />
                  <span className="font-medium">Help with chores</span>
                </div>
                <Badge variant="outline" className="border-orange-300 text-orange-600">
                  In Progress
                </Badge>
              </div>
            </div>

            <div className="text-center p-3 bg-yellow-100 dark:bg-yellow-900 rounded-lg">
              <p className="text-lg font-bold text-yellow-700 dark:text-yellow-300">🌟 2/3 Goals Complete! 🌟</p>
              <p className="text-sm text-yellow-600 dark:text-yellow-400">
                Finish your last goal to earn bonus screen time!
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="border-4 border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl text-purple-700 dark:text-purple-300">
              <Gamepad2 className="h-8 w-8" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full h-12 text-lg bg-blue-500 hover:bg-blue-600 text-white rounded-xl">
              🎮 Play Educational Games
            </Button>
            <Button className="w-full h-12 text-lg bg-green-500 hover:bg-green-600 text-white rounded-xl">
              📚 Reading Corner
            </Button>
            <Button className="w-full h-12 text-lg bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl">
              🎨 Creative Zone
            </Button>
            <Button className="w-full h-12 text-lg bg-purple-500 hover:bg-purple-600 text-white rounded-xl">
              🧮 Math Practice
            </Button>
          </CardContent>
        </Card>

        {/* Today's Achievements */}
        <Card className="border-4 border-yellow-200 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900 dark:to-yellow-800">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-2xl text-yellow-700 dark:text-yellow-300">
              🏆 Today's Achievements
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-white/50 rounded-lg">
              <div className="text-2xl">🌟</div>
              <div>
                <div className="font-bold">Reading Star</div>
                <div className="text-sm text-muted-foreground">Read for 30 minutes</div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-white/50 rounded-lg">
              <div className="text-2xl">🧠</div>
              <div>
                <div className="font-bold">Smart Cookie</div>
                <div className="text-sm text-muted-foreground">Completed all homework</div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-white/50 rounded-lg">
              <div className="text-2xl">⚡</div>
              <div>
                <div className="font-bold">Speed Learner</div>
                <div className="text-sm text-muted-foreground">Finished math quiz in record time</div>
              </div>
            </div>

            <div className="text-center p-3 bg-gradient-to-r from-yellow-400 to-orange-400 rounded-lg text-white">
              <p className="font-bold">🎉 You earned 15 stars today! 🎉</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
