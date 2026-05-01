import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export default function SettingsPage() {
  const queryClient = useQueryClient();

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ["auth-status"],
    queryFn: api.getAuthStatus,
  });

  const handleLogout = async () => {
    await api.logout();
    queryClient.invalidateQueries({ queryKey: ["auth-status"] });
  };

  return (
    <div className="max-w-xl space-y-6">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-3">Gmail Connection</h2>
        {isLoading ? (
          <p className="text-slate-400">Checking authentication...</p>
        ) : authStatus?.authenticated ? (
          <div>
            <p className="text-green-400 mb-2">Connected as {authStatus.email}</p>
            <button
              onClick={handleLogout}
              className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
            >
              Disconnect
            </button>
          </div>
        ) : (
          <div>
            <p className="text-slate-400 mb-3">Not connected. Sign in to start tracking.</p>
            <a
              href="/api/auth/login"
              className="inline-block px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
            >
              Connect Gmail
            </a>
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-3">Email Sync</h2>
        <p className="text-slate-400 mb-3">
          Fetch and review emails before processing them with AI.
        </p>
        <Link
          to="/review"
          className="inline-block px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
        >
          Go to Email Review
        </Link>
      </div>
    </div>
  );
}
