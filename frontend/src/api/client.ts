const BASE = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  getAuthStatus: () => request<{ authenticated: boolean; email: string | null }>("/auth/status"),
  logout: () => request("/auth/logout", { method: "POST" }),

  startSync: (start_date: string) =>
    request("/sync/start", { method: "POST", body: JSON.stringify({ start_date }) }),
  getSyncStatus: () =>
    request<{ running: boolean; progress: { fetched: number; parsed: number; total: number } }>("/sync/status"),

  fetchEmails: (start_date: string) =>
    request("/sync/fetch", { method: "POST", body: JSON.stringify({ start_date }) }),
  getStagedEmails: () =>
    request<{ emails: import("../types").StagedEmail[] }>("/sync/staged"),
  processSelected: (gmail_message_ids: string[]) =>
    request("/sync/process", { method: "POST", body: JSON.stringify({ gmail_message_ids }) }),
  dismissEmails: (gmail_message_ids: string[]) =>
    request("/sync/dismiss", { method: "POST", body: JSON.stringify({ gmail_message_ids }) }),
  autoProcess: () =>
    request<{ status: string; count?: number }>("/sync/auto-process", { method: "POST" }),

  getApplications: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return request<{
      applications: import("../types").ApplicationSummary[];
      total: number;
      page: number;
      per_page: number;
    }>(`/applications${qs}`);
  },
  getApplication: (id: number) =>
    request<import("../types").ApplicationDetail>(`/applications/${id}`),

  getDashboardStats: () => request<import("../types").DashboardStats>("/dashboard/stats"),
  getDashboardFunnel: () => request<import("../types").FunnelData>("/dashboard/funnel"),
  getDashboardTimeline: () =>
    request<{ entries: import("../types").TimelineEntry[] }>("/dashboard/timeline"),
  getDashboardActivity: () => request<import("../types").ActivityData>("/dashboard/activity"),
};
