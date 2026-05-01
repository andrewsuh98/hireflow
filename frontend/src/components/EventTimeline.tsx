import type { ApplicationEvent } from "../types";

const TYPE_COLORS: Record<string, string> = {
  applied: "bg-blue-500",
  phone_screen: "bg-purple-500",
  technical_interview: "bg-violet-500",
  onsite: "bg-fuchsia-500",
  offer: "bg-green-500",
  rejection: "bg-red-500",
  withdrawn: "bg-gray-500",
  oa_invite: "bg-amber-500",
  take_home: "bg-orange-500",
  hiring_manager: "bg-pink-500",
  final_round: "bg-cyan-500",
};

interface Props {
  events: ApplicationEvent[];
}

export default function EventTimeline({ events }: Props) {
  return (
    <div className="space-y-4">
      {events.map((event, i) => (
        <div key={event.id} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div
              className={`w-3 h-3 rounded-full ${TYPE_COLORS[event.event_type] || "bg-indigo-500"}`}
            />
            {i < events.length - 1 && <div className="w-px flex-1 bg-slate-600 mt-1" />}
          </div>
          <div className="pb-4 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm font-medium text-white">
                {event.event_label || event.event_type}
              </span>
              <span className="text-xs text-slate-400">{event.event_date}</span>
              {event.confidence < 0.8 && (
                <span className="text-xs text-amber-400">Low confidence</span>
              )}
            </div>
            {event.summary && <p className="text-sm text-slate-300">{event.summary}</p>}
            {event.raw_subject && (
              <p className="text-xs text-slate-500 mt-1">Subject: {event.raw_subject}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
