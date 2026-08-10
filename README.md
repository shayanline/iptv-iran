<a id="english"></a>

# IPTV Iran

M3U playlists of Iranian and Persian language television channels, grouped by operator and
distribution first and by subject matter second.

202 channels across 14 categories, from 324 verified streams.
198 channels are reachable from anywhere, 4 only from Iranian IP
addresses. Every stream is re-checked automatically every two weeks.

[![Refresh playlists](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml/badge.svg)](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml)
![Channels](https://img.shields.io/badge/channels-202-1f6feb)
![Streams](https://img.shields.io/badge/verified%20streams-324-8250df)
![Last checked](https://img.shields.io/badge/last%20checked-10%20August%202026-2da44e)

**🇮🇷 [این راهنما به فارسی هم موجود است](#persian)**

## Contents

- [Get the playlist](#get-the-playlist)
- [How streams are checked](#how-streams-are-checked)
- [How a channel's stream is chosen](#how-a-stream-is-chosen)
- [How channels are categorised](#how-channels-are-categorised)
- [How duplicates are removed](#how-duplicates-are-removed)
- [How it stays current](#how-it-stays-current)
- [Adding or fixing a channel](#adding-or-fixing-a-channel)
- [Sources](#sources)
- [Licence](#licence)
- [Categories](#categories)
- [Channel list](#channel-list)

<a id="get-the-playlist"></a>

## Get the playlist

Paste one of these URLs into VLC, IPTV Smarters, TiviMate, Kodi, OTT Navigator, or any
other client that reads M3U. There is nothing to install and no account to create.

```
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u
```

| Playlist | Contents |
|:--|:--|
| [iran.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) | Every channel, one stream each |
| [iran-global.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u) | Only channels reachable outside Iran |
| [iran-domestic.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u) | Only channels that require an Iranian IP address |
| [iran-all-streams.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u) | Every working stream, backups included |

### Title language

The same four playlists are published in three title styles. Pick the folder that suits
you and keep the file name the same.

| Folder | Titles | Example |
|:--|:--|:--|
| [`playlists/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) | Bilingual, `English \| فارسی` | `IRIB TV1 \| شبکه یک FHD` |
| [`playlists/en/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u) | English only | `IRIB TV1 FHD` |
| [`playlists/fa/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) | Persian only, Persian category names | `شبکه یک FHD` |

Resolution tags (`HD`, `FHD`, `4K`) are appended to the title from the resolution the
probe measured, and `[IR]` marks a channel that needs an Iranian IP address. Current mix:
1 4K, 58 FHD, 45 HD, 84 SD, 14 unknown.

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

<a id="how-streams-are-checked"></a>

## How streams are checked

Streams are verified rather than trusted, because a playlist entry can point at a manifest
that still exists after the video behind it has stopped.

- **The check reads video.** It follows the HLS chain, master playlist to variant playlist
  to a media segment, and passes a stream only when media bytes come back.
- **Failure by location is recorded, not punished.** Some endpoints answer only to Iranian
  IP addresses. A GitHub Actions runner is outside Iran, so those requests time out. Those
  streams are marked `iran_only` and published in `iran-domestic.m3u` instead of being
  deleted. This affects the domestic IRIB CDN, which is why 34 provincial
  networks and the national networks are listed here at all.
- **Removal requires repetition.** A stream must fail three consecutive fortnightly runs,
  about six weeks, before it is dropped.
- **Backups are kept.** Extra working streams for a channel stay in
  `iran-all-streams.m3u`, ordered best first.

<a id="how-a-stream-is-chosen"></a>

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

<a id="how-channels-are-categorised"></a>

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

<a id="how-duplicates-are-removed"></a>

## How duplicates are removed

Two kinds of duplicate are handled separately, in `scripts/identity.py`:

- **Streams.** The same endpoint appears across sources with a different scheme, host
  case, default port, trailing slash or session parameter. Each URL is reduced to a
  canonical key, so those collapse into one entry, and `https` is preferred over `http`
  for the same endpoint.
- **Channels.** The iptv-org id is the identity whenever a source supplies one. Entries
  with no id, or with different ids for one service, are grouped by a normalised name key
  that removes non-distinguishing words (`TV`, `channel`, `HD`) and folds Persian spelling
  variants such as `ك`/`ک` and `ي`/`ی`.

<a id="how-it-stays-current"></a>

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

Hostnames are resolved over DNS-over-HTTPS, so a local filter such as AdGuard Home or
Pi-hole cannot make a working channel look dead. Set `IPTV_DNS=system` to opt out.

<a id="adding-or-fixing-a-channel"></a>

## Adding or fixing a channel

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

<a id="sources"></a>

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
[open an issue](https://github.com/shayanline/iptv-iran/issues).

<a id="licence"></a>

## Licence

[MIT](LICENSE) for the code and the curated data. The channels belong to their
broadcasters.

<a id="categories"></a>

## Categories

| Category | Channels | Anywhere | Iran only | Playlist |
|:--|--:|--:|--:|:--|
| IRIB National Networks | 24 | 24 | 0 | [irib-national](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u) |
| IRIB Provincial Networks | 34 | 34 | 0 | [irib-provincial](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u) |
| IRIB International Services | 13 | 9 | 4 | [irib-international](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u) |
| Satellite · General | 17 | 17 | 0 | [sat-general](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u) |
| Satellite · Entertainment | 23 | 23 | 0 | [sat-entertainment](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-entertainment.m3u) |
| Satellite · Movies & Series | 22 | 22 | 0 | [sat-movies](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u) |
| Satellite · News | 16 | 16 | 0 | [sat-news](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u) |
| Satellite · Music | 15 | 15 | 0 | [sat-music](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u) |
| Satellite · Kids | 1 | 1 | 0 | [sat-kids](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u) |
| Satellite · Sports | 1 | 1 | 0 | [sat-sports](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u) |
| Satellite · Documentary & Learning | 4 | 4 | 0 | [sat-documentary](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u) |
| Religious · Islamic | 17 | 17 | 0 | [religious-islamic](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u) |
| Religious · Christian | 11 | 11 | 0 | [religious-christian](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u) |
| Religious · Other Faiths & Spiritual | 4 | 4 | 0 | [religious-other](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u) |
| **Total** | **202** | **198** | **4** | |

<a id="channel-list"></a>

## Channel list

### IRIB National Networks

Channels operated by IRIB and distributed nationally.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Golkhane | شبکه گلخانه | 720p | Anywhere | 2 |
| iFilm | آی‌فیلم | 1080p | Anywhere | 5 |
| Iran Nama | ایران نما | 576p | Anywhere | 1 |
| IRIB Amoozesh | شبکه آموزش | 576p | Anywhere | 3 |
| IRIB Mostanad | شبکه مستند | 1080p | Anywhere | 3 |
| IRIB Namayesh | شبکه نمایش | 1080p | Anywhere | 3 |
| IRIB Nasim | شبکه نسیم | 1080p | Anywhere | 3 |
| IRIB Ofogh | شبکه افق | 1080p | Anywhere | 3 |
| IRIB Omid | شبکه امید | 1080p | Anywhere | 3 |
| IRIB Pooya & Nahal | شبکه پویا و نهال | 1080p | Anywhere | 3 |
| IRIB Quran | شبکه قرآن و معارف سیما | 1080p | Anywhere | 3 |
| IRIB Salamat | شبکه سلامت | 576p | Anywhere | 3 |
| IRIB Tamasha | شبکه تماشا | 1080p | Anywhere | 3 |
| IRIB TV1 | شبکه یک | 1080p | Anywhere | 3 |
| IRIB TV1 + | شبکه یک پلاس | 1080p | Anywhere | 2 |
| IRIB TV2 | شبکه دو | 1080p | Anywhere | 3 |
| IRIB TV3 | شبکه سه | 1082p | Anywhere | 3 |
| IRIB TV4 | شبکه چهار | 576p | Anywhere | 3 |
| IRIB TV5 (Tehran) | شبکه پنج (تهران) | 1080p | Anywhere | 2 |
| IRIB UHD | شبکه فراگیر (UHD) | 2160p | Anywhere | 3 |
| IRIB Varzesh | شبکه ورزش | 1082p | Anywhere | 3 |
| IRINN | شبکه خبر | 576p | Anywhere | 4 |
| IRINN 2 | شبکه خبر ۲ | 1080p | Anywhere | 2 |
| Roya | شبکه رویا | 720p | Anywhere | 2 |

### IRIB Provincial Networks

IRIB channels assigned to a specific province or city.

| Channel | Persian name | Province | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|:--|
| Abadan | شبکه آبادان | Abadan | 1080p | Anywhere | 2 |
| Aflak | شبکه افلاک | Lorestan | 576p | Anywhere | 2 |
| Aftab | شبکه آفتاب | Markazi | 1080p | Anywhere | 2 |
| Alborz | شبکه البرز | Alborz | 1080p | Anywhere | 2 |
| Atrak | شبکه اترک | North Khorasan | 576p | Anywhere | 2 |
| Baran | شبکه باران | Gilan | 576p | Anywhere | 2 |
| Bushehr | شبکه بوشهر | Bushehr | 1080p | Anywhere | 2 |
| Dena | شبکه دنا | Kohgiluyeh & Boyer-Ahmad | 1080p | Anywhere | 2 |
| Eshragh | شبکه اشراق | Zanjan | 1080p | Anywhere | 2 |
| Fars | شبکه فارس | Fars | 1080p | Anywhere | 2 |
| Hamedan | شبکه همدان | Hamadan | 576p | Anywhere | 2 |
| Hamoon | شبکه هامون | Sistan & Baluchestan | 1080p | Anywhere | 2 |
| Ilam | شبکه ایلام | Ilam | 576p | Anywhere | 2 |
| Isfahan | شبکه اصفهان | Isfahan | 1080p | Anywhere | 2 |
| Jahanbin | شبکه جهان‌بین | Chaharmahal & Bakhtiari | 1080p | Anywhere | 2 |
| Kerman | شبکه کرمان | Kerman | 1080p | Anywhere | 2 |
| Khalij-e Fars | شبکه خلیج فارس | Hormozgan | 1080p | Anywhere | 2 |
| Khavaran | شبکه خاوران | South Khorasan | 1080p | Anywhere | 2 |
| Khorasan Razavi | شبکه خراسان رضوی | Khorasan Razavi | 1080p | Anywhere | 2 |
| Khuzestan | شبکه خوزستان | Khuzestan | 576p | Anywhere | 2 |
| Kish | شبکه کیش | Kish | 576p | Anywhere | 2 |
| Kordestan | شبکه کردستان | Kurdistan | 1080p | Anywhere | 2 |
| Mahabad | شبکه مهاباد | Mahabad | 1080p | Anywhere | 2 |
| Makran | شبکه مکران | Sistan & Baluchestan | 1080p | Anywhere | 2 |
| Noor | شبکه نور | Qom | 1080p | Anywhere | 2 |
| Qazvin | شبکه قزوین | Qazvin | 1080p | Anywhere | 2 |
| Sabalan | شبکه سبلان | Ardabil | 576p | Anywhere | 2 |
| Sabz | شبکه سبز | Golestan | 576p | Anywhere | 2 |
| Sahand | شبکه سهند | East Azerbaijan | 1080p | Anywhere | 2 |
| Semnan | شبکه سمنان | Semnan | 1080p | Anywhere | 2 |
| Tabarestan | شبکه تبرستان | Mazandaran | 1080p | Anywhere | 2 |
| West Azerbaijan | شبکه آذربایجان غربی | West Azerbaijan | 576p | Anywhere | 2 |
| Yazd | شبکه تابان یزد | Yazd | 1080p | Anywhere | 2 |
| Zagros | شبکه زاگرس | Kermanshah | 576p | Anywhere | 2 |

### IRIB International Services

IRIB channels produced for audiences outside Iran, in Persian and other languages.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Al-Kawthar TV | شبکه الکوثر | 576p | Anywhere | 3 |
| HispanTV | هیسپان تی‌وی | 576p | Anywhere | 1 |
| iFilm 2 | آی‌فیلم ۲ | 576p | Anywhere | 3 |
| iFilm Arabic | آی‌فیلم عربی | 576p | Anywhere | 3 |
| iFilm English | آی‌فیلم انگلیسی | 576p | Anywhere | 3 |
| Iran Press | ایران پرس | 576p | Anywhere | 1 |
| Palestine TV | شبکه فلسطین | 720p | Anywhere | 2 |
| Press TV | پرس تی‌وی | 720p | Anywhere | 5 |
| Press TV French | پرس تی‌وی فرانسه | 1080p | Anywhere | 2 |
| Sahar TV Azeri | سحر آذری | 576p | Iran only | 1 |
| Sahar TV Balkan | سحر بالکان | 576p | Iran only | 1 |
| Sahar TV Kurdish | سحر کردی | 576p | Iran only | 1 |
| Sahar TV Urdu | سحر اردو | 576p | Iran only | 1 |

### Satellite · General

Persian language channels with mixed programming, distributed by satellite.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Arax TV | آراکس تی‌وی | 720p | Anywhere | 1 |
| Arko TV | آرکو تی‌وی | 720p | Anywhere | 1 |
| Arvan TV | آروان تی‌وی | 720p | Anywhere | 2 |
| Asil TV | اصیل تی‌وی | 576p | Anywhere | 1 |
| Atrina TV | آترینا تی‌وی | 720p | Anywhere | 1 |
| Cafe Trade TV | کافه ترید | 480p | Anywhere | 1 |
| Dej TV | دژ تی‌وی | 720p | Anywhere | 1 |
| GordAfarid TV | گردآفرید | n/a | Anywhere | 1 |
| Khalij TV | خلیج تی‌وی | 720p | Anywhere | 1 |
| MelliG TV | ملی‌گرا | n/a | Anywhere | 1 |
| MTC | ام‌تی‌سی | 720p | Anywhere | 1 |
| Nahade Azadi | نهاد آزادی | n/a | Anywhere | 1 |
| Novin TV | نوین تی‌وی | 720p | Anywhere | 1 |
| Shorai TV | شورای تی‌وی | 1080p | Anywhere | 1 |
| TM TV | تی‌ام تی‌وی | 480p | Anywhere | 1 |
| Woman TV | شبکه زن | n/a | Anywhere | 1 |
| Zed TV | زد تی‌وی | 720p | Anywhere | 1 |

### Satellite · Entertainment

Variety, talk, comedy, lifestyle and reality programming.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| 247 Box TV | ۲۴۷ باکس | 576p | Anywhere | 1 |
| 4U Family | فور یو فمیلی | n/a | Anywhere | 1 |
| 4U TV | فور یو تی‌وی | 576p | Anywhere | 1 |
| AVA Family | آوا فامیلی | 576p | Anywhere | 1 |
| FX 1 | اف‌ایکس ۱ | 576p | Anywhere | 1 |
| FX 2 | اف‌ایکس ۲ | 576p | Anywhere | 1 |
| ITN | آی‌تی‌ان | 576p | Anywhere | 1 |
| Kanal Jadid | کانال جدید | 576p | Anywhere | 1 |
| MBC Persia | ام‌بی‌سی پرشیا | 1080p | Anywhere | 2 |
| Net TV | نت تی‌وی | n/a | Anywhere | 1 |
| Omid-e Iran | امید ایران | 480p | Anywhere | 1 |
| Oxir TV | اکسیر تی‌وی | 576p | Anywhere | 1 |
| Persiana Comedy | پرشیانا کمدی | 576p | Anywhere | 1 |
| Persiana Reality | پرشیانا ریالیتی | 720p | Anywhere | 1 |
| Persiana Turkiye | پرشیانا ترکیه | 576p | Anywhere | 1 |
| Project Leon | پروژه لئون | n/a | Anywhere | 1 |
| Setareh TV | ستاره | 576p | Anywhere | 1 |
| Shabakeh 7 | شبکه ۷ | 480p | Anywhere | 1 |
| Tapesh 2 | تپش ۲ | 480p | Anywhere | 1 |
| Tapesh Iran | تپش ایران | 1080p | Anywhere | 1 |
| Tapesh TV | تپش تی‌وی | 1080p | Anywhere | 2 |
| Tin TV | تین تی‌وی | 720p | Anywhere | 2 |
| YourTime TV | یورتایم تی‌وی | 576p | Anywhere | 1 |

### Satellite · Movies & Series

Film and drama channels, including dubbed foreign titles.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Afra Film | آفرا فیلم | 720p | Anywhere | 1 |
| AVA Series | آوا سریال | 576p | Anywhere | 1 |
| Bravo Farsi TV | براوو فارسی | 576p | Anywhere | 1 |
| Cafe Film | کافه فیلم | 720p | Anywhere | 1 |
| Classic TV | کلاسیک تی‌وی | 720p | Anywhere | 1 |
| GEM Pixel | جم پیکسل | 576p | Anywhere | 1 |
| Gold Star | گلد استار | 720p | Anywhere | 1 |
| Grand Cinema | گراند سینما | 576p | Anywhere | 1 |
| HomePlus | هوم پلاس | 720p | Anywhere | 1 |
| ICC Plus | آی‌سی‌سی پلاس | 576p | Anywhere | 1 |
| Maah TV | ماه تی‌وی | 576p | Anywhere | 1 |
| Meta Film TV | متا فیلم | 576p | Anywhere | 1 |
| NewFlix | نیوفلیکس | 720p | Anywhere | 1 |
| Persiana Cinema | پرشیانا سینما | 576p | Anywhere | 1 |
| Persiana Family | پرشیانا فمیلی | 576p | Anywhere | 1 |
| Persiana Iranian | پرشیانا ایرانیان | 576p | Anywhere | 1 |
| Persiana Korea | پرشیانا کره | 576p | Anywhere | 1 |
| Persiana Latino | پرشیانا لاتین | 576p | Anywhere | 1 |
| Persiana Plus | پرشیانا پلاس | 576p | Anywhere | 1 |
| Persiana Series | پرشیانا سریال | 720p | Anywhere | 1 |
| SL 1 | اس‌ال ۱ | 576p | Anywhere | 1 |
| SL 2 | اس‌ال ۲ | 576p | Anywhere | 1 |

### Satellite · News

Persian language news channels.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| BBC News Persian | بی‌بی‌سی فارسی | 720p | Anywhere | 9 |
| Channel One | شبکه یک (لس‌آنجلس) | 480p | Anywhere | 1 |
| Didgah TV | دیدگاه | 486p | Anywhere | 1 |
| Iran Independent | ایران ایندیپندنت | n/a | Anywhere | 1 |
| Iran International | ایران اینترنشنال | 1080p | Anywhere | 5 |
| Iran National Revolution TV | تلویزیون انقلاب ملی ایران | 720p | Anywhere | 1 |
| Irane Farda | ایران فردا | n/a | Anywhere | 1 |
| IranWire | ایران‌وایر | n/a | Anywhere | 1 |
| IRNA TV | تلویزیون ایرنا | n/a | Anywhere | 1 |
| Israel Pars TV | ایسرائل پارس | 360p | Anywhere | 1 |
| Mihan TV | میهن تی‌وی | 1080p | Anywhere | 1 |
| National Iranian Congress TV | تلویزیون کنگره ملی ایرانیان | 720p | Anywhere | 1 |
| Pars TV | پارس تی‌وی | 720p | Anywhere | 2 |
| Pulse Media | پالس مدیا | n/a | Anywhere | 1 |
| Radio Farda TV | رادیو فردا | 576p | Anywhere | 1 |
| VOA Persian | صدای آمریکا فارسی | 1080p | Anywhere | 2 |

### Satellite · Music

Music video and concert channels.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| 4 Kurd | فور کورد | 576p | Anywhere | 1 |
| 4 Music | فور موزیک | 720p | Anywhere | 2 |
| AFN TV | ای‌اف‌ان تی‌وی | 720p | Anywhere | 1 |
| Avang TV | آونگ | 480p | Anywhere | 1 |
| High Vision TV | های ویژن | 576p | Anywhere | 2 |
| Navahang TV | نواهنگ | 576p | Anywhere | 2 |
| Persiana Folk | پرشیانا فولک | 720p | Anywhere | 1 |
| Persiana Nostalgia | پرشیانا نوستالژی | 576p | Anywhere | 1 |
| Persiana SetMix | پرشیانا ست‌میکس | n/a | Anywhere | 1 |
| Persiana Vibe | پرشیانا وایب | 720p | Anywhere | 1 |
| PMC | پی‌ام‌سی | 576p | Anywhere | 1 |
| PMC Royale | پی‌ام‌سی رویال | 576p | Anywhere | 1 |
| RJTV | آر‌جی تی‌وی | 480p | Anywhere | 1 |
| Sun Music | سان موزیک | n/a | Anywhere | 1 |
| T2 TV | تی۲ تی‌وی | 576p | Anywhere | 1 |

### Satellite · Kids

Programming for children, including animation.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Persiana Junior | پرشیانا جونیور | 576p | Anywhere | 1 |

### Satellite · Sports

Sport and fitness channels.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Persiana Fight | پرشیانا فایت | 720p | Anywhere | 1 |

### Satellite · Documentary & Learning

Documentary, science, medical and educational channels.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| E Planet TV | ای‌پلنت | 720p | Anywhere | 1 |
| Payam Javan TV | پیام جوان | 720p | Anywhere | 1 |
| Persiana Docs | پرشیانا مستند | 720p | Anywhere | 1 |
| Persiana Medical | پرشیانا مدیکال | 720p | Anywhere | 2 |

### Religious · Islamic

Islamic religious channels, registered in Iran, Iraq and elsewhere.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Al Wilayah | شبکه الولایه | 576p | Anywhere | 1 |
| Al-Mahdi TV | شبکه المهدی | 1080p | Anywhere | 1 |
| Assirat TV | شبکه الصراط | 1080p | Anywhere | 1 |
| Habib TV | شبکه حبیب | 720p | Anywhere | 2 |
| Hadi TV | شبکه هادی | 1080p | Anywhere | 1 |
| Imam Hussein TV 1 | امام حسین ۱ | 1080p | Anywhere | 2 |
| Imam Hussein TV 6 | امام حسین ۶ | 1080p | Anywhere | 1 |
| Labbayk TV | شبکه لبیک | 720p | Anywhere | 2 |
| Marjaeyat TV Persian | شبکه مرجعیت | 1080p | Anywhere | 1 |
| Nour TV | شبکه نور (امارات) | 576p | Anywhere | 1 |
| Payam-e Aramesh | پیام آرامش | 480p | Anywhere | 1 |
| Payvand TV | شبکه پیوند | 720p | Anywhere | 2 |
| Rasoulallah TV | شبکه رسول‌الله | 1080p | Anywhere | 1 |
| Razavi TV | شبکه رضوی | 720p | Anywhere | 2 |
| Tekye Madahi | تکیه مداحی | 720p | Anywhere | 2 |
| Velayat TV | شبکه ولایت | 720p | Anywhere | 2 |
| Velayat TV Network | شبکه ولایت (آمریکا) | 480p | Anywhere | 1 |

### Religious · Christian

Persian language Christian channels.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Derakhte Zendegi TV | درخت زندگی | 480p | Anywhere | 1 |
| ICnet 1 | آی‌سی‌نت ۱ | 480p | Anywhere | 1 |
| ICnet 2 | آی‌سی‌نت ۲ | 480p | Anywhere | 1 |
| ICnet 3 | آی‌سی‌نت ۳ | 720p | Anywhere | 1 |
| Kalemeh TV | شبکه کلمه | 576p | Anywhere | 1 |
| LoveWorld Persia | لاوورلد پرشیا | 720p | Anywhere | 1 |
| Mohabat TV | شبکه محبت | 1080p | Anywhere | 2 |
| Omid Javedan | امید جاودان | 720p | Anywhere | 1 |
| Rahe Nejat TV | راه نجات | 480p | Anywhere | 1 |
| SAT-7 Pars | ست‌۷ پارس | 576p | Anywhere | 1 |
| TBN Nejat TV | شبکه نجات | 576p | Anywhere | 1 |

### Religious · Other Faiths & Spiritual

Channels of other faiths, and spiritual or philosophical programming.

| Channel | Persian name | Quality | Reachable from | Streams |
|:--|:--|:--|:--|:--|
| Erfan Halgheh TV | عرفان حلقه | 480p | Anywhere | 1 |
| Ganj-e Hozour | گنج حضور | 1080p | Anywhere | 1 |
| Iran Jewish TV | تلویزیون یهودیان ایرانی | 720p | Anywhere | 1 |
| Wise Human TV | انسان خردمند | 1080p | Anywhere | 1 |


---

<a id="persian"></a>

<div dir="rtl" align="right">

# IPTV ایران

پلی‌لیست‌های M3U از شبکه‌های تلویزیونی ایرانی و فارسی‌زبان، دسته‌بندی‌شده بر اساس اینکه چه
کسی شبکه را اداره می‌کند و چطور پخش می‌شود، و بعد بر اساس موضوع برنامه‌ها.

در مجموع ۲۰۲ شبکه در ۱۴ دسته، از ۳۲۴
استریم بررسی‌شده. ۱۹۸ شبکه از هر جای دنیا باز می‌شود و
۴ شبکه فقط با IP ایران. همه استریم‌ها هر دو هفته یک‌بار به‌صورت
خودکار دوباره بررسی می‌شوند.

**🇬🇧 [English version](#english)**

## فهرست مطالب

- [دریافت پلی‌لیست](#fa-download)
- [استریم‌ها چطور بررسی می‌شوند](#fa-checking)
- [استریم هر شبکه چطور انتخاب می‌شود](#fa-choosing)
- [شبکه‌ها چطور دسته‌بندی می‌شوند](#fa-categories-how)
- [لینک‌های تکراری چطور حذف می‌شوند](#fa-duplicates)
- [چطور به‌روز می‌ماند](#fa-updates)
- [اضافه یا اصلاح کردن یک شبکه](#fa-contributing)
- [منابع](#fa-sources)
- [مجوز](#fa-licence)
- [دسته‌ها](#fa-categories)
- [فهرست شبکه‌ها](#fa-channels)

<a id="fa-download"></a>

## دریافت پلی‌لیست

یکی از لینک‌های زیر را در VLC، IPTV Smarters، TiviMate، Kodi، OTT Navigator یا هر برنامه
دیگری که M3U را پشتیبانی می‌کند وارد کنید. نه چیزی برای نصب لازم است و نه حساب کاربری.

```
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u
https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u
```

| پلی‌لیست | محتوا |
|:--|:--|
| [iran.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) | همه شبکه‌ها، برای هر شبکه یک استریم |
| [iran-global.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u) | فقط شبکه‌هایی که از خارج ایران باز می‌شوند |
| [iran-domestic.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u) | فقط شبکه‌هایی که به IP ایران نیاز دارند |
| [iran-all-streams.m3u](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u) | همه استریم‌های سالم، همراه با نسخه‌های پشتیبان |

### زبان عنوان‌ها

همین چهار پلی‌لیست با سه حالت عنوان‌گذاری منتشر می‌شود. هر کدام را که می‌پسندید انتخاب
کنید. نام فایل‌ها در هر سه پوشه یکسان است.

| پوشه | عنوان‌ها | نمونه |
|:--|:--|:--|
| [`playlists/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) | دوزبانه | `IRIB TV1 \| شبکه یک FHD` |
| [`playlists/en/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u) | فقط انگلیسی | `IRIB TV1 FHD` |
| [`playlists/fa/`](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) | فقط فارسی، با نام دسته‌های فارسی | `شبکه یک FHD` |

برچسب کیفیت (`HD`، `FHD`، `4K`) بر اساس رزولوشنی که هنگام بررسی اندازه‌گیری شده به عنوان
اضافه می‌شود، و `[IR]` یعنی آن شبکه فقط با IP ایران باز می‌شود. ترکیب فعلی:
۱ 4K، ۵۸ FHD، ۴۵ HD، ۸۴ کیفیت معمولی، ۱۴ نامشخص.

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

<a id="fa-checking"></a>

## استریم‌ها چطور بررسی می‌شوند

به هیچ لینکی اعتماد نمی‌شود و همه بررسی می‌شوند، چون ممکن است فایل مانیفست هنوز سر جایش
باشد ولی ویدیویی پشت آن پخش نشود.

- **ویدیوی واقعی خوانده می‌شود.** بررسی، کل زنجیره HLS را دنبال می‌کند، از پلی‌لیست اصلی
  به پلی‌لیست کیفیت و بعد به یک قطعه ویدیو، و فقط وقتی استریم را سالم می‌شمارد که داده
  ویدیو برگردد.
- **مسدود بودن جغرافیایی به معنای مرده بودن نیست.** بعضی سرورها فقط به IP های ایران جواب
  می‌دهند. چون این بررسی روی سرور GitHub و بیرون از ایران اجرا می‌شود، آن درخواست‌ها
  timeout می‌خورند. این استریم‌ها با برچسب `iran_only` ثبت و در `iran-domestic.m3u`
  منتشر می‌شوند و حذف نمی‌شوند. این موضوع شامل CDN داخلی صداوسیما می‌شود و دلیل اینکه
  ۳۴ شبکه استانی و شبکه‌های سراسری اصلاً در این فهرست هستند همین است.
- **برای حذف شدن، تکرار لازم است.** یک استریم باید در سه بررسی دوهفتگی پشت سر هم ناموفق
  باشد، یعنی حدود شش هفته، تا از فهرست بیرون برود.
- **نسخه پشتیبان نگه داشته می‌شود.** اگر شبکه‌ای چند استریم سالم داشته باشد، بقیه در
  `iran-all-streams.m3u` می‌مانند، از بهترین به پایین.

<a id="fa-choosing"></a>

## استریم هر شبکه چطور انتخاب می‌شود

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

<a id="fa-categories-how"></a>

## شبکه‌ها چطور دسته‌بندی می‌شوند

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

<a id="fa-duplicates"></a>

## لینک‌های تکراری چطور حذف می‌شوند

دو نوع تکرار جداگانه در `scripts/identity.py` مدیریت می‌شود:

- **استریم‌ها.** یک آدرس ممکن است در منابع مختلف با `http` به جای `https`، حروف بزرگ و
  کوچک متفاوت در دامنه، پورت پیش‌فرض، اسلش اضافه در انتها یا یک پارامتر موقتی نوشته شده
  باشد. هر آدرس به یک شکل استاندارد تبدیل می‌شود تا همه این‌ها یکی حساب شوند، و بین دو
  شکل یکسان `https` انتخاب می‌شود.
- **شبکه‌ها.** هر جا منبعی شناسه iptv-org داشته باشد، همان ملاک است. ورودی‌های بدون شناسه،
  یا ورودی‌هایی که برای یک شبکه شناسه‌های متفاوت دارند، با نام استانداردشده کنار هم قرار
  می‌گیرند. در این استانداردسازی کلمه‌هایی که تفاوتی ایجاد نمی‌کنند مثل `TV`، `channel` و
  `HD` حذف می‌شوند و شکل‌های نوشتاری متفاوت فارسی مثل `ك`/`ک` و `ي`/`ی` یکسان می‌شوند.

<a id="fa-updates"></a>

## چطور به‌روز می‌ماند

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

<a id="fa-contributing"></a>

## اضافه یا اصلاح کردن یک شبکه

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

<a id="fa-sources"></a>

## منابع

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
[یک issue باز کنید](https://github.com/shayanline/iptv-iran/issues).

<a id="fa-licence"></a>

## مجوز

کد و داده‌های این پروژه با مجوز [MIT](LICENSE) منتشر شده‌اند. خود شبکه‌ها متعلق به
پخش‌کننده‌های آن‌ها هستند.

<a id="fa-categories"></a>

## دسته‌ها

| دسته | تعداد | همه‌جا | فقط ایران | فهرست |
|:--|--:|--:|--:|:--|
| شبکه‌های سراسری سیما | 24 | 24 | 0 | [irib-national](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u) |
| شبکه‌های استانی | 34 | 34 | 0 | [irib-provincial](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u) |
| شبکه‌های برون‌مرزی | 13 | 9 | 4 | [irib-international](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u) |
| ماهواره‌ای · عمومی | 17 | 17 | 0 | [sat-general](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u) |
| ماهواره‌ای · سرگرمی | 23 | 23 | 0 | [sat-entertainment](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-entertainment.m3u) |
| ماهواره‌ای · فیلم و سریال | 22 | 22 | 0 | [sat-movies](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u) |
| ماهواره‌ای · خبری | 16 | 16 | 0 | [sat-news](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u) |
| ماهواره‌ای · موسیقی | 15 | 15 | 0 | [sat-music](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u) |
| ماهواره‌ای · کودک | 1 | 1 | 0 | [sat-kids](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u) |
| ماهواره‌ای · ورزشی | 1 | 1 | 0 | [sat-sports](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u) |
| ماهواره‌ای · مستند و آموزش | 4 | 4 | 0 | [sat-documentary](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u) |
| مذهبی · اسلامی | 17 | 17 | 0 | [religious-islamic](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u) |
| مذهبی · مسیحی | 11 | 11 | 0 | [religious-christian](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u) |
| مذهبی · سایر ادیان و معنوی | 4 | 4 | 0 | [religious-other](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u) |
| **مجموع** | **202** | **198** | **4** | |

<a id="fa-channels"></a>

## فهرست شبکه‌ها

### شبکه‌های سراسری سیما

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| شبکه گلخانه | Golkhane | 720p | همه‌جا | 2 |
| آی‌فیلم | iFilm | 1080p | همه‌جا | 5 |
| ایران نما | Iran Nama | 576p | همه‌جا | 1 |
| شبکه آموزش | IRIB Amoozesh | 576p | همه‌جا | 3 |
| شبکه مستند | IRIB Mostanad | 1080p | همه‌جا | 3 |
| شبکه نمایش | IRIB Namayesh | 1080p | همه‌جا | 3 |
| شبکه نسیم | IRIB Nasim | 1080p | همه‌جا | 3 |
| شبکه افق | IRIB Ofogh | 1080p | همه‌جا | 3 |
| شبکه امید | IRIB Omid | 1080p | همه‌جا | 3 |
| شبکه پویا و نهال | IRIB Pooya & Nahal | 1080p | همه‌جا | 3 |
| شبکه قرآن و معارف سیما | IRIB Quran | 1080p | همه‌جا | 3 |
| شبکه سلامت | IRIB Salamat | 576p | همه‌جا | 3 |
| شبکه تماشا | IRIB Tamasha | 1080p | همه‌جا | 3 |
| شبکه یک | IRIB TV1 | 1080p | همه‌جا | 3 |
| شبکه یک پلاس | IRIB TV1 + | 1080p | همه‌جا | 2 |
| شبکه دو | IRIB TV2 | 1080p | همه‌جا | 3 |
| شبکه سه | IRIB TV3 | 1082p | همه‌جا | 3 |
| شبکه چهار | IRIB TV4 | 576p | همه‌جا | 3 |
| شبکه پنج (تهران) | IRIB TV5 (Tehran) | 1080p | همه‌جا | 2 |
| شبکه فراگیر (UHD) | IRIB UHD | 2160p | همه‌جا | 3 |
| شبکه ورزش | IRIB Varzesh | 1082p | همه‌جا | 3 |
| شبکه خبر | IRINN | 576p | همه‌جا | 4 |
| شبکه خبر ۲ | IRINN 2 | 1080p | همه‌جا | 2 |
| شبکه رویا | Roya | 720p | همه‌جا | 2 |

### شبکه‌های استانی

| نام فارسی | نام انگلیسی | استان | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|:--|
| شبکه آبادان | Abadan | آبادان | 1080p | همه‌جا | 2 |
| شبکه افلاک | Aflak | لرستان | 576p | همه‌جا | 2 |
| شبکه آفتاب | Aftab | مرکزی | 1080p | همه‌جا | 2 |
| شبکه البرز | Alborz | البرز | 1080p | همه‌جا | 2 |
| شبکه اترک | Atrak | خراسان شمالی | 576p | همه‌جا | 2 |
| شبکه باران | Baran | گیلان | 576p | همه‌جا | 2 |
| شبکه بوشهر | Bushehr | بوشهر | 1080p | همه‌جا | 2 |
| شبکه دنا | Dena | کهگیلویه و بویراحمد | 1080p | همه‌جا | 2 |
| شبکه اشراق | Eshragh | زنجان | 1080p | همه‌جا | 2 |
| شبکه فارس | Fars | فارس | 1080p | همه‌جا | 2 |
| شبکه همدان | Hamedan | همدان | 576p | همه‌جا | 2 |
| شبکه هامون | Hamoon | سیستان و بلوچستان | 1080p | همه‌جا | 2 |
| شبکه ایلام | Ilam | ایلام | 576p | همه‌جا | 2 |
| شبکه اصفهان | Isfahan | اصفهان | 1080p | همه‌جا | 2 |
| شبکه جهان‌بین | Jahanbin | چهارمحال و بختیاری | 1080p | همه‌جا | 2 |
| شبکه کرمان | Kerman | کرمان | 1080p | همه‌جا | 2 |
| شبکه خلیج فارس | Khalij-e Fars | هرمزگان | 1080p | همه‌جا | 2 |
| شبکه خاوران | Khavaran | خراسان جنوبی | 1080p | همه‌جا | 2 |
| شبکه خراسان رضوی | Khorasan Razavi | خراسان رضوی | 1080p | همه‌جا | 2 |
| شبکه خوزستان | Khuzestan | خوزستان | 576p | همه‌جا | 2 |
| شبکه کیش | Kish | کیش | 576p | همه‌جا | 2 |
| شبکه کردستان | Kordestan | کردستان | 1080p | همه‌جا | 2 |
| شبکه مهاباد | Mahabad | مهاباد | 1080p | همه‌جا | 2 |
| شبکه مکران | Makran | سیستان و بلوچستان | 1080p | همه‌جا | 2 |
| شبکه نور | Noor | قم | 1080p | همه‌جا | 2 |
| شبکه قزوین | Qazvin | قزوین | 1080p | همه‌جا | 2 |
| شبکه سبلان | Sabalan | اردبیل | 576p | همه‌جا | 2 |
| شبکه سبز | Sabz | گلستان | 576p | همه‌جا | 2 |
| شبکه سهند | Sahand | آذربایجان شرقی | 1080p | همه‌جا | 2 |
| شبکه سمنان | Semnan | سمنان | 1080p | همه‌جا | 2 |
| شبکه تبرستان | Tabarestan | مازندران | 1080p | همه‌جا | 2 |
| شبکه آذربایجان غربی | West Azerbaijan | آذربایجان غربی | 576p | همه‌جا | 2 |
| شبکه تابان یزد | Yazd | یزد | 1080p | همه‌جا | 2 |
| شبکه زاگرس | Zagros | کرمانشاه | 576p | همه‌جا | 2 |

### شبکه‌های برون‌مرزی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| شبکه الکوثر | Al-Kawthar TV | 576p | همه‌جا | 3 |
| هیسپان تی‌وی | HispanTV | 576p | همه‌جا | 1 |
| آی‌فیلم ۲ | iFilm 2 | 576p | همه‌جا | 3 |
| آی‌فیلم عربی | iFilm Arabic | 576p | همه‌جا | 3 |
| آی‌فیلم انگلیسی | iFilm English | 576p | همه‌جا | 3 |
| ایران پرس | Iran Press | 576p | همه‌جا | 1 |
| شبکه فلسطین | Palestine TV | 720p | همه‌جا | 2 |
| پرس تی‌وی | Press TV | 720p | همه‌جا | 5 |
| پرس تی‌وی فرانسه | Press TV French | 1080p | همه‌جا | 2 |
| سحر آذری | Sahar TV Azeri | 576p | فقط ایران | 1 |
| سحر بالکان | Sahar TV Balkan | 576p | فقط ایران | 1 |
| سحر کردی | Sahar TV Kurdish | 576p | فقط ایران | 1 |
| سحر اردو | Sahar TV Urdu | 576p | فقط ایران | 1 |

### ماهواره‌ای · عمومی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| آراکس تی‌وی | Arax TV | 720p | همه‌جا | 1 |
| آرکو تی‌وی | Arko TV | 720p | همه‌جا | 1 |
| آروان تی‌وی | Arvan TV | 720p | همه‌جا | 2 |
| اصیل تی‌وی | Asil TV | 576p | همه‌جا | 1 |
| آترینا تی‌وی | Atrina TV | 720p | همه‌جا | 1 |
| کافه ترید | Cafe Trade TV | 480p | همه‌جا | 1 |
| دژ تی‌وی | Dej TV | 720p | همه‌جا | 1 |
| گردآفرید | GordAfarid TV | نامشخص | همه‌جا | 1 |
| خلیج تی‌وی | Khalij TV | 720p | همه‌جا | 1 |
| ملی‌گرا | MelliG TV | نامشخص | همه‌جا | 1 |
| ام‌تی‌سی | MTC | 720p | همه‌جا | 1 |
| نهاد آزادی | Nahade Azadi | نامشخص | همه‌جا | 1 |
| نوین تی‌وی | Novin TV | 720p | همه‌جا | 1 |
| شورای تی‌وی | Shorai TV | 1080p | همه‌جا | 1 |
| تی‌ام تی‌وی | TM TV | 480p | همه‌جا | 1 |
| شبکه زن | Woman TV | نامشخص | همه‌جا | 1 |
| زد تی‌وی | Zed TV | 720p | همه‌جا | 1 |

### ماهواره‌ای · سرگرمی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| ۲۴۷ باکس | 247 Box TV | 576p | همه‌جا | 1 |
| فور یو فمیلی | 4U Family | نامشخص | همه‌جا | 1 |
| فور یو تی‌وی | 4U TV | 576p | همه‌جا | 1 |
| آوا فامیلی | AVA Family | 576p | همه‌جا | 1 |
| اف‌ایکس ۱ | FX 1 | 576p | همه‌جا | 1 |
| اف‌ایکس ۲ | FX 2 | 576p | همه‌جا | 1 |
| آی‌تی‌ان | ITN | 576p | همه‌جا | 1 |
| کانال جدید | Kanal Jadid | 576p | همه‌جا | 1 |
| ام‌بی‌سی پرشیا | MBC Persia | 1080p | همه‌جا | 2 |
| نت تی‌وی | Net TV | نامشخص | همه‌جا | 1 |
| امید ایران | Omid-e Iran | 480p | همه‌جا | 1 |
| اکسیر تی‌وی | Oxir TV | 576p | همه‌جا | 1 |
| پرشیانا کمدی | Persiana Comedy | 576p | همه‌جا | 1 |
| پرشیانا ریالیتی | Persiana Reality | 720p | همه‌جا | 1 |
| پرشیانا ترکیه | Persiana Turkiye | 576p | همه‌جا | 1 |
| پروژه لئون | Project Leon | نامشخص | همه‌جا | 1 |
| ستاره | Setareh TV | 576p | همه‌جا | 1 |
| شبکه ۷ | Shabakeh 7 | 480p | همه‌جا | 1 |
| تپش ۲ | Tapesh 2 | 480p | همه‌جا | 1 |
| تپش ایران | Tapesh Iran | 1080p | همه‌جا | 1 |
| تپش تی‌وی | Tapesh TV | 1080p | همه‌جا | 2 |
| تین تی‌وی | Tin TV | 720p | همه‌جا | 2 |
| یورتایم تی‌وی | YourTime TV | 576p | همه‌جا | 1 |

### ماهواره‌ای · فیلم و سریال

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| آفرا فیلم | Afra Film | 720p | همه‌جا | 1 |
| آوا سریال | AVA Series | 576p | همه‌جا | 1 |
| براوو فارسی | Bravo Farsi TV | 576p | همه‌جا | 1 |
| کافه فیلم | Cafe Film | 720p | همه‌جا | 1 |
| کلاسیک تی‌وی | Classic TV | 720p | همه‌جا | 1 |
| جم پیکسل | GEM Pixel | 576p | همه‌جا | 1 |
| گلد استار | Gold Star | 720p | همه‌جا | 1 |
| گراند سینما | Grand Cinema | 576p | همه‌جا | 1 |
| هوم پلاس | HomePlus | 720p | همه‌جا | 1 |
| آی‌سی‌سی پلاس | ICC Plus | 576p | همه‌جا | 1 |
| ماه تی‌وی | Maah TV | 576p | همه‌جا | 1 |
| متا فیلم | Meta Film TV | 576p | همه‌جا | 1 |
| نیوفلیکس | NewFlix | 720p | همه‌جا | 1 |
| پرشیانا سینما | Persiana Cinema | 576p | همه‌جا | 1 |
| پرشیانا فمیلی | Persiana Family | 576p | همه‌جا | 1 |
| پرشیانا ایرانیان | Persiana Iranian | 576p | همه‌جا | 1 |
| پرشیانا کره | Persiana Korea | 576p | همه‌جا | 1 |
| پرشیانا لاتین | Persiana Latino | 576p | همه‌جا | 1 |
| پرشیانا پلاس | Persiana Plus | 576p | همه‌جا | 1 |
| پرشیانا سریال | Persiana Series | 720p | همه‌جا | 1 |
| اس‌ال ۱ | SL 1 | 576p | همه‌جا | 1 |
| اس‌ال ۲ | SL 2 | 576p | همه‌جا | 1 |

### ماهواره‌ای · خبری

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| بی‌بی‌سی فارسی | BBC News Persian | 720p | همه‌جا | 9 |
| شبکه یک (لس‌آنجلس) | Channel One | 480p | همه‌جا | 1 |
| دیدگاه | Didgah TV | 486p | همه‌جا | 1 |
| ایران ایندیپندنت | Iran Independent | نامشخص | همه‌جا | 1 |
| ایران اینترنشنال | Iran International | 1080p | همه‌جا | 5 |
| تلویزیون انقلاب ملی ایران | Iran National Revolution TV | 720p | همه‌جا | 1 |
| ایران فردا | Irane Farda | نامشخص | همه‌جا | 1 |
| ایران‌وایر | IranWire | نامشخص | همه‌جا | 1 |
| تلویزیون ایرنا | IRNA TV | نامشخص | همه‌جا | 1 |
| ایسرائل پارس | Israel Pars TV | 360p | همه‌جا | 1 |
| میهن تی‌وی | Mihan TV | 1080p | همه‌جا | 1 |
| تلویزیون کنگره ملی ایرانیان | National Iranian Congress TV | 720p | همه‌جا | 1 |
| پارس تی‌وی | Pars TV | 720p | همه‌جا | 2 |
| پالس مدیا | Pulse Media | نامشخص | همه‌جا | 1 |
| رادیو فردا | Radio Farda TV | 576p | همه‌جا | 1 |
| صدای آمریکا فارسی | VOA Persian | 1080p | همه‌جا | 2 |

### ماهواره‌ای · موسیقی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| فور کورد | 4 Kurd | 576p | همه‌جا | 1 |
| فور موزیک | 4 Music | 720p | همه‌جا | 2 |
| ای‌اف‌ان تی‌وی | AFN TV | 720p | همه‌جا | 1 |
| آونگ | Avang TV | 480p | همه‌جا | 1 |
| های ویژن | High Vision TV | 576p | همه‌جا | 2 |
| نواهنگ | Navahang TV | 576p | همه‌جا | 2 |
| پرشیانا فولک | Persiana Folk | 720p | همه‌جا | 1 |
| پرشیانا نوستالژی | Persiana Nostalgia | 576p | همه‌جا | 1 |
| پرشیانا ست‌میکس | Persiana SetMix | نامشخص | همه‌جا | 1 |
| پرشیانا وایب | Persiana Vibe | 720p | همه‌جا | 1 |
| پی‌ام‌سی | PMC | 576p | همه‌جا | 1 |
| پی‌ام‌سی رویال | PMC Royale | 576p | همه‌جا | 1 |
| آر‌جی تی‌وی | RJTV | 480p | همه‌جا | 1 |
| سان موزیک | Sun Music | نامشخص | همه‌جا | 1 |
| تی۲ تی‌وی | T2 TV | 576p | همه‌جا | 1 |

### ماهواره‌ای · کودک

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| پرشیانا جونیور | Persiana Junior | 576p | همه‌جا | 1 |

### ماهواره‌ای · ورزشی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| پرشیانا فایت | Persiana Fight | 720p | همه‌جا | 1 |

### ماهواره‌ای · مستند و آموزش

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| ای‌پلنت | E Planet TV | 720p | همه‌جا | 1 |
| پیام جوان | Payam Javan TV | 720p | همه‌جا | 1 |
| پرشیانا مستند | Persiana Docs | 720p | همه‌جا | 1 |
| پرشیانا مدیکال | Persiana Medical | 720p | همه‌جا | 2 |

### مذهبی · اسلامی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| شبکه الولایه | Al Wilayah | 576p | همه‌جا | 1 |
| شبکه المهدی | Al-Mahdi TV | 1080p | همه‌جا | 1 |
| شبکه الصراط | Assirat TV | 1080p | همه‌جا | 1 |
| شبکه حبیب | Habib TV | 720p | همه‌جا | 2 |
| شبکه هادی | Hadi TV | 1080p | همه‌جا | 1 |
| امام حسین ۱ | Imam Hussein TV 1 | 1080p | همه‌جا | 2 |
| امام حسین ۶ | Imam Hussein TV 6 | 1080p | همه‌جا | 1 |
| شبکه لبیک | Labbayk TV | 720p | همه‌جا | 2 |
| شبکه مرجعیت | Marjaeyat TV Persian | 1080p | همه‌جا | 1 |
| شبکه نور (امارات) | Nour TV | 576p | همه‌جا | 1 |
| پیام آرامش | Payam-e Aramesh | 480p | همه‌جا | 1 |
| شبکه پیوند | Payvand TV | 720p | همه‌جا | 2 |
| شبکه رسول‌الله | Rasoulallah TV | 1080p | همه‌جا | 1 |
| شبکه رضوی | Razavi TV | 720p | همه‌جا | 2 |
| تکیه مداحی | Tekye Madahi | 720p | همه‌جا | 2 |
| شبکه ولایت | Velayat TV | 720p | همه‌جا | 2 |
| شبکه ولایت (آمریکا) | Velayat TV Network | 480p | همه‌جا | 1 |

### مذهبی · مسیحی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| درخت زندگی | Derakhte Zendegi TV | 480p | همه‌جا | 1 |
| آی‌سی‌نت ۱ | ICnet 1 | 480p | همه‌جا | 1 |
| آی‌سی‌نت ۲ | ICnet 2 | 480p | همه‌جا | 1 |
| آی‌سی‌نت ۳ | ICnet 3 | 720p | همه‌جا | 1 |
| شبکه کلمه | Kalemeh TV | 576p | همه‌جا | 1 |
| لاوورلد پرشیا | LoveWorld Persia | 720p | همه‌جا | 1 |
| شبکه محبت | Mohabat TV | 1080p | همه‌جا | 2 |
| امید جاودان | Omid Javedan | 720p | همه‌جا | 1 |
| راه نجات | Rahe Nejat TV | 480p | همه‌جا | 1 |
| ست‌۷ پارس | SAT-7 Pars | 576p | همه‌جا | 1 |
| شبکه نجات | TBN Nejat TV | 576p | همه‌جا | 1 |

### مذهبی · سایر ادیان و معنوی

| نام فارسی | نام انگلیسی | کیفیت | قابل دسترس از | تعداد پخش |
|:--|:--|:--|:--|:--|
| عرفان حلقه | Erfan Halgheh TV | 480p | همه‌جا | 1 |
| گنج حضور | Ganj-e Hozour | 1080p | همه‌جا | 1 |
| تلویزیون یهودیان ایرانی | Iran Jewish TV | 720p | همه‌جا | 1 |
| انسان خردمند | Wise Human TV | 1080p | همه‌جا | 1 |


</div>
