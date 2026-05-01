import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import StatsCards from "../components/StatsCards";
import FunnelChart from "../components/FunnelChart";
import TimelineChart from "../components/TimelineChart";
import ActivityChart from "../components/ActivityChart";

export default function DashboardPage() {
  const stats = useQuery({ queryKey: ["dashboard-stats"], queryFn: api.getDashboardStats });
  const funnel = useQuery({ queryKey: ["dashboard-funnel"], queryFn: api.getDashboardFunnel });
  const timeline = useQuery({ queryKey: ["dashboard-timeline"], queryFn: api.getDashboardTimeline });
  const activity = useQuery({ queryKey: ["dashboard-activity"], queryFn: api.getDashboardActivity });

  if (stats.isLoading) {
    return <div className="text-slate-400">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>

      {stats.data && <StatsCards stats={stats.data} />}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {funnel.data && <FunnelChart data={funnel.data} />}
        {activity.data && <ActivityChart data={activity.data} />}
      </div>

      {timeline.data && <TimelineChart entries={timeline.data.entries} />}
    </div>
  );
}
