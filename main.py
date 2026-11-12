import os
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse

app = FastAPI(title="Subnet & VLSM Calculator API")


# ── Error Handlers ────────────────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"] if errors else "Parameter input tidak valid."
    return JSONResponse(status_code=400, content={"detail": msg})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


# ── Helper Functions ──────────────────────────────────────────────────────────
def validate_ip(ip: str) -> list[int]:
    """
    Validasi alamat IPv4:
    - Harus berupa string tanpa spasi
    - Tepat 4 oktet dipisahkan titik
    - Tiap oktet 0-255 tanpa leading zero
    """
    if not isinstance(ip, str):
        raise ValueError("Alamat IP harus berupa teks (string).")

    if ip != ip.strip() or any(c.isspace() for c in ip):
        raise ValueError("Alamat IP tidak boleh mengandung spasi.")

    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError("Alamat IP harus terdiri dari tepat 4 oktet.")

    octets = []
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"Oktet '{part}' tidak valid. Harus berupa angka 0-255.")

        # Tolak leading zero: panjang > 1 dan dimulai dengan '0'
        if len(part) > 1 and part.startswith("0"):
            raise ValueError(f"Oktet '{part}' tidak boleh memiliki angka nol di depan (leading zero).")

        val = int(part)
        if not (0 <= val <= 255):
            raise ValueError(f"Oktet '{part}' di luar rentang valid 0-255.")

        octets.append(val)

    return octets


def validate_prefix(prefix: int) -> int:
    """Validasi prefix CIDR: bilangan bulat 0 sampai 32."""
    if not isinstance(prefix, int) or isinstance(prefix, bool):
        raise ValueError("Prefix harus berupa bilangan bulat.")
    if not (0 <= prefix <= 32):
        raise ValueError(f"Prefix {prefix} tidak valid. Harus berada di rentang 0 s.d. 32.")
    return prefix


def int_to_ip(n: int) -> str:
    """Konversi 32-bit unsigned int ke format dotted decimal string."""
    return f"{(n >> 24) & 0xFF}.{(n >> 16) & 0xFF}.{(n >> 8) & 0xFF}.{n & 0xFF}"


# ── Core Calculation ──────────────────────────────────────────────────────────
def hitung_subnet(ip: str, prefix: int) -> dict:
    """
    Menghitung parameter subnet IPv4:
    - Mask, network (AND bitwise), broadcast, first_host, last_host, usable_hosts
    - Penanganan khusus RFC 3021 untuk /31 dan host route untuk /32
    """
    octets = validate_ip(ip)
    prefix = validate_prefix(prefix)

    # 32-bit unsigned integer untuk IP
    ip_int = (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]

    # Subnet mask
    if prefix == 0:
        mask_int = 0
    else:
        mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

    wildcard_int = (~mask_int) & 0xFFFFFFFF

    # Network address dihitung dengan operasi bitwise AND antara IP dan subnet mask
    network_int = (ip_int & mask_int) & 0xFFFFFFFF
    broadcast_int = (network_int | wildcard_int) & 0xFFFFFFFF

    mask_str = int_to_ip(mask_int)
    network_str = int_to_ip(network_int)

    if prefix == 32:
        # /32: 1 host, broadcast = None, first_host = last_host = IP itu
        usable_hosts = 1
        broadcast_str = None
        first_host_str = int_to_ip(ip_int)
        last_host_str = int_to_ip(ip_int)
    elif prefix == 31:
        # /31: aturan RFC 3021 point-to-point, 2 host, broadcast = None
        usable_hosts = 2
        broadcast_str = None
        first_host_str = int_to_ip(network_int)
        last_host_str = int_to_ip(network_int + 1)
    else:
        # /0 s.d. /30
        usable_hosts = (1 << (32 - prefix)) - 2
        broadcast_str = int_to_ip(broadcast_int)
        first_host_str = int_to_ip(network_int + 1)
        last_host_str = int_to_ip(broadcast_int - 1)

    return {
        "mask": mask_str,
        "network": network_str,
        "broadcast": broadcast_str,
        "first_host": first_host_str,
        "last_host": last_host_str,
        "usable_hosts": usable_hosts,
    }


def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]:
    """
    Mengalokasikan blok subnet VLSM dari network_cidr induk
    berdasarkan kebutuhan_host yang diurutkan descending.
    """
    raise NotImplementedError


# ── API Endpoints ─────────────────────────────────────────────────────────────
@app.get("/")
def get_index():
    """Mengembalikan halaman web index.html."""
    if not os.path.exists("index.html"):
        raise HTTPException(status_code=404, detail="File index.html tidak ditemukan.")
    return FileResponse("index.html", media_type="text/html")


@app.get("/style.css")
def get_style():
    """Melayani file CSS statis."""
    if os.path.exists("style.css"):
        return FileResponse("style.css", media_type="text/css")
    raise HTTPException(status_code=404, detail="File style.css tidak ditemukan.")


@app.get("/subnet.js")
def get_script():
    """Melayani file JavaScript statis."""
    if os.path.exists("subnet.js"):
        return FileResponse("subnet.js", media_type="application/javascript")
    raise HTTPException(status_code=404, detail="File subnet.js tidak ditemukan.")


@app.get("/api/subnet")
def api_subnet(ip: str = Query(...), prefix: int = Query(...)):
    """Endpoint kalkulasi subnet IPv4."""
    try:
        return hitung_subnet(ip, prefix)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/vlsm")
def api_vlsm(payload: dict):
    """Endpoint alokasi VLSM."""
    raise NotImplementedError

