#!/usr/bin/env python3
"""Merge base.json (map array) with details/<id>.json into the app's mikvaos.json.
Keeps women's mikvaos only: drops entries whose name says keilim / men's / vessels.
"""
import json, os, re, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "mikvaos.json")
base = json.load(open(os.path.join(HERE, "base.json")))

drop_re = re.compile(r"\bkeilim\b|\bkelim\b|\bmen'?s\b|\bmens\b|\bvessel|\butensil|\bdishes\b|\bmikvah tahara for men\b", re.I)

def norm_country(c, state):
    if c in ("", None, "USA", "United States", "US"): return "United States"
    if c == "England": return "United Kingdom"
    return c

out = []
dropped = []
for m in base:
    name = (m.get("name") or "").strip()
    if drop_re.search(name):
        dropped.append(name); continue
    d = {}
    p = os.path.join(HERE, "details", f"{m['id']}.json")
    if os.path.exists(p): d = json.load(open(p))
    addr_lines = d.get("AddressBlock") or [l for l in [m.get("addr")] if l]
    # The block ends with city/state/zip and country lines; keep street lines only.
    city = (m.get("city") or "").strip(); zipc = (m.get("zip") or "").strip(); raw_country = (m.get("country") or "").strip()
    countries = {c.lower() for c in (raw_country, norm_country(raw_country, m.get("state")), "usa", "united states", "us", "england") if c}
    def is_street(l):
        if not l or l.lower() in countries: return False
        if zipc and zipc in l: return False
        if city and l.lower().startswith(city.lower()): return False
        if re.search(r"\d{5}|,\s*[A-Z]{2}\b", l): return False
        return True
    street = [l for l in addr_lines if is_street(l)] or addr_lines[:1]
    schedule = d.get("Schedule") or ""
    entry = {
        "id": m["id"],
        "name": name,
        "lat": round(float(m["lat"]), 6),
        "lng": round(float(m["lng"]), 6),
        "street": street,
        "city": (m.get("city") or "").strip(),
        "state": (m.get("state") or "").strip(),
        "zip": (m.get("zip") or "").strip(),
        "country": norm_country((m.get("country") or "").strip(), m.get("state")),
        "phone": (d.get("Phone") or m.get("phone") or "").strip() or None,
        "contact": d.get("Contact") or None,
        "schedule": schedule or None,
        "byAppointment": bool(re.search(r"appointment", schedule, re.I)),
        "shul": d.get("Shul") or None,
        "supervision": d.get("Supervision") or None,
        "type": d.get("Type") or m.get("type") or None,
        "accessible": (d.get("Handicap Access") or "").strip().lower() == "yes" or bool(m.get("acc")),
        "email": d.get("Email") or None,
        "website": d.get("Website") or None,
        "url": "https://mikvah.org" + m["url"],
    }
    out.append({k: v for k, v in entry.items() if v not in (None, "", [])})

out.sort(key=lambda e: (e["country"], e.get("state", ""), e["city"], e["name"]))
doc = {
    "source": "mikvah.org directory",
    "sourceURL": "https://mikvah.org/directory",
    "fetched": datetime.date.today().isoformat(),
    "count": len(out),
    "mikvaos": out,
}
json.dump(doc, open(out_path, "w"), ensure_ascii=False, separators=(",", ":"))
print(f"wrote {len(out)} mikvaos to {out_path} ({os.path.getsize(out_path)//1024} KB); dropped {len(dropped)}: {dropped}")
