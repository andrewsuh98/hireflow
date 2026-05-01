import { useState, useEffect, useRef, useCallback } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { StagedEmail } from "../types";

export default function EmailReviewPage() {
  const [startDate, setStartDate] = useState("2025-01-01");
  const [fetching, setFetching] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState({ fetched: 0, parsed: 0, total: 0 });
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const intervalRef = useRef<number | null>(null);
  const queryClient = useQueryClient();

  const { data, refetch } = useQuery({
    queryKey: ["staged-emails"],
    queryFn: api.getStagedEmails,
  });

  const emails = data?.emails ?? [];
  const newEmails = emails.filter((e) => e.status === "new");
  const processedEmails = emails.filter((e) => e.status !== "new");

  useEffect(() => {
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  const pollUntilDone = useCallback(
    (onDone: () => void) => {
      intervalRef.current = window.setInterval(async () => {
        const status = await api.getSyncStatus();
        setProgress(status.progress);
        if (!status.running) {
          if (intervalRef.current) clearInterval(intervalRef.current);
          intervalRef.current = null;
          onDone();
        }
      }, 2000);
    },
    [],
  );

  const handleFetch = async () => {
    if (!startDate) return;
    setFetching(true);
    setProgress({ fetched: 0, parsed: 0, total: 0 });
    await api.fetchEmails(startDate);
    pollUntilDone(() => {
      setFetching(false);
      refetch();
    });
  };

  const handleProcess = async () => {
    if (selectedIds.size === 0) return;
    setProcessing(true);
    setProgress({ fetched: 0, parsed: 0, total: 0 });
    await api.processSelected(Array.from(selectedIds));
    pollUntilDone(() => {
      setProcessing(false);
      setSelectedIds(new Set());
      refetch();
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-funnel"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-timeline"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-activity"] });
      queryClient.invalidateQueries({ queryKey: ["applications"] });
    });
  };

  const handleDismiss = async () => {
    if (selectedIds.size === 0) return;
    await api.dismissEmails(Array.from(selectedIds));
    setSelectedIds(new Set());
    refetch();
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === newEmails.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(newEmails.map((e) => e.gmail_message_id)));
    }
  };

  const busy = fetching || processing;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Email Review</h1>

      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <div className="flex items-end gap-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">
              Start date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white focus:outline-none focus:border-indigo-500"
            />
          </div>
          <button
            onClick={handleFetch}
            disabled={busy || !startDate}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {fetching ? "Fetching..." : "Fetch Emails"}
          </button>
        </div>
        {fetching && progress.total > 0 && (
          <div className="mt-3">
            <div className="w-full bg-slate-700 rounded-full h-2">
              <div
                className="bg-indigo-500 h-2 rounded-full transition-all"
                style={{
                  width: `${(progress.fetched / progress.total) * 100}%`,
                }}
              />
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Fetched {progress.fetched} / {progress.total} emails
            </p>
          </div>
        )}
      </div>

      {newEmails.length > 0 && (
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700 flex items-center gap-4">
          <button
            onClick={toggleSelectAll}
            className="text-sm text-indigo-400 hover:text-indigo-300"
          >
            {selectedIds.size === newEmails.length
              ? "Deselect All"
              : "Select All New"}
          </button>
          <span className="text-sm text-slate-400">
            {selectedIds.size} selected
          </span>
          <div className="flex-1" />
          <button
            onClick={handleProcess}
            disabled={busy || selectedIds.size === 0}
            className="px-4 py-2 bg-indigo-600 text-white rounded text-sm hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {processing
              ? "Processing..."
              : `Process Selected (${selectedIds.size})`}
          </button>
          <button
            onClick={handleDismiss}
            disabled={busy || selectedIds.size === 0}
            className="px-4 py-2 bg-slate-600 text-white rounded text-sm hover:bg-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Dismiss Selected ({selectedIds.size})
          </button>
        </div>
      )}

      {processing && progress.total > 0 && (
        <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="w-full bg-slate-700 rounded-full h-2">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all"
              style={{
                width: `${(progress.parsed / progress.total) * 100}%`,
              }}
            />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Parsed {progress.parsed} / {progress.total} emails
          </p>
        </div>
      )}

      {newEmails.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">
            New Emails ({newEmails.length})
          </h2>
          <EmailTable
            emails={newEmails}
            selectedIds={selectedIds}
            onToggle={toggleSelect}
            selectable
          />
        </div>
      )}

      {processedEmails.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-white mb-3">
            Previously Processed ({processedEmails.length})
          </h2>
          <EmailTable emails={processedEmails} />
        </div>
      )}

      {emails.length === 0 && !fetching && (
        <div className="bg-slate-800 rounded-lg p-8 border border-slate-700 text-center">
          <p className="text-slate-400">
            No emails yet. Set a start date and click Fetch Emails to get
            started.
          </p>
        </div>
      )}
    </div>
  );
}

function StatusBadge({ status }: { status: StagedEmail["status"] }) {
  if (status === "new") {
    return (
      <span className="px-2 py-0.5 rounded text-xs bg-indigo-600/30 text-indigo-300">
        New
      </span>
    );
  }
  if (status === "processed_relevant") {
    return (
      <span className="px-2 py-0.5 rounded text-xs bg-green-600/30 text-green-300">
        Relevant
      </span>
    );
  }
  return (
    <span className="px-2 py-0.5 rounded text-xs bg-slate-600/30 text-slate-400">
      Not Relevant
    </span>
  );
}

function EmailTable({
  emails,
  selectedIds,
  onToggle,
  selectable,
}: {
  emails: StagedEmail[];
  selectedIds?: Set<string>;
  onToggle?: (id: string) => void;
  selectable?: boolean;
}) {
  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700 text-left text-slate-400">
            {selectable && <th className="p-3 w-8" />}
            <th className="p-3">Subject</th>
            <th className="p-3">From</th>
            <th className="p-3 w-28">Date</th>
            <th className="p-3 w-24">Status</th>
          </tr>
        </thead>
        <tbody>
          {emails.map((email) => (
            <tr
              key={email.gmail_message_id}
              className="border-b border-slate-700/50 hover:bg-slate-700/30"
            >
              {selectable && (
                <td className="p-3">
                  <input
                    type="checkbox"
                    checked={selectedIds?.has(email.gmail_message_id) ?? false}
                    onChange={() => onToggle?.(email.gmail_message_id)}
                    className="rounded border-slate-500 bg-slate-700 text-indigo-500 focus:ring-indigo-500"
                  />
                </td>
              )}
              <td className="p-3">
                <div className="text-white truncate max-w-md">
                  {email.subject || "(no subject)"}
                </div>
                <div className="text-xs text-slate-500 truncate max-w-md mt-0.5">
                  {email.snippet}
                </div>
                {email.result && (
                  <div className="text-xs text-green-400 mt-0.5">
                    {email.result.company_name}
                    {email.result.role_title
                      ? ` / ${email.result.role_title}`
                      : ""}
                    {" "}
                    ({email.result.event_type})
                  </div>
                )}
              </td>
              <td className="p-3 text-slate-300 truncate max-w-[200px]">
                {email.sender}
              </td>
              <td className="p-3 text-slate-400 whitespace-nowrap">
                {formatDate(email.date)}
              </td>
              <td className="p-3">
                <StatusBadge status={email.status} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}
