const API_BASE_URL = 'http://localhost:8000/api';

async function fetchJson<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorDetail = response.statusText;
    try {
      const errData = await response.json();
      errorDetail = errData.detail || errorDetail;
    } catch {
      // ignore
    }
    throw new Error(`API Error [${response.status}]: ${errorDetail}`);
  }

  return response.json();
}

export const api = {
  // Customers
  getCustomers: (params?: { skip?: number; limit?: number; search?: string; preferred_channel?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.search) q.append('search', params.search);
    if (params?.preferred_channel) q.append('preferred_channel', params.preferred_channel);
    return fetchJson<{ total: number; items: any[] }>(`/customers?${q.toString()}`);
  },
  getCustomerById: (id: string) => fetchJson<any>(`/customers/${id}`),

  // Consents
  getConsents: (params?: { skip?: number; limit?: number; channel?: string; status?: string; customer_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.channel) q.append('channel', params.channel);
    if (params?.status) q.append('status', params.status);
    if (params?.customer_id) q.append('customer_id', params.customer_id);
    return fetchJson<{ total: number; items: any[] }>(`/consents?${q.toString()}`);
  },

  // Carts
  getCarts: (params?: { skip?: number; limit?: number; status?: string; customer_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.status) q.append('status', params.status);
    if (params?.customer_id) q.append('customer_id', params.customer_id);
    return fetchJson<{ total: number; items: any[] }>(`/carts?${q.toString()}`);
  },
  getAbandonedCarts: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    return fetchJson<{ total: number; items: any[] }>(`/carts/abandoned?${q.toString()}`);
  },
  getEligibleCarts: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    return fetchJson<{ total: number; items: any[] }>(`/carts/eligible?${q.toString()}`);
  },
  getSuppressedCarts: (params?: { skip?: number; limit?: number }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    return fetchJson<{ total: number; items: any[] }>(`/carts/suppressed?${q.toString()}`);
  },
  getCartById: (id: string) => fetchJson<any>(`/carts/${id}`),

  // Campaigns
  getCampaigns: (params?: { skip?: number; limit?: number; channel?: string; is_active?: boolean }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.channel) q.append('channel', params.channel);
    if (params?.is_active !== undefined) q.append('is_active', String(params.is_active));
    return fetchJson<{ total: number; items: any[] }>(`/campaigns?${q.toString()}`);
  },
  createCampaign: (data: any) =>
    fetchJson<any>('/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  getCampaignById: (id: string) => fetchJson<any>(`/campaigns/${id}`),

  // Send Attempts
  getSendAttempts: (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    channel?: string;
    campaign_id?: string;
    customer_id?: string;
    suppression_reason?: string;
  }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.status) q.append('status', params.status);
    if (params?.channel) q.append('channel', params.channel);
    if (params?.campaign_id) q.append('campaign_id', params.campaign_id);
    if (params?.customer_id) q.append('customer_id', params.customer_id);
    if (params?.suppression_reason) q.append('suppression_reason', params.suppression_reason);
    return fetchJson<{ total: number; items: any[] }>(`/send-attempts?${q.toString()}`);
  },
  getSendAttemptById: (id: string) => fetchJson<any>(`/send-attempts/${id}`),

  // Orders
  getOrders: (params?: { skip?: number; limit?: number; customer_id?: string; cart_id?: string; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.customer_id) q.append('customer_id', params.customer_id);
    if (params?.cart_id) q.append('cart_id', params.cart_id);
    if (params?.status) q.append('status', params.status);
    return fetchJson<{ total: number; items: any[] }>(`/orders?${q.toString()}`);
  },
  getOrderById: (id: string) => fetchJson<any>(`/orders/${id}`),

  // Attributions
  getAttributions: (params?: { skip?: number; limit?: number; campaign_id?: string; order_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.campaign_id) q.append('campaign_id', params.campaign_id);
    if (params?.order_id) q.append('order_id', params.order_id);
    return fetchJson<{ total: number; items: any[] }>(`/attributions?${q.toString()}`);
  },

  // Analytics
  getOverviewAnalytics: () => fetchJson<any>('/analytics/overview'),
  getCampaignPerformance: () => fetchJson<any[]>('/analytics/campaign-performance'),
  getRecoveryAnalytics: () => fetchJson<any>('/analytics/recovery'),
  getRevenueAnalytics: () => fetchJson<any>('/analytics/revenue'),
  getAttributionAnalytics: () => fetchJson<any>('/analytics/attribution'),

  // Anomalies
  getAnomalies: (params?: { skip?: number; limit?: number; issue_type?: string; affected_entity?: string; resolution_status?: string }) => {
    const q = new URLSearchParams();
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));
    if (params?.issue_type) q.append('issue_type', params.issue_type);
    if (params?.affected_entity) q.append('affected_entity', params.affected_entity);
    if (params?.resolution_status) q.append('resolution_status', params.resolution_status);
    return fetchJson<{ total: number; items: any[] }>(`/anomalies?${q.toString()}`);
  },
  updateAnomalyStatus: (id: string, status: string) =>
    fetchJson<any>(`/anomalies/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    }),

  // Validation
  runValidation: () =>
    fetchJson<any>('/validation/run', {
      method: 'POST',
    }),
  getValidationReport: () => fetchJson<any>('/validation/report'),

  // Generator
  triggerGenerator: (scale: string = 'starter', seed: number = 20261022, populate_db: boolean = true) =>
    fetchJson<any>('/generator/run', {
      method: 'POST',
      body: JSON.stringify({ scale, seed, populate_db }),
    }),
  getGeneratorStatus: () => fetchJson<any>('/generator/status'),

  // Exports
  getExports: () => fetchJson<{ files: any[]; manifest: any }>('/exports'),
  getExportFileUrl: (filename: string) => `${API_BASE_URL}/exports/${encodeURIComponent(filename)}`,
};
