import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import ApplicationTable from "../components/ApplicationTable";
import Filters from "../components/Filters";

export default function ApplicationsPage() {
  const [company, setCompany] = useState("");
  const [status, setStatus] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [page, setPage] = useState(1);

  const params: Record<string, string> = { page: String(page) };
  if (company) params.company = company;
  if (status) params.status = status;
  if (fromDate) params.from_date = fromDate;
  if (toDate) params.to_date = toDate;

  const { data, isLoading } = useQuery({
    queryKey: ["applications", params],
    queryFn: () => api.getApplications(params),
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-4">Applications</h1>

      <Filters
        company={company}
        status={status}
        fromDate={fromDate}
        toDate={toDate}
        onCompanyChange={(v) => { setCompany(v); setPage(1); }}
        onStatusChange={(v) => { setStatus(v); setPage(1); }}
        onFromDateChange={(v) => { setFromDate(v); setPage(1); }}
        onToDateChange={(v) => { setToDate(v); setPage(1); }}
      />

      {isLoading ? (
        <div className="text-slate-400">Loading...</div>
      ) : (
        <>
          <ApplicationTable applications={data?.applications || []} />
          {data && data.total > data.per_page && (
            <div className="flex gap-2 mt-4 justify-center">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 bg-slate-700 text-white rounded disabled:opacity-50"
              >
                Prev
              </button>
              <span className="text-slate-400 py-1">
                Page {page} of {Math.ceil(data.total / data.per_page)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / data.per_page)}
                className="px-3 py-1 bg-slate-700 text-white rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
