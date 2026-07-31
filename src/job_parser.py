"""Best-effort extraction of role and location from an HN job title.

The HN API only exposes a free-text `title` for job items (no structured
fields), so role/location have to be inferred from the usual phrasings:

    Company (YC W23) Is Hiring a Head of Engineering
    Company (YC W25) Is Hiring Full Stack Engineers (SF)
    Company (YC P26) Is Hiring in Austin, TX
    Company (YC S22) - Senior Software Engineer - Remote (US) - Full-Time

Anything that cannot be recognised comes back as None.
"""

import re

# "Company Name (YC S24)" prefix, including the two-word "Stealth startup" cases.
_COMPANY_PREFIX = re.compile(r"^.*?\(\s*YC\s+[A-Z]{0,2}\s*\d{2,4}\s*\)\s*", re.IGNORECASE)

# Segment separators: en/em dash, pipe, or a spaced hyphen (never intra-word).
_SEGMENT_SPLIT = re.compile(r"\s+[–—|]\s+|\s+-\s+")

_HIRING = re.compile(r"\b(?:is\s+|are\s+|we(?:'re|\s+are)\s+|now\s+)?hiring\b", re.IGNORECASE)
_LEADING_FILLER = re.compile(r"^(?:an?|the|our|its|their|for|to\s+join\s+as|as)\b\s*", re.IGNORECASE)
# Purpose/relative clauses tacked onto the role ("... to build the MCP cloud").
_TRAILING_CLAUSE = re.compile(r"\s+(?:to|who|that|so|and\s+help)\s+[a-z].*$")
_TRAILING_PAREN = re.compile(r"\s*\(([^()]*)\)\s*$")
_TRAILING_IN = re.compile(r"\bin\s+((?:[A-Z][\w.'’-]*)(?:[\s,]+(?:[A-Z][\w.'’-]*|[a-z]{2,3}))*)\s*$")
_REMOTE = re.compile(r"\b(?:fully\s+)?remote\b", re.IGNORECASE)

_ROLE_WORDS = re.compile(
    r"\b(engineer|engineering|developer|dev|designer|scientist|researcher|manager|lead|head|"
    r"director|founding|founder|chief|officer|president|vp|analyst|architect|intern|"
    r"marketer|recruiter|sales|success|support|ops|operations|counsel|writer|hires?|team|"
    r"staff|people|ae|sdr|fde|pm|cto|ceo|cfo|coo)\b",
    re.IGNORECASE,
)

# Places seen often enough in HN job titles to be worth recognising by name.
_PLACES = {
    "remote", "hybrid", "onsite", "on-site", "in-person", "anywhere", "worldwide", "global",
    "bay area", "sf bay area", "silicon valley", "san francisco", "sf", "south bay",
    "palo alto", "mountain view", "menlo park", "san mateo", "sunnyvale", "san jose",
    "oakland", "berkeley", "new york", "new york city", "nyc", "brooklyn", "manhattan",
    "los angeles", "la", "san diego", "seattle", "portland", "austin", "dallas", "houston",
    "denver", "boulder", "chicago", "boston", "cambridge", "miami", "atlanta", "detroit",
    "philadelphia", "washington", "dc", "pittsburgh", "phoenix", "nashville", "salt lake city",
    "toronto", "vancouver", "montreal", "waterloo", "mexico city", "sao paulo", "são paulo",
    "buenos aires", "bogota", "bogotá", "santiago", "lima",
    "london", "dublin", "edinburgh", "manchester", "berlin", "munich", "hamburg", "paris",
    "amsterdam", "rotterdam", "brussels", "zurich", "geneva", "vienna", "madrid", "barcelona",
    "lisbon", "porto", "milan", "rome", "athens", "stockholm", "copenhagen", "oslo", "helsinki",
    "warsaw", "krakow", "prague", "budapest", "bucharest", "istanbul", "tallinn", "vilnius",
    "tel aviv", "jerusalem", "dubai", "abu dhabi", "riyadh", "cairo", "lagos", "nairobi",
    "cape town", "johannesburg", "accra",
    "bangalore", "bengaluru", "mumbai", "delhi", "new delhi", "hyderabad", "pune", "chennai",
    "gurgaon", "singapore", "hong kong", "tokyo", "osaka", "seoul", "shanghai", "beijing",
    "shenzhen", "taipei", "jakarta", "manila", "bangkok", "ho chi minh city", "sydney",
    "melbourne", "brisbane", "auckland", "wellington",
    "usa", "us", "u.s.", "u.s.a.", "united states", "canada", "uk", "u.k.", "united kingdom",
    "eu", "europe", "emea", "apac", "latam", "north america", "south america", "asia",
    "africa", "australia", "new zealand", "india", "japan", "china", "korea", "brazil",
    "mexico", "argentina", "colombia", "chile", "germany", "france", "spain", "italy",
    "portugal", "netherlands", "belgium", "switzerland", "austria", "poland", "sweden",
    "norway", "denmark", "finland", "ireland", "israel", "uae", "nigeria", "kenya",
    "south africa", "singapore",
}

_PLACE_SPLIT = re.compile(r"\s*(?:/|,|\bor\b|\band\b|\+)\s*", re.IGNORECASE)

# Words that decorate a place without being one ("CA/US remote OK", "SF based").
_PLACE_QUALIFIERS = {
    "ok", "okay", "only", "preferred", "pref", "based", "friendly", "welcome", "eligible",
    "optional", "area", "region", "timezone", "timezones", "tz", "hq", "office", "offices",
    "first", "ish",
}


def parse_job_details(title):
    """Return (role, location) parsed from a job title; either may be None."""
    body = _COMPANY_PREFIX.sub("", title or "", count=1).strip()
    if not body:
        body = (title or "").strip()

    locations = []
    role_parts = []
    for segment in _SEGMENT_SPLIT.split(body):
        segment = segment.strip(" ,;–—-")
        if not segment:
            continue
        remainder, location = _pop_location(segment)
        if location:
            locations.append(location)
        if remainder:
            role_parts.append(remainder)

    role = _extract_role(role_parts)
    if not locations:
        role, remote = _pop_remote(role)
        if remote:
            locations.append(remote)

    return role, _join_unique(locations)


def _pop_location(segment):
    """Split a trailing/standalone location off a segment: (remainder, location)."""
    if _looks_like_location(segment):
        return "", _tidy(segment)

    match = _TRAILING_PAREN.search(segment)
    if match and _looks_like_location(match.group(1)):
        head = segment[: match.start()].strip(" ,;")
        location = _tidy(match.group(1))
        # "... - Remote (US)" -> keep both halves together.
        tail_match = _TRAILING_IN.search(head) or None
        if tail_match is None and _looks_like_location(head.split()[-1] if head.split() else ""):
            words = head.split()
            location = f"{words[-1]} ({location})"
            head = " ".join(words[:-1]).strip(" ,;")
        return head, location

    match = _TRAILING_IN.search(segment)
    if match and not _ROLE_WORDS.search(match.group(1)):
        return segment[: match.start()].strip(" ,;"), _tidy(match.group(1))

    return segment, None


def _pop_remote(role):
    """Pull an inline 'remote' qualifier out of a role ('remote AEs' -> 'AEs')."""
    if not role or not _REMOTE.search(role):
        return role, None
    cleaned = _tidy(_REMOTE.sub(" ", role))
    return (cleaned or None), "Remote"


def _extract_role(segments):
    candidates = []
    for segment in segments:
        match = _HIRING.search(segment)
        candidate = segment[match.end():] if match else segment
        candidate = _clean_role(candidate)
        if candidate:
            candidates.append(candidate)

    if not candidates:
        return None
    for candidate in candidates:
        if _ROLE_WORDS.search(candidate):
            return candidate
    return candidates[0]


def _clean_role(text):
    # Unwrap "(Head of Security)" without eating the tail of "developers (CA/US OK)".
    text = re.sub(r"^\(([^()]*)\)$", r"\1", _tidy(text))
    while True:  # "for our GTM team" -> "GTM team"
        stripped = _LEADING_FILLER.sub("", text).strip()
        if stripped == text:
            break
        text = stripped
    text = _TRAILING_CLAUSE.sub("", text)
    text = _tidy(text).strip(" ,;.:!–—-")
    if len(text) < 2:
        return None
    return text


def _looks_like_location(text):
    text = _tidy(text or "").strip(" .,").replace("(", " ").replace(")", " ")
    if not text or len(text) > 40 or _ROLE_WORDS.search(text):
        return False
    parts = [part.strip() for part in _PLACE_SPLIT.split(text) if part.strip()]
    return bool(parts) and all(_is_place(part) for part in parts)


def _is_place(token):
    token = token.strip()
    if not token:
        return False
    if token.lower() in _PLACES:
        return True
    # State/country/region abbreviations: TX, CA, NY, USA, EMEA...
    if re.fullmatch(r"[A-Z]{2,4}", token):
        return True
    words = token.split()
    kept = [word for word in words if word.lower() not in _PLACE_QUALIFIERS]
    if len(kept) < len(words):  # dropped a qualifier ("CA/US remote OK"), retry
        return bool(kept) and all(_is_place(word) for word in kept)
    # Multi-word phrases made only of places: "US remote", "Berlin onsite".
    return len(words) > 1 and all(_is_place(word) for word in words)


def _join_unique(values):
    seen = []
    for value in values:
        if value and value.lower() not in {item.lower() for item in seen}:
            seen.append(value)
    return " / ".join(seen) or None


def _tidy(text):
    return re.sub(r"\s+", " ", (text or "")).strip()
