// API Response Types

export interface BusinessContext {
    industry?: string;
    employee_count?: number;
    annual_revenue?: number;
    region?: string;
    years_in_operation?: number;
}

export interface ChatRequest {
    message: string;
    business_context?: BusinessContext;
    conversation_id?: string;
}

export interface DocumentSource {
    title: string;
    document_id: string;
    url?: string;
    relevance_score: number;
    excerpt: string;
}

export interface MatchedPrivilege {
    name: string;
    privilege_type: 'grant' | 'subsidy' | 'tax_holiday' | 'loan' | 'other';
    eligibility?: string;
    deadline?: string;
    amount?: string;
}

export interface ChatResponse {
    response: string;
    sources: DocumentSource[];
    matched_privileges: MatchedPrivilege[];
    conversation_id: string;
    timestamp: string;
}

export interface ScoutStatusDetails {
    document_id?: string;
    title?: string;
    url?: string;
    relevance?: boolean;
    progress: number;
}

export interface ScoutStatusEvent {
    event_type: 'search' | 'judge' | 'ingest' | 'complete' | 'error';
    message: string;
    details: ScoutStatusDetails;
    timestamp: string;
}

export interface ScoutTriggerRequest {
    keywords?: string[];
    date_filter?: string;
    force_refresh?: boolean;
}

export interface ScoutTriggerResponse {
    status: 'started' | 'already_running';
    job_id: string;
    message: string;
    estimated_duration_seconds: number;
}

export interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    sources?: DocumentSource[];
    privileges?: MatchedPrivilege[];
    timestamp: Date;
    isLoading?: boolean;
}

export interface HealthResponse {
    status: string;
    app_name: string;
    version: string;
    document_count: number;
    llm_provider: string;
    llm_model: string;
}
