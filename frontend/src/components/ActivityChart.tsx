import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { format, parse } from "date-fns";
import type { ActivityData } from "../types";

interface Props {
  data: ActivityData;
}

export default function ActivityChart({ data }: Props) {
  if (data.months.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data yet</div>;
  }

  const chartData = data.months.map((month, i) => ({
    month,
    label: format(parse(month, "yyyy-MM", new Date()), "MMM yy"),
    count: data.counts[i],
  }));

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-2">Activity Over Time</h2>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={chartData} margin={{ left: 0, right: 10, top: 5, bottom: 5 }}>
          <defs>
            <linearGradient id="activityGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 12 }} />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} width={35} />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e293b",
              border: "1px solid #334155",
              color: "#e2e8f0",
              borderRadius: "6px",
              fontSize: "13px",
            }}
            labelFormatter={(label) => label}
            formatter={(value: number) => [value, "Events"]}
          />
          <Area
            type="monotone"
            dataKey="count"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#activityGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
