interface Props {
  company: string;
  status: string;
  fromDate: string;
  toDate: string;
  onCompanyChange: (v: string) => void;
  onStatusChange: (v: string) => void;
  onFromDateChange: (v: string) => void;
  onToDateChange: (v: string) => void;
}

const STATUSES = [
  "",
  "applied",
  "phone_screen",
  "technical_interview",
  "onsite",
  "offer",
  "rejection",
  "withdrawn",
];

export default function Filters({
  company,
  status,
  fromDate,
  toDate,
  onCompanyChange,
  onStatusChange,
  onFromDateChange,
  onToDateChange,
}: Props) {
  return (
    <div className="flex flex-wrap gap-3 mb-4">
      <input
        type="text"
        placeholder="Search company..."
        value={company}
        onChange={(e) => onCompanyChange(e.target.value)}
        className="px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500"
      />
      <select
        value={status}
        onChange={(e) => onStatusChange(e.target.value)}
        className="px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-indigo-500"
      >
        <option value="">All statuses</option>
        {STATUSES.filter(Boolean).map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <input
        type="date"
        value={fromDate}
        onChange={(e) => onFromDateChange(e.target.value)}
        className="px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-indigo-500"
      />
      <input
        type="date"
        value={toDate}
        onChange={(e) => onToDateChange(e.target.value)}
        className="px-3 py-2 bg-slate-800 border border-slate-600 rounded text-sm text-white focus:outline-none focus:border-indigo-500"
      />
    </div>
  );
}
