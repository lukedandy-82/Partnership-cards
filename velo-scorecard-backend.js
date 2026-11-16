// Wix Velo: paste into backend/http-functions.js (create the file if it does not exist).
// Endpoint once published: https://www.gctechallies.com/_functions/analyze?url=example.com
// Reads a company's public website and returns partnership-readiness signals. No API key needed.
// NOT yet tested inside Wix: test in the Velo editor with the "Test" panel before connecting scorecard.html.

import { ok, badRequest, response } from 'wix-http-functions';
import { fetch } from 'wix-fetch';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Content-Type': 'application/json'
};

export function options_analyze() { return response({ status: 204, headers: CORS }); }

export async function get_analyze(request) {
  const host = cleanHost(request.query.url);
  if (!host) return badRequest({ headers: CORS, body: JSON.stringify({ error: 'invalid_url' }) });

  const base = 'https://' + host;
  const home = await grab(base + '/');
  if (!home.ok) return ok({ headers: CORS, body: JSON.stringify({ read: false, reason: 'site_unreachable' }) });

  const html = home.text.slice(0, 400000);
  const lower = html.toLowerCase();
  const links = (lower.match(/<a [^>]*>[^<]{0,80}<\/a>/g) || []).join(' ');

  // Probe common paths in parallel (status only)
  const probe = async (paths) => {
    const res = await Promise.all(paths.map((p) => grab(base + p, true)));
    return res.some((r) => r.ok);
  };
  const [partnerPath, integrationsPath, devPath, customersPath] = await Promise.all([
    probe(['/partners', '/partnerships', '/partner-program', '/become-a-partner']),
    probe(['/integrations', '/apps', '/marketplace', '/ecosystem']),
    probe(['/developers', '/developer', '/docs', '/api']),
    probe(['/customers', '/case-studies', '/success-stories'])
  ]);

  const has = (re) => re.test(links) || re.test(lower.slice(0, 120000));
  const signals = {
    partnerProgram: partnerPath || /(become a partner|partner program|partners?<)/.test(links),
    integrations: integrationsPath || /(integrations|marketplace|ecosystem)/.test(links),
    developerDocs: devPath || /(api|developers|documentation)/.test(links),
    customerProof: customersPath || /(customers|case stud|success stor)/.test(links),
    pricing: /pricing/.test(links),
    trust: /(gdpr|soc ?2|iso ?27001|iso 27001)/.test(lower),
    europe: /(hreflang="(de|fr|es|it|nl|pt|pl|sv|da|fi)[-"])|\beurope(an)?\b|\bgdpr\b|\beu\b/.test(lower),
    multiLanguage: (lower.match(/hreflang=/g) || []).length >= 2
  };

  // Weights sum to 100
  const W = { partnerProgram: 24, integrations: 18, developerDocs: 14, customerProof: 14, trust: 10, europe: 8, multiLanguage: 6, pricing: 6 };
  let score = 0;
  Object.keys(W).forEach((k) => { if (signals[k]) score += W[k]; });

  const title = ((html.match(/<title[^>]*>([^<]{0,160})/i) || [])[1] || '').trim();
  return ok({ headers: CORS, body: JSON.stringify({ read: true, host, title, signals, score }) });
}

// ---- helpers ----
function cleanHost(input) {
  const raw = String(input || '').trim().toLowerCase().replace(/^https?:\/\//, '').replace(/^www\./, '').split(/[\/?#]/)[0];
  if (!/^[a-z0-9-]+(\.[a-z0-9-]+)+$/.test(raw)) return '';      // hostname only: no ports, credentials, IPs with brackets
  if (/^\d+(\.\d+){3}$/.test(raw)) return '';                   // no raw IPv4 (blocks internal addresses)
  if (/(^|\.)(local|localhost|internal|lan|corp)$/.test(raw)) return '';
  return raw;
}

async function grab(url, statusOnly) {
  try {
    const r = await Promise.race([
      fetch(url, { method: 'GET', headers: { 'User-Agent': 'GcTechAlliesScorecard/1.0 (+https://www.gctechallies.com)' } }),
      new Promise((_, rej) => setTimeout(() => rej(new Error('timeout')), 6000))
    ]);
    if (!r.ok) return { ok: false };
    return { ok: true, text: statusOnly ? '' : await r.text() };
  } catch (e) { return { ok: false }; }
}
