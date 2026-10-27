#!/usr/bin/env python3
"""Fetch every mikvah.org detail page listed in base.json and extract its info rows.
Polite: one request at a time, 0.5 s apart, identifying user agent. Resumable: skips ids already in details/.
"""
import json, os, re, sys, time, html, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = "Mozilla/5.0 (Macintosh) MikvahApp-personal/1.0 (personal mikvah calendar; contact work@tsuriel.co)"
base = json.load(open(os.path.join(HERE, "base.json")))
out_dir = os.path.join(HERE, "details"); os.makedirs(out_dir, exist_ok=True)

row_re = re.compile(r'<p class="mikvah-info-row__label">(.*?)</p>\s*<p class="mikvah-info-row__value">(.*?)</p>', re.S)
addr_re = re.compile(r'<p class="mikvah-info-row__label">Address</p>(.*?)</div>', re.S)

def clean(t):
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    return re.sub(r"[ \t]+", " ", t).strip()

def parse(page):
    info = {}
    for label, value in row_re.findall(page):
        info[clean(label)] = clean(value)
    m = addr_re.search(page)
    if m:
        info["AddressBlock"] = [l.strip() for l in clean(m.group(1)).split("\n") if l.strip()]
    links = re.findall(r'href="(mailto:[^"]+)"', page)
    if links: info["Email"] = links[0][7:]
    site = re.findall(r'class="mikvah-info-row__value"[^>]*>\s*<a href="(https?://[^"]+)"', page)
    if site: info["Website"] = site[0]
    return info

done = 0; failed = []
for i, m in enumerate(base):
    path = os.path.join(out_dir, f"{m['id']}.json")
    if os.path.exists(path): continue
    url = "https://mikvah.org" + m["url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
        json.dump(parse(page), open(path, "w"), indent=1)
        done += 1
    except Exception as e:
        failed.append((m["id"], str(e)))
        print("FAIL", m["id"], e, flush=True)
    if (i + 1) % 50 == 0: print(f"{i+1}/{len(base)}", flush=True)
    time.sleep(0.5)
print(f"fetched {done}, failed {len(failed)}")
json.dump(failed, open(os.path.join(HERE, "failed.json"), "w"))
