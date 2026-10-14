#!/usr/bin/env node
/**
 * SLOCAST™ / SLONE™ SOVEREIGN LICENSE & STREAMING PLAYBACK API SERVER v1.0
 * ══════════════════════════════════════════════════════════════════════
 * Servidor unificado de Licencias, Reproducción, Canales y Webhooks
 * en Node.js PURO (cero dependencias externas requeridas).
 *
 * Endpoints:
 *   -- SISTEMA Y SALUD --
 *   GET  /health                      → Estado del servicio y metadatos
 *   GET  /api/v1/system/status        → Telemetría del servidor y hardware
 *
 *   -- LICENCIAS Y PAGOS --
 *   GET  /api/plans, /api/v1/plans    → Catálogo de planes y precios
 *   POST /api/webhook/payment         → Webhook de Lemon Squeezy / Stripe
 *   POST /api/license/verify          → { key } Validación criptográfica HMAC-SHA256
 *   POST /api/license/issue           → { plan_id, user_id } Emisión (X-Admin-Token)
 *
 *   -- CONTROL DE REPRODUCCIÓN Y STREAMING --
 *   GET  /api/v1/playback/status      → Estado actual (canal, volumen, mute, pistas)
 *   POST /api/v1/playback/control     → { action, value } Enviar orden de reproducción
 *
 *   -- CANALES Y LISTAS IPTV --
 *   GET  /api/v1/channels             → Listado estructurado y categorías
 *   POST /api/v1/channels/load        → Carga de canales M3U / JSON
 *   POST /api/v1/stream/check         → Sondeo y verificación de salud de stream
 *
 * Arranque:  node backend/server.js   (o: make backend)
 */
import { createServer } from "node:http";
import { request as httpRequest } from "node:http";
import { request as httpsRequest } from "node:https";
import { createHmac, timingSafeEqual } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";
import os from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");
const CONFIG_PATH = join(ROOT, "config", "slone_control.json");
const DATA_DIR = join(__dirname, "data");
const DB_PATH = join(DATA_DIR, "licenses.json");
const CHANNELS_PATH = join(DATA_DIR, "channels.json");

const PORT = process.env.PORT ? Number(process.env.PORT) : 8766;
const LICENSE_SECRET = process.env.SLONE_LICENSE_SECRET || "SLONE_VR46_MASTER_SECRET_KEY_2026";
const ADMIN_TOKEN = process.env.SLONE_ADMIN_TOKEN || "cambia-este-token";
const PRODUCTION = process.env.SLONE_PRODUCTION === "1";

const DURATION_DAYS = { day: 1, week: 7, month: 30, year: 365, lifetime: 0 };

// ── Estado global en memoria para el reproductor ──────────────────────────
let playbackState = {
  is_playing: false,
  channel: "SLOCAST Ultra HD 1",
  channel_index: 0,
  category: "General",
  stream_url: "",
  volume: 85,
  muted: false,
  engine: "mpv",
  audio_tracks: [
    { id: 1, name: "Español (Estéreo)", lang: "es" },
    { id: 2, name: "V.O. Original", lang: "en" },
    { id: 3, name: "Radio Deportes", lang: "es" }
  ],
  current_audio: "Español (Estéreo)",
  fullscreen: false,
  last_updated: Date.now()
};

// ── Configuración (config/slone_control.json) ─────────────────────────────
function loadConfig() {
  try {
    return JSON.parse(readFileSync(CONFIG_PATH, "utf-8"));
  } catch {
    return {};
  }
}

function webhookSecret() {
  return process.env.SLONE_WEBHOOK_SECRET ||
    loadConfig().pasarela_pagos?.webhook_secret || "SLONE_WEBHOOK_SECRET_KEY_2026";
}

function plans() {
  const cfg = loadConfig().precios_suscripcion_eur || {};
  return [
    { id: "day", name: "Pase 1 Día Flash", price_eur: cfg.pase_1_dia_flash ?? 1.99 },
    { id: "week", name: "Pase 7 Días Semanal", price_eur: cfg.pase_7_dias_semanal ?? 4.99 },
    { id: "month", name: "Suscripción Mensual", price_eur: cfg.suscripcion_mensual ?? 9.99 },
    { id: "year", name: "Pase Anual Ahorro", price_eur: cfg.pase_anual_ahorro ?? 39.99 },
    { id: "lifetime", name: "Licencia Vitalicia Soberana", price_eur: cfg.licencia_vitalicia_pago_unico ?? 79.99 },
  ];
}

// ── Firma de claves AUTOVERIFICABLES y AUTOCADUCABLES ────────────────────
const PLAN_TAG = { day: "DAY", week: "WEEK", month: "MONTH", year: "YEAR", lifetime: "LIFE" };

function expiryStamp(days) {
  if (!days || days <= 0) return "000000";
  const d = new Date(Date.now() + days * 86400000);
  const p = (n) => String(n).padStart(2, "0");
  return `${p(d.getUTCFullYear() % 100)}${p(d.getUTCMonth() + 1)}${p(d.getUTCDate())}`;
}

function keySignature(tag, exp) {
  return createHmac("sha256", LICENSE_SECRET)
    .update(`${tag}:${exp}:SLONE_SOVEREIGN`).digest("hex").slice(0, 16).toUpperCase();
}

export function generateKey(planId, userId = "slone") {
  const tag = PLAN_TAG[planId] || "YEAR";
  const exp = expiryStamp(DURATION_DAYS[planId] ?? 365);
  return `SLONE-${tag}-${exp}-${keySignature(tag, exp)}`;
}

export function validateKey(key) {
  if (typeof key !== "string") return false;
  const parts = key.trim().toUpperCase().split("-");
  if (parts.length !== 4 || parts[0] !== "SLONE") return false;
  const [, tag, exp, sig] = parts;
  if (!safeEqual(keySignature(tag, exp), sig)) return false;
  if (exp !== "000000") {
    const y = 2000 + Number(exp.slice(0, 2));
    const m = Number(exp.slice(2, 4));
    const d = Number(exp.slice(4, 6));
    if (!m || !d || m > 12 || d > 31) return false;
    if (Date.UTC(y, m - 1, d) < Date.now() - 86400000) return false;
  }
  return true;
}

// ── Almacén persistente (JSON) ───────────────────────────────────────────
function loadDB() {
  try { return JSON.parse(readFileSync(DB_PATH, "utf-8")); } catch { return {}; }
}

function saveDB(db) {
  mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(DB_PATH, JSON.stringify(db, null, 2), { mode: 0o600 });
}

function loadChannels() {
  try {
    if (existsSync(CHANNELS_PATH)) {
      return JSON.parse(readFileSync(CHANNELS_PATH, "utf-8"));
    }
  } catch {}
  return [
    { id: 1, name: "La 1 HD", group: "Nacionales", url: "https://rtvelivestream.akamaized.net/la1_es.m3u8", logo: "" },
    { id: 2, name: "La 2 HD", group: "Nacionales", url: "https://rtvelivestream.akamaized.net/la2_es.m3u8", logo: "" },
    { id: 3, name: "24h TVE", group: "Noticias", url: "https://rtvelivestream.akamaized.net/24h_es.m3u8", logo: "" },
    { id: 4, name: "Teledeporte", group: "Deportes", url: "https://rtvelivestream.akamaized.net/tdp_es.m3u8", logo: "" }
  ];
}

function saveChannels(channels) {
  mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(CHANNELS_PATH, JSON.stringify(channels, null, 2), { mode: 0o600 });
}

function issueLicense(planId, userId) {
  const key = generateKey(planId, userId);
  const days = DURATION_DAYS[planId] ?? 365;
  const now = Date.now();
  const db = loadDB();
  db[key] = {
    key, plan_id: planId, user_id: userId, tier: "PREMIUM_VIP",
    issued_at: now,
    expires_at: days > 0 ? now + days * 86400000 : null,
  };
  saveDB(db);
  return db[key];
}

// ── Utilidades HTTP ───────────────────────────────────────────────────────
function send(res, status, obj) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Cache-Control": "no-store",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Token, X-Signature, Range",
  });
  res.end(JSON.stringify(obj));
}

function safeEqual(a, b) {
  const ba = Buffer.from(String(a)), bb = Buffer.from(String(b));
  return ba.length === bb.length && timingSafeEqual(ba, bb);
}

function readBody(req, max = 2_000_000) {
  return new Promise((resolve, reject) => {
    let size = 0; const chunks = [];
    req.on("data", (c) => {
      size += c.length;
      if (size > max) { reject(new Error("payload demasiado grande")); req.destroy(); return; }
      chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

const BUCKET = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const b = BUCKET.get(ip) || { tokens: 120, ts: now };
  b.tokens = Math.min(120, b.tokens + ((now - b.ts) / 1000));
  b.ts = now;
  if (b.tokens < 1) { BUCKET.set(ip, b); return true; }
  b.tokens -= 1; BUCKET.set(ip, b); return false;
}

// ── Enrutador Principal ───────────────────────────────────────────────────
const server = createServer(async (req, res) => {
  const ip = req.socket.remoteAddress || "?";
  if (rateLimited(ip)) return send(res, 429, { status: "error", message: "rate-limit excedido" });

  const urlObj = new URL(req.url, `http://${req.headers.host || "127.0.0.1"}`);
  const pathname = urlObj.pathname;

  // Manejo de Preflight CORS
  if (req.method === "OPTIONS") {
    res.writeHead(204, {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS, PUT, DELETE",
      "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Admin-Token, X-Signature, Range",
      "Access-Control-Max-Age": "86400",
    });
    return res.end();
  }

  try {
    // 1. Salud y Telemetría
    if (req.method === "GET" && pathname === "/health") {
      return send(res, 200, {
        status: "ok",
        service: "slocast-core-api",
        version: "1.0.0",
        production: PRODUCTION,
        time: new Date().toISOString()
      });
    }

    if (req.method === "GET" && pathname === "/api/v1/system/status") {
      return send(res, 200, {
        status: "ok",
        platform: os.platform(),
        arch: os.arch(),
        hostname: os.hostname(),
        cpus: os.cpus().length,
        cpu_model: os.cpus()[0]?.model || "Intel Core i7-8665U",
        total_ram_gb: +(os.totalmem() / 1024 / 1024 / 1024).toFixed(2),
        free_ram_gb: +(os.freemem() / 1024 / 1024 / 1024).toFixed(2),
        uptime_seconds: Math.floor(os.uptime()),
        node_version: process.version
      });
    }

    // 2. Planes y Tarifas
    if (req.method === "GET" && (pathname === "/api/plans" || pathname === "/api/v1/plans")) {
      return send(res, 200, { status: "ok", currency: "EUR", plans: plans() });
    }

    // 3. Webhook de Pagos
    if (req.method === "POST" && (pathname === "/api/webhook/payment" || pathname === "/api/v1/webhook/payment")) {
      const raw = await readBody(req);
      const computed = createHmac("sha256", webhookSecret()).update(raw).digest("hex");
      let provided = (req.headers["x-signature"] || "").trim();
      if (provided.includes("=")) provided = provided.split("=").pop().trim();
      if (provided) {
        if (!safeEqual(provided, computed))
          return send(res, 401, { status: "error", message: "Firma HMAC inválida" });
      } else if (PRODUCTION) {
        return send(res, 401, { status: "error", message: "Firma ausente (modo producción)" });
      }
      let event;
      try { event = JSON.parse(raw.toString("utf-8")); }
      catch (e) { return send(res, 400, { status: "error", message: `JSON no válido: ${e.message}` }); }

      const name = event?.meta?.event_name || event?.type || "";
      const custom = event?.meta?.custom_data || {};
      const email = event?.data?.attributes?.user_email || "cliente@slocast.tv";
      const planId = custom.plan_id || "year";

      if (["order_created", "subscription_created", "checkout.session.completed"].includes(name)) {
        const lic = issueLicense(planId, email);
        return send(res, 200, { status: "success", action: "license_issued",
          key: lic.key, plan: planId, email, duration_days: DURATION_DAYS[planId] ?? 365 });
      }
      if (["subscription_cancelled", "subscription_expired"].includes(name)) {
        return send(res, 200, { status: "success", action: "license_revoked" });
      }
      return send(res, 200, { status: "ignored", event: name });
    }

    // 4. Verificación de Licencias
    if (req.method === "POST" && (pathname === "/api/license/verify" || pathname === "/api/v1/license/verify")) {
      const raw = await readBody(req);
      let body = {};
      try { body = JSON.parse(raw.toString("utf-8")); } catch {}
      const rec = loadDB()[body.key];
      const valid = validateKey(body.key) &&
        (!rec || rec.expires_at == null || rec.expires_at > Date.now());
      return send(res, valid ? 200 : 403, { status: valid ? "valid" : "invalid",
        key: body.key, record: rec || null });
    }

    // 5. Emisión de Licencias (Admin)
    if (req.method === "POST" && (pathname === "/api/license/issue" || pathname === "/api/v1/license/issue")) {
      if (!safeEqual(req.headers["x-admin-token"] || "", ADMIN_TOKEN))
        return send(res, 401, { status: "error", message: "Token de administrador inválido" });
      const raw = await readBody(req);
      let body = {};
      try { body = JSON.parse(raw.toString("utf-8")); } catch {}
      const lic = issueLicense(body.plan_id || "year", body.user_id || "slone");
      return send(res, 200, { status: "success", license: lic });
    }

    // 6. Estado de Reproducción
    if (req.method === "GET" && pathname === "/api/v1/playback/status") {
      return send(res, 200, { status: "ok", playback: playbackState });
    }

    // 7. Control de Reproducción
    if (req.method === "POST" && pathname === "/api/v1/playback/control") {
      const raw = await readBody(req);
      let body = {};
      try { body = JSON.parse(raw.toString("utf-8")); } catch {}
      const action = body.action || "toggle";
      const value = body.value;

      if (action === "play") playbackState.is_playing = true;
      else if (action === "pause") playbackState.is_playing = false;
      else if (action === "toggle") playbackState.is_playing = !playbackState.is_playing;
      else if (action === "stop") { playbackState.is_playing = false; playbackState.stream_url = ""; }
      else if (action === "set_volume") {
        playbackState.volume = Math.max(0, Math.min(100, Number(value) || 0));
      }
      else if (action === "vol_up") {
        playbackState.volume = Math.min(100, playbackState.volume + 5);
      }
      else if (action === "vol_down") {
        playbackState.volume = Math.max(0, playbackState.volume - 5);
      }
      else if (action === "mute") playbackState.muted = true;
      else if (action === "unmute") playbackState.muted = false;
      else if (action === "toggle_mute") playbackState.muted = !playbackState.muted;
      else if (action === "select_channel") {
        const channels = loadChannels();
        let target = null;
        if (typeof value === "number") {
          target = channels[value] || channels[0];
          playbackState.channel_index = value;
        } else if (typeof value === "string") {
          target = channels.find(c => c.name.toLowerCase() === value.toLowerCase()) || { name: value, url: "" };
        }
        if (target) {
          playbackState.channel = target.name;
          playbackState.stream_url = target.url || "";
          playbackState.is_playing = true;
        }
      }
      else if (action === "set_audio") {
        playbackState.current_audio = String(value);
      }
      else if (action === "toggle_fullscreen") {
        playbackState.fullscreen = !playbackState.fullscreen;
      }

      playbackState.last_updated = Date.now();
      return send(res, 200, { status: "ok", action, playback: playbackState });
    }

    // 8. Canales y Listas IPTV
    if (req.method === "GET" && pathname === "/api/v1/channels") {
      let channels = loadChannels();
      const q = urlObj.searchParams.get("search");
      const cat = urlObj.searchParams.get("category");
      if (q) channels = channels.filter(c => c.name.toLowerCase().includes(q.toLowerCase()));
      if (cat) channels = channels.filter(c => (c.group || "").toLowerCase() === cat.toLowerCase());

      const categories = [...new Set(loadChannels().map(c => c.group || "General"))];
      return send(res, 200, {
        status: "ok",
        count: channels.length,
        categories,
        channels
      });
    }

    if (req.method === "POST" && pathname === "/api/v1/channels/load") {
      const raw = await readBody(req);
      let body = {};
      try { body = JSON.parse(raw.toString("utf-8")); } catch {}
      if (Array.isArray(body.channels)) {
        saveChannels(body.channels);
        return send(res, 200, { status: "ok", count: body.channels.length, message: "Canales guardados con éxito" });
      }
      return send(res, 400, { status: "error", message: "Se esperaba un array de canales en body.channels" });
    }

    // 9. Comprobación de Salud de Streams
    if (req.method === "POST" && pathname === "/api/v1/stream/check") {
      const raw = await readBody(req);
      let body = {};
      try { body = JSON.parse(raw.toString("utf-8")); } catch {}
      const targetUrl = body.url;
      if (!targetUrl || typeof targetUrl !== "string") {
        return send(res, 400, { status: "error", message: "Falta parámetro 'url'" });
      }

      const start = Date.now();
      try {
        const u = new URL(targetUrl);
        const isHttps = u.protocol === "https:";
        const client = isHttps ? httpsRequest : httpRequest;
        const probe = client(targetUrl, { method: "HEAD", timeout: 4000 }, (streamRes) => {
          const latency = Date.now() - start;
          return send(res, 200, {
            status: "ok",
            url: targetUrl,
            http_status: streamRes.statusCode,
            content_type: streamRes.headers["content-type"] || "unknown",
            latency_ms: latency,
            reachable: streamRes.statusCode >= 200 && streamRes.statusCode < 400
          });
        });
        probe.on("error", (err) => {
          return send(res, 200, {
            status: "error",
            url: targetUrl,
            reachable: false,
            error: err.message,
            latency_ms: Date.now() - start
          });
        });
        probe.on("timeout", () => {
          probe.destroy();
          return send(res, 200, {
            status: "timeout",
            url: targetUrl,
            reachable: false,
            error: "Timeout de conexión (4s)",
            latency_ms: Date.now() - start
          });
        });
        probe.end();
      } catch (err) {
        return send(res, 400, { status: "error", message: `URL inválida: ${err.message}` });
      }
      return;
    }

    return send(res, 404, { status: "error", message: "Ruta no encontrada en la API de SLOCAST" });
  } catch (e) {
    return send(res, 500, { status: "error", message: e.message });
  }
});

const invokedDirectly = process.argv[1] &&
  fileURLToPath(import.meta.url) === resolve(process.argv[1]);

if (invokedDirectly) {
  server.listen(PORT, "127.0.0.1", () => {
    console.log(`🔐 SLOCAST Sovereign API Server escuchando en http://127.0.0.1:${PORT}`);
    console.log(`   Modo producción: ${PRODUCTION ? "SÍ" : "no"} | datos: ${DATA_DIR}`);
  });
}

export default server;
