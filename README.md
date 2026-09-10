<a id="english"></a>

# IPTV Iran

IPTV Iran provides 203 curated Iranian and Persian language television channels as remote M3U playlists. Add a playlist URL to a compatible player, with no project account or project software to install.

[![Refresh playlists](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml/badge.svg)](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml) ![Channels](https://img.shields.io/badge/channels-203-1f6feb) ![Checked](https://img.shields.io/badge/last%20checked-10%20September%202026-2da44e) [![License: MIT](https://img.shields.io/github/license/shayanline/iptv-iran)](LICENSE)

> **Status:** This community maintained project checks streams twice each month. Availability can change between checks, and 2 channels in the main playlist are currently being rechecked during the six week grace period.

**[راهنمای فارسی](#persian)**

[Quick start](#quick-start) &nbsp;·&nbsp; [Choose content](#choose-content) &nbsp;·&nbsp; [Smart TVs](#smart-tv-playback) &nbsp;·&nbsp; [Privacy](#network-access-data-and-privacy) &nbsp;·&nbsp; [Channels](#channels) &nbsp;·&nbsp; [Troubleshooting](#troubleshooting) &nbsp;·&nbsp; [Support](#support-and-security)

<a id="quick-start"></a>

## Quick start

### Requirements

- Use a player that accepts a remote M3U playlist and supports the stream formats offered by each channel, which include HLS, DASH, and direct media.
- Allow network access to GitHub Raw and channel providers. Entries marked `[IR]` require an Iranian IP address.

### Choose a playlist

| Playlist | Use it when | Contents | Link |
|:--|:--|--:|:--|
| **Main playlist** | You want one entry for every channel. | 203 channels | [Open the main playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) |
| **With backups** | You want alternate entries for a channel. | 627 streams | [Open the backup playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u) |
| **Smart TV safe** | Your player shows one frame and then stops. | 131 channels | [Open the compatibility playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-compat.m3u) |

The **Main playlist** contains every channel, including 2 channels that are being rechecked during the grace period. Entries marked `[IR]` require an Iranian connection.

The backup playlist lists alternate entries separately. It does not switch streams automatically.

### Recommended playlist

For most viewers, [open the main playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u).

### First use with VLC

1. Copy the link address for the **Main playlist**.
2. In VLC 3 on Windows or Linux, select **Media > Open Network Stream**, paste the URL into the network address field, then select **Play**. [VLC documents this network stream flow](https://docs.videolan.me/vlc-user/desktop/3.0/en/basic/media.html#playing-a-network-stream).
3. Open VLC's playlist view to choose a channel.

Other IPTV applications use labels such as **Add playlist**, **Playlist URL**, or **M3U URL**. Use the label that imports a remote playlist URL rather than a local file.

### Receive future updates

Keep the remote URL in your player when it supports URL based playlists. The player can then reload the current file after each project refresh. If your player imports a fixed copy, repeat the import when you want updated channel links.

<a id="choose-content"></a>

## Choose content and titles

<details>
<summary>Use one category</summary>

| Category | Channels | Playlist |
|:--|--:|:--|
| IRIB National Networks | 23 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u) |
| IRIB Provincial Networks | 34 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u) |
| IRIB International Services | 13 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u) |
| Satellite · General & Variety | 18 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u) |
| Satellite · Film & Series | 28 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u) |
| Satellite · News & Current Affairs | 27 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u) |
| Satellite · Music | 16 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u) |
| Satellite · Children | 1 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u) |
| Satellite · Sports | 4 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u) |
| Satellite · Factual, Culture & Lifestyle | 7 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u) |
| Religious · Islamic | 17 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u) |
| Religious · Christian | 11 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u) |
| Religious · Other Faiths & Spiritual | 4 | [Open playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u) |

</details>

<a id="titles"></a>

## Titles in your language

The main playlist has bilingual, English, and Persian naming variants. Use the matching link below when you want a specific display language.

| Titles | Example | Main playlist |
|:--|:--|:--|
| Both languages | `IRIB TV1 \| شبکه یک` | [Open the bilingual playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) |
| English | `IRIB TV1` | [Open the English playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u) |
| Persian | `شبکه یک` | [Open the Persian playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) |

Each entry can include a measured `tvg-quality` value of `SD`, `HD`, `FHD`, or `4K`. The current channel mix is 1 4K, 52 FHD, 39 HD, 89 SD, 22 unknown.

The project stores logos for 203 channels in this repository to avoid dependence on logo hosts that may block some regions. Programme data is currently unavailable because the previous external guide feed was retired. Players may still accept a separately configured guide.

<a id="smart-tv-playback"></a>

## Smart TV playback

Use the **Smart TV safe** playlist when a channel displays one frame and then stops, or when a television reports an HLS manifest error. It contains the 131 channels whose public streams avoid manifest shapes known to break limited players.

Some streams in the backup playlist require the public `User-Agent` or `Referer` header included in `#EXTVLCOPT` lines. Players that ignore these lines may fail on those streams even when VLC can play them.

The optional source code under [`worker/`](worker) documents a Telewebion compatibility workaround for browser CORS restrictions and HLS media sequence values that exceed a signed 32 bit integer. People who need the workaround can deploy the code to their own Cloudflare account. This project does not deploy the Worker, and none of its published playlists use a Worker route.

<a id="network-access-data-and-privacy"></a>

## Network access, data, and privacy

The published playlist service has no user account system, advertising, project telemetry, or analytics client. The repository does not set cookies for playlist users, and using a playlist does not send viewing history to this repository or its maintainer.

Your player first downloads the playlist and channel logos from GitHub Raw. It then downloads media from each broadcaster or stream provider named in the playlist. Those services receive ordinary request information, which can include your IP address, request time, requested path, and `User-Agent`. Some stream addresses use HTTP, so those requests do not have HTTPS transport protection.

The project stores public channel details, public stream URLs, probe times, response status, latency, resolution, and uptime history in [`data/`](data). It does not store viewer requests, viewing history, drafts, attachments, credentials, or recoverable media. The maintenance probe can hold a provider cookie in memory while following a stream redirect, but it does not save that cookie. The workflow downloads a small media sample to verify a stream without committing video or audio.

Your IPTV player may store playlist URLs, cached guide data, viewing history, account details, or logs on your device or in its own service. Review that player's settings and privacy policy because IPTV Iran cannot control those records. GitHub handles repository and GitHub Raw requests under the [GitHub General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). The policies of each stream provider apply to their requests.

Before sharing a public issue, log, or screenshot, remove private subscription URLs, account names, credentials, access tokens, personal IP addresses, and unrelated viewing history. The playlists published by this repository contain public source addresses and do not require project credentials.

<a id="maintained"></a>

## Maintenance and limitations

The refresh workflow runs at 04:10 UTC on the first and fifteenth day of each month. It collects public sources, resolves known provider URL patterns, fetches real media bytes from every candidate stream, mirrors valid logos, rebuilds the playlists and README, then validates the generated files before publication.

A stream remains eligible during three consecutive failed refreshes if it has worked before. This six week grace period prevents a temporary provider outage from immediately removing a channel. A stream URL that disappears from every source remains in probe history for up to 45 days when it previously worked.

Stream availability, regional restrictions, and broadcaster rights can change without notice. The project provides the latest checked public addresses without guaranteeing continuous access or permission to view a channel in every location.

<a id="channels"></a>

## Channel catalogue

The current publication contains 203 channels in 13 categories from 627 tracked working or grace period streams. Read the [English channel catalogue](CHANNELS.md) or the [Persian channel catalogue](CHANNELS.fa.md).

<a id="troubleshooting"></a>

## Troubleshooting

| Problem | What to do |
|:--|:--|
| The playlist does not load. | Open its link in a browser to confirm that your network can reach GitHub Raw, then remove and add the remote URL again. |
| A channel fails outside Iran. | Check whether the channel is marked `[IR]` in the main playlist. Region restricted channels require an Iranian IP address. |
| A channel shows one frame and stops. | Try the Smart TV safe playlist. If VLC works while the television still fails, the device probably cannot parse that stream's manifest. |
| One primary stream is unavailable. | Try the backup playlist, which lists alternate streams after the preferred one. Report the channel if every listed stream fails. |
| Programme data is missing. | The generated playlists currently have no programme guide because the previous external feed was retired. Configure a separate guide in the player if you have a verified source. |
| Logos are missing. | Confirm that the player can reach `raw.githubusercontent.com` and reload its cached playlist metadata. |

<a id="support-and-security"></a>

## Support and security

Read [SUPPORT.md](SUPPORT.md) before [opening a public issue](https://github.com/shayanline/iptv-iran/issues). Include the channel, playlist, player, device, country, test time, and VLC comparison so another person can reproduce the problem.

Do not publish vulnerability details in an issue. Follow [SECURITY.md](SECURITY.md) to send a private report through GitHub's vulnerability reporting form.

## Contributing

[CONTRIBUTING.md](CONTRIBUTING.md) explains the source files, Python 3.13 setup, focused checks, generated outputs, optional Worker, and publication workflow. Edit `data/curated.json` for channel curation and `scripts/readme.py` for the generated README.

<a id="credits"></a>

## Credits

This project collects and checks public addresses. It hosts no video, restreams nothing, and commits no media files.

- [iptv-org](https://github.com/iptv-org/iptv) and its [channel database](https://github.com/iptv-org/database) provide most stream links, logos, and channel details.
- [Free-TV/IPTV](https://github.com/Free-TV/IPTV) maintains an [Iran list](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) that records domestic IRIB addresses.
- [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa) is the Persian playlist builder that prompted this project.
- [lashkari20/iptv](https://github.com/lashkari20/iptv) provides a 2022 snapshot whose addresses remain useful for testing.

Rights holders can request removal through a [public issue](https://github.com/shayanline/iptv-iran/issues). Include the channel name, the affected address, and evidence that you represent the rights holder.

## License

The code and curated data use the [MIT License](LICENSE). Channel names, logos, programme data, and broadcasts remain subject to their respective owners' rights and provider terms.

---

<a id="persian"></a>

<div dir="rtl" align="right">

# IPTV ایران

این پروژه ۲۰۳ شبکه تلویزیونی ایرانی و فارسی‌زبان را در قالب پلی‌لیست‌های M3U ارائه می‌کند. لینک یکی از پلی‌لیست‌ها را در یک برنامه پخش سازگار وارد کنید تا شبکه‌ها در دسترس شما قرار بگیرند. استفاده از این پلی‌لیست‌ها به حساب کاربری یا نصب نرم‌افزار جداگانه‌ای از طرف پروژه نیاز ندارد.

> **وضعیت پروژه:** این پروژه به‌صورت داوطلبانه نگهداری می‌شود و لینک‌های پخش ماهی دو بار بررسی می‌شوند. ممکن است وضعیت یک شبکه در فاصله میان دو بررسی تغییر کند. در حال حاضر، ۲ شبکه از پلی‌لیست اصلی دوباره بررسی می‌شوند و تا شش هفته برای بازگشت آن‌ها صبر می‌کنیم.

**[راهنمای انگلیسی](#english)**

[شروع سریع](#fa-quick-start) &nbsp;·&nbsp; [انتخاب محتوا](#fa-choose-content) &nbsp;·&nbsp; [تلویزیون هوشمند](#fa-smart-tv) &nbsp;·&nbsp; [حریم خصوصی](#fa-privacy) &nbsp;·&nbsp; [فهرست شبکه‌ها](#fa-channels) &nbsp;·&nbsp; [رفع مشکل](#fa-troubleshooting) &nbsp;·&nbsp; [پشتیبانی](#fa-support)

<a id="fa-quick-start"></a>

## شروع سریع

### پیش‌نیازها

- به یک برنامه پخش IPTV نیاز دارید که بتواند پلی‌لیست آنلاین M3U، استریم‌های HLS و DASH و لینک‌های پخش مستقیم را باز کند.
- برنامه باید به GitHub Raw و سرورهای پخش شبکه‌ها دسترسی داشته باشد. شبکه‌هایی که با `[IR]` مشخص شده‌اند، فقط با آی‌پی ایران باز می‌شوند.

### انتخاب پلی‌لیست

| پلی‌لیست | چه زمانی از آن استفاده کنیم؟ | محتوا | لینک |
|:--|:--|--:|:--|
| **پلی‌لیست اصلی** | برای هر شبکه فقط یک لینک پخش می‌خواهید. | ۲۰۳ شبکه | [باز کردن پلی‌لیست اصلی](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) |
| **پلی‌لیست پشتیبان** | لینک‌های جایگزین هر شبکه را هم می‌خواهید. | ۶۲۷ استریم | [باز کردن پلی‌لیست پشتیبان](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran-all-streams.m3u) |
| **نسخه سازگار با تلویزیون هوشمند** | تصویر شبکه نمایش داده می‌شود، اما پخش ادامه پیدا نمی‌کند. | ۱۳۱ شبکه | [باز کردن نسخه سازگار](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran-compat.m3u) |

**پلی‌لیست اصلی** شامل همه شبکه‌هاست. در حال حاضر، ۲ شبکه از این فهرست دوباره بررسی می‌شوند. شبکه‌های دارای نشان `[IR]` فقط با آی‌پی ایران در دسترس هستند.

پلی‌لیست پشتیبان، لینک‌های جایگزین را به‌صورت ورودی‌های جداگانه نشان می‌دهد. اگر یک استریم قطع شود، پلی‌لیست به‌تنهایی نمی‌تواند استریم دیگری را جایگزین کند.

### کدام پلی‌لیست را انتخاب کنم؟

برای بیشتر کاربران، [پلی‌لیست اصلی](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) انتخاب مناسبی است.

### راه‌اندازی در VLC

1. لینک **پلی‌لیست اصلی** را کپی کنید.
2. در نسخه ۳ VLC برای ویندوز یا لینوکس، از منوی **Media** گزینه **Open Network Stream** را انتخاب کنید. لینک پلی‌لیست را در کادر مربوط بچسبانید و **Play** را بزنید. این مراحل در [راهنمای رسمی VLC](https://docs.videolan.me/vlc-user/desktop/3.0/en/basic/media.html#playing-a-network-stream) هم آمده است.
3. فهرست پخش VLC را باز کنید و شبکه موردنظر را انتخاب کنید.

در برنامه‌های دیگر IPTV معمولاً گزینه‌هایی مانند **Add playlist**، **Playlist URL** یا **M3U URL** وجود دارد. گزینه مربوط به افزودن پلی‌لیست آنلاین را انتخاب کنید. گزینه باز کردن فایل ذخیره‌شده روی دستگاه برای این کار مناسب نیست.

### دریافت خودکار به‌روزرسانی‌ها

اگر برنامه پلی‌لیست را مستقیماً از لینک آن می‌خواند، همان لینک را در برنامه نگه دارید تا همیشه نسخه تازه را دریافت کنید. بعضی برنامه‌ها یک نسخه ثابت از پلی‌لیست را ذخیره می‌کنند. در این برنامه‌ها باید پلی‌لیست را دوباره اضافه کنید تا لینک‌های تازه نمایش داده شوند.

<a id="fa-choose-content"></a>

## انتخاب محتوا و نام شبکه‌ها

<details>
<summary>پلی‌لیست‌های هر دسته‌بندی</summary>

| دسته‌بندی | تعداد شبکه‌ها | پلی‌لیست |
|:--|--:|:--|
| شبکه‌های سراسری سیما | ۲۳ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u) |
| شبکه‌های استانی | ۳۴ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u) |
| شبکه‌های برون‌مرزی | ۱۳ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u) |
| ماهواره‌ای · عمومی و متنوع | ۱۸ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u) |
| ماهواره‌ای · فیلم و سریال | ۲۸ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u) |
| ماهواره‌ای · خبر و امور جاری | ۲۷ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u) |
| ماهواره‌ای · موسیقی | ۱۶ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u) |
| ماهواره‌ای · کودک | ۱ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u) |
| ماهواره‌ای · ورزش | ۴ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u) |
| ماهواره‌ای · مستند، فرهنگ و سبک زندگی | ۷ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u) |
| مذهبی · اسلامی | ۱۷ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u) |
| مذهبی · مسیحی | ۱۱ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u) |
| مذهبی · سایر ادیان و معنوی | ۴ | [باز کردن پلی‌لیست](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u) |

</details>

<a id="fa-titles"></a>

## زبان نمایش نام شبکه‌ها

پلی‌لیست اصلی در سه نسخه دوزبانه، انگلیسی و فارسی منتشر می‌شود. نسخه‌ای را انتخاب کنید که نام شبکه‌ها را به زبان دلخواه شما نشان می‌دهد.

| زبان نام شبکه‌ها | نمونه | پلی‌لیست |
|:--|:--|:--|
| دوزبانه | `IRIB TV1 \| شبکه یک` | [باز کردن نسخه دوزبانه](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u) |
| انگلیسی | `IRIB TV1` | [باز کردن نسخه انگلیسی](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u) |
| فارسی | `شبکه یک` | [باز کردن نسخه فارسی](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u) |

اگر کیفیت یک شبکه قابل تشخیص باشد، مقدار `tvg-quality` آن با یکی از گزینه‌های `SD`، `HD`، `FHD` یا `4K` ثبت می‌شود. وضعیت فعلی شامل ۱ شبکه با کیفیت 4K، ۵۲ شبکه با کیفیت FHD، ۳۹ شبکه با کیفیت HD، ۸۹ شبکه با کیفیت SD، ۲۲ شبکه با کیفیت نامشخص است.

لوگوی ۲۰۳ شبکه داخل همین مخزن قرار دارد تا نمایش لوگوها به سایت‌هایی وابسته نباشد که ممکن است در بعضی کشورها باز نشوند. اطلاعات راهنمای برنامه‌ها یا EPG فعلاً در پلی‌لیست‌ها وجود ندارد، چون منبع قبلی دیگر فعال نیست. اگر منبع معتبر دیگری دارید، می‌توانید آن را جداگانه در برنامه پخش خود وارد کنید.

<a id="fa-smart-tv"></a>

## پخش در تلویزیون هوشمند

اگر تصویر یک شبکه فقط برای لحظه‌ای نمایش داده می‌شود، یا تلویزیون خطای مانیفست HLS نشان می‌دهد، **نسخه سازگار با تلویزیون هوشمند** را امتحان کنید. این پلی‌لیست شامل ۱۳۱ شبکه است که ساختار استریم آن‌ها روی پخش‌کننده‌های محدود بهتر کار می‌کند.

بعضی استریم‌های پلی‌لیست پشتیبان به هدر `User-Agent` یا `Referer` نیاز دارند. این هدرها در خطوط `#EXTVLCOPT` نوشته شده‌اند. برنامه‌ای که این خطوط را نادیده بگیرد ممکن است نتواند استریمی را باز کند که در VLC بدون مشکل پخش می‌شود.

کد اختیاری موجود در پوشه [`worker/`](worker) راهکار سازگاری Telewebion برای محدودیت CORS مرورگر و مقدارهای `EXT-X-MEDIA-SEQUENCE` بزرگ‌تر از ظرفیت عدد صحیح ۳۲ بیتی علامت‌دار را مستند می‌کند. افرادی که به این راهکار نیاز دارند می‌توانند کد را در حساب Cloudflare خود مستقر کنند. این پروژه Worker را مستقر نمی‌کند و هیچ‌یک از پلی‌لیست‌های منتشرشده آن از مسیر Worker استفاده نمی‌کنند.

<a id="fa-privacy"></a>

## ارتباط با سرورها و حریم خصوصی

این پروژه حساب کاربری یا تبلیغات ندارد و از ابزار آمارگیری یا ردیابی کاربران استفاده نمی‌کند. هنگام استفاده از پلی‌لیست نیز هیچ کوکی از طرف این مخزن روی دستگاه شما ذخیره نمی‌شود. سابقه تماشای شما در اختیار این پروژه یا نگهدارنده آن قرار نمی‌گیرد.

برنامه پخش ابتدا پلی‌لیست و لوگوی شبکه‌ها را از GitHub Raw دریافت می‌کند. سپس صدا و تصویر هر شبکه را مستقیماً از سرور آن شبکه یا ارائه‌دهنده استریم می‌گیرد. این سرورها اطلاعات عادی هر درخواست، از جمله آی‌پی، زمان درخواست، مسیر درخواستی و `User-Agent` را دریافت می‌کنند. بعضی لینک‌های پخش از HTTP استفاده می‌کنند، بنابراین ارتباط با آن‌ها رمزگذاری HTTPS ندارد.

این پروژه فقط اطلاعات فنی منابع عمومی، مانند مشخصات شبکه، لینک استریم، زمان بررسی، وضعیت پاسخ، تأخیر، وضوح تصویر و سابقه فعال بودن را در پوشه [`data/`](data) نگه می‌دارد. درخواست کاربران، سابقه تماشا، پیش‌نویس‌ها، فایل‌های پیوست، اطلاعات ورود و فایل‌های صوتی یا تصویری قابل بازیابی ذخیره نمی‌شوند. هنگام دنبال کردن تغییر مسیر یک استریم، ممکن است کوکی سرور تا پایان همان بررسی در حافظه بماند، اما در هیچ فایلی ذخیره نمی‌شود. فرایند بررسی برای اطمینان از سالم بودن استریم، بخش کوچکی از محتوای آن را دریافت می‌کند، ولی آن محتوا را در مخزن قرار نمی‌دهد.

برنامه IPTV شما ممکن است لینک پلی‌لیست، اطلاعات EPG، سابقه تماشا، اطلاعات حساب یا لاگ‌های فنی را روی دستگاه یا سرورهای خود ذخیره کند. تنظیمات و سیاست حریم خصوصی برنامه را بررسی کنید، چون IPTV ایران کنترلی بر این اطلاعات ندارد. درخواست‌های مربوط به مخزن و GitHub Raw طبق [بیانیه حریم خصوصی GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement) پردازش می‌شوند. درخواست‌های هر استریم نیز تابع سیاست‌های همان ارائه‌دهنده هستند.

پیش از انتشار گزارش، لاگ یا اسکرین‌شات، لینک‌های اشتراک خصوصی، نام حساب، اطلاعات ورود، توکن دسترسی، آی‌پی شخصی و سابقه تماشای نامرتبط را پاک کنید. پلی‌لیست‌های این پروژه فقط شامل لینک منابع عمومی هستند و برای استفاده از آن‌ها به اطلاعات ورود نیاز ندارید.

<a id="fa-maintained"></a>

## نحوه نگهداری و محدودیت‌ها

فرایند به‌روزرسانی در روزهای اول و پانزدهم هر ماه، ساعت ۰۴:۱۰ به وقت UTC اجرا می‌شود. این فرایند منابع عمومی را جمع‌آوری می‌کند، لینک‌های نهایی را از الگوهای شناخته‌شده ارائه‌دهندگان به دست می‌آورد و برای بررسی هر استریم بخشی از محتوای واقعی آن را دریافت می‌کند. سپس لوگوهای معتبر را در مخزن ذخیره می‌کند، پلی‌لیست‌ها و فایل README را می‌سازد و همه خروجی‌ها را پیش از انتشار بررسی می‌کند.

اگر یک استریم قبلاً کار کرده باشد، پس از سه بررسی ناموفق پیاپی تا شش هفته در پلی‌لیست باقی می‌ماند. این مهلت باعث می‌شود شبکه‌ای به دلیل قطعی موقت سرور فوراً حذف نشود. اگر لینک استریم از همه منابع حذف شود، ولی قبلاً کار کرده باشد، سابقه بررسی آن تا ۴۵ روز نگهداری می‌شود.

لینک‌های پخش، محدودیت‌های جغرافیایی و مجوز پخش شبکه‌ها ممکن است بدون اطلاع قبلی تغییر کنند. این پروژه تازه‌ترین لینک‌های عمومی بررسی‌شده را ارائه می‌کند، اما کارکرد همیشگی آن‌ها یا مجاز بودن تماشای هر شبکه در محل زندگی شما را تضمین نمی‌کند.

<a id="fa-channels"></a>

## فهرست شبکه‌ها

نسخه فعلی شامل ۲۰۳ شبکه در ۱۳ دسته‌بندی است. این شبکه‌ها از میان ۶۲۷ استریم فعال و استریم‌هایی که موقتاً دوباره بررسی می‌شوند انتخاب شده‌اند. برای دیدن جزئیات، [فهرست فارسی شبکه‌ها](CHANNELS.fa.md) یا [فهرست انگلیسی شبکه‌ها](CHANNELS.md) را باز کنید.

<a id="fa-troubleshooting"></a>

## رفع مشکل

| مشکل | راه‌حل |
|:--|:--|
| پلی‌لیست باز نمی‌شود. | لینک پلی‌لیست را در مرورگر باز کنید تا مطمئن شوید به GitHub Raw دسترسی دارید. سپس لینک را از برنامه حذف کنید و دوباره اضافه کنید. |
| یک شبکه خارج از ایران باز نمی‌شود. | بررسی کنید که شبکه در پلی‌لیست اصلی نشان `[IR]` دارد یا خیر. این شبکه‌ها فقط با آی‌پی ایران باز می‌شوند. |
| تصویر شبکه نمایش داده می‌شود، اما پخش ادامه پیدا نمی‌کند. | نسخه سازگار با تلویزیون هوشمند را امتحان کنید. اگر شبکه در VLC پخش می‌شود، ولی روی تلویزیون باز نمی‌شود، احتمالاً تلویزیون نمی‌تواند مانیفست آن استریم را پردازش کند. |
| لینک اصلی یک شبکه کار نمی‌کند. | پلی‌لیست پشتیبان را امتحان کنید. این پلی‌لیست لینک‌های جایگزین را پس از گزینه اصلی نشان می‌دهد. اگر هیچ‌کدام کار نمی‌کنند، مشکل شبکه را گزارش دهید. |
| راهنمای برنامه‌ها یا EPG نمایش داده نمی‌شود. | پلی‌لیست‌ها فعلاً اطلاعات EPG ندارند، چون منبع قبلی دیگر فعال نیست. اگر منبع معتبری دارید، آن را جداگانه در برنامه پخش وارد کنید. |
| لوگوی شبکه‌ها نمایش داده نمی‌شود. | مطمئن شوید برنامه به `raw.githubusercontent.com` دسترسی دارد، سپس اطلاعات ذخیره‌شده پلی‌لیست را در برنامه دوباره بارگیری کنید. |

<a id="fa-support"></a>

## پشتیبانی و امنیت

پیش از [ثبت مشکل در GitHub](https://github.com/shayanline/iptv-iran/issues)، راهنمای [پشتیبانی](SUPPORT.md) را بخوانید. در گزارش خود نام شبکه، پلی‌لیست، برنامه پخش، مدل دستگاه، کشور، زمان آزمایش و نتیجه مقایسه با VLC را بنویسید تا دیگران بتوانند مشکل را تکرار کنند.

جزئیات آسیب‌پذیری امنیتی را در گزارش‌های عمومی مخزن منتشر نکنید. برای ارسال گزارش خصوصی از فرم گزارش آسیب‌پذیری GitHub استفاده کنید. روش انجام این کار در [راهنمای امنیت](SECURITY.md) آمده است.

## مشارکت در پروژه

در [راهنمای مشارکت](CONTRIBUTING.md) با ساختار فایل‌ها، راه‌اندازی Python 3.13، روش اجرای بررسی‌ها، خروجی‌های تولیدشده، Worker اختیاری و فرایند انتشار آشنا می‌شوید. برای اصلاح اطلاعات شبکه‌ها، فایل `data/curated.json` را ویرایش کنید. متن README نیز از فایل `scripts/readme.py` ساخته می‌شود.

<a id="fa-credits"></a>

## منابع

این پروژه لینک‌های عمومی پخش را جمع‌آوری و بررسی می‌کند. هیچ ویدیویی را میزبانی یا بازپخش نمی‌کند و هیچ فایل صوتی یا تصویری در مخزن قرار نمی‌دهد.

- پروژه [iptv-org](https://github.com/iptv-org/iptv) و [پایگاه داده آن](https://github.com/iptv-org/database) بیشتر لینک‌های پخش، لوگوها و مشخصات شبکه‌ها را فراهم می‌کنند.
- پروژه [Free-TV/IPTV](https://github.com/Free-TV/IPTV) یک [فهرست مخصوص ایران](https://github.com/Free-TV/IPTV/blob/master/lists/iran.md) دارد که لینک‌های داخلی شبکه‌های صداوسیما را ثبت می‌کند.
- پروژه [itsyebekhe/nexa](https://github.com/itsyebekhe/nexa) یک ابزار ساخت پلی‌لیست فارسی است که ایده اولیه IPTV ایران از آن گرفته شد.
- پروژه [lashkari20/iptv](https://github.com/lashkari20/iptv) نسخه‌ای مربوط به سال ۲۰۲۲ دارد که بعضی لینک‌های آن هنوز برای آزمایش مفید هستند.

دارندگان حق پخش می‌توانند از طریق [ثبت درخواست در GitHub](https://github.com/shayanline/iptv-iran/issues) حذف یک لینک را درخواست کنند. نام شبکه، لینک موردنظر و مدرکی را ارائه کنید که نشان دهد از طرف دارنده حق پخش آن شبکه درخواست می‌دهید.

## مجوز

کد و داده‌های گردآوری‌شده این پروژه با [مجوز MIT](LICENSE) منتشر می‌شوند. نام و لوگوی شبکه‌ها، اطلاعات EPG و برنامه‌های پخش‌شده متعلق به صاحبان آن‌ها هستند. استفاده از این موارد تابع شرایط ارائه‌دهندگان مربوط است.

</div>
