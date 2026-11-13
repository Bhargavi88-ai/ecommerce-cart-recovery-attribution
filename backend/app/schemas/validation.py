from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Dict, Any, Optional


class AnomalyRecordResponse(BaseModel):
    anomaly_id: str
    issue_type: str
    affected_entity: str
    affected_record_id: str
    detected_at: datetime
    observed_value: str
    expected_value: str
    ground_truth_label: str
    expected_decision: str
    actual_decision: str
    resolution_status: str

    model_config = ConfigDict(from_attributes=True)


class AnomalyListResponse(BaseModel):
    total: int
    items: List[AnomalyRecordResponse]


class RuleResultSchema(BaseModel):
    rule_name: str
    status: str
    error_count: int
    sample_errors: List[str]


class ValidationSummaryResponse(BaseModel):
    validation_timestamp: str
    total_rules: int
    passed_rules: int
    failed_rules: int
    total_violations: int
    overall_status: str
    rule_results: List[RuleResultSchema]
