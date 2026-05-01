import Plot from "react-plotly.js";
import type { TimelineEntry } from "../types";

const STATUS_COLORS: Record<string, string> = {
  applied: "#6366f1",
  phone_screen: "#8b5cf6",
  technical_interview: "#a855f7",
  onsite: "#d946ef",
  offer: "#22c55e",
  rejection: "#ef4444",
  withdrawn: "#6b7280",
};

interface Props {
  entries: TimelineEntry[];
}

export default function TimelineChart({ entries }: Props) {
  if (entries.length === 0) {
    return <div className="text-slate-400 text-center py-8">No data yet</div>;
  }

  const labels = entries.map((e) =>
    e.role_title ? `${e.company_name} - ${e.role_title}` : e.company_name
  );

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-2">Application Timeline</h2>
      <Plot
        data={[
          {
            type: "bar",
            orientation: "h",
            y: labels,
            x: entries.map(() => 1),
            marker: {
              color: entries.map((e) => STATUS_COLORS[e.current_status] || "#6366f1"),
            },
            text: entries.map((e) => e.current_status),
            textposition: "inside",
            hovertext: entries.map(
              (e) => `${e.company_name}<br>Status: ${e.current_status}<br>First: ${e.first_event_at}<br>Last: ${e.last_event_at}`
            ),
            hoverinfo: "text",
          },
        ]}
        layout={{
          margin: { l: 200, r: 40, t: 10, b: 30 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          font: { color: "#e2e8f0", size: 11 },
          height: Math.max(300, entries.length * 28),
          xaxis: { visible: false },
          yaxis: { autorange: "reversed" },
          bargap: 0.3,
        }}
        config={{ displayModeBar: false, responsive: true }}
        style={{ width: "100%" }}
      />
    </div>
  );
}
