from __future__ import annotations

import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from typing import Dict, List, Any

# OmegaTruth research layer
# Generic by design: no claim-specific answers or hard-coded topics.

RSS_URL = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
DDG_URL = "https://html.duckduckgo.com/html/?q={query}"
DDG_LITE_URL = "https://lite.duckduckgo.com/lite/?q={query}"
WIKI_API = "https://en.wikipedia.org/w/api.php"
PUBMED_API = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

_STOPWORDS = {
    "the","a","an","is","are","was","were","be","been","being","do","does","did",
    "can","could","should","would","will","may","might","must","has","have","had",
    "to","of","in","on","for","with","and","or","but","that","this","these","those",
    "it","its","as","by","from","than","into","about","after","before","between",
    "whether","how","why","what","which","who","whom","their","they","them","there",
    "here","true","false","claim","according","accordingto","stated","proposition",
    "not","necessarily"
}

_SUPPORT_CUES = (
    "study found","studies found","research found","trial found","randomized trial",
    "clinical trial","systematic review","meta-analysis","evidence suggests",
    "evidence shows","evidence supports","supports the claim","associated with",
    "improves","improved","improvement","benefit","benefits","demonstrates",
    "demonstrated","shows that","showed that","found that","consistent with",
    "significantly improved","significant improvement","increased","reduces",
    "reduced","decreased","is composed","consists of","made up of","contains",
    "chemical formula"
)

_COUNTER_CUES = (
    "no evidence","lack of evidence","insufficient evidence","not supported",
    "unsupported","does not improve","doesn't improve","did not improve",
    "didn't improve","no significant improvement","no significant difference",
    "no significant effect","failed to improve","failed to show","not associated",
    "not linked","not effective","ineffective","ineffectiveness","contradicts",
    "contradict","refutes","refuted","disproves","disproved","debunked","debunk",
    "false","not true","incorrect","misleading","cannot","could not",
    "was not","were not","has not","have not","does not","do not","is not","are not"
)

_AUTHORITY_HINTS = (
    ".gov", ".edu", ".ac.", "nih", "pubmed", "who.int", "nature.com",
    "sciencedirect", "springer", "cochrane", "bmj", "reuters", "apnews",
    "britannica", "mayoclinic", "harvard", "stanford", "ox.ac"
)

def _tokens(text: str) -> List[str]:
    return [
        w for w in re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
        if len(w) > 2 and w not in _STOPWORDS
    ]

def _clean(value: str) -> str:
    value = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", value).strip()

def _request(url: str, timeout: int = 5) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 OmegaTruth/1.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read()

def _google_news(query: str, limit: int = 8) -> List[Dict[str, str]]:
    try:
        url = RSS_URL.format(query=urllib.parse.quote_plus(query))
        root = ET.fromstring(_request(url, timeout=5))
    except Exception:
        return []

    out = []
    for item in root.findall(".//item")[:limit]:
        title = _clean(item.findtext("title") or "")
        url = _clean(item.findtext("link") or "")
        pub = _clean(item.findtext("pubDate") or "")
        source_el = item.find("source")
        source = _clean(source_el.text if source_el is not None else "Google News")
        snippet = _clean(item.findtext("description") or "")
        if title:
            out.append({
                "title": title,
                "source": source or "Google News",
                "url": url,
                "published": pub,
                "snippet": snippet[:1200],
                "search_channel": "Google News",
            })
    return out

class _SearchParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.items = []
        self.current = None
        self.capture = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = a.get("class", "")
        if "result__a" in classes or "result-link" in classes:
            if self.current and self.current.get("title"):
                self.items.append(self.current)
            self.current = {
                "title": "",
                "source": "DuckDuckGo",
                "url": a.get("href", ""),
                "published": "",
                "snippet": "",
            }
            self.capture = "title"
        elif self.current and (
            "result__snippet" in classes or "result-snippet" in classes
        ):
            self.capture = "snippet"

    def handle_data(self, data):
        if self.current and self.capture:
            self.current[self.capture] += data

    def handle_endtag(self, tag):
        if self.current and self.capture == "title" and tag == "a":
            self.capture = None
        elif self.current and self.capture == "snippet" and tag in ("a", "div", "td"):
            self.capture = None

    def close(self):
        super().close()
        if self.current and self.current.get("title"):
            self.items.append(self.current)
            self.current = None

def _parse_ddg(raw: bytes) -> List[Dict[str, str]]:
    parser = _SearchParser()
    try:
        parser.feed(raw.decode("utf-8", errors="ignore"))
        parser.close()
    except Exception:
        return []

    out, seen = [], set()
    for x in parser.items:
        title = _clean(x.get("title", ""))
        url = html.unescape(x.get("url", ""))
        snippet = _clean(x.get("snippet", ""))
        key = (title.lower(), url.lower())
        if title and key not in seen:
            seen.add(key)
            out.append({
                "title": title,
                "source": "DuckDuckGo",
                "url": url,
                "published": "",
                "snippet": snippet[:1200],
                "search_channel": "DuckDuckGo",
            })
    return out

def _duckduckgo(query: str, limit: int = 8) -> List[Dict[str, str]]:
    for endpoint in (DDG_URL, DDG_LITE_URL):
        try:
            results = _parse_ddg(
                _request(
                    endpoint.format(query=urllib.parse.quote_plus(query)),
                    timeout=5,
                )
            )
            if results:
                return results[:limit]
        except Exception:
            continue
    return []


def _pubmed(query: str, limit: int = 6) -> List[Dict[str, str]]:
    """Search PubMed for claim-specific scientific literature."""
    try:
        params = {
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(limit),
        }
        data = json.loads(_request(PUBMED_API + "?" + urllib.parse.urlencode(params), timeout=6))
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []

        params2 = {
            "db": "pubmed",
            "id": ",".join(ids),
            "retmode": "json",
        }
        summary = json.loads(_request(PUBMED_SUMMARY + "?" + urllib.parse.urlencode(params2), timeout=6))
        result = summary.get("result", {})
        out = []
        for pmid in ids:
            row = result.get(pmid, {})
            title = _clean(row.get("title", ""))
            if not title:
                continue
            pubdate = _clean(row.get("pubdate", ""))
            journal = _clean(row.get("fulljournalname", "") or row.get("source", ""))
            out.append({
                "title": title,
                "source": f"PubMed — {journal}" if journal else "PubMed",
                "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "published": pubdate,
                "snippet": _clean(row.get("sortfirstauthor", "")) + (" — " if row.get("sortfirstauthor") else "") + "PubMed-indexed research result.",
                "search_channel": "PubMed",
            })
        return out
    except Exception:
        return []

def _wikipedia(query: str, limit: int = 1) -> List[Dict[str, str]]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srlimit": str(limit),
        "format": "json",
        "utf8": "1",
    }
    try:
        data = json.loads(
            _request(
                WIKI_API + "?" + urllib.parse.urlencode(params),
                timeout=5,
            )
        )
    except Exception:
        return []

    rows = data.get("query", {}).get("search", [])
    titles = [r.get("title", "") for r in rows if r.get("title")]
    extracts = {}

    if titles:
        p2 = {
            "action": "query",
            "prop": "extracts",
            "exintro": "1",
            "explaintext": "1",
            "titles": "|".join(titles),
            "format": "json",
            "utf8": "1",
        }
        try:
            data2 = json.loads(
                _request(
                    WIKI_API + "?" + urllib.parse.urlencode(p2),
                    timeout=5,
                )
            )
            for page in data2.get("query", {}).get("pages", {}).values():
                extracts[page.get("title", "")] = page.get("extract", "")
        except Exception:
            pass

    out = []
    for row in rows:
        title = row.get("title", "")
        snippet = _clean(extracts.get(title) or row.get("snippet", ""))
        page = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(
            title.replace(" ", "_")
        )
        out.append({
            "title": title,
            "source": "Wikipedia",
            "url": page,
            "published": "",
            "snippet": snippet[:1400],
            "search_channel": "Wikipedia",
        })
    return out

def _search_one(query: str, limit: int = 8) -> List[Dict[str, str]]:
    # Independent public search channels run concurrently.
    out = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [
            pool.submit(_duckduckgo, query, limit),
            pool.submit(_google_news, query, limit),
            pool.submit(_wikipedia, query, 1),
            pool.submit(_pubmed, query, min(limit, 6)),
        ]
        for future in as_completed(futures):
            try:
                out.extend(future.result())
            except Exception:
                pass
    return out

def search_web(query: str, limit: int = 8) -> List[Dict[str, str]]:
    return _dedupe(_search_one(query, limit), limit)

def _claim_terms(claim: str) -> set[str]:
    return set(_tokens(claim))

def _evidence_text(item: Dict[str, Any]) -> str:
    return " ".join(
        str(item.get(k, "")) for k in ("title", "snippet", "source")
    ).lower()

def _claim_overlap(item: Dict[str, Any], claim: str) -> float:
    terms = _claim_terms(claim)
    if not terms:
        return 0.0
    text_terms = set(_tokens(_evidence_text(item)))
    return len(terms & text_terms) / len(terms)

def _meaningful_overlap(item: Dict[str, Any], claim: str) -> int:
    terms = _claim_terms(claim)
    text_terms = set(_tokens(_evidence_text(item)))
    return len(terms & text_terms)

def _is_authoritative(item: Dict[str, Any]) -> bool:
    source = str(item.get("source", "")).lower()
    url = str(item.get("url", "")).lower()
    return any(h in source or h in url for h in _AUTHORITY_HINTS)

def _passes_evidence_filter(
    item: Dict[str, Any], claim: str, side: str
) -> bool:
    """
    Generic evidence gate.

    It deliberately does NOT require exact wording, because search engines often
    paraphrase scientific findings. It DOES require several claim-specific terms,
    which blocks dictionary/song/general-topic noise.
    """
    overlap = _claim_overlap(item, claim)
    matched = _meaningful_overlap(item, claim)
    text = _evidence_text(item)

    term_count = len(_claim_terms(claim))
    minimum_terms = 2 if term_count <= 6 else 3

    if matched < minimum_terms:
        return False

    if side == "support":
        # A highly relevant result is usable even when the snippet does not contain
        # a literal "supports" phrase. Strong support cues make it easier to pass.
        cues = sum(1 for cue in _SUPPORT_CUES if cue in text)
        return (
            overlap >= 0.40
            or cues > 0
            or (_is_authoritative(item) and overlap >= 0.30)
        )

    if side == "counter":
        # Counter-evidence must have an explicit null/negative/contradictory signal.
        return overlap >= 0.30 and any(cue in text for cue in _COUNTER_CUES)

    return overlap >= 0.40

def _normalise_question(claim: str) -> str:
    q = claim.strip().rstrip("?.!")
    low = q.lower()
    prefixes = (
        "does ", "do ", "is ", "are ", "can ", "could ",
        "should ", "will ", "has ", "have "
    )
    for prefix in prefixes:
        if low.startswith(prefix):
            return q[len(prefix):].strip()
    return q

def _core_phrase(claim: str) -> str:
    # Preserve natural word order instead of using a set, so search engines
    # receive a meaningful phrase.
    terms = _tokens(_normalise_question(claim))
    return " ".join(terms[:10]) if terms else _normalise_question(claim)


def _dedupe(
    results: List[Dict[str, str]],
    limit: int,
    claim: str = "",
    side: str = "",
) -> List[Dict[str, str]]:
    out, seen = [], set()
    for item in results:
        key = (
            item.get("url")
            or item.get("title")
            or ""
        ).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        if claim and side and not _passes_evidence_filter(item, claim, side):
            continue
        out.append(item)
        if len(out) >= limit:
            break
    return out

def _rank(
    results: List[Dict[str, str]],
    claim: str,
    side: str,
    limit: int,
) -> List[Dict[str, str]]:
    scored = []
    seen = set()

    for item in results:
        key = (
            item.get("url")
            or item.get("title")
            or ""
        ).strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)

        if not _passes_evidence_filter(item, claim, side):
            continue

        text = _evidence_text(item)
        overlap = _claim_overlap(item, claim)
        matched = _meaningful_overlap(item, claim)

        if side == "support":
            cues = sum(1 for cue in _SUPPORT_CUES if cue in text)
        else:
            cues = sum(1 for cue in _COUNTER_CUES if cue in text)

        authority = 0.25 if _is_authoritative(item) else 0.0
        source = str(item.get("source", "")).lower()

        # Penalize obvious generic sources unless they have strong claim overlap.
        generic_penalty = 0.0
        if source in {"duckduckgo", "google news", "wikipedia"}:
            generic_penalty = 0.0

        score = (
            overlap * 2.0
            + min(matched, 6) * 0.08
            + min(cues, 5) * 0.10
            + authority
            - generic_penalty
        )
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)

    out = []
    seen_sources = set()

    # Prefer source diversity first.
    for _, item in scored:
        source = str(item.get("source", "")).strip().lower()
        if source in seen_sources and len(out) < limit - 1:
            continue
        out.append(item)
        seen_sources.add(source)
        if len(out) >= limit:
            return out

    # Fill remaining slots.
    for _, item in scored:
        if item not in out:
            out.append(item)
            if len(out) >= limit:
                break

    return out

def _search_queries(claim: str, side: str) -> List[str]:
    original = claim.strip().rstrip("?.!")
    prop = _normalise_question(claim)
    core = _core_phrase(claim)

    if side == "support":
        return [
            f"{prop} study",
            f"{core} study",
            f"{core} systematic review",
            f"{core} meta-analysis",
            f"{core} evidence",
        ]

    return [
        f"{prop} no significant effect",
        f"{core} did not improve",
        f"{core} no evidence",
        f"{core} systematic review mixed evidence",
        f"{core} trial null result",
    ]


def _collect(
    claim: str,
    queries: List[str],
    side: str,
    limit: int,
) -> List[Dict[str, str]]:
    raw = []

    # Five focused queries, each using multiple public search channels.
    with ThreadPoolExecutor(max_workers=min(5, len(queries))) as pool:
        futures = [pool.submit(_search_one, q, 8) for q in queries]
        for future in as_completed(futures):
            try:
                raw.extend(future.result())
            except Exception:
                pass

    return _rank(raw, claim, side, limit)

def research_supporting(
    claim: str, limit: int = 6
) -> List[Dict[str, str]]:
    return _collect(
        claim,
        _search_queries(claim, "support"),
        "support",
        limit,
    )

def research_challenging(
    claim: str, limit: int = 6
) -> List[Dict[str, str]]:
    return _collect(
        claim,
        _search_queries(claim, "counter"),
        "counter",
        limit,
    )

# Compatibility aliases for the earlier project architecture.
research_opposing = research_challenging
research_challenge_sources = research_challenging
research_claim = research_supporting

def evidence_text(results: List[Dict[str, str]]) -> List[str]:
    return [
        f"{x.get('title', 'Untitled')} — {x.get('source', 'Web source')}"
        for x in results
    ]
