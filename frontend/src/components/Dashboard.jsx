import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { TodaysSummary } from "./TodaysSummary"
import { TimelineView } from "./TimelineView"
import { ReportsTab } from "./ReportsTab"
import { FocusModePanel } from "./FocusModePanel"
import { KidsDashboard } from "./KidsDashboard"

export function Dashboard({ currentMode, isTracking, trackingData, systemInfo }) {
  // If in Kids mode, show the kids dashboard instead
  if (currentMode === "Kids") {
    return <KidsDashboard isTracking={isTracking} trackingData={trackingData} />
  }

  return (
    <div className="flex-1 p-6">
      <Tabs defaultValue="summary" className="h-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="summary">Today's Summary</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="focus">Focus Mode</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="mt-6">
          <TodaysSummary trackingData={trackingData} />
        </TabsContent>

        <TabsContent value="timeline" className="mt-6">
          <TimelineView trackingData={trackingData} />
        </TabsContent>

        <TabsContent value="reports" className="mt-6">
          <ReportsTab trackingData={trackingData} />
        </TabsContent>

        <TabsContent value="focus" className="mt-6">
          <FocusModePanel trackingData={trackingData} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
