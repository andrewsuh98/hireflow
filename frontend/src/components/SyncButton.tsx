import { useState, useEffect, useRef } from "react";
import { api } from "../api/client";

interface Props {
  startDate: string;
  onComplete?: () => void;
}

export default function SyncButton({ startDate, onComplete }: Props) {
  const [syncing, setSyncing] = useState(false);
  const [progress, setProgress] = useState({ fetched: 0, parsed: 0, total: 0 });
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const startSync = async () => {
    if (!startDate) return;
    setSyncing(true);
    await api.startSync(startDate);

    intervalRef.current = window.setInterval(async () => {
      const status = await api.getSyncStatus();
      setProgress(status.progress);
      if (!status.running) {
        if (intervalRef.current) clearInterval(intervalRef.current);
        intervalRef.current = null;
        setSyncing(false);
        onComplete?.();
      }
    }, 2000);
  };

  return (
    <div>
      <button
        onClick={startSync}
        disabled={syncing || !startDate}
        className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {syncing ? "Syncing..." : "Sync Now"}
      </button>
      {syncing && progress.total > 0 && (
        <div className="mt-3">
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all"
              style={{ width: `${(progress.parsed / progress.total) * 100}%` }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Parsed {progress.parsed} / {progress.total} emails
          </p>
        </div>
      )}
    </div>
  );
}
