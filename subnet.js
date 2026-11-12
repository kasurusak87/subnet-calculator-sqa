/* =============================================
   Subnet Calculator — subnet.js
   ============================================= */

'use strict';

// ── Helpers ──────────────────────────────────

/**
 * Convert a 32-bit integer to dotted-decimal notation.
 * @param {number} n
 * @returns {string}
 */
function intToIP(n) {
  return [
    (n >>> 24) & 0xff,
    (n >>> 16) & 0xff,
    (n >>>  8) & 0xff,
     n         & 0xff,
  ].join('.');
}

/**
 * Convert a dotted-decimal IP string to a 32-bit unsigned integer.
 * @param {string} ip
 * @returns {number}
 */
function ipToInt(ip) {
  return ip.split('.').reduce((acc, oct) => (acc << 8) | (parseInt(oct, 10) & 0xff), 0) >>> 0;
}

/**
 * Format a 32-bit int as a dotted binary string (e.g. "11000000.10101000.00000001.00000000").
 * @param {number} n
 * @returns {string}
 */
function intToBin(n) {
  return [24, 16, 8, 0]
    .map(shift => ((n >>> shift) & 0xff).toString(2).padStart(8, '0'))
    .join('.');
}

/**
 * Format a large number with thousand-separator.
 * @param {number} n
 * @returns {string}
 */
function fmt(n) {
  return typeof n === 'number' ? n.toLocaleString('id-ID') : n;
}

/** Shorthand setter */
function set(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

// ── Tab Navigation ────────────────────────────
function switchMode(mode) {
  const tabSubnet = document.getElementById('tab-subnet');
  const tabVlsm = document.getElementById('tab-vlsm');
  const modeSubnet = document.getElementById('mode-subnet');
  const modeVlsm = document.getElementById('mode-vlsm');
  const errorBanner = document.getElementById('error-banner');

  if (errorBanner) errorBanner.classList.add('hidden');

  if (mode === 'subnet') {
    tabSubnet.classList.add('active');
    tabVlsm.classList.remove('active');
    modeSubnet.classList.remove('hidden');
    modeVlsm.classList.add('hidden');
  } else {
    tabVlsm.classList.add('active');
    tabSubnet.classList.remove('active');
    modeVlsm.classList.remove('hidden');
    modeSubnet.classList.add('hidden');
  }
}

// ── Main Calculator (Connected to FastAPI /api/subnet) ──
async function calculate() {
  const ipInput = document.getElementById('ip');
  const prefixInput = document.getElementById('prefix');
  const errorBanner = document.getElementById('error-banner');
  const errorText = document.getElementById('error-text');
  const resultSec = document.getElementById('subnet-result-section');

  const ip = ipInput.value.trim();
  const prefix = prefixInput.value.trim();

  // Reset UI status
  if (errorBanner) errorBanner.classList.add('hidden');
  ipInput.classList.remove('invalid');
  const prefixWrap = document.querySelector('.prefix-input-wrap');
  if (prefixWrap) prefixWrap.classList.remove('invalid');

  try {
    const url = `/api/subnet?ip=${encodeURIComponent(ip)}&prefix=${encodeURIComponent(prefix)}`;
    const response = await fetch(url);
    const data = await response.json();

    if (!response.ok) {
      // Tampilkan pesan error langsung dari field "detail" yang dikirim backend
      if (errorBanner && errorText) {
        errorText.textContent = data.detail || 'Terjadi kesalahan saat memproses perhitungan.';
        errorBanner.classList.remove('hidden');
      }
      if (resultSec) resultSec.classList.add('hidden');
      return;
    }

    // Sembunyikan error dan tampilkan hasil
    if (errorBanner) errorBanner.classList.add('hidden');

    const prefixNum = parseInt(prefix, 10);

    // Kartu Metrik Ringkasan
    set('res-network', data.network);
    set('res-cidr', `/${prefixNum}  •  Mask: ${data.mask}`);
    set('res-broadcast', data.broadcast !== null ? data.broadcast : 'None (RFC 3021 / 32)');
    set('res-broadcast-sub', data.broadcast !== null ? 'Broadcast Address' : 'Tidak ada broadcast');

    if (prefixNum === 32) {
      set('res-range', data.first_host);
      set('res-range-sub', 'Host route (/32)');
    } else if (prefixNum === 31) {
      set('res-range', `${data.first_host} – ${data.last_host}`);
      set('res-range-sub', 'Point-to-point (RFC 3021)');
    } else {
      set('res-range', `${data.first_host} – ${data.last_host}`);
      set('res-range-sub', `${fmt(data.usable_hosts)} alamat host tersedia`);
    }

    set('res-hosts', fmt(data.usable_hosts));
    set('res-hosts-sub', 'Host efektif yang dapat digunakan');

    // Tabel Detail Konfigurasi
    set('d-mask', data.mask);
    set('d-net', `${data.network} /${prefixNum}`);
    set('d-bcast', data.broadcast !== null ? data.broadcast : 'None (RFC 3021 / 32)');
    set('d-first', data.first_host);
    set('d-last', data.last_host);
    set('d-usable', `${fmt(data.usable_hosts)} host`);

    // Representasi Biner 32-Bit
    try {
      const parsedIp = ip.split('.').map(Number);
      if (parsedIp.length === 4 && parsedIp.every(n => n >= 0 && n <= 255)) {
        set('bin-ip', intToBin(ipToInt(ip)));
      } else {
        set('bin-ip', intToBin(ipToInt(data.network)));
      }
    } catch (_) {
      set('bin-ip', intToBin(ipToInt(data.network)));
    }

    const maskInt = ipToInt(data.mask);
    const netInt = ipToInt(data.network);
    set('bin-mask', intToBin(maskInt));
    set('bin-net', intToBin(netInt));
    set('bin-bcast', data.broadcast !== null ? intToBin(ipToInt(data.broadcast)) : 'None (tanpa broadcast)');

    if (resultSec) {
      resultSec.classList.remove('hidden');
      resultSec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  } catch (err) {
    if (errorBanner && errorText) {
      errorText.textContent = 'Gagal menghubungi server API: ' + err.message;
      errorBanner.classList.remove('hidden');
    }
    if (resultSec) resultSec.classList.add('hidden');
  }
}

function handleSubnetCalc() {
  calculate();
}

async function handleVlsmCalc() {
  const netInput = document.getElementById('vlsm-network');
  const hostsInput = document.getElementById('vlsm-hosts');
  const errorBanner = document.getElementById('error-banner');
  const errorText = document.getElementById('error-text');
  const resultSec = document.getElementById('vlsm-result-section');
  const tbody = document.getElementById('vlsm-table-body');

  const network = netInput ? netInput.value.trim() : '';
  const hostsRaw = hostsInput ? hostsInput.value.trim() : '';

  // Reset UI
  if (errorBanner) errorBanner.classList.add('hidden');
  if (netInput) netInput.classList.remove('invalid');
  if (hostsInput) hostsInput.classList.remove('invalid');

  if (!network) {
    if (errorBanner && errorText) {
      errorText.textContent = "Alamat network induk (CIDR) wajib diisi.";
      errorBanner.classList.remove('hidden');
    }
    return;
  }

  // Parse daftar kebutuhan host
  const hostParts = hostsRaw.split(',').map(s => s.trim()).filter(Boolean);
  if (hostParts.length === 0) {
    if (errorBanner && errorText) {
      errorText.textContent = "Daftar kebutuhan host tidak boleh kosong.";
      errorBanner.classList.remove('hidden');
    }
    return;
  }

  const kebutuhan_host = [];
  for (const p of hostParts) {
    const num = Number(p);
    if (!/^\d+$/.test(p) || isNaN(num) || num < 1) {
      if (errorBanner && errorText) {
        errorText.textContent = `Nilai kebutuhan '${p}' tidak valid. Harus berupa bilangan bulat >= 1.`;
        errorBanner.classList.remove('hidden');
      }
      return;
    }
    kebutuhan_host.push(num);
  }

  try {
    const response = await fetch('/api/vlsm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ network, kebutuhan_host }),
    });
    const data = await response.json();

    if (!response.ok) {
      if (errorBanner && errorText) {
        errorText.textContent = data.detail || 'Terjadi kesalahan pada alokasi VLSM.';
        errorBanner.classList.remove('hidden');
      }
      if (resultSec) resultSec.classList.add('hidden');
      return;
    }

    // Render tabel alokasi VLSM
    if (tbody) {
      tbody.innerHTML = '';
      data.forEach((sub, idx) => {
        const tr = document.createElement('tr');
        const bcastDisplay = sub.broadcast !== null ? sub.broadcast : 'None (/31)';
        const rangeDisplay = `${sub.first_host} – ${sub.last_host}`;

        tr.innerHTML = `
          <td><strong>#${idx + 1}</strong></td>
          <td><span style="background:#eef2ff;color:#4f46e5;padding:2px 8px;border-radius:6px;font-weight:600;">${fmt(sub.kebutuhan)} host</span></td>
          <td><code>${sub.network_cidr}</code></td>
          <td><code>${sub.mask}</code></td>
          <td><code>${sub.network}</code></td>
          <td><code>${rangeDisplay}</code></td>
          <td><code>${bcastDisplay}</code></td>
          <td><strong>${fmt(sub.usable_hosts)}</strong></td>
        `;
        tbody.appendChild(tr);
      });
    }

    if (resultSec) {
      resultSec.classList.remove('hidden');
      resultSec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  } catch (err) {
    if (errorBanner && errorText) {
      errorText.textContent = 'Gagal menghubungi server API: ' + err.message;
      errorBanner.classList.remove('hidden');
    }
    if (resultSec) resultSec.classList.add('hidden');
  }
}

// ── Keyboard shortcut: Enter to calculate ────
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const modeSubnet = document.getElementById('mode-subnet');
    const modeVlsm = document.getElementById('mode-vlsm');
    if (modeSubnet && !modeSubnet.classList.contains('hidden')) {
      calculate();
    } else if (modeVlsm && !modeVlsm.classList.contains('hidden')) {
      handleVlsmCalc();
    }
  }
});
