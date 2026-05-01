import Plot from "react-plotly.js";
import type { FunnelData } from "../types";

interface Props {
  data: FunnelData;
}

export default function FunnelChart({ data }: Props) {
  if (data.stages.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data yet</div>;
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-2">Application Funnel</h2>
      <Plot
        data={[
          {
            type: "funnel",
            y: data.stages,
            x: data.counts,
            textinfo: "value+percent initial",
            marker: { color: ["#6366f1", "#818cf8", "#a5b4fc", "#c7d2fe", "#e0e7ff"] },
          },
        ]}
        layout={{
          margin: { l: 150, r: 40, t: 10, b: 30 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#e2e8f0" },
          height: 300,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%" }}
      />
    </div>
  );
}
