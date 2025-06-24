import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { KidsHomeTab } from "./KidsHomeTab"
import { KidsGamesTab } from "./KidsGamesTab"
import { KidsRewardsTab } from "./KidsRewardsTab"
import { KidsStatsTab } from "./KidsStatsTab"

export function KidsDashboard({ isTracking, trackingData }) {
  return (
    <div className="flex-1 p-6 bg-gradient-to-br from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950">
      <Tabs defaultValue="home" className="h-full">
        <TabsList className="grid w-full grid-cols-4 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm">
          <TabsTrigger value="home" className="text-lg font-bold text-blue-600 data-[state=active]:bg-blue-100">
            🏠 Home
          </TabsTrigger>
          <TabsTrigger value="games" className="text-lg font-bold text-green-600 data-[state=active]:bg-green-100">
            🎮 Games
          </TabsTrigger>
          <TabsTrigger value="rewards" className="text-lg font-bold text-yellow-600 data-[state=active]:bg-yellow-100">
            🏆 Rewards
          </TabsTrigger>
          <TabsTrigger value="stats" className="text-lg font-bold text-purple-600 data-[state=active]:bg-purple-100">
            📊 My Stats
          </TabsTrigger>
        </TabsList>

        <TabsContent value="home" className="mt-6">
          <KidsHomeTab isTracking={isTracking} />
        </TabsContent>

        <TabsContent value="games" className="mt-6">
          <KidsGamesTab />
        </TabsContent>

        <TabsContent value="rewards" className="mt-6">
          <KidsRewardsTab />
        </TabsContent>

        <TabsContent value="stats" className="mt-6">
          <KidsStatsTab />
        </TabsContent>
      </Tabs>
    </div>
  )
}
