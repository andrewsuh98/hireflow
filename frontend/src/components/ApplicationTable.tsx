import { Link } from "react-router-dom";
import type { ApplicationSummary } from "../types";

const STATUS_STYLES: Record<string, string> = {
  applied: "bg-blue-900 text-blue-300",
  offer: "bg-green-900 text-green-300",
  rejection: "bg-red-900 text-red-300",
  withdrawn: "bg-gray-700 text-gray-300",
};

interface Props {
  applications: ApplicationSummary[];
}

export default function ApplicationTable({ applications }: Props) {
  if (applications.length === 0) {
    return <div className="text-slate-400 text-center py-8">No applications found</div>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-slate-400 uppercase border-b border-slate-700">
          <tr>
            <th className="px-4 py-3">Company</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">First Contact</th>
            <th className="px-4 py-3">Last Update</th>
          </tr>
        </thead>
        <tbody>
          {applications.map((app) => (
            <tr key={app.id} className="border-b border-slate-700 hover:bg-slate-800">
              <td className="px-4 py-3">
                <Link to={`/applications/${app.id}`} className="text-indigo-400 hover:underline">
                  {app.company_name}
                </Link>
              </td>
              <td className="px-4 py-3 text-slate-300">{app.role_title || "N/A"}</td>
              <td className="px-4 py-3">
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${
                    STATUS_STYLES[app.current_status] || "bg-purple-900 text-purple-300"
                  }`}
                >
                  {app.current_status}
                </span>
              </td>
              <td className="px-4 py-3 text-slate-400">{app.first_event_at}</td>
              <td className="px-4 py-3 text-slate-400">{app.last_event_at}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
