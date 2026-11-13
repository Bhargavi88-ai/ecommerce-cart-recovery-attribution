import pytest
from app.validation.validator import DataQualityValidator


def test_validation_suite_on_dataset(test_dataset):
    validator = DataQualityValidator(test_dataset)
    summary = validator.run_all_validations()

    assert summary["total_rules"] == 16
    assert summary["passed_rules"] == 16
    assert summary["failed_rules"] == 0
    assert summary["overall_status"] == "PASS"

    # Verify key rules
    rule_map = {r["rule_name"]: r for r in summary["rule_results"]}
    assert rule_map["primary_key_uniqueness"]["status"] == "PASS"
    assert rule_map["foreign_key_integrity"]["status"] == "PASS"
    assert rule_map["frequency_caps"]["status"] == "PASS"
    assert rule_map["duplicate_attribution_detection"]["status"] == "PASS"
    assert rule_map["cart_total_reconciliation"]["status"] == "PASS"
    assert rule_map["event_chronology"]["status"] == "PASS"
