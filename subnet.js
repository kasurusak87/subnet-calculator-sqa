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
 * Validate an IPv4 address string.
 * @param {string} ip
 * @returns {boolean}
 */
function isValidIP(ip) {
  const parts = ip.trim().split('.');
  if (parts.length !== 4) return false;
  return parts.every(p => /^\d+$/.test(p) && +p >= 0 && +p <= 255);
}

/**
 * Determine the IP address class (A/B/C/D/E).
 * @param {number} ipInt  32-bit unsigned integer
 * @returns {string}
 */
function getIPClass(ipInt) {
  const first = (ipInt >>> 24) & 0xff;
  if (first < 128)  return 'A';
  if (first < 192)  return 'B';
  if (first < 224)  return 'C';
  if (first < 240)  return 'D (Multicast)';
  return 'E (Reserved)';
}

/**
 * Determine whether an IP is private (RFC 1918) or public.
 * @param {number} ipInt  32-bit unsigned integer
 * @returns {string}
 */
function getNetworkType(ipInt) {
  const first  = (ipInt >>> 24) & 0xff;
  const second = (ipInt >>> 16) & 0xff;

  if (first === 10) return 'Private (RFC 1918)';
  if (first === 172 && second >= 16 && second <= 31) return 'Private (RFC 1918)';
  if (first === 192 && second === 168) return 'Private (RFC 1918)';
  if (first === 127) return 'Loopback';
  if (first === 169 && second === 254) return 'Link-local (APIPA)';
  return 'Public';
}

/**
 * Format a large number with thousand-separator.
 * @param {number} n
 * @returns {string}
 */
function fmt(n) {
  return n.toLocaleString('id-ID');
}

// ── Main Calculator ───────────────────────────

function calculate() {
  const ipInput     = document.getElementById('ip');
  const prefixInput = document.getElementById('prefix');
  const errorEl     = document.getElementById('error-msg');
  const resultSec   = document.getElementById('result-section');

  const ip     = ipInput.value.trim();
  const prefix = parseInt(prefixInput.value.trim(), 10);

  // ── Reset UI ──
  ipInput.classList.remove('invalid');
  document.querySelector('.prefix-input-wrap').classList.remove('invalid');
  errorEl.classList.add('hidden');
  errorEl.textContent = '';

  // ── Validation ──
  let errors = [];
  if (!isValidIP(ip)) {
    ipInput.classList.add('invalid');
    errors.push('Alamat IP tidak valid. Pastikan format xxx.xxx.xxx.xxx dan setiap oktet 0–255.');
  }
  if (isNaN(prefix) || prefix < 0 || prefix > 32) {
    document.querySelector('.prefix-input-wrap').classList.add('invalid');
    errors.push('Prefix tidak valid. Gunakan nilai antara 0 sampai 32.');
  }
  if (errors.length) {
    errorEl.textContent = errors[0];
    errorEl.classList.remove('hidden');
    resultSec.classList.add('hidden');
    return;
  }

  // ── Core Calculation ──
  const ipInt       = ipToInt(ip);

  // Build subnet mask: prefix 1-bits from the left, rest 0
  const maskInt     = prefix === 0
    ? 0
    : (0xffffffff << (32 - prefix)) >>> 0;

  const wildcardInt = (~maskInt) >>> 0;
  const networkInt  = (ipInt & maskInt) >>> 0;
  const broadcastInt = (networkInt | wildcardInt) >>> 0;

  // Total addresses in the block
  const totalAddresses = Math.pow(2, 32 - prefix);

  // Usable hosts: subtract network + broadcast, but guard edge cases
  let usableHosts = totalAddresses - 2;
  let firstHostInt, lastHostInt;

  if (prefix === 32) {
    // /32 → host route: single host, no network/broadcast distinction
    usableHosts  = 1;
    firstHostInt = networkInt;
    lastHostInt  = networkInt;
  } else if (prefix === 31) {
    // /31 (RFC 3021) → 2 usable hosts (point-to-point links)
    usableHosts  = 2;
    firstHostInt = networkInt;
    lastHostInt  = broadcastInt;
  } else {
    firstHostInt = (networkInt + 1) >>> 0;
    lastHostInt  = (broadcastInt - 1) >>> 0;
  }

  const ipClass    = getIPClass(networkInt);
  const netType    = getNetworkType(ipInt);

  // ── Populate Summary Cards ──
  set('res-network',   intToIP(networkInt));
  set('res-cidr',      `/${prefix}  •  Mask: ${intToIP(maskInt)}`);
  set('res-broadcast', intToIP(broadcastInt));
  set('res-broadcast-bin', intToBin(broadcastInt));

  if (prefix === 32) {
    set('res-range', intToIP(firstHostInt));
    set('res-range-sub', 'Host route (/32)');
  } else if (prefix === 31) {
    set('res-range', `${intToIP(firstHostInt)} – ${intToIP(lastHostInt)}`);
    set('res-range-sub', 'Point-to-point (RFC 3021)');
  } else {
    set('res-range', `${intToIP(firstHostInt)} – ${intToIP(lastHostInt)}`);
    set('res-range-sub', `${fmt(usableHosts)} alamat tersedia`);
  }

  set('res-hosts',     fmt(usableHosts));
  set('res-hosts-sub', `dari ${fmt(totalAddresses)} total alamat`);

  // ── Populate Detail Table ──
  set('d-mask',    intToIP(maskInt));
  set('d-wildcard',intToIP(wildcardInt));
  set('d-ip-dec',  String(ipInt >>> 0));
  set('d-net',     `${intToIP(networkInt)} /${prefix}`);
  set('d-bcast',   intToIP(broadcastInt));
  set('d-first',   prefix === 32 ? '(host route)' : intToIP(firstHostInt));
  set('d-last',    prefix === 32 ? '(host route)' : intToIP(lastHostInt));
  set('d-usable',  fmt(usableHosts) + ' host');
  set('d-class',   ipClass);
  set('d-type',    netType);

  // ── Binary Representations ──
  set('bin-ip',    intToBin(ipInt));
  set('bin-mask',  intToBin(maskInt));
  set('bin-net',   intToBin(networkInt));
  set('bin-bcast', intToBin(broadcastInt));

  // ── Show results ──
  resultSec.classList.remove('hidden');
  resultSec.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

/** Shorthand setter */
function set(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

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

function handleSubnetCalc() {
  calculate();
}

function handleVlsmCalc() {
  // To be connected to POST /api/vlsm
}

// ── Keyboard shortcut: Enter to calculate ────
document.addEventListener('keydown', e => {
  if (e.key === 'Enter') calculate();
});

// ── Auto-format: jump to next octet on dot ───
document.getElementById('ip').addEventListener('input', function () {
  this.classList.remove('invalid');
});
document.getElementById('prefix').addEventListener('input', function () {
  document.querySelector('.prefix-input-wrap').classList.remove('invalid');
});

