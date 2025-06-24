import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Gamepad2, Trophy, Star } from "lucide-react"

export function KidsGamesTab() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-green-600 mb-2">🎮 Fun Games!</h2>
        <p className="text-gray-600 dark:text-gray-400">Play games and earn points while staying focused!</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Gamepad2 className="h-5 w-5 text-blue-500" />
              Focus Challenge
            </CardTitle>
            <CardDescription>Complete tasks to unlock new levels</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Level 3</span>
                <span className="text-sm font-medium text-green-600">150 points</span>
              </div>
              <Button className="w-full" variant="outline">
                Play Now
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Achievement Hunt
            </CardTitle>
            <CardDescription>Collect badges and achievements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">5/10 Badges</span>
                <span className="text-sm font-medium text-yellow-600">75 points</span>
              </div>
              <Button className="w-full" variant="outline">
                View Badges
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5 text-purple-500" />
              Daily Quest
            </CardTitle>
            <CardDescription>Complete daily challenges</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">2/3 Complete</span>
                <span className="text-sm font-medium text-purple-600">200 points</span>
              </div>
              <Button className="w-full" variant="outline">
                Start Quest
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="text-center mt-8">
        <p className="text-sm text-gray-500">More games coming soon! 🚀</p>
      </div>
    </div>
  )
} 