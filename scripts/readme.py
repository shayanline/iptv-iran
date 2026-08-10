"""Render the bilingual README from the generated channel list.

The prose here is deliberately descriptive: it states what the code does and what the
probe measured. It does not characterise channels, broadcasters or audiences.
"""
import datetime as dt

import taxonomy

REPO = "shayanline/iptv-iran"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/playlists"

PLAYLIST_FILES = [
    ("iran.m3u", "Every channel, one stream each",
     "همه شبکه‌ها، برای هر شبکه یک استریم"),
    ("iran-global.m3u", "Only channels reachable outside Iran",
     "فقط شبکه‌هایی که از خارج ایران باز می‌شوند"),
    ("iran-domestic.m3u", "Only channels that require an Iranian IP address",
     "فقط شبکه‌هایی که به IP ایران نیاز دارند"),
    ("iran-all-streams.m3u", "Every working stream, backups included",
     "همه استریم‌های سالم، همراه با نسخه‌های پشتیبان"),
]


def fa_digits(value):
    """Persian digits, for numbers that sit inside Persian prose."""
    return str(value).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

def quality(channel, unknown):
    """Resolution measured by the probe, falling back to the database's format string."""
    resolution = str(channel.get("resolution") or "")
    if "x" in resolution:
        height = resolution.split("x")[1]
        if height.isdigit():
            return f"{height}p"
    if channel.get("height"):
        return f'{channel["height"]}p'
    return unknown


def counts(channels):
    total = len(channels)
    globally = sum(1 for c in channels if c["reach"] == "global")
    return total, globally, total - globally


def channel_tables(channels, lang):
    """One table per category, in the taxonomy's own order."""
    out = []
    for cid, en, fa, about in taxonomy.CATEGORIES:
        members = [c for c in channels if c["category"] == cid]
        if not members:
            continue
        provincial = cid == "irib-provincial"
        if lang == "en":
            out.append(f"### {en}\n")
            out.append(f"{about}\n")
            head = ["Channel", "Persian name"] + (["Province"] if provincial else []) \
                + ["Quality", "Reachable from", "Streams"]
            out.append("| " + " | ".join(head) + " |")
            out.append("|" + "|".join([":--"] * len(head)) + "|")
            for c in members:
                row = [c["name_en"], c["name_fa"] or "n/a"]
                if provincial:
                    row.append(c["province_en"] or "n/a")
                row += [quality(c, "n/a"),
                        "Anywhere" if c["reach"] == "global" else "Iran only",
                        str(len(c["streams"]))]
                out.append("| " + " | ".join(row) + " |")
            out.append("")
        else:
            out.append(f"### {fa}\n")
            head = ["نام فارسی", "نام انگلیسی"] + (["استان"] if provincial else []) \
                + ["کیفیت", "قابل دسترس از", "تعداد پخش"]
            out.append("| " + " | ".join(head) + " |")
            out.append("|" + "|".join([":--"] * len(head)) + "|")
            for c in members:
                row = [c["name_fa"] or "نامشخص", c["name_en"]]
                if provincial:
                    row.append(c["province_fa"] or "نامشخص")
                row += [quality(c, "نامشخص"),
                        "همه‌جا" if c["reach"] == "global" else "فقط ایران",
                        str(len(c["streams"]))]
                out.append("| " + " | ".join(row) + " |")
            out.append("")
    return "\n".join(out)


def category_summary(channels, lang):
    rows = []
    if lang == "en":
        rows.append("| Category | Channels | Anywhere | Iran only | Playlist |")
        rows.append("|:--|--:|--:|--:|:--|")
    else:
        rows.append("| دسته | تعداد | همه‌جا | فقط ایران | فهرست |")
        rows.append("|:--|--:|--:|--:|:--|")
    for cid, en, fa, _ in taxonomy.CATEGORIES:
        members = [c for c in channels if c["category"] == cid]
        if not members:
            continue
        anywhere = sum(1 for c in members if c["reach"] == "global")
        link = f"[{cid}]({RAW}/categories/{cid}.m3u)"
        rows.append(f"| {en if lang == 'en' else fa} | {len(members)} | {anywhere} "
                    f"| {len(members) - anywhere} | {link} |")
    total, globally, iran_only = counts(channels)
    label = "**Total**" if lang == "en" else "**مجموع**"
    rows.append(f"| {label} | **{total}** | **{globally}** | **{iran_only}** | |")
    return "\n".join(rows)


def quality_summary(channels, lang):
    buckets = {}
    for channel in channels:
        buckets.setdefault(channel["quality"] or "unknown", []).append(channel)
    order = ["4K", "FHD", "HD", "SD", "unknown"]
    labels_fa = {"4K": "4K", "FHD": "FHD", "HD": "HD", "SD": "کیفیت معمولی",
                 "unknown": "نامشخص"}
    parts = []
    for tag in order:
        if buckets.get(tag):
            if lang == "en":
                parts.append(f"{len(buckets[tag])} {tag}")
            else:
                parts.append(f"{fa_digits(len(buckets[tag]))} {labels_fa[tag]}")
    return "، ".join(parts) if lang == "fa" else ", ".join(parts)


EN_SECTIONS = [
    ("get-the-playlist", "Get the playlist"),
    ("how-streams-are-checked", "How streams are checked"),
    ("how-a-stream-is-chosen", "How a channel's stream is chosen"),
    ("how-channels-are-categorised", "How channels are categorised"),
    ("how-duplicates-are-removed", "How duplicates are removed"),
    ("how-it-stays-current", "How it stays current"),
    ("adding-or-fixing-a-channel", "Adding or fixing a channel"),
    ("sources", "Sources"),
    ("licence", "Licence"),
    ("categories", "Categories"),
    ("channel-list", "Channel list"),
]

FA_SECTIONS = [
    ("fa-download", "دریافت پلی‌لیست"),
    ("fa-checking", "استریم‌ها چطور بررسی می‌شوند"),
    ("fa-choosing", "استریم هر شبکه چطور انتخاب می‌شود"),
    ("fa-categories-how", "شبکه‌ها چطور دسته‌بندی می‌شوند"),
    ("fa-duplicates", "لینک‌های تکراری چطور حذف می‌شوند"),
    ("fa-updates", "چطور به‌روز می‌ماند"),
    ("fa-contributing", "اضافه یا اصلاح کردن یک شبکه"),
    ("fa-sources", "منابع"),
    ("fa-licence", "مجوز"),
    ("fa-categories", "دسته‌ها"),
    ("fa-channels", "فهرست شبکه‌ها"),
]


def toc(sections, bullet="-"):
    return "\n".join(f"{bullet} [{title}](#{anchor})" for anchor, title in sections)


def heading(anchor, title, level=2):
    """A heading with an explicit anchor, so links work for Persian titles too."""
    return f'<a id="{anchor}"></a>\n\n{"#" * level} {title}'


def render(channels):
    total, globally, iran_only = counts(channels)
    today = f"{dt.datetime.now(dt.timezone.utc):%d %B %Y}"
    provincial = sum(1 for c in channels if c["category"] == "irib-provincial")
    streams = sum(len(c["streams"]) for c in channels)
    categories = len({c["category"] for c in channels})
    playlist_rows = "\n".join(f"| [{n}]({RAW}/{n}) | {d} |" for n, d, _ in PLAYLIST_FILES)
    playlist_rows_fa = "\n".join(f"| [{n}]({RAW}/{n}) | {f} |" for n, _, f in PLAYLIST_FILES)

    english = f"""<a id="english"></a>

# IPTV Iran

M3U playlists of Iranian and Persian language television channels, grouped by operator and
distribution first and by subject matter second.

{total} channels across {categories} categories, from {streams} verified streams.
{globally} channels are reachable from anywhere, {iran_only} only from Iranian IP
addresses. Every stream is re-checked automatically every two weeks.

[![Refresh playlists](https://github.com/{REPO}/actions/workflows/refresh.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/refresh.yml)
![Channels](https://img.shields.io/badge/channels-{total}-1f6feb)
![Streams](https://img.shields.io/badge/verified%20streams-{streams}-8250df)
![Last checked](https://img.shields.io/badge/last%20checked-{today.replace(' ', '%20')}-2da44e)

**🇮🇷 [این راهنما به فارسی هم موجود است](#persian)**

## Contents

{toc(EN_SECTIONS)}

{heading("get-the-playlist", "Get the playlist")}

Paste one of these URLs into VLC, IPTV Smarters, TiviMate, Kodi, OTT Navigator, or any
other client that reads M3U. There is nothing to install and no account to create.

```
{RAW}/iran.m3u
{RAW}/iran-global.m3u
{RAW}/iran-domestic.m3u
{RAW}/iran-all-streams.m3u
```

| Playlist | Contents |
|:--|:--|
{playlist_rows}

### Title language

The same four playlists are published in three title styles. Pick the folder that suits
you and keep the file name the same.

| Folder | Titles | Example |
|:--|:--|:--|
| [`playlists/`]({RAW}/iran.m3u) | Bilingual, `English \\| فارسی` | `IRIB TV1 \\| شبکه یک FHD` |
| [`playlists/en/`]({RAW}/en/iran.m3u) | English only | `IRIB TV1 FHD` |
| [`playlists/fa/`]({RAW}/fa/iran.m3u) | Persian only, Persian category names | `شبکه یک FHD` |

Resolution tags (`HD`, `FHD`, `4K`) are appended to the title from the resolution the
probe measured, and `[IR]` marks a channel that needs an Iranian IP address. Current mix:
{quality_summary(channels, "en")}.

An EPG is referenced through `x-tvg-url`, so clients that support it will load a programme
guide without further configuration.

### Logos

Channel logos are mirrored into [`assets/logos/`](assets/logos) and served from this
repository rather than hotlinked. Most upstream logos live on imgur, which geo-blocks
several countries including the United Kingdom and Iran, and does not fail cleanly: it
answers HTTP 200 with an image reading "Content not viewable in your region", so players
render that error card beside the channel name. Serving the images from here means the
playlist looks the same everywhere, from the same origin that already serves the playlist
itself. Once a logo has been captured it is kept even if the original URL later breaks,
and it is removed only when the channel leaves every source.

{heading("how-streams-are-checked", "How streams are checked")}

Streams are verified rather than trusted, because a playlist entry can point at a manifest
that still exists after the video behind it has stopped.

- **The check reads video.** It follows the HLS chain, master playlist to variant playlist
  to a media segment, and passes a stream only when media bytes come back.
- **Failure by location is recorded, not punished.** Some endpoints answer only to Iranian
  IP addresses. A GitHub Actions runner is outside Iran, so those requests time out. Those
  streams are marked `iran_only` and published in `iran-domestic.m3u` instead of being
  deleted. This affects the domestic IRIB CDN, which is why {provincial} provincial
  networks and the national networks are listed here at all.
- **Removal requires repetition.** A stream must fail three consecutive fortnightly runs,
  about six weeks, before it is dropped.
- **Backups are kept.** Extra working streams for a channel stay in
  `iran-all-streams.m3u`, ordered best first.

{heading("how-a-stream-is-chosen", "How a channel's stream is chosen")}

Where several streams exist for one channel, they are scored and the highest is used in the
main playlists. The score uses only measured values:

| Factor | Weight | Why |
|:--|--:|:--|
| Reachable worldwide | 100 | A stream that answers is worth more than a sharper one that does not |
| Uptime across past checks | up to 30 | Ratio of successful checks to total checks, scaled by how many checks exist |
| No custom headers needed | 25 | A stream needing a Referer or User-Agent only plays in clients that read `#EXTVLCOPT` |
| Resolution | up to 24 | Measured from the master playlist, not from a label |
| Adaptive bitrate | 8 | More than one variant lets a client adapt to bandwidth |
| Response time | up to 3 | Breaks ties only, never outweighs a resolution step |
| Malformed manifest | minus 40 | A playlist that breaks the HLS spec stalls strict clients, so a clean equivalent always wins |

Uptime is the heaviest ongoing factor, so the choice improves as history accumulates.

Some providers publish a master playlist that breaks the HLS specification. Telewebion, the
platform behind the IRIB channels, writes `EXT-X-VERSION:6` without its leading `#`. Under
RFC 8216 any line that is not blank and does not start with `#` is a URI, so a strict client
requests that tag text as though it were the stream, receives a 403 and stops after the
first frame. ffmpeg and VLC tolerate it, several set top box clients do not. For those
providers the master is read once to learn which renditions exist and the direct rendition
URL is published instead, which is a clean media playlist. The master is kept in
`iran-all-streams.m3u` as a fallback.

{heading("how-channels-are-categorised", "How channels are categorised")}

Categories describe two observable things: who operates the channel and how it is
distributed, then its subject matter. Assignment is deterministic and always runs in this
order, so the result is reproducible:

1. An explicit `category_overrides` entry in [`data/curated.json`](data/curated.json).
2. Membership of a named list under `sets`, checked in the order `irib_provincial`,
   `irib_international`, `religious_christian`, `religious_other`, `irib_national`.
3. A `religious` tag in the channel's iptv-org categories.
4. The first iptv-org genre tag with a mapping in `scripts/taxonomy.py`.
5. `sat-general`, the fallback.

Each channel also carries machine readable `tags` in
[`data/channels.json`](data/channels.json), covering operator, distribution, resolution,
language and whether a backup stream exists.

{heading("how-duplicates-are-removed", "How duplicates are removed")}

Two kinds of duplicate are handled separately, in `scripts/identity.py`:

- **Streams.** The same endpoint appears across sources with a different scheme, host
  case, default port, trailing slash or session parameter. Each URL is reduced to a
  canonical key, so those collapse into one entry, and `https` is preferred over `http`
  for the same endpoint.
- **Channels.** The iptv-org id is the identity whenever a source supplies one. Entries
  with no id, or with different ids for one service, are grouped by a normalised name key
  that removes non-distinguishing words (`TV`, `channel`, `HD`) and folds Persian spelling
  variants such as `ك`/`ک` and `ي`/`ی`.

{heading("how-it-stays-current", "How it stays current")}

A GitHub Actions workflow runs on the 1st and 15th of each month:

1. **Harvest.** Re-read the iptv-org database and API, the generated iptv-org playlists for
   Iran and Persian, Free-TV's Iran list, and itsyebekhe/nexa. Then expand the provider
   templates in `scripts/discover.py`, which generate candidate URLs for channels the
   public lists do not carry.
2. **Probe.** Check every candidate and merge the result into `data/status.json`, which
   holds a first seen date, a last working date, a consecutive failure count and a running
   uptime ratio per URL.
3. **Rebuild.** Regenerate the playlists, `data/channels.json` and the tables in this
   README, and commit only when something changed.

Hostnames are resolved over DNS-over-HTTPS, so a local filter such as AdGuard Home or
Pi-hole cannot make a working channel look dead. Set `IPTV_DNS=system` to opt out.

{heading("adding-or-fixing-a-channel", "Adding or fixing a channel")}

Names, categories, discovery templates and any stream the public sources lack live in
[`data/curated.json`](data/curated.json), which the refresh never overwrites. Everything
under `playlists/` and the tables below are generated, so please do not edit them by hand.

`data/` holds only three files: `curated.json` as the hand maintained input,
`status.json` as the probe history, and `channels.json` as the published output.
Intermediates are written to `build/`, which is not committed.

- **Wrong category:** add the iptv-org id to the correct list under `sets`, or to
  `category_overrides`.
- **Wrong or missing name:** edit the entry under `channels`.
- **A working stream that is missing:** add it to `streams`, and the next probe verifies it.
- **A channel the database does not list:** describe it under `local_channels`, and add its
  provider slug under `discovery`.

Everything runs on Python 3.11 or newer with no third party packages:

```bash
python scripts/sources.py          # harvest candidates into build/
python scripts/probe.py            # check what is live
python scripts/logos.py            # reuse the committed logos
python scripts/build.py            # regenerate playlists and this README
python scripts/discover.py         # list configured discovery URLs
python scripts/logos.py --mirror   # re-download logos, only needed in CI
```

{heading("sources", "Sources")}

This project curates and verifies. It hosts no video, restreams nothing and contains no
media files. Every URL is a public endpoint published by a broadcaster or already listed in
an open playlist.

- [iptv-org](https://github.com/iptv-org/iptv) and its
  [channel database](https://github.com/iptv-org/database), the origin of most stream URLs,
  logos and channel metadata.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV), whose
  [Iran list](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) records the
  domestic IRIB endpoints.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa), a Persian language playlist
  builder that prompted this project.
- [lashkari20/iptv](https://github.com/lashkari20/iptv), a 2022 snapshot, retained only as
  a set of URLs to test.

Some public players reach otherwise unavailable channels through third party proxies, for
example a Cloudflare Worker that forwards a blocked origin. Those URLs are deliberately not
published here. They would route this project's users through infrastructure someone else
pays for and can withdraw at any time. Only endpoints served by a broadcaster or its own
CDN are included, which is why a few channels carried by other lists are absent.

To request removal of a channel you hold the rights to,
[open an issue](https://github.com/{REPO}/issues).

{heading("licence", "Licence")}

[MIT](LICENSE) for the code and the curated data. The channels belong to their
broadcasters.

{heading("categories", "Categories")}

{category_summary(channels, "en")}

{heading("channel-list", "Channel list")}

{channel_tables(channels, "en")}

---
"""

    persian = f"""<a id="persian"></a>

<div dir="rtl" align="right">

# IPTV ایران

پلی‌لیست‌های M3U از شبکه‌های تلویزیونی ایرانی و فارسی‌زبان، دسته‌بندی‌شده بر اساس اینکه چه
کسی شبکه را اداره می‌کند و چطور پخش می‌شود، و بعد بر اساس موضوع برنامه‌ها.

در مجموع {fa_digits(total)} شبکه در {fa_digits(categories)} دسته، از {fa_digits(streams)}
استریم بررسی‌شده. {fa_digits(globally)} شبکه از هر جای دنیا باز می‌شود و
{fa_digits(iran_only)} شبکه فقط با IP ایران. همه استریم‌ها هر دو هفته یک‌بار به‌صورت
خودکار دوباره بررسی می‌شوند.

**🇬🇧 [English version](#english)**

## فهرست مطالب

{toc(FA_SECTIONS)}

{heading("fa-download", "دریافت پلی‌لیست")}

یکی از لینک‌های زیر را در VLC، IPTV Smarters، TiviMate، Kodi، OTT Navigator یا هر برنامه
دیگری که M3U را پشتیبانی می‌کند وارد کنید. نه چیزی برای نصب لازم است و نه حساب کاربری.

```
{RAW}/iran.m3u
{RAW}/iran-global.m3u
{RAW}/iran-domestic.m3u
{RAW}/iran-all-streams.m3u
```

| پلی‌لیست | محتوا |
|:--|:--|
{playlist_rows_fa}

### زبان عنوان‌ها

همین چهار پلی‌لیست با سه حالت عنوان‌گذاری منتشر می‌شود. هر کدام را که می‌پسندید انتخاب
کنید. نام فایل‌ها در هر سه پوشه یکسان است.

| پوشه | عنوان‌ها | نمونه |
|:--|:--|:--|
| [`playlists/`]({RAW}/iran.m3u) | دوزبانه | `IRIB TV1 \\| شبکه یک FHD` |
| [`playlists/en/`]({RAW}/en/iran.m3u) | فقط انگلیسی | `IRIB TV1 FHD` |
| [`playlists/fa/`]({RAW}/fa/iran.m3u) | فقط فارسی، با نام دسته‌های فارسی | `شبکه یک FHD` |

برچسب کیفیت (`HD`، `FHD`، `4K`) بر اساس رزولوشنی که هنگام بررسی اندازه‌گیری شده به عنوان
اضافه می‌شود، و `[IR]` یعنی آن شبکه فقط با IP ایران باز می‌شود. ترکیب فعلی:
{quality_summary(channels, "fa")}.

آدرس EPG با `x-tvg-url` داخل فایل قرار دارد، پس برنامه‌هایی که از آن پشتیبانی می‌کنند
جدول پخش را بدون تنظیم اضافه نشان می‌دهند.

### لوگوها

لوگوی شبکه‌ها در [`assets/logos/`](assets/logos) داخل همین مخزن نگه داشته می‌شود و از
سایت دیگری لینک نمی‌شود. بیشتر لوگوهای منابع اصلی روی imgur هستند که چند کشور از جمله
بریتانیا و ایران را مسدود کرده، آن هم نه با خطای درست: جواب ۲۰۰ می‌دهد و تصویری می‌فرستد
که رویش نوشته «Content not viewable in your region»، و برنامه همان تصویر خطا را کنار نام
شبکه نشان می‌دهد. با نگه داشتن تصویرها در همین مخزن، پلی‌لیست همه‌جا یک شکل دیده می‌شود و
از همان جایی می‌آید که خود پلی‌لیست از آن گرفته می‌شود. هر لوگو بعد از یک بار ذخیره شدن
باقی می‌ماند، حتی اگر لینک اصلی‌اش بعداً خراب شود، و فقط وقتی پاک می‌شود که آن شبکه از
همه منابع حذف شده باشد.

{heading("fa-checking", "استریم‌ها چطور بررسی می‌شوند")}

به هیچ لینکی اعتماد نمی‌شود و همه بررسی می‌شوند، چون ممکن است فایل مانیفست هنوز سر جایش
باشد ولی ویدیویی پشت آن پخش نشود.

- **ویدیوی واقعی خوانده می‌شود.** بررسی، کل زنجیره HLS را دنبال می‌کند، از پلی‌لیست اصلی
  به پلی‌لیست کیفیت و بعد به یک قطعه ویدیو، و فقط وقتی استریم را سالم می‌شمارد که داده
  ویدیو برگردد.
- **مسدود بودن جغرافیایی به معنای مرده بودن نیست.** بعضی سرورها فقط به IP های ایران جواب
  می‌دهند. چون این بررسی روی سرور GitHub و بیرون از ایران اجرا می‌شود، آن درخواست‌ها
  timeout می‌خورند. این استریم‌ها با برچسب `iran_only` ثبت و در `iran-domestic.m3u`
  منتشر می‌شوند و حذف نمی‌شوند. این موضوع شامل CDN داخلی صداوسیما می‌شود و دلیل اینکه
  {fa_digits(provincial)} شبکه استانی و شبکه‌های سراسری اصلاً در این فهرست هستند همین است.
- **برای حذف شدن، تکرار لازم است.** یک استریم باید در سه بررسی دوهفتگی پشت سر هم ناموفق
  باشد، یعنی حدود شش هفته، تا از فهرست بیرون برود.
- **نسخه پشتیبان نگه داشته می‌شود.** اگر شبکه‌ای چند استریم سالم داشته باشد، بقیه در
  `iran-all-streams.m3u` می‌مانند، از بهترین به پایین.

{heading("fa-choosing", "استریم هر شبکه چطور انتخاب می‌شود")}

وقتی یک شبکه چند استریم دارد، به هر کدام امتیاز داده می‌شود و بهترین در پلی‌لیست‌های اصلی
قرار می‌گیرد. امتیاز فقط بر اساس چیزهایی است که واقعاً اندازه‌گیری شده‌اند:

| عامل | وزن | دلیل |
|:--|--:|:--|
| باز شدن از سراسر دنیا | ۱۰۰ | استریمی که جواب می‌دهد از استریم باکیفیت‌تری که باز نمی‌شود بهتر است |
| سابقه سالم بودن در بررسی‌های قبلی | تا ۳۰ | نسبت بررسی‌های موفق به کل بررسی‌ها، متناسب با تعداد دفعات بررسی |
| نیاز نداشتن به هدر خاص | ۲۵ | استریمی که Referer یا User-Agent می‌خواهد فقط در برنامه‌هایی باز می‌شود که `#EXTVLCOPT` را می‌خوانند |
| رزولوشن | تا ۲۴ | از خود پلی‌لیست اصلی خوانده می‌شود، نه از روی برچسب |
| کیفیت تطبیقی | ۸ | وجود چند کیفیت به برنامه اجازه می‌دهد خودش را با سرعت اینترنت هماهنگ کند |
| زمان پاسخ | تا ۳ | فقط وقتی به کار می‌آید که بقیه عامل‌ها برابر باشند |
| مانیفست خراب | منفی ۴۰ | پلی‌لیستی که استاندارد HLS را رعایت نکند در بعضی برنامه‌ها گیر می‌کند، پس نسخه سالم همیشه اولویت دارد |

سابقه سالم بودن مهم‌ترین عامل در طول زمان است، پس هرچه بررسی‌های بیشتری انجام شود انتخاب
دقیق‌تر می‌شود.

بعضی سرویس‌ها پلی‌لیست اصلی را طوری منتشر می‌کنند که استاندارد HLS را رعایت نمی‌کند.
Telewebion، همان پلتفرمی که شبکه‌های صداوسیما را پخش می‌کند، خط `EXT-X-VERSION:6` را بدون
`#` ابتدای آن می‌نویسد. طبق استاندارد RFC 8216 هر خطی که خالی نباشد و با `#` شروع نشود یک
آدرس به حساب می‌آید، بنابراین برنامه‌هایی که استاندارد را دقیق پیاده کرده‌اند همان متن را
مثل آدرس استریم درخواست می‌کنند، جواب 403 می‌گیرند و بعد از اولین فریم متوقف می‌شوند.
ffmpeg و VLC این ایراد را نادیده می‌گیرند ولی خیلی از باکس‌ها و اپلیکیشن‌های تلویزیون نه.
برای این سرویس‌ها پلی‌لیست اصلی یک بار خوانده می‌شود تا مشخص شود چه کیفیت‌هایی دارد، و بعد
آدرس مستقیم همان کیفیت منتشر می‌شود که یک پلی‌لیست تمیز است. نسخه اصلی هم در
`iran-all-streams.m3u` به عنوان پشتیبان می‌ماند.

{heading("fa-categories-how", "شبکه‌ها چطور دسته‌بندی می‌شوند")}

دسته‌ها دو چیز مشخص را نشان می‌دهند: اینکه چه کسی شبکه را اداره می‌کند و چطور پخش می‌شود،
و بعد موضوع برنامه‌ها. این کار قطعی است و همیشه با همین ترتیب انجام می‌شود، پس نتیجه
همیشه یکسان درمی‌آید:

۱. اگر برای آن شبکه در `category_overrides` داخل [`data/curated.json`](data/curated.json)
   چیزی تعریف شده باشد، همان اعمال می‌شود.

۲. عضویت در یکی از فهرست‌های `sets`، به ترتیب `irib_provincial`، `irib_international`،
   `religious_christian`، `religious_other` و `irib_national`.

۳. وجود برچسب `religious` در دسته‌های iptv-org آن شبکه.

۴. اولین برچسب موضوعی iptv-org که در `scripts/taxonomy.py` معادل دارد.

۵. اگر هیچ‌کدام نبود، `sat-general`.

هر شبکه برچسب‌های ماشین‌خوان هم در [`data/channels.json`](data/channels.json) دارد که
گرداننده، شیوه پخش، کیفیت، زبان و داشتن یا نداشتن استریم پشتیبان را نشان می‌دهد.

{heading("fa-duplicates", "لینک‌های تکراری چطور حذف می‌شوند")}

دو نوع تکرار جداگانه در `scripts/identity.py` مدیریت می‌شود:

- **استریم‌ها.** یک آدرس ممکن است در منابع مختلف با `http` به جای `https`، حروف بزرگ و
  کوچک متفاوت در دامنه، پورت پیش‌فرض، اسلش اضافه در انتها یا یک پارامتر موقتی نوشته شده
  باشد. هر آدرس به یک شکل استاندارد تبدیل می‌شود تا همه این‌ها یکی حساب شوند، و بین دو
  شکل یکسان `https` انتخاب می‌شود.
- **شبکه‌ها.** هر جا منبعی شناسه iptv-org داشته باشد، همان ملاک است. ورودی‌های بدون شناسه،
  یا ورودی‌هایی که برای یک شبکه شناسه‌های متفاوت دارند، با نام استانداردشده کنار هم قرار
  می‌گیرند. در این استانداردسازی کلمه‌هایی که تفاوتی ایجاد نمی‌کنند مثل `TV`، `channel` و
  `HD` حذف می‌شوند و شکل‌های نوشتاری متفاوت فارسی مثل `ك`/`ک` و `ي`/`ی` یکسان می‌شوند.

{heading("fa-updates", "چطور به‌روز می‌ماند")}

یک workflow در GitHub Actions روز اول و پانزدهم هر ماه اجرا می‌شود:

۱. **جمع‌آوری.** خواندن دوباره پایگاه داده و API پروژه iptv-org، پلی‌لیست‌های آماده ایران
   و فارسی همان پروژه، فهرست ایران در Free-TV و مخزن itsyebekhe/nexa. بعد الگوهای
   `scripts/discover.py` باز می‌شوند که برای شبکه‌هایی که در فهرست‌های عمومی نیستند لینک
   می‌سازند.

۲. **بررسی.** آزمایش همه لینک‌ها و ادغام نتیجه در `data/status.json` که برای هر لینک
   تاریخ اولین بار، تاریخ آخرین باری که سالم بوده، تعداد خرابی‌های پشت سر هم و نسبت سالم
   بودن را نگه می‌دارد.

۳. **ساخت دوباره.** ساختن دوباره پلی‌لیست‌ها، فایل `data/channels.json` و جدول‌های همین
   README، و ثبت تغییر فقط وقتی که واقعاً چیزی عوض شده باشد.

نام دامنه‌ها از طریق DNS-over-HTTPS حل می‌شوند تا فیلترهای محلی مثل AdGuard Home یا
Pi-hole نتوانند یک شبکه سالم را مرده نشان دهند. با `IPTV_DNS=system` می‌توان این را
غیرفعال کرد.

{heading("fa-contributing", "اضافه یا اصلاح کردن یک شبکه")}

نام‌ها، دسته‌ها، الگوهای کشف لینک و هر استریمی که در منابع عمومی نیست در
[`data/curated.json`](data/curated.json) نگه داشته می‌شود و به‌روزرسانی خودکار هیچ‌وقت
روی آن نمی‌نویسد. هر چیزی که در `playlists/` است و جدول‌های پایین ساخته می‌شوند، پس آن‌ها
را دستی ویرایش نکنید.

پوشه `data/` فقط سه فایل دارد: `curated.json` به عنوان ورودی دستی، `status.json` برای
تاریخچه بررسی‌ها، و `channels.json` به عنوان خروجی منتشرشده. فایل‌های میانی در `build/`
ساخته می‌شوند و در مخزن ثبت نمی‌شوند.

- **دسته اشتباه است:** شناسه iptv-org آن را به فهرست درست در `sets` یا به
  `category_overrides` اضافه کنید.
- **نام اشتباه است یا نام فارسی ندارد:** ورودی آن را در `channels` ویرایش کنید.
- **استریم سالمی می‌شناسید که اینجا نیست:** آن را در `streams` اضافه کنید تا در بررسی
  بعدی آزمایش شود.
- **شبکه‌ای که در پایگاه داده نیست:** آن را در `local_channels` معرفی کنید و شناسه
  ارائه‌دهنده‌اش را در `discovery` بگذارید.

همه چیز با Python نسخه ۳.۱۱ به بالا و بدون هیچ کتابخانه بیرونی اجرا می‌شود:

```bash
python scripts/sources.py
python scripts/probe.py
python scripts/logos.py
python scripts/build.py
```

{heading("fa-sources", "منابع")}

این پروژه فقط جمع‌آوری و بررسی می‌کند. هیچ ویدیویی را میزبانی یا بازپخش نمی‌کند و هیچ
فایل ویدیویی ندارد. همه لینک‌ها آدرس‌های عمومی هستند که یا خود پخش‌کننده منتشر کرده یا از
قبل در یک فهرست آزاد بوده‌اند.

- [iptv-org](https://github.com/iptv-org/iptv) و
  [پایگاه داده شبکه‌های آن](https://github.com/iptv-org/database)، منبع بیشتر لینک‌ها،
  لوگوها و اطلاعات شبکه‌ها.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV) که
  [فهرست ایران](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) آن آدرس‌های
  داخلی صداوسیما را ثبت کرده است.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa)، یک سازنده پلی‌لیست فارسی که
  ایده این پروژه از آن گرفته شد.
- [lashkari20/iptv](https://github.com/lashkari20/iptv)، یک نسخه از سال ۲۰۲۲ که فقط به
  عنوان مجموعه‌ای از لینک‌ها برای آزمایش نگه داشته شده است.

بعضی پخش‌کننده‌های اینترنتی، شبکه‌هایی را که در دسترس نیستند از طریق پروکسی‌های شخص ثالث
باز می‌کنند، مثلاً یک Cloudflare Worker که یک آدرس مسدود را واسطه می‌شود. آن لینک‌ها
عمداً اینجا منتشر نشده‌اند، چون کاربران این پروژه را از زیرساختی رد می‌کنند که هزینه‌اش
را کس دیگری می‌دهد و هر لحظه می‌تواند آن را ببندد. فقط آدرس‌هایی اینجا هستند که خود
پخش‌کننده یا CDN خودش ارائه می‌کند، و به همین دلیل چند شبکه که در فهرست‌های دیگر هست
اینجا نیست.

اگر حق پخش شبکه‌ای در این فهرست را دارید و می‌خواهید حذف شود،
[یک issue باز کنید](https://github.com/{REPO}/issues).

{heading("fa-licence", "مجوز")}

کد و داده‌های این پروژه با مجوز [MIT](LICENSE) منتشر شده‌اند. خود شبکه‌ها متعلق به
پخش‌کننده‌های آن‌ها هستند.

{heading("fa-categories", "دسته‌ها")}

{category_summary(channels, "fa")}

{heading("fa-channels", "فهرست شبکه‌ها")}

{channel_tables(channels, "fa")}

</div>
"""
    return english + "\n" + persian
