import Plot from "react-plotly.js";
import type { ActivityData } from "../types";

interface Props {
  data: ActivityData;
}

export default function ActivityChart({ data }: Props) {
  if (data.weeks.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data yet</div>;
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-2">Weekly Activity</h2>
      <Plot
        data={[
          {
            type: "bar",
            x: data.weeks,
            y: data.counts,
            marker: { color: "#6366f1" },
          },
        ]}
        layout={{
          margin: { l: 40, r: 20, t: 10, b: 40 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#e2e8f0" },
          height: 250,
          xaxis: { title: "Week" },
          yaxis: { title: "Events" },
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%" }}
      />
    </div>
  );
}
