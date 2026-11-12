import pytest
from fastapi.testclient import TestClient
from main import app, hitung_subnet

client = TestClient(app)


# ==============================================================================
# 1. Unit Test: hitung_subnet (Kasus Valid)
# ==============================================================================
@pytest.mark.parametrize(
    "ip,prefix,expected",
    [
        (
            "172.16.5.130",
            25,
            {
                "mask": "255.255.255.128",
                "network": "172.16.5.128",
                "broadcast": "172.16.5.255",
                "first_host": "172.16.5.129",
                "last_host": "172.16.5.254",
                "usable_hosts": 126,
            },
        ),
        (
            "10.0.0.0",
            30,
            {
                "mask": "255.255.255.252",
                "network": "10.0.0.0",
                "broadcast": "10.0.0.3",
                "first_host": "10.0.0.1",
                "last_host": "10.0.0.2",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.0",
            31,
            {
                "mask": "255.255.255.254",
                "network": "192.168.1.0",
                "broadcast": None,
                "first_host": "192.168.1.0",
                "last_host": "192.168.1.1",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.5",
            32,
            {
                "mask": "255.255.255.255",
                "network": "192.168.1.5",
                "broadcast": None,
                "first_host": "192.168.1.5",
                "last_host": "192.168.1.5",
                "usable_hosts": 1,
            },
        ),
    ],
)
def test_hitung_subnet_valid(ip, prefix, expected):
    result = hitung_subnet(ip, prefix)
    assert result == expected


# ==============================================================================
# 2. Unit Test: hitung_subnet (Kasus Tidak Valid)
# ==============================================================================
@pytest.mark.parametrize(
    "ip,prefix",
    [
        ("256.1.1.1", 24),    # Oktet > 255
        ("192.168.01.1", 24),  # Leading zero
        ("192.168.1", 24),     # Kurang dari 4 oktet
        ("abc", 24),           # Bukan angka
        ("", 24),              # String kosong
        ("192.168.1.1", 33),   # Prefix > 32
        ("192.168.1.1", -1),   # Prefix < 0
    ],
)
def test_hitung_subnet_invalid(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


# ==============================================================================
# 3. Integration Test: API Endpoint GET /
# ==============================================================================
def test_get_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


# ==============================================================================
# 4. Integration Test: API Endpoint GET /api/subnet (Sukses 200)
# ==============================================================================
@pytest.mark.parametrize(
    "ip,prefix,expected_network,expected_usable",
    [
        ("172.16.5.130", 25, "172.16.5.128", 126),
        ("10.0.0.0", 30, "10.0.0.0", 2),
        ("192.168.1.0", 31, "192.168.1.0", 2),
        ("192.168.1.5", 32, "192.168.1.5", 1),
    ],
)
def test_api_subnet_valid(ip, prefix, expected_network, expected_usable):
    response = client.get(f"/api/subnet?ip={ip}&prefix={prefix}")
    assert response.status_code == 200
    data = response.json()
    assert data["network"] == expected_network
    assert data["usable_hosts"] == expected_usable
    for key in ["mask", "network", "broadcast", "first_host", "last_host", "usable_hosts"]:
        assert key in data


# ==============================================================================
# 5. Integration Test: API Endpoint GET /api/subnet (Invalid 400 Bad Request)
# ==============================================================================
@pytest.mark.parametrize(
    "ip,prefix",
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        ("192.168.1.1", 33),
        ("192.168.1.1", -1),
    ],
)
def test_api_subnet_invalid(ip, prefix):
    response = client.get(f"/api/subnet?ip={ip}&prefix={prefix}")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
