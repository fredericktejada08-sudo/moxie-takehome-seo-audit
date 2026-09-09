import json, os, sys, time, urllib.error, urllib.parse, urllib.request

API_BASE = "https://api.ahrefs.com/v3"
ENV_PATH = "/home/fredericktejada/TMC/Ahrefs API/.env"

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env

def api_get(path, params, token):
    url = f"{API_BASE}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        sys.stderr.write(f"[{e.code}] {path} {params.get('target','')}: {body}\n")
        return None

env = load_env(ENV_PATH)
token = env.get("AHREFS_API_TOKEN", "")
if not token:
    print("AHREFS_API_TOKEN is empty")
    sys.exit(1)

domains = ["musemedspaaustin.com", "refineaesthetics.com", "www.vivadayspa.com", "beauxmedspa.com"]
results = {}
for d in domains:
    out = {}
    dr = api_get("/site-explorer/domain-rating", {"target": d, "date": (__import__("datetime").date.today() - __import__("datetime").timedelta(days=1)).isoformat(), "protocol": "both"}, token)
    time.sleep(1.1)
    if dr and "domain_rating" in dr:
        out["dr"] = dr["domain_rating"].get("domain_rating")
        out["ahrefs_rank"] = dr["domain_rating"].get("ahrefs_rank")
    m = api_get("/site-explorer/metrics", {"target": d, "date": (__import__("datetime").date.today() - __import__("datetime").timedelta(days=1)).isoformat(), "country": "us", "mode": "subdomains", "protocol": "both", "volume_mode": "monthly"}, token)
    time.sleep(1.1)
    if m and "metrics" in m:
        out["org_traffic"] = m["metrics"].get("org_traffic")
        out["org_keywords"] = m["metrics"].get("org_keywords")
        out["org_cost"] = m["metrics"].get("org_cost")
    results[d] = out
    print(d, json.dumps(out))

with open("ahrefs_results.json", "w") as f:
    json.dump(results, f, indent=2)
