"""Channel identity and URL canonicalisation, used for deduplication.

Two separate problems are solved here.

Streams: the same endpoint is written several ways across sources, differing only in
scheme, host case, a default port, a trailing slash or a cache busting query parameter.
`canonical_url` reduces those to one key so a channel does not appear three times.

Channels: iptv-org ids are the primary identity and are trusted whenever present. Some
playlist entries carry no id at all, and a few sources use different ids for the same
service. `channel_key` produces a normalised name key that groups those together, after
stripping the words that carry no distinguishing information (TV, network, channel, HD)
and folding Persian spelling variants that differ only in Unicode form.
"""
import re
import unicodedata
import urllib.parse

# Query parameters that identify a session or a cache buster rather than the stream.
VOLATILE_PARAMS = {
    "token", "t", "ts", "timestamp", "expires", "expire", "exp", "sig", "signature",
    "hash", "key", "session", "sessionid", "sid", "cb", "_", "rand", "random", "nocache",
    "isp", "city", "utm_source", "utm_medium", "utm_campaign",
}

# Words that appear inside channel names without distinguishing one channel from another.
# Country and language words are deliberately absent: "Iran Press" and "Press TV" are
# different channels, and dropping "Iran" collapses them into the same key.
NOISE_WORDS = {
    "tv", "television", "channel", "shabakeh", "shabake", "shabakey",
    "hd", "fhd", "sd", "uhd", "4k", "1080p", "720p", "576i", "480i", "live",
    "the", "official",
}

# Persian and Arabic letter forms that vary between sources but read identically.
ARABIC_FOLD = str.maketrans({
    "ك": "ک", "ي": "ی", "ى": "ی", "ﻯ": "ی", "ﻱ": "ی",
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ة": "ه",
    "ؤ": "و", "ئ": "ی", "\u200c": " ", "\u200f": "", "\u200e": "",
    "ۀ": "ه", "ﻻ": "لا",
})
PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
DIACRITICS = re.compile(r"[\u064B-\u0652\u0670\u0640]")


def canonical_url(url):
    """A stable key for one stream endpoint, ignoring cosmetic and volatile differences."""
    try:
        parts = urllib.parse.urlsplit(url.strip())
    except ValueError:
        return url.strip().lower()

    host = (parts.hostname or "").lower().removeprefix("www.")
    if parts.port and not ((parts.scheme == "http" and parts.port == 80)
                           or (parts.scheme == "https" and parts.port == 443)):
        host = f"{host}:{parts.port}"

    path = re.sub(r"/{2,}", "/", parts.path).rstrip("/") or "/"

    kept = [(k, v) for k, v in urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
            if k.lower() not in VOLATILE_PARAMS]
    query = urllib.parse.urlencode(sorted(kept))

    # http and https to the same host and path are the same stream for dedup purposes.
    return urllib.parse.urlunsplit(("", host, path, query, ""))


def fold_persian(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(ARABIC_FOLD).translate(PERSIAN_DIGITS)
    return DIACRITICS.sub("", text)


def normalise_name(name):
    """Reduce a channel name to comparable tokens."""
    if not name:
        return ""
    text = fold_persian(name).lower()
    text = re.sub(r"[\u0600-\u06FF]", lambda m: m.group(0), text)
    text = re.sub(r"[^\w\u0600-\u06FF]+", " ", text)
    tokens = [t for t in text.split() if t and t not in NOISE_WORDS]
    return " ".join(tokens)


def channel_key(channel_id, name, country):
    """Grouping key for a channel. The iptv-org id wins whenever one exists."""
    if channel_id:
        return f"id:{channel_id}"
    normalised = normalise_name(name)
    if not normalised:
        return None
    return f"name:{country or '??'}:{normalised}"


def dedupe_streams(streams):
    """Collapse streams that point at the same endpoint, keeping the first of each."""
    seen, out = set(), []
    for stream in streams:
        key = canonical_url(stream["url"])
        if key in seen:
            continue
        seen.add(key)
        out.append(stream)
    return out
