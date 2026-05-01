import type { DashboardStats } from "../types";

interface Props {
  stats: DashboardStats;
}

export default function StatsCards({ stats }: Props) {
  const cards = [
    { label: "Total Applications", value: stats.total_applications },
    { label: "Response Rate", value: `${stats.response_rate}%` },
    {
      label: "Avg Days to Response",
      value: stats.avg_days_to_response !== null ? stats.avg_days_to_response : "N/A",
    },
    {
      label: "Active Interviews",
      value: Object.entries(stats.status_counts)
        .filter(([k]) => !["applied", "rejection", "offer", "withdrawn"].includes(k))
        .reduce((sum, [, v]) => sum + v, 0),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.label} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="text-2xl font-bold text-white mt-1">{card.value}</p>
        </div>
      ))}
    </div>
  );
}
