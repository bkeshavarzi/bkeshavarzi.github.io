"""Refresh data.json with the latest market news using the Anthropic API + web search."""
import json, os, re, datetime, anthropic

d = json.load(open("data.json"))
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
prompt = f"""Refresh this learning-focused market news site for Behrooz, a software engineer new to finance.
Current time (Eastern): {now:%a, %b %d · %I:%M %p} ET. Use web search for the latest US market news (free sources: CNBC, MarketWatch, Reuters, Federal Reserve, SEC EDGAR, Yahoo Finance).
Return ONLY the complete new data.json as JSON, same schema as the current one below.
Rules: simple English; spell out abbreviations; 5-8 stories, new ones section "today", still-useful older ones section "earlier", drop anything older than 5 days;
every story needs news, history, says, impact, terms, optional chart, and at least one real source URL you actually saw in search results (never invent URLs);
only use numbers you found; price/changePct null when unknown; no investment advice; confidence Confirmed/Likely/Unexplained;
every story needs an "added" field (e.g. "Oct 27, 5:55 p.m. ET", the time you add it; keep the old value for kept stories) and an "updated" field when you change it; set updatedAt (ISO) and updatedLabel like "Tue, Oct 27 · 12:25 p.m. ET"; keep quotes for every ticker in keyStocks.
CURRENT data.json:
{json.dumps(d)}"""
c = anthropic.Anthropic()
r = c.messages.create(model=os.environ.get("MODEL", "claude-sonnet-5-5"), max_tokens=32000,
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}],
    messages=[{"role": "user", "content": prompt}])
text = "".join(b.text for b in r.content if b.type == "text")
m = re.search(r"\{.*\}", text, re.S)
new = json.loads(m.group(0))
assert new["stories"] and all(s.get("sources") for s in new["stories"]), "story without source"
json.dump(new, open("data.json", "w"), indent=2, ensure_ascii=False)
