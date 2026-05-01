import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

const STATUS_COLORS: Record<string, string> = {
  applied: "#6366f1",
  rejection: "#ef4444",
  other_interview: "#8b5cf6",
  oa_invite: "#06b6d4",
  follow_up: "#f59e0b",
  final_round: "#ec4899",
  offer: "#22c55e",
  onsite: "#d946ef",
  withdrawn: "#6b7280",
};

interface Props {
  statusCounts: Record<string, number>;
}

export default function StatusDistribution({ statusCounts }: Props) {
  const data = Object.entries(statusCounts)
    .map(([name, value]) => ({
      name: name.replace(/_/g, " "),
      value,
      fill: STATUS_COLORS[name] || "#6366f1",
    }))
    .sort((a, b) => b.value - a.value);

  if (data.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data yet</div>;
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-2">Status Distribution</h2>
      <div className="flex items-center">
        <ResponsiveContainer width="60%" height={280}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={95}
              paddingAngle={2}
              dataKey="value"
              nameKey="name"
            >
              {data.map((entry, i) => (
                <Cell key={i} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#1e293b",
                border: "1px solid #334155",
                color: "#e2e8f0",
                borderRadius: "6px",
                fontSize: "13px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="w-[40%] space-y-1.5 pl-2">
          {data.map((entry) => (
            <div key={entry.name} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <div
                  className="w-2.5 h-2.5 rounded-full shrink-0"
                  style={{ backgroundColor: entry.fill }}
                />
                <span className="text-slate-300 capitalize">{entry.name}</span>
              </div>
              <span className="text-slate-400 font-medium tabular-nums">{entry.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
