import pytest
from fastapi.testclient import TestClient
from main import app, hitung_subnet, alokasi_vlsm

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


# ==============================================================================
# 6. Unit Test: alokasi_vlsm (Kasus Valid)
# ==============================================================================
def test_alokasi_vlsm_normal():
    network_cidr = "192.168.1.0/24"
    kebutuhan = [100, 50, 20, 2]
    hasil = alokasi_vlsm(network_cidr, kebutuhan)

    assert len(hasil) == 4

    # Subnet 1: 100 host -> /25 (192.168.1.0)
    assert hasil[0]["kebutuhan"] == 100
    assert hasil[0]["network_cidr"] == "192.168.1.0/25"
    assert hasil[0]["network"] == "192.168.1.0"
    assert hasil[0]["mask"] == "255.255.255.128"
    assert hasil[0]["broadcast"] == "192.168.1.127"
    assert hasil[0]["first_host"] == "192.168.1.1"
    assert hasil[0]["last_host"] == "192.168.1.126"
    assert hasil[0]["usable_hosts"] == 126

    # Subnet 2: 50 host -> /26 (192.168.1.128)
    assert hasil[1]["kebutuhan"] == 50
    assert hasil[1]["network_cidr"] == "192.168.1.128/26"
    assert hasil[1]["network"] == "192.168.1.128"
    assert hasil[1]["mask"] == "255.255.255.192"
    assert hasil[1]["broadcast"] == "192.168.1.191"
    assert hasil[1]["first_host"] == "192.168.1.129"
    assert hasil[1]["last_host"] == "192.168.1.190"
    assert hasil[1]["usable_hosts"] == 62

    # Subnet 3: 20 host -> /27 (192.168.1.192)
    assert hasil[2]["kebutuhan"] == 20
    assert hasil[2]["network_cidr"] == "192.168.1.192/27"
    assert hasil[2]["network"] == "192.168.1.192"
    assert hasil[2]["mask"] == "255.255.255.224"
    assert hasil[2]["broadcast"] == "192.168.1.223"
    assert hasil[2]["first_host"] == "192.168.1.193"
    assert hasil[2]["last_host"] == "192.168.1.222"
    assert hasil[2]["usable_hosts"] == 30

    # Subnet 4: 2 host -> /30 (192.168.1.224)
    assert hasil[3]["kebutuhan"] == 2
    assert hasil[3]["network_cidr"] == "192.168.1.224/30"
    assert hasil[3]["network"] == "192.168.1.224"
    assert hasil[3]["mask"] == "255.255.255.252"
    assert hasil[3]["broadcast"] == "192.168.1.227"
    assert hasil[3]["first_host"] == "192.168.1.225"
    assert hasil[3]["last_host"] == "192.168.1.226"
    assert hasil[3]["usable_hosts"] == 2


# ==============================================================================
# 7. Unit Test: alokasi_vlsm (Kasus Tidak Valid)
# ==============================================================================
@pytest.mark.parametrize(
    "network_cidr,kebutuhan",
    [
        ("192.168.1.0/24", [200, 100]),   # Kapasitas kurang (SPEC Test 10)
        ("192.168.1.5/24", [10, 5]),      # IP bukan network address
        ("192.168.1.0/24", []),           # Kebutuhan kosong
        ("192.168.1.0/24", [10, 0]),      # Nilai kebutuhan < 1
        ("192.168.1.0/24", [-5]),         # Nilai kebutuhan negatif
        ("invalid_cidr", [10]),           # Format CIDR tidak valid
    ],
)
def test_alokasi_vlsm_invalid(network_cidr, kebutuhan):
    with pytest.raises(ValueError):
        alokasi_vlsm(network_cidr, kebutuhan)


# ==============================================================================
# 8. Integration Test: API Endpoint POST /api/vlsm (Sukses 200)
# ==============================================================================
def test_api_vlsm_valid():
    payload = {
        "network": "192.168.1.0/24",
        "kebutuhan_host": [100, 50, 20, 2],
    }
    response = client.post("/api/vlsm", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4
    assert data[0]["network_cidr"] == "192.168.1.0/25"
    assert data[3]["network_cidr"] == "192.168.1.224/30"


# ==============================================================================
# 9. Integration Test: API Endpoint POST /api/vlsm (Invalid 400 Bad Request)
# ==============================================================================
@pytest.mark.parametrize(
    "payload",
    [
        {"network": "192.168.1.0/24", "kebutuhan_host": [200, 100]},
        {"network": "192.168.1.5/24", "kebutuhan_host": [10]},
        {"network": "192.168.1.0/24", "kebutuhan_host": []},
        {"network": "192.168.1.0/24", "kebutuhan_host": [0]},
    ],
)
def test_api_vlsm_invalid(payload):
    response = client.post("/api/vlsm", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

