"""Category definitions and the rules that assign them.

Categories are split on two observable facts about a channel: who operates it and how it
is distributed, then its subject matter. Both come from the iptv-org database or from the
explicit lists in data/curated.json. No category encodes a judgement about a channel's
content, ownership or audience.

Classification is deterministic and runs in a fixed order, so the same input always
produces the same category:

  1. `category_overrides` in data/curated.json, an explicit id to category mapping.
  2. The named lists under `sets` in data/curated.json, checked in this order:
     irib_provincial, irib_international, religious_christian, religious_other,
     irib_national.
  3. `religious` in the channel's iptv-org categories.
  4. The first iptv-org category that appears in GENRE_MAP.
  5. FALLBACK.
"""

CATEGORIES = [
    ("irib-national", "IRIB National Networks", "شبکه‌های سراسری سیما",
     "Channels operated by IRIB and distributed nationally."),
    ("irib-provincial", "IRIB Provincial Networks", "شبکه‌های استانی",
     "IRIB channels assigned to a specific province or city."),
    ("irib-international", "IRIB International Services", "شبکه‌های برون‌مرزی",
     "IRIB channels produced for audiences outside Iran, in Persian and other languages."),
    ("sat-general", "Satellite · General", "ماهواره‌ای · عمومی",
     "Persian language channels with mixed programming, distributed by satellite."),
    ("sat-entertainment", "Satellite · Entertainment", "ماهواره‌ای · سرگرمی",
     "Variety, talk, comedy, lifestyle and reality programming."),
    ("sat-movies", "Satellite · Movies & Series", "ماهواره‌ای · فیلم و سریال",
     "Film and drama channels, including dubbed foreign titles."),
    ("sat-news", "Satellite · News", "ماهواره‌ای · خبری",
     "Persian language news channels."),
    ("sat-music", "Satellite · Music", "ماهواره‌ای · موسیقی",
     "Music video and concert channels."),
    ("sat-kids", "Satellite · Kids", "ماهواره‌ای · کودک",
     "Programming for children, including animation."),
    ("sat-sports", "Satellite · Sports", "ماهواره‌ای · ورزشی",
     "Sport and fitness channels."),
    ("sat-documentary", "Satellite · Documentary & Learning", "ماهواره‌ای · مستند و آموزش",
     "Documentary, science, medical and educational channels."),
    ("religious-islamic", "Religious · Islamic", "مذهبی · اسلامی",
     "Islamic religious channels, registered in Iran, Iraq and elsewhere."),
    ("religious-christian", "Religious · Christian", "مذهبی · مسیحی",
     "Persian language Christian channels."),
    ("religious-other", "Religious · Other Faiths & Spiritual", "مذهبی · سایر ادیان و معنوی",
     "Channels of other faiths, and spiritual or philosophical programming."),
]

LABELS = {cid: {"en": en, "fa": fa, "about": about} for cid, en, fa, about in CATEGORIES}
ORDER = {cid: i for i, (cid, *_) in enumerate(CATEGORIES)}
FALLBACK = "sat-general"

SET_RULES = [
    ("irib_provincial", "irib-provincial"),
    ("irib_international", "irib-international"),
    ("religious_christian", "religious-christian"),
    ("religious_other", "religious-other"),
    ("irib_national", "irib-national"),
]

# iptv-org genre tags mapped onto the satellite second level.
GENRE_MAP = {
    "news": "sat-news", "weather": "sat-news", "business": "sat-news", "politics": "sat-news",
    "movies": "sat-movies", "series": "sat-movies", "classic": "sat-movies",
    "music": "sat-music",
    "kids": "sat-kids", "animation": "sat-kids", "family": "sat-kids",
    "sports": "sat-sports", "outdoor": "sat-sports",
    "documentary": "sat-documentary", "education": "sat-documentary",
    "science": "sat-documentary", "travel": "sat-documentary", "history": "sat-documentary",
    "entertainment": "sat-entertainment", "comedy": "sat-entertainment",
    "lifestyle": "sat-entertainment", "cooking": "sat-entertainment",
    "culture": "sat-entertainment", "shop": "sat-entertainment",
    "general": "sat-general",
}


def classify(channel_id, db_categories, curated):
    """Return the category id for a channel, following the documented rule order."""
    override = curated.get("category_overrides", {}).get(channel_id)
    if override:
        return override

    sets = curated.get("sets", {})
    for set_name, category in SET_RULES:
        if channel_id in sets.get(set_name, []):
            return category

    if "religious" in db_categories:
        return "religious-islamic"
    for genre in db_categories:
        if genre in GENRE_MAP:
            return GENRE_MAP[genre]
    return FALLBACK


def quality_tag(height):
    """Standard resolution label, or an empty string when the height is unknown."""
    if not height:
        return ""
    if height >= 2160:
        return "4K"
    if height >= 1080:
        return "FHD"
    if height >= 720:
        return "HD"
    return "SD"


def tags(channel):
    """Factual, machine readable labels describing operator, distribution and quality."""
    out = []
    category = channel["category"]
    if category.startswith("irib-"):
        out += ["irib", category.split("-", 1)[1]]
    elif category.startswith("sat-"):
        out += ["satellite", category.split("-", 1)[1]]
    elif category.startswith("religious-"):
        out += ["religious", category.split("-", 1)[1]]
    out.append({"iran-only": "iran-only", "failing": "failing"}.get(channel["reach"], "worldwide"))
    tag = quality_tag(channel.get("height"))
    if tag:
        out.append(tag.lower())
    out += sorted(channel.get("languages") or [])
    if len(channel.get("streams", [])) > 1:
        out.append("has-backup")
    return out
