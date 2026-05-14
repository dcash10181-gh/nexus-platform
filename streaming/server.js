/**
 * NEXUS Streaming Proxy — Node.js HLS passthrough + adaptive bitrate
 *
 * Responsibilities:
 * - Proxy HLS manifest and segment requests from CDN/origin to client
 * - Inject NEXUS session token into playlist requests (DRM hook)
 * - Emit real-time watch telemetry back to the recommendation API
 * - Rate-limit per user session
 */

const http = require('http');
const https = require('https');
const url = require('url');

const PORT     = process.env.PORT    || 8001;
const API_URL  = process.env.API_URL || 'http://api:8000';

const server = http.createServer((req, res) => {
  const parsed = url.parse(req.url, true);

  // ── Health check ─────────────────────────────────────────────────
  if (parsed.pathname === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok', ts: Date.now() }));
  }

  // ── CORS ──────────────────────────────────────────────────────────
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Authorization, X-Nexus-Session');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    return res.end();
  }

  // ── HLS proxy ─────────────────────────────────────────────────────
  // /stream/:content_id → proxy to origin CDN
  const streamMatch = parsed.pathname.match(/^\/stream\/([^/]+)(\/.*)?$/);
  if (streamMatch) {
    const contentId = streamMatch[1];
    const subPath   = streamMatch[2] || '/master.m3u8';

    // In production: resolve CDN URL from content catalog
    // For demo: return a 302 to a public test stream
    const publicDemoStream = 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8';

    // Emit telemetry to recommendation API (fire and forget)
    const userId = req.headers['x-nexus-session'] || 'anonymous';
    emitTelemetry(API_URL, userId, contentId, 'stream_start');

    res.writeHead(302, { Location: publicDemoStream });
    return res.end();
  }

  // ── Telemetry receiver ────────────────────────────────────────────
  // POST /telemetry — client sends watch progress events
  if (parsed.pathname === '/telemetry' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const event = JSON.parse(body);
        // Forward to recommendation API for real-time preference updates
        const opts = {
          method:   'POST',
          hostname: new URL(API_URL).hostname,
          port:     new URL(API_URL).port || 80,
          path:     '/v1/users/watch-event',
          headers:  { 'Content-Type': 'application/json' },
        };
        const apiReq = http.request(opts);
        apiReq.on('error', () => {}); // silent
        apiReq.end(JSON.stringify({
          user_id:          event.userId,
          content_id:       event.contentId,
          watch_percentage: event.percentage || 0,
          completed:        event.completed  || false,
        }));
      } catch {}
      res.writeHead(204);
      res.end();
    });
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

function emitTelemetry(apiUrl, userId, contentId, event) {
  try {
    const body = JSON.stringify({ user_id: userId, content_id: contentId, event });
    const u = new URL(`${apiUrl}/v1/users/watch-event`);
    const mod = u.protocol === 'https:' ? https : http;
    const req = mod.request({ method: 'POST', hostname: u.hostname, port: u.port || 80, path: u.pathname,
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) } });
    req.on('error', () => {});
    req.end(body);
  } catch {}
}

server.listen(PORT, () => {
  console.log(`NEXUS Streaming Proxy listening on :${PORT}`);
  console.log(`  → Forwarding telemetry to ${API_URL}`);
});
