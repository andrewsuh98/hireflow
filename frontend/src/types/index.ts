export interface ApplicationSummary {
  id: number;
  company_name: string;
  role_title: string | null;
  current_status: string;
  first_event_at: string;
  last_event_at: string;
}

export interface ApplicationEvent {
  id: number;
  event_type: string;
  event_label: string | null;
  event_date: string;
  summary: string | null;
  raw_subject: string | null;
  raw_from: string | null;
  confidence: number;
}

export interface ApplicationDetail extends ApplicationSummary {
  events: ApplicationEvent[];
}

export interface DashboardStats {
  total_applications: number;
  response_rate: number;
  avg_days_to_response: number | null;
  status_counts: Record<string, number>;
}

export interface ActivityData {
  months: string[];
  counts: number[];
}

export interface RecentActivityEntry {
  event_type: string;
  event_date: string;
  summary: string | null;
  company_name: string;
  role_title: string | null;
}

export interface RecentActivityData {
  entries: RecentActivityEntry[];
}

export interface SyncStatus {
  running: boolean;
  progress: {
    fetched: number;
    parsed: number;
    total: number;
  };
}

export interface AuthStatus {
  authenticated: boolean;
  email: string | null;
}

export interface StagedEmail {
  gmail_message_id: string;
  subject: string;
  sender: string;
  date: string;
  snippet: string;
  status: "new" | "processed_relevant" | "processed_irrelevant";
  source_tier?: string | null;
  triage_status?: string | null;
  result?: {
    event_type: string;
    company_name: string;
    role_title: string | null;
  };
}
