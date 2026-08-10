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
     "همه کانال‌ها، یک پخش برای هر کانال"),
    ("iran-global.m3u", "Only channels reachable outside Iran",
     "فقط کانال‌های قابل دسترس از خارج ایران"),
    ("iran-domestic.m3u", "Only channels that require an Iranian IP address",
     "فقط کانال‌هایی که به آی‌پی ایران نیاز دارند"),
    ("iran-all-streams.m3u", "Every working stream, backups included",
     "همه پخش‌های سالم، همراه با نسخه‌های پشتیبان"),
]

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
    labels_fa = {"4K": "۴K", "FHD": "فول‌اچ‌دی", "HD": "اچ‌دی", "SD": "معمولی",
                 "unknown": "نامشخص"}
    parts = []
    for tag in order:
        if buckets.get(tag):
            name = tag if lang == "en" else labels_fa[tag]
            parts.append(f"{len(buckets[tag])} {name}")
    return ", ".join(parts)


def render(channels):
    total, globally, iran_only = counts(channels)
    today = f"{dt.datetime.now(dt.timezone.utc):%d %B %Y}"
    provincial = sum(1 for c in channels if c["category"] == "irib-provincial")
    streams = sum(len(c["streams"]) for c in channels)
    categories = len({c["category"] for c in channels})

    english = f"""# IPTV Iran

M3U playlists of Iranian and Persian language television channels, grouped by operator and
distribution first and by subject matter second.

{total} channels across {categories} categories, from {streams} verified streams.
{globally} channels are reachable from anywhere, {iran_only} only from Iranian IP
addresses. Every stream is re-checked automatically every two weeks.

[![Refresh playlists](https://github.com/{REPO}/actions/workflows/refresh.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/refresh.yml)
![Channels](https://img.shields.io/badge/channels-{total}-1f6feb)
![Streams](https://img.shields.io/badge/verified%20streams-{streams}-8250df)
![Last checked](https://img.shields.io/badge/last%20checked-{today.replace(' ', '%20')}-2da44e)

## Get the playlist

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
""" + "\n".join(
        f"| [{name}]({RAW}/{name}) | {desc} |" for name, desc, _ in PLAYLIST_FILES
    ) + f"""

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

## How streams are checked

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

## How a channel's stream is chosen

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

Uptime is the heaviest ongoing factor, so the choice improves as history accumulates.

## How channels are categorised

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

## How duplicates are removed

Two kinds of duplicate are handled separately, in `scripts/identity.py`:

- **Streams.** The same endpoint appears across sources with a different scheme, host
  case, default port, trailing slash or session parameter. Each URL is reduced to a
  canonical key, so those collapse into one entry, and `https` is preferred over `http`
  for the same endpoint.
- **Channels.** The iptv-org id is the identity whenever a source supplies one. Entries
  with no id, or with different ids for one service, are grouped by a normalised name key
  that removes non-distinguishing words (`TV`, `network`, `channel`, `HD`) and folds
  Persian spelling variants such as `ك`/`ک` and `ي`/`ی`.

## How it stays current

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

## Adding or fixing a channel

Names, categories, discovery templates and any stream the public sources lack live in
[`data/curated.json`](data/curated.json), which the refresh never overwrites. Everything
under `playlists/` and the tables above are generated, so please do not edit them by hand.

- **Wrong category:** add the iptv-org id to the correct list under `sets`, or to
  `category_overrides`.
- **Wrong or missing name:** edit the entry under `channels`.
- **A working stream that is missing:** add it to `streams`, and the next probe verifies it.
- **A channel the database does not list:** describe it under `local_channels`, and add its
  provider slug under `discovery`.

Everything runs on Python 3.11 or newer with no third party packages:

```bash
python scripts/sources.py   # harvest candidates
python scripts/probe.py     # check what is live
python scripts/build.py     # regenerate playlists and this README
python scripts/discover.py  # list configured discovery URLs
```

## Sources

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

## Licence

[MIT](LICENSE) for the code and the curated data. The channels belong to their
broadcasters.

## Categories

{category_summary(channels, "en")}

## Channel list

{channel_tables(channels, "en")}

---
"""

    persian = f"""<div dir="rtl" align="right">

# آی‌پی‌تی‌وی ایران

فهرست‌های پخش M3U از شبکه‌های تلویزیونی ایران و فارسی‌زبان، دسته‌بندی‌شده نخست بر پایه
گرداننده و شیوه پخش، و سپس بر پایه موضوع برنامه‌ها.

{total} کانال در {categories} دسته، از {streams} پخش راستی‌آزمایی‌شده. {globally} کانال از
هر نقطه قابل دسترس است و {iran_only} کانال تنها از آی‌پی‌های ایران. سلامت همه پخش‌ها هر دو
هفته یک‌بار به‌صورت خودکار بررسی می‌شود.

## دریافت فهرست پخش

یکی از نشانی‌های زیر را در وی‌ال‌سی، IPTV Smarters، TiviMate، کدی، OTT Navigator یا هر
برنامه دیگری که M3U می‌خواند وارد کنید. نه چیزی برای نصب لازم است و نه حسابی برای ساختن.

```
{RAW}/iran.m3u
{RAW}/iran-global.m3u
{RAW}/iran-domestic.m3u
{RAW}/iran-all-streams.m3u
```

| فهرست پخش | محتوا |
|:--|:--|
""" + "\n".join(
        f"| [{name}]({RAW}/{name}) | {fa} |" for name, _, fa in PLAYLIST_FILES
    ) + f"""

### زبان عنوان‌ها

همان چهار فهرست در سه حالت عنوان‌گذاری منتشر می‌شود. پوشه مناسب خود را انتخاب کنید، نام
پرونده‌ها یکسان است.

| پوشه | عنوان‌ها | نمونه |
|:--|:--|:--|
| [`playlists/`]({RAW}/iran.m3u) | دوزبانه | `IRIB TV1 \\| شبکه یک FHD` |
| [`playlists/en/`]({RAW}/en/iran.m3u) | فقط انگلیسی | `IRIB TV1 FHD` |
| [`playlists/fa/`]({RAW}/fa/iran.m3u) | فقط فارسی، با نام دسته‌های فارسی | `شبکه یک FHD` |

برچسب کیفیت (`HD`، `FHD`، `4K`) بر پایه رزولوشنی که بررسی‌کننده اندازه گرفته به عنوان
افزوده می‌شود، و `[IR]` نشان می‌دهد کانال به آی‌پی ایران نیاز دارد. ترکیب کنونی:
{quality_summary(channels, "fa")}.

نشانی راهنمای برنامه‌ها (EPG) با `x-tvg-url` در فایل آمده است، پس برنامه‌هایی که از آن
پشتیبانی می‌کنند بدون تنظیم اضافه جدول پخش را می‌گیرند.

## شیوه بررسی پخش‌ها

پخش‌ها راستی‌آزمایی می‌شوند و به آن‌ها اعتماد نمی‌شود، چون یک ورودی می‌تواند به مانیفستی
اشاره کند که پس از قطع شدن ویدیو هم سر جایش مانده است.

- **بررسی، ویدیو می‌خواند.** زنجیره HLS را دنبال می‌کند، از فهرست اصلی به فهرست کیفیت و
  سپس به یک قطعه ویدیو، و تنها زمانی پخش را سالم می‌شمارد که بایت‌های ویدیو برگردند.
- **ناکامی به دلیل موقعیت جغرافیایی ثبت می‌شود، نه مجازات.** برخی نشانی‌ها تنها به
  آی‌پی‌های ایران پاسخ می‌دهند. اجراکننده GitHub Actions بیرون از ایران است، پس آن
  درخواست‌ها به وقفه زمانی می‌خورند. این پخش‌ها با برچسب `iran_only` ثبت و در
  `iran-domestic.m3u` منتشر می‌شوند و حذف نمی‌شوند. این موضوع سرورهای پخش داخلی صداوسیما
  را در بر می‌گیرد و همین دلیلِ فهرست شدن {provincial} شبکه استانی و شبکه‌های سراسری در
  این مخزن است.
- **حذف، تکرار می‌خواهد.** یک پخش باید سه بررسی دوهفتگی پشت‌سرهم، نزدیک شش هفته، ناموفق
  باشد تا کنار گذاشته شود.
- **نسخه پشتیبان نگه داشته می‌شود.** پخش‌های سالم دیگر هر کانال در
  `iran-all-streams.m3u` می‌مانند، از بهترین به پایین.

## شیوه انتخاب پخش هر کانال

اگر یک کانال چند پخش داشته باشد، به آن‌ها امتیاز داده می‌شود و بهترین در فهرست‌های اصلی
می‌آید. امتیاز تنها بر پایه مقادیر اندازه‌گیری‌شده است:

| عامل | وزن | دلیل |
|:--|--:|:--|
| قابل دسترس از همه‌جا | ۱۰۰ | پخشی که پاسخ می‌دهد از پخش باکیفیت‌ترِ بی‌پاسخ ارزشمندتر است |
| سابقه سلامت در بررسی‌های پیشین | تا ۳۰ | نسبت بررسی‌های موفق به کل، متناسب با تعداد بررسی‌ها |
| بی‌نیاز به هدر سفارشی | ۲۵ | پخشی که Referer یا User-Agent می‌خواهد تنها در برنامه‌های پشتیبان `#EXTVLCOPT` باز می‌شود |
| رزولوشن | تا ۲۴ | اندازه‌گیری‌شده از فهرست اصلی، نه از برچسب |
| نرخ بیت تطبیقی | ۸ | چند کیفیت به برنامه امکان هم‌سازی با پهنای باند می‌دهد |
| زمان پاسخ | تا ۳ | تنها برای رفع تساوی، هرگز بر یک پله رزولوشن نمی‌چربد |

سابقه سلامت سنگین‌ترین عامل جاری است، پس انتخاب با گذر زمان بهتر می‌شود.

## شیوه دسته‌بندی کانال‌ها

دسته‌ها دو چیز قابل مشاهده را توصیف می‌کنند: گرداننده کانال و شیوه پخش آن، و سپس موضوع
برنامه‌ها. تخصیص دسته قطعی است و همیشه به این ترتیب انجام می‌شود، پس نتیجه تکرارپذیر است:

۱. ورودی صریح در `category_overrides` در پرونده [`data/curated.json`](data/curated.json).

۲. عضویت در یکی از فهرست‌های `sets`، به ترتیب `irib_provincial`، `irib_international`،
   `religious_christian`، `religious_other`، `irib_national`.

۳. برچسب `religious` در دسته‌های iptv-org آن کانال.

۴. نخستین برچسب موضوعی iptv-org که در `scripts/taxonomy.py` نگاشت دارد.

۵. `sat-general` به عنوان پیش‌فرض.

هر کانال برچسب‌های ماشین‌خوان هم در [`data/channels.json`](data/channels.json) دارد، شامل
گرداننده، شیوه پخش، کیفیت، زبان و وجود یا نبود پخش پشتیبان.

## شیوه حذف تکراری‌ها

دو نوع تکراری جداگانه در `scripts/identity.py` مدیریت می‌شود:

- **پخش‌ها.** یک نشانی در منابع مختلف با پروتکل، بزرگی و کوچکی حرف‌های دامنه، پورت
  پیش‌فرض، اسلش پایانی یا پارامتر نشست متفاوت ظاهر می‌شود. هر نشانی به یک کلید یکتا
  کاهش می‌یابد تا این‌ها در یک ورودی جمع شوند، و برای یک نشانی یکسان `https` بر `http`
  ترجیح دارد.
- **کانال‌ها.** شناسه iptv-org هر جا که منبعی آن را بدهد هویت اصلی است. ورودی‌های بدون
  شناسه، یا با شناسه‌های متفاوت برای یک سرویس، با کلید نام هنجارشده گروه می‌شوند که
  واژه‌های بی‌تمایز (`TV`، `network`، `channel`، `HD`) را حذف و گونه‌های نوشتاری فارسی
  مانند `ك`/`ک` و `ي`/`ی` را یکسان می‌کند.

## چگونه به‌روز می‌ماند

یک گردش‌کار GitHub Actions روز اول و پانزدهم هر ماه اجرا می‌شود:

۱. **گردآوری.** خواندن دوباره پایگاه داده و API پروژه iptv-org، فهرست‌های آماده ایران و
   فارسی همان پروژه، فهرست ایران در Free-TV، و مخزن itsyebekhe/nexa. سپس گسترش الگوهای
   `scripts/discover.py` که نشانی‌های نامزد را برای کانال‌هایی می‌سازد که فهرست‌های عمومی
   ندارند.

۲. **بررسی.** آزمودن همه نامزدها و ادغام نتیجه در `data/status.json` که برای هر نشانی
   تاریخ نخستین دیدار، تاریخ آخرین پخش سالم، شمار ناکامی‌های پشت‌سرهم و نسبت سلامت جاری
   را نگه می‌دارد.

۳. **بازسازی.** ساختن دوباره فهرست‌های پخش، پرونده `data/channels.json` و جدول‌های همین
   README، و ثبت تغییر تنها هنگامی که چیزی عوض شده باشد.

## افزودن یا اصلاح یک کانال

نام‌ها، دسته‌ها، الگوهای کشف و هر پخشی که در منابع عمومی نیست در
[`data/curated.json`](data/curated.json) نگه داشته می‌شود و به‌روزرسانی خودکار هرگز روی
آن نمی‌نویسد. هر چه در `playlists/` است و جدول‌های بالا ساخته می‌شوند، پس دستی ویرایشش
نکنید.

- **دسته نادرست:** شناسه iptv-org را به فهرست درست در `sets` یا به `category_overrides`
  اضافه کنید.
- **نام نادرست یا نبودن نام:** ورودی آن را در `channels` ویرایش کنید.
- **پخش سالمی که نیست:** آن را در `streams` بگذارید تا در بررسی بعدی سنجیده شود.
- **کانالی که در پایگاه داده نیست:** آن را در `local_channels` توصیف کنید و شناسه
  ارائه‌دهنده‌اش را در `discovery` بیفزایید.

همه چیز با پایتون ۳.۱۱ یا بالاتر و بدون هیچ بسته بیرونی اجرا می‌شود:

```bash
python scripts/sources.py
python scripts/probe.py
python scripts/build.py
python scripts/discover.py
```

## منابع

این پروژه گردآوری و راستی‌آزمایی می‌کند. هیچ ویدیویی میزبانی یا بازپخش نمی‌کند و هیچ
پرونده رسانه‌ای ندارد. همه نشانی‌ها نقاط پایانی عمومی هستند که یا خود پخش‌کننده منتشر
کرده یا پیش‌تر در فهرستی آزاد آمده‌اند.

- [iptv-org](https://github.com/iptv-org/iptv) و
  [پایگاه داده کانال‌های آن](https://github.com/iptv-org/database)، سرچشمه بیشتر
  نشانی‌ها، نشان‌ها و اطلاعات کانال‌ها.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV) که
  [فهرست ایران](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) آن نشانی‌های
  داخلی صداوسیما را ثبت کرده است.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa)، سازنده فهرست پخش فارسی که جرقه
  این پروژه را زد.
- [lashkari20/iptv](https://github.com/lashkari20/iptv)، تصویری از سال ۲۰۲۲ که تنها به
  عنوان مجموعه‌ای از نشانی‌ها برای آزمودن نگه داشته شده است.

برخی پخش‌کننده‌های عمومی، کانال‌هایی را که در دسترس نیستند از راه پروکسی‌های شخص ثالث باز
می‌کنند، برای نمونه یک Cloudflare Worker که نشانی مسدود را بازارسال می‌کند. آن نشانی‌ها
عمداً اینجا منتشر نمی‌شوند، چون کاربران این پروژه را از زیرساختی عبور می‌دهند که هزینه‌اش
را کسی دیگر می‌پردازد و هر زمان می‌تواند آن را ببندد. تنها نشانی‌هایی می‌آیند که خود
پخش‌کننده یا شبکه توزیع خودش ارائه می‌کند، و به همین دلیل چند کانال که در فهرست‌های دیگر
هست اینجا نیست.

برای درخواست حذف کانالی که حق پخش آن را دارید،
[یک issue باز کنید](https://github.com/{REPO}/issues).

## پروانه

کد و داده‌های گردآوری‌شده زیر پروانه [MIT](LICENSE) هستند. کانال‌ها به پخش‌کنندگان خود
تعلق دارند.

## دسته‌ها

{category_summary(channels, "fa")}

## فهرست کانال‌ها

{channel_tables(channels, "fa")}

</div>
"""
    return english + "\n" + persian
