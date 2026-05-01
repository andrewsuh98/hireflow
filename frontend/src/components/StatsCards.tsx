import type { DashboardStats } from "../types";

interface Props {
  stats: DashboardStats;
}

export default function StatsCards({ stats }: Props) {
  const activeInterviews = Object.entries(stats.status_counts)
    .filter(([k]) => !["applied", "rejection", "offer", "withdrawn"].includes(k))
    .reduce((sum, [, v]) => sum + v, 0);

  const cards = [
    {
      label: "Total Applications",
      value: stats.total_applications,
      border: "border-l-indigo-500",
      text: "text-indigo-400",
    },
    {
      label: "Response Rate",
      value: `${stats.response_rate}%`,
      border: "border-l-cyan-500",
      text: "text-cyan-400",
    },
    {
      label: "Avg Days to Response",
      value: stats.avg_days_to_response !== null ? stats.avg_days_to_response : "N/A",
      border: "border-l-amber-500",
      text: "text-amber-400",
    },
    {
      label: "Active Interviews",
      value: activeInterviews,
      border: "border-l-emerald-500",
      text: "text-emerald-400",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className={`bg-slate-800 rounded-lg p-5 border border-slate-700 border-l-4 ${card.border}`}
        >
          <p className="text-sm text-slate-400 font-medium">{card.label}</p>
          <p className={`text-3xl font-bold mt-2 ${card.text}`}>{card.value}</p>
        </div>
      ))}
    </div>
  );
}
