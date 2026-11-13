"""
Deterministic zero-padded identifier generator.
Ensures identical IDs across runs for identical sequence indices.
"""

def customer_id(index: int) -> str:
    return f"CUS-{index:06d}"

def cart_id(index: int, year: int = 2026) -> str:
    return f"CART-{year}-{index:06d}"

def campaign_id(index: int, year: int = 2026) -> str:
    return f"CMP-{year}-{index:06d}"

def message_id(c_id: str, sequence: int = 1) -> str:
    return f"MSG-{c_id}-{sequence:02d}"

def send_id(index: int, year: int = 2026) -> str:
    return f"SEND-{year}-{index:06d}"

def order_id(index: int, year: int = 2026) -> str:
    return f"ORD-{year}-{index:06d}"

def product_id(index: int) -> str:
    return f"PRD-{index:06d}"

def consent_id(index: int) -> str:
    return f"CNS-{index:06d}"

def session_id(index: int, year: int = 2026) -> str:
    return f"SES-{year}-{index:06d}"

def cart_line_id(c_id: str, item_index: int) -> str:
    # e.g., CL-CART-2026-000001-01
    parts = c_id.split("-")
    if len(parts) >= 3:
        return f"CL-{parts[1]}-{parts[2]}-{item_index:02d}"
    return f"CL-{c_id}-{item_index:02d}"

def order_line_id(o_id: str, item_index: int) -> str:
    parts = o_id.split("-")
    if len(parts) >= 3:
        return f"OL-{parts[1]}-{parts[2]}-{item_index:02d}"
    return f"OL-{o_id}-{item_index:02d}"

def template_id(index: int) -> str:
    return f"TMPL-{index:06d}"

def communication_event_id(index: int, year: int = 2026) -> str:
    return f"EVT-{year}-{index:06d}"

def attribution_id(index: int, year: int = 2026) -> str:
    return f"ATTR-{year}-{index:06d}"

def anomaly_id(index: int) -> str:
    return f"ANO-{index:06d}"
