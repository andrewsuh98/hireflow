import { formatDistanceToNow, parseISO } from "date-fns";
import type { RecentActivityEntry } from "../types";

const DOT_COLORS: Record<string, string> = {
  applied: "bg-indigo-500",
  rejection: "bg-red-500",
  other_interview: "bg-violet-500",
  oa_invite: "bg-cyan-500",
  follow_up: "bg-amber-500",
  final_round: "bg-pink-500",
  offer: "bg-emerald-500",
  onsite: "bg-fuchsia-500",
  phone_screen: "bg-violet-500",
  technical_interview: "bg-purple-500",
  withdrawn: "bg-gray-500",
};

const EVENT_LABELS: Record<string, string> = {
  applied: "Applied to",
  rejection: "Rejected by",
  other_interview: "Interview at",
  oa_invite: "OA invite from",
  follow_up: "Follow-up with",
  final_round: "Final round at",
  offer: "Offer from",
  onsite: "Onsite at",
  phone_screen: "Phone screen with",
  technical_interview: "Technical interview at",
  withdrawn: "Withdrew from",
};

interface Props {
  entries: RecentActivityEntry[];
}

export default function RecentActivity({ entries }: Props) {
  if (entries.length === 0) {
    return <div className="text-slate-400 text-center py-8">No recent activity</div>;
  }

  return (
    <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
      <h2 className="text-lg font-semibold text-white mb-4">Recent Activity</h2>
      <div className="space-y-3">
        {entries.map((entry, i) => {
          const dotColor = DOT_COLORS[entry.event_type] || "bg-indigo-500";
          const label = EVENT_LABELS[entry.event_type] || entry.event_type.replace(/_/g, " ");
          let timeAgo = "";
          try {
            timeAgo = formatDistanceToNow(parseISO(entry.event_date), { addSuffix: true });
          } catch {
            // leave blank
          }

          return (
            <div key={i} className="flex items-start gap-3">
              <div className={`w-2.5 h-2.5 rounded-full mt-1.5 shrink-0 ${dotColor}`} />
              <div className="min-w-0 flex-1">
                <p className="text-sm text-slate-200">
                  <span className="text-slate-400">{label}</span>{" "}
                  <span className="font-medium text-white">{entry.company_name}</span>
                  {entry.role_title && (
                    <span className="text-slate-400"> - {entry.role_title}</span>
                  )}
                </p>
                {timeAgo && <p className="text-xs text-slate-500 mt-0.5">{timeAgo}</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
