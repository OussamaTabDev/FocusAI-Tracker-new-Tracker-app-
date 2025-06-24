import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card"
import { Button } from "./ui/button"
import { Gift, Medal, Zap } from "lucide-react"

export function KidsRewardsTab() {
  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-yellow-600 mb-2">🏆 Your Rewards!</h2>
        <p className="text-gray-600 dark:text-gray-400">Earn points and unlock amazing rewards!</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="border-2 border-yellow-200 bg-yellow-50 dark:bg-yellow-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-700 dark:text-yellow-300">
              <Gift className="h-5 w-5" />
              Available Rewards
            </CardTitle>
            <CardDescription>Rewards you can unlock with your points</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-3">
              <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div>
                  <h4 className="font-medium">Extra Screen Time</h4>
                  <p className="text-sm text-gray-600">30 minutes of bonus time</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-yellow-600">500 points</span>
                  <Button size="sm" className="ml-2">Claim</Button>
                </div>
              </div>

              <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg">
                <div>
                  <h4 className="font-medium">Special Badge</h4>
                  <p className="text-sm text-gray-600">"Focus Master" achievement</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-yellow-600">1000 points</span>
                  <Button size="sm" className="ml-2">Claim</Button>
                </div>
              </div>

              <div className="flex justify-between items-center p-3 bg-white dark:bg-gray-800 rounded-lg opacity-50">
                <div>
                  <h4 className="font-medium">Custom Theme</h4>
                  <p className="text-sm text-gray-600">Unlock new app theme</p>
                </div>
                <div className="text-right">
                  <span className="text-sm font-medium text-gray-500">2000 points</span>
                  <span className="text-xs text-gray-500 ml-2">Need 500 more</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-2 border-green-200 bg-green-50 dark:bg-green-950/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700 dark:text-green-300">
              <Medal className="h-5 w-5" />
              Your Progress
            </CardTitle>
            <CardDescription>Track your points and achievements</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">1,500</div>
              <p className="text-sm text-gray-600">Total Points Earned</p>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">This Week</span>
                <span className="text-sm font-medium text-green-600">+450 points</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">This Month</span>
                <span className="text-sm font-medium text-green-600">+1,200 points</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Streak</span>
                <span className="text-sm font-medium text-orange-600">7 days 🔥</span>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Zap className="h-4 w-4 text-yellow-500" />
                <span>Next milestone: 2,000 points</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }}></div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 