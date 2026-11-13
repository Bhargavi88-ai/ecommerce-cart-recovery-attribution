import pytest
from app.generator.synthetic_data_generator import SyntheticDataGenerator


def test_generator_deterministic_reproducibility():
    gen1 = SyntheticDataGenerator(seed=20261022, scale="starter")
    data1 = gen1.generate_dataset()

    gen2 = SyntheticDataGenerator(seed=20261022, scale="starter")
    data2 = gen2.generate_dataset()

    # Verify identical counts
    assert len(data1["customers"]) == len(data2["customers"])
    assert len(data1["carts"]) == len(data2["carts"])
    assert len(data1["orders"]) == len(data2["orders"])
    assert len(data1["send_attempts"]) == len(data2["send_attempts"])
    assert len(data1["attributions"]) == len(data2["attributions"])

    # Verify identical contents on sample entities
    for i in range(50):
        assert data1["customers"][i]["customer_id"] == data2["customers"][i]["customer_id"]
        assert data1["customers"][i]["email"] == data2["customers"][i]["email"]
        assert data1["carts"][i]["cart_id"] == data2["carts"][i]["cart_id"]
        assert data1["carts"][i]["status"] == data2["carts"][i]["status"]
        assert data1["carts"][i]["total_amount"] == data2["carts"][i]["total_amount"]
