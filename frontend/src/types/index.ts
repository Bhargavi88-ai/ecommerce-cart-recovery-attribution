export interface Customer {
  customer_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  preferred_channel: string;
  created_at: string;
  updated_at: string;
}

export interface Consent {
  consent_id: string;
  customer_id: string;
  channel: string;
  status: string;
  effective_at: string;
  source: string;
  created_at: string;
}

export interface CartLine {
  cart_line_id: string;
  cart_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Cart {
  cart_id: string;
  customer_id: string;
  session_id?: string;
  status: string;
  subtotal: number;
  discount_total: number;
  total_amount: number;
  created_at: string;
  updated_at: string;
  last_activity_at: string;
  abandoned_at?: string;
  recovered_at?: string;
  cart_lines?: CartLine[];
}

export interface MessageTemplate {
  template_id: string;
  campaign_id: string;
  channel: string;
  variant: string;
  subject?: string;
  body_template: string;
  is_active: boolean;
}

export interface Campaign {
  campaign_id: string;
  name: string;
  channel: string;
  trigger_delay_minutes: number;
  discount_percent: number;
  is_active: boolean;
  created_at: string;
  templates?: MessageTemplate[];
}

export interface CommunicationEvent {
  event_id: string;
  send_id: string;
  event_type: string;
  timestamp: string;
  metadata_json?: string;
}

export interface SendAttempt {
  send_id: string;
  message_id: string;
  campaign_id: string;
  template_id?: string;
  cart_id: string;
  customer_id: string;
  channel: string;
  status: string;
  suppression_reason?: string;
  scheduled_at: string;
  sent_at?: string;
  created_at: string;
  communication_events?: CommunicationEvent[];
}

export interface OrderLine {
  order_line_id: string;
  order_id: string;
  product_id: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

export interface Order {
  order_id: string;
  customer_id: string;
  cart_id?: string;
  total_amount: number;
  order_timestamp: string;
  status: string;
  order_lines?: OrderLine[];
}

export interface Attribution {
  attribution_id: string;
  order_id: string;
  send_id: string;
  campaign_id: string;
  cart_id?: string;
  order_timestamp: string;
  qualifying_click_at: string;
  latency_hours: number;
  attributed_revenue: number;
  model: string;
  created_at: string;
}

export interface OverviewKpis {
  total_customers: number;
  total_carts: number;
  abandoned_carts: number;
  eligible_carts: number;
  suppressed_carts: number;
  campaigns: number;
  send_attempts: number;
  delivery_rate: number;
  open_rate: number;
  click_rate: number;
  recovered_orders: number;
  recovered_revenue: number;
  recovery_rate: number;
  conversion_rate: number;
  abandonment_rate: number;
  revenue_per_recovered_cart: number;
  suppression_rate: number;
}

export interface ChartDataPoint {
  name: string;
  value: number;
  secondary_value?: number;
}

export interface OverviewAnalytics {
  kpis: OverviewKpis;
  cart_lifecycle_distribution: ChartDataPoint[];
  channel_performance: ChartDataPoint[];
  suppression_reasons: ChartDataPoint[];
  revenue_recovery_trends: ChartDataPoint[];
  anomaly_distribution: ChartDataPoint[];
}

export interface CampaignPerformanceMetric {
  campaign_id: string;
  name: string;
  channel: string;
  sends: number;
  delivered: number;
  opens: number;
  clicks: number;
  conversions: number;
  revenue: number;
  conversion_rate: number;
}

export interface AnomalyRecord {
  anomaly_id: string;
  issue_type: string;
  affected_entity: string;
  affected_record_id: string;
  detected_at: string;
  observed_value: string;
  expected_value: string;
  ground_truth_label: string;
  expected_decision: string;
  actual_decision: string;
  resolution_status: string;
}

export interface RuleResult {
  rule_name: string;
  status: string;
  error_count: number;
  sample_errors: string[];
}

export interface ValidationSummary {
  validation_timestamp: string;
  total_rules: number;
  passed_rules: number;
  failed_rules: number;
  total_violations: number;
  overall_status: string;
  rule_results: RuleResult[];
}

