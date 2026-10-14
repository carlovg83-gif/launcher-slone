// Pruebas completas del servidor de API SLOCAST — ejecutar con: node --test backend/
import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createHmac } from "node:crypto";
import server, { generateKey, validateKey } from "./server.js";

const TEST_PORT = 8999;
const baseUrl = `http://127.0.0.1:${TEST_PORT}`;

before(async () => {
  await new Promise((res) => server.listen(TEST_PORT, "127.0.0.1", res));
});

after(async () => {
  await new Promise((res) => server.close(res));
});

// ── 1. Pruebas Criptográficas del Núcleo de Licencias ──────────────────────
test("generateKey produce claves auto-verificables SLONE-<PLAN>-<FECHA>-<FIRMA>", () => {
  assert.match(generateKey("year"), /^SLONE-YEAR-\d{6}-[0-9A-F]{16}$/);
  assert.match(generateKey("day"), /^SLONE-DAY-\d{6}-[0-9A-F]{16}$/);
  assert.match(generateKey("month"), /^SLONE-MONTH-\d{6}-[0-9A-F]{16}$/);
});

test("la licencia vitalicia no caduca (000000) y es válida", () => {
  assert.match(generateKey("lifetime"), /^SLONE-LIFE-000000-[0-9A-F]{16}$/);
  assert.equal(validateKey(generateKey("lifetime")), true);
});

test("una clave recién generada es válida", () => {
  assert.equal(validateKey(generateKey("year")), true);
  assert.equal(validateKey(generateKey("week")), true);
});

test("SE RECHAZAN claves falsificadas (formato válido, firma inválida)", () => {
  assert.equal(validateKey("SLONE-AAAA-BBBB-CCCC"), false);
  assert.equal(validateKey("SLONE-YEAR-991231-DEADBEEFDEADBEEF"), false);
  assert.equal(validateKey("SLONE-LIFE-000000-0000000000000000"), false);
  assert.equal(validateKey("BASURA"), false);
  assert.equal(validateKey(""), false);
  assert.equal(validateKey(null), false);
});

test("la firma coincide con HMAC-SHA256(secreto, 'PLAN:FECHA:SLONE_SOVEREIGN')", () => {
  const [, tag, exp, sig] = generateKey("year").split("-");
  const expected = createHmac("sha256", "SLONE_VR46_MASTER_SECRET_KEY_2026")
    .update(`${tag}:${exp}:SLONE_SOVEREIGN`).digest("hex").slice(0, 16).toUpperCase();
  assert.equal(sig, expected);
});

// ── 2. Pruebas de la API HTTP REST ─────────────────────────────────────────
test("GET /health devuelve 200 y metadatos del servicio", async () => {
  const res = await fetch(`${baseUrl}/health`);
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.status, "ok");
  assert.equal(data.service, "slocast-core-api");
});

test("GET /api/v1/system/status devuelve telemetría de hardware y del SO", async () => {
  const res = await fetch(`${baseUrl}/api/v1/system/status`);
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.status, "ok");
  assert.ok(data.cpus > 0);
  assert.ok(data.total_ram_gb > 0);
});

test("GET /api/v1/plans devuelve catálogo de planes y precios en EUR", async () => {
  const res = await fetch(`${baseUrl}/api/v1/plans`);
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.status, "ok");
  assert.equal(data.currency, "EUR");
  assert.ok(Array.isArray(data.plans));
  assert.ok(data.plans.length >= 5);
});

test("GET y POST /api/v1/playback/status y control gestionan el reproductor", async () => {
  // 1. Obtener estado inicial
  const stRes = await fetch(`${baseUrl}/api/v1/playback/status`);
  assert.equal(stRes.status, 200);
  const stData = await stRes.json();
  assert.equal(stData.status, "ok");
  assert.ok("playback" in stData);

  // 2. Modificar volumen por API
  const volRes = await fetch(`${baseUrl}/api/v1/playback/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "set_volume", value: 92 })
  });
  assert.equal(volRes.status, 200);
  const volData = await volRes.json();
  assert.equal(volData.playback.volume, 92);

  // 3. Activar reproducción
  const playRes = await fetch(`${baseUrl}/api/v1/playback/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "play" })
  });
  const playData = await playRes.json();
  assert.equal(playData.playback.is_playing, true);
});

test("GET /api/v1/channels devuelve lista de canales y categorías", async () => {
  const res = await fetch(`${baseUrl}/api/v1/channels`);
  assert.equal(res.status, 200);
  const data = await res.json();
  assert.equal(data.status, "ok");
  assert.ok(data.count > 0);
  assert.ok(Array.isArray(data.channels));
  assert.ok(Array.isArray(data.categories));
});

test("OPTIONS responde 204 con cabeceras CORS permisivas", async () => {
  const res = await fetch(`${baseUrl}/api/v1/playback/status`, { method: "OPTIONS" });
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("access-control-allow-origin"), "*");
  assert.ok(res.headers.get("access-control-allow-methods").includes("POST"));
});

test("POST /api/v1/license/verify valida correctamente claves válidas e inválidas", async () => {
  const validKey = generateKey("year");
  const resValid = await fetch(`${baseUrl}/api/v1/license/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key: validKey })
  });
  assert.equal(resValid.status, 200);

  const resInvalid = await fetch(`${baseUrl}/api/v1/license/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key: "SLONE-FALSA-000000-XXXXXXXX" })
  });
  assert.equal(resInvalid.status, 403);
});
