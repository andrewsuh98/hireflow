import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import EventTimeline from "../components/EventTimeline";

export default function ApplicationDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading } = useQuery({
    queryKey: ["application", id],
    queryFn: () => api.getApplication(Number(id)),
    enabled: !!id,
  });

  if (isLoading) return <div className="text-slate-400">Loading...</div>;
  if (!data) return <div className="text-slate-400">Application not found</div>;

  return (
    <div>
      <Link to="/applications" className="text-indigo-400 hover:underline text-sm">
        Back to applications
      </Link>

      <div className="mt-4 mb-6">
        <h1 className="text-2xl font-bold text-white">{data.company_name}</h1>
        {data.role_title && <p className="text-slate-300 mt-1">{data.role_title}</p>}
        <div className="flex gap-3 mt-2 text-sm text-slate-400">
          <span>Status: <span className="text-white">{data.current_status}</span></span>
          <span>First contact: {data.first_event_at}</span>
          <span>Last update: {data.last_event_at}</span>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">Event History</h2>
        <EventTimeline events={data.events} />
      </div>
    </div>
  );
}
