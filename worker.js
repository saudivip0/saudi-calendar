const RAW_BASE = "https://raw.githubusercontent.com/saudivip0/saudi-calendar/main";

const ROUTES = new Map([
  ["/", ["index.html", "text/html; charset=utf-8"]],
  ["/index.html", ["index.html", "text/html; charset=utf-8"]],
  ["/events.json", ["events.json", "application/json; charset=utf-8"]],
  ["/saudi-calendar.ics", ["saudi-calendar.ics", "text/calendar; charset=utf-8"]],
  ["/calendar.ics", ["saudi-calendar.ics", "text/calendar; charset=utf-8"]],
  ["/salaries.ics", ["salaries.ics", "text/calendar; charset=utf-8"]],
  ["/education.ics", ["education.ics", "text/calendar; charset=utf-8"]],
  ["/islamic.ics", ["islamic.ics", "text/calendar; charset=utf-8"]],
  ["/national.ics", ["national.ics", "text/calendar; charset=utf-8"]],
  ["/seasons.ics", ["seasons.ics", "text/calendar; charset=utf-8"]],
]);

function securityHeaders(type) {
  const h = {
    "Content-Type": type,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Access-Control-Allow-Origin": "*",
  };
  if (type.startsWith("text/html")) {
    h["Content-Security-Policy"] =
      "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'";
  }
  return h;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);

    if (url.pathname === "/health") {
      return Response.json({
        ok: true,
        service: "saudi-calendar",
        version: "3.0.0",
        checkedAt: new Date().toISOString(),
      }, { headers: { "Cache-Control": "no-store" } });
    }

    const route = ROUTES.get(url.pathname);
    if (!route) {
      return new Response("Not found", {
        status: 404,
        headers: securityHeaders("text/plain; charset=utf-8"),
      });
    }

    const [file, type] = route;
    const upstream = await fetch(`${RAW_BASE}/${file}`, {
      cf: { cacheTtl: type.startsWith("text/calendar") ? 300 : 120, cacheEverything: true },
    });

    if (!upstream.ok) {
      return new Response("The requested resource is temporarily unavailable.", {
        status: 502,
        headers: securityHeaders("text/plain; charset=utf-8"),
      });
    }

    let body = await upstream.text();
    if (type.startsWith("text/html")) {
      body = body.replaceAll(
        "https://saudi-calendar.saudivip0o.workers.dev",
        url.origin
      );
    }

    const headers = securityHeaders(type);
    headers["Cache-Control"] = type.startsWith("text/calendar")
      ? "public, max-age=300, stale-while-revalidate=3600"
      : "public, max-age=120, stale-while-revalidate=600";

    if (type.startsWith("text/calendar")) {
      headers["Content-Disposition"] = `inline; filename="${file.split("/").pop()}"`;
    }

    return new Response(body, { status: 200, headers });
  },
};
