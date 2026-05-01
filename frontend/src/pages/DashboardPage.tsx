import { lazy, Suspense, Component, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import StatsCards from "../components/StatsCards";

const StatusDistribution = lazy(() => import("../components/StatusDistribution"));
const ActivityChart = lazy(() => import("../components/ActivityChart"));
const RecentActivity = lazy(() => import("../components/RecentActivity"));

class ChartErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
          <p className="text-slate-400">Chart failed to load.</p>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function DashboardPage() {
  const stats = useQuery({ queryKey: ["dashboard-stats"], queryFn: api.getDashboardStats });
  const activity = useQuery({ queryKey: ["dashboard-activity"], queryFn: api.getDashboardActivity });
  const recent = useQuery({
    queryKey: ["dashboard-recent-activity"],
    queryFn: api.getDashboardRecentActivity,
  });

  const isLoading = stats.isLoading || activity.isLoading || recent.isLoading;
  const hasError = stats.isError || activity.isError || recent.isError;
  const hasData = stats.data || activity.data || recent.data;

  if (isLoading) {
    return <div className="text-slate-400">Loading dashboard...</div>;
  }

  if (hasError && !hasData) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
          <p className="text-slate-400">
            Could not load dashboard data. Make sure the backend server is running.
          </p>
        </div>
      </div>
    );
  }

  if (!hasData) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
          <p className="text-slate-400">
            No data yet. Sync your emails to start tracking applications.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>

      {stats.data && <StatsCards stats={stats.data} />}

      <ChartErrorBoundary>
        <Suspense fallback={<div className="text-slate-400 text-sm">Loading charts...</div>}>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {stats.data && <StatusDistribution statusCounts={stats.data.status_counts} />}
            {activity.data && <ActivityChart data={activity.data} />}
          </div>

          {recent.data && <RecentActivity entries={recent.data.entries} />}
        </Suspense>
      </ChartErrorBoundary>
    </div>
  );
}
