# Verification & Evaluation Prompts

This file records the verification commands and evaluation criteria applied to validate system correctness.

## 1. Fresh Clone & Execution Protocol
```bash
git clone https://github.com/Bhargavi88-ai/ecommerce-cart-recovery-attribution fresh-test
cd fresh-test
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -v
```

## 2. Deterministic Generation & Validation Protocol
```bash
python generate.py --seed 20261022 --out run1
python generate.py --seed 20261022 --out run2
python validate.py --data run1
```

## 3. Checksum Identity Verification
```bash
sha256sum run1/* > a.txt && sha256sum run2/* > b.txt
sed -i 's/run2/run1/g' b.txt && diff -u a.txt b.txt
```

## 4. Independent Frequency-Cap Audit
```bash
python check_cap.py --data run1
```
Expected output:
```text
Total sent attempts checked: 10000
customers over cap: 0
```
