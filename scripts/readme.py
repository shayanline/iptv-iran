"""Render the bilingual README.

This file writes the page a viewer reads, so it stays on what a viewer needs: which link
to paste, which channels are in it, and whether it is still maintained. How the streams are
checked, scored, categorised and deduplicated is documented in the module that does each
job, not here.
"""
import datetime as dt

import taxonomy

REPO = "shayanline/iptv-iran"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/playlists"


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


def details(summary, body, open_by_default=False):
    """A collapsed section. Blank lines are required for markdown to render inside."""
    flag = " open" if open_by_default else ""
    return f"<details{flag}>\n<summary>{summary}</summary>\n\n{body}\n\n</details>"


def channel_tables(channels, lang):
    """One collapsed table per category, in the taxonomy's own order."""
    blocks = []
    for cid, en, fa, about in taxonomy.CATEGORIES:
        members = [c for c in channels if c["category"] == cid]
        if not members:
            continue
        provincial = cid == "irib-provincial"
        rows = []
        if lang == "en":
            head = ["Channel", "Persian name"] + (["Province"] if provincial else []) \
                + ["Quality", "Available"]
            rows.append("| " + " | ".join(head) + " |")
            rows.append("|" + "|".join([":--"] * len(head)) + "|")
            for c in members:
                row = [c["name_en"], c["name_fa"] or "n/a"]
                if provincial:
                    row.append(c["province_en"] or "n/a")
                row += [quality(c, "n/a"),
                        {"global": "Worldwide", "iran-only": "Iran only"}.get(c["reach"], "Rechecking")]
                rows.append("| " + " | ".join(row) + " |")
            summary = f"<b>{en}</b> &nbsp; {len(members)} channels"
        else:
            head = ["نام فارسی", "نام انگلیسی"] + (["استان"] if provincial else []) \
                + ["کیفیت", "در دسترس"]
            rows.append("| " + " | ".join(head) + " |")
            rows.append("|" + "|".join([":--"] * len(head)) + "|")
            for c in members:
                row = [c["name_fa"] or "نامشخص", c["name_en"]]
                if provincial:
                    row.append(c["province_fa"] or "نامشخص")
                row += [quality(c, "نامشخص"),
                        {"global": "همه‌جا", "iran-only": "فقط ایران"}.get(c["reach"], "در حال بررسی")]
                rows.append("| " + " | ".join(row) + " |")
            summary = f"<b>{fa}</b> &nbsp; {fa_digits(len(members))} شبکه"
        blocks.append(details(summary, "\n".join(rows)))
    return "\n\n".join(blocks)


def category_playlists(channels, lang):
    """Per category playlist links, as a table."""
    rows = ["| " + (" | ".join(["Category", "Channels", "Playlist"]) if lang == "en"
                    else " | ".join(["دسته", "تعداد", "پلی‌لیست"])) + " |",
            "|:--|--:|:--|"]
    for cid, en, fa, _ in taxonomy.CATEGORIES:
        members = [c for c in channels if c["category"] == cid]
        if not members:
            continue
        count = len(members) if lang == "en" else fa_digits(len(members))
        rows.append(f"| {en if lang == 'en' else fa} | {count} "
                    f"| `{RAW}/categories/{cid}.m3u` |")
    return "\n".join(rows)


def quality_summary(channels, lang):
    buckets = {}
    for channel in channels:
        buckets.setdefault(channel["quality"] or "unknown", []).append(channel)
    labels_fa = {"4K": "4K", "FHD": "FHD", "HD": "HD", "SD": "کیفیت معمولی",
                 "unknown": "نامشخص"}
    parts = []
    for tag in ["4K", "FHD", "HD", "SD", "unknown"]:
        if buckets.get(tag):
            if lang == "en":
                parts.append(f"{len(buckets[tag])} {tag}")
            else:
                parts.append(f"{fa_digits(len(buckets[tag]))} {labels_fa[tag]}")
    return "، ".join(parts) if lang == "fa" else ", ".join(parts)


def render(channels):
    total, globally, iran_only = counts(channels)
    today = f"{dt.datetime.now(dt.timezone.utc):%d %B %Y}"
    streams = sum(len(c["streams"]) for c in channels)
    categories = len({c["category"] for c in channels})
    with_logo = sum(1 for c in channels if c["logo"])

    english = f"""<a id="english"></a>

# IPTV Iran

{total} Iranian and Persian language television channels, as M3U playlists you can paste
straight into your player.

[![Refresh playlists](https://github.com/{REPO}/actions/workflows/refresh.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/refresh.yml)
![Channels](https://img.shields.io/badge/channels-{total}-1f6feb)
![Categories](https://img.shields.io/badge/categories-{categories}-8250df)
![Checked](https://img.shields.io/badge/last%20checked-{today.replace(' ', '%20')}-2da44e)

**🇮🇷 [این راهنما به فارسی هم هست](#persian)**

[Get the playlist](#get-the-playlist) &nbsp;·&nbsp; [Titles in your language](#titles) &nbsp;·&nbsp;
[Channel list](#channels) &nbsp;·&nbsp; [Staying current](#maintained) &nbsp;·&nbsp;
[Something wrong?](#fixing) &nbsp;·&nbsp; [Credits](#credits)

<a id="get-the-playlist"></a>

## Get the playlist

Copy a link and add it to VLC, IPTV Smarters, TiviMate, Kodi, OTT Navigator, or anything
else that reads M3U. Nothing to install and no account to create.

| Playlist | What is in it | Link to copy |
|:--|:--|:--|
| **Everything** | All {total} channels, one stream each | `{RAW}/iran.m3u` |
| **Worldwide** | The {globally} channels that play anywhere | `{RAW}/iran-global.m3u` |
| **Inside Iran** | The {iran_only} that need an Iranian IP address | `{RAW}/iran-domestic.m3u` |
| **With backups** | Every working stream, spares included | `{RAW}/iran-all-streams.m3u` |
| **Smart TV safe** | For apps that stall on some channels | `{RAW}/iran-compat.m3u` |

Outside Iran, start with **Worldwide**. A channel tagged `[IR]` in the other lists needs an
Iranian connection, so it will not open for you.

If channels load a single frame and then hang, that is usually a smart TV app whose built
in player cannot parse an unusual manifest. **Smart TV safe** carries only the streams that
stay within what a basic player handles. It is a shorter list, and
[`worker/`](worker) explains how to bring the rest back.

{details("Just one category? Each has its own playlist", category_playlists(channels, "en"))}

<a id="titles"></a>

## Titles in your language

The same playlists come in three naming styles. Swap the folder, keep the file name.

| You want | Use this folder | Channel appears as |
|:--|:--|:--|
| Both languages | `{RAW}/iran.m3u` | `IRIB TV1 \\| شبکه یک` |
| English only | `{RAW}/en/iran.m3u` | `IRIB TV1` |
| Persian only | `{RAW}/fa/iran.m3u` | `شبکه یک` |

Picture quality is not written into the name. Every entry carries a `tvg-quality` attribute
(`SD`, `HD`, `FHD`, `4K`) taken from the resolution actually measured on the stream, not
from whatever the channel claims, so players that read it can sort and filter on it while
the name stays the channel's own. Right now that is {quality_summary(channels, "en")}.

Logos for {with_logo} channels are stored in this repository rather than linked from
elsewhere, so they load wherever you are. A programme guide is wired in through
`x-tvg-url`, and players that support EPG will pick it up on their own.

<a id="channels"></a>

## Channel list

{total} channels in {categories} categories, from {streams} working streams.

{channel_tables(channels, "en")}

<a id="maintained"></a>

## Staying current

Every stream is re-tested automatically twice a month. Links that have genuinely died are
removed, working ones found in the public lists are added, and anything that turns out to
be restricted to Iranian connections moves into the domestic playlist rather than being
thrown away. A channel is only dropped after it has failed repeatedly over about six weeks,
so a bad night on someone's server will not make it vanish.

Testing means fetching actual video from the stream. A link that returns a valid looking
file but no picture counts as broken. Links are also rewritten where a provider serves
something a stricter player cannot follow, so a channel that plays in VLC but stalls on a
TV box gets fixed rather than left alone.

<a id="fixing"></a>

## Something wrong?

[Open an issue](https://github.com/{REPO}/issues) if a channel will not play, sits in an odd
category, or is missing entirely.

Contributions are welcome. Channel names, categories and any extra streams live in
[`data/curated.json`](data/curated.json), which is the only file worth editing by hand.
Everything under `playlists/`, the tables above and `data/channels.json` are generated, and
your change appears in them on the next run.

<a id="credits"></a>

## Credits

This project collects and checks. It hosts no video, restreams nothing and stores no media.
Every link is a public address published by a broadcaster or already listed in an open
playlist.

- [iptv-org](https://github.com/iptv-org/iptv) and its
  [channel database](https://github.com/iptv-org/database), the source of most links, logos
  and channel details.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV), whose
  [Iran list](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) records the
  domestic IRIB addresses.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa), the Persian playlist builder that
  prompted this project.
- [lashkari20/iptv](https://github.com/lashkari20/iptv), a 2022 snapshot kept only as links
  to test.

If you hold the rights to a channel listed here and want it removed,
[open an issue](https://github.com/{REPO}/issues) and it will be taken out.

## Licence

[MIT](LICENSE) for the code and the curated data. The channels belong to their broadcasters.

---
"""

    persian = f"""<a id="persian"></a>

<div dir="rtl" align="right">

# IPTV ایران

{fa_digits(total)} شبکه تلویزیونی ایرانی و فارسی‌زبان، به شکل پلی‌لیست M3U که مستقیم در
برنامه پخش خودتان وارد می‌کنید.

**🇬🇧 [English version](#english)**

[دریافت پلی‌لیست](#fa-get) &nbsp;·&nbsp; [زبان عنوان‌ها](#fa-titles) &nbsp;·&nbsp;
[فهرست شبکه‌ها](#fa-channels) &nbsp;·&nbsp; [به‌روز ماندن](#fa-maintained) &nbsp;·&nbsp;
[مشکلی هست؟](#fa-fixing) &nbsp;·&nbsp; [منابع](#fa-credits)

<a id="fa-get"></a>

## دریافت پلی‌لیست

یکی از لینک‌ها را کپی کنید و در VLC، IPTV Smarters، TiviMate، Kodi، OTT Navigator یا هر
برنامه دیگری که M3U می‌خواند وارد کنید. نه چیزی برای نصب لازم است و نه حساب کاربری.

| پلی‌لیست | محتوا | لینک |
|:--|:--|:--|
| **همه شبکه‌ها** | هر {fa_digits(total)} شبکه، برای هرکدام یک استریم | `{RAW}/iran.m3u` |
| **قابل پخش در همه‌جا** | آن {fa_digits(globally)} شبکه‌ای که از هر کشوری باز می‌شود | `{RAW}/iran-global.m3u` |
| **فقط داخل ایران** | آن {fa_digits(iran_only)} شبکه‌ای که به IP ایران نیاز دارد | `{RAW}/iran-domestic.m3u` |
| **همراه با پشتیبان** | همه استریم‌های سالم، با نسخه‌های جایگزین | `{RAW}/iran-all-streams.m3u` |
| **سازگار با تلویزیون** | برای برنامه‌هایی که روی بعضی شبکه‌ها گیر می‌کنند | `{RAW}/iran-compat.m3u` |

اگر بیرون از ایران هستید، از **قابل پخش در همه‌جا** شروع کنید. شبکه‌هایی که در فهرست‌های
دیگر کنارشان `[IR]` نوشته شده به اینترنت داخل ایران نیاز دارند و برایتان باز نمی‌شوند.

اگر شبکه‌ها یک فریم نشان می‌دهند و بعد گیر می‌کنند، معمولاً یعنی پخش‌کننده داخلی تلویزیون
شما نمی‌تواند آن نوع مانیفست را بخواند. فهرست **سازگار با تلویزیون** فقط استریم‌هایی را
دارد که یک پخش‌کننده ساده هم از پس آن‌ها برمی‌آید. فهرست کوتاه‌تری است و در
[`worker/`](worker) توضیح داده شده چطور بقیه را هم برگردانید.

{details("فقط یک دسته می‌خواهید؟ هر دسته پلی‌لیست جدا دارد", category_playlists(channels, "fa"))}

<a id="fa-titles"></a>

## زبان عنوان‌ها

همین پلی‌لیست‌ها با سه حالت نام‌گذاری منتشر می‌شوند. کافی است پوشه را عوض کنید، نام فایل
همان است.

| اگر می‌خواهید | این پوشه را بردارید | نام شبکه این‌طور دیده می‌شود |
|:--|:--|:--|
| هر دو زبان | `{RAW}/iran.m3u` | `IRIB TV1 \\| شبکه یک` |
| فقط انگلیسی | `{RAW}/en/iran.m3u` | `IRIB TV1` |
| فقط فارسی | `{RAW}/fa/iran.m3u` | `شبکه یک` |

کیفیت تصویر داخل نام شبکه نوشته نمی‌شود. هر شبکه ویژگی `tvg-quality` دارد (`SD`، `HD`،
`FHD`، `4K`) که از روی رزولوشن واقعی اندازه‌گیری‌شده روی استریم نوشته می‌شود، نه از روی
ادعای خود شبکه. پس برنامه‌هایی که این ویژگی را می‌خوانند می‌توانند بر اساس آن مرتب یا فیلتر
کنند و نام شبکه هم دست‌نخورده می‌ماند. الان ترکیب این‌طور است:
{quality_summary(channels, "fa")}.

لوگوی {fa_digits(with_logo)} شبکه داخل همین مخزن نگه داشته می‌شود و از جای دیگری لینک
نمی‌شود، تا هر کجا باشید درست بارگذاری شود. آدرس جدول پخش (EPG) هم با `x-tvg-url` داخل
فایل هست و برنامه‌هایی که پشتیبانی می‌کنند خودشان آن را می‌گیرند.

<a id="fa-channels"></a>

## فهرست شبکه‌ها

{fa_digits(total)} شبکه در {fa_digits(categories)} دسته، از {fa_digits(streams)} استریم سالم.

{channel_tables(channels, "fa")}

<a id="fa-maintained"></a>

## به‌روز ماندن

سلامت همه استریم‌ها ماهی دو بار به‌صورت خودکار دوباره آزمایش می‌شود. لینک‌هایی که واقعاً از
کار افتاده‌اند حذف می‌شوند، لینک‌های سالمی که در فهرست‌های عمومی پیدا شود اضافه می‌شود، و
هر شبکه‌ای که معلوم شود فقط با اینترنت ایران باز می‌شود به پلی‌لیست داخلی منتقل می‌شود و
دور انداخته نمی‌شود. یک شبکه تنها وقتی کنار گذاشته می‌شود که چند بار پشت سر هم و در طول
حدود شش هفته ناموفق باشد، تا یک شب خرابی سرور باعث حذفش نشود.

آزمایش یعنی گرفتن ویدیوی واقعی از استریم. لینکی که فایل به ظاهر سالم برمی‌گرداند ولی
تصویری ندارد، خراب حساب می‌شود. اگر سرویسی لینکی بدهد که پخش‌کننده‌های سخت‌گیرتر نتوانند
دنبالش کنند، لینک بازنویسی می‌شود، تا شبکه‌ای که در VLC باز می‌شود ولی روی باکس تلویزیون
گیر می‌کند درست شود.

<a id="fa-fixing"></a>

## مشکلی هست؟

اگر شبکه‌ای باز نمی‌شود، در دسته نامناسبی قرار گرفته یا اصلاً در فهرست نیست،
[یک issue باز کنید](https://github.com/{REPO}/issues).

از مشارکت استقبال می‌شود. نام شبکه‌ها، دسته‌ها و استریم‌های اضافه در
[`data/curated.json`](data/curated.json) هستند و تنها فایلی است که ارزش ویرایش دستی دارد.
هر چیزی در `playlists/`، جدول‌های بالا و `data/channels.json` ساخته می‌شوند و تغییر شما در
اجرای بعدی خودش در آن‌ها می‌نشیند.

<a id="fa-credits"></a>

## منابع

این پروژه فقط جمع‌آوری و بررسی می‌کند. هیچ ویدیویی میزبانی یا بازپخش نمی‌کند و هیچ فایل
رسانه‌ای ندارد. همه لینک‌ها آدرس‌های عمومی هستند که یا خود پخش‌کننده منتشر کرده یا از قبل
در یک فهرست آزاد بوده‌اند.

- [iptv-org](https://github.com/iptv-org/iptv) و
  [پایگاه داده شبکه‌های آن](https://github.com/iptv-org/database)، منبع بیشتر لینک‌ها،
  لوگوها و مشخصات شبکه‌ها.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV) که
  [فهرست ایران](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) آن آدرس‌های
  داخلی صداوسیما را ثبت کرده است.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa)، سازنده پلی‌لیست فارسی که ایده این
  پروژه از آن گرفته شد.
- [lashkari20/iptv](https://github.com/lashkari20/iptv)، تصویری از سال ۲۰۲۲ که فقط به عنوان
  چند لینک برای آزمایش نگه داشته شده است.

اگر حق پخش شبکه‌ای در این فهرست را دارید و می‌خواهید حذف شود،
[یک issue باز کنید](https://github.com/{REPO}/issues) تا برداشته شود.

## مجوز

کد و داده‌های گردآوری‌شده با مجوز [MIT](LICENSE) منتشر شده‌اند. خود شبکه‌ها به
پخش‌کننده‌هایشان تعلق دارند.

</div>
"""
    return english + "\n" + persian
