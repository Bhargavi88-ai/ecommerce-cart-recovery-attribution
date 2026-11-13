from typing import Dict, Any, List
from datetime import datetime, timedelta


class ValidationRuleResult:
    def __init__(self, rule_name: str, passed: bool, error_count: int = 0, errors: List[str] = None):
        self.rule_name = rule_name
        self.passed = passed
        self.error_count = error_count
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_name": self.rule_name,
            "status": "PASS" if self.passed else "FAIL",
            "passed": self.passed,
            "error_count": self.error_count,
            "sample_errors": self.errors[:10]
        }

