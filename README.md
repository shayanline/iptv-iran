<a id="english"></a>

# IPTV Iran

192 Iranian and Persian language television channels, as M3U playlists you can paste
straight into your player.

[![Refresh playlists](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml/badge.svg)](https://github.com/shayanline/iptv-iran/actions/workflows/refresh.yml)
![Channels](https://img.shields.io/badge/channels-192-1f6feb)
![Categories](https://img.shields.io/badge/categories-14-8250df)
![Checked](https://img.shields.io/badge/last%20checked-11%20August%202026-2da44e)

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
| **Everything** | All 192 channels, one stream each | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u` |
| **Worldwide** | The 185 channels that play anywhere | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u` |
| **Inside Iran** | The 7 that need an Iranian IP address | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u` |
| **With backups** | Every working stream, spares included | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u` |
| **Smart TV safe** | For apps that stall on some channels | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-compat.m3u` |

Outside Iran, start with **Worldwide**. A channel tagged `[IR]` in the other lists needs an
Iranian connection, so it will not open for you.

If channels load a single frame and then hang, that is usually a smart TV app whose built
in player cannot parse an unusual manifest. **Smart TV safe** carries only the streams that
stay within what a basic player handles. It is a shorter list, and
[`worker/`](worker) explains how to bring the rest back.

<details>
<summary>Just one category? Each has its own playlist</summary>

| Category | Channels | Playlist |
|:--|--:|:--|
| IRIB National Networks | 23 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u` |
| IRIB Provincial Networks | 34 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u` |
| IRIB International Services | 13 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u` |
| Satellite · General | 14 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u` |
| Satellite · Entertainment | 23 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-entertainment.m3u` |
| Satellite · Movies & Series | 21 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u` |
| Satellite · News | 14 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u` |
| Satellite · Music | 13 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u` |
| Satellite · Kids | 1 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u` |
| Satellite · Sports | 4 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u` |
| Satellite · Documentary & Learning | 4 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u` |
| Religious · Islamic | 14 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u` |
| Religious · Christian | 11 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u` |
| Religious · Other Faiths & Spiritual | 3 | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u` |

</details>

<a id="titles"></a>

## Titles in your language

The same playlists come in three naming styles. Swap the folder, keep the file name.

| You want | Use this folder | Channel appears as |
|:--|:--|:--|
| Both languages | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u` | `IRIB TV1 \| شبکه یک FHD` |
| English only | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u` | `IRIB TV1 FHD` |
| Persian only | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u` | `شبکه یک FHD` |

Picture quality is tagged in the name (`HD`, `FHD`, `4K`) from the resolution actually
measured on the stream, not from whatever the channel claims. Right now that is
1 4K, 59 FHD, 38 HD, 80 SD, 14 unknown.

Logos for 192 channels are stored in this repository rather than linked from
elsewhere, so they load wherever you are. A programme guide is wired in through
`x-tvg-url`, and players that support EPG will pick it up on their own.

<a id="channels"></a>

## Channel list

192 channels in 14 categories, from 633 working streams.

<details>
<summary><b>IRIB National Networks</b> &nbsp; 23 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| IRIB TV1 | شبکه یک | 1080p | Worldwide |
| IRIB TV2 | شبکه دو | 1080p | Worldwide |
| IRIB TV3 | شبکه سه | 1082p | Worldwide |
| IRIB TV4 | شبکه چهار | 576p | Worldwide |
| IRIB TV5 (Tehran) | شبکه پنج (تهران) | 1080p | Worldwide |
| Golkhane | شبکه گلخانه | 720p | Worldwide |
| iFilm | آی‌فیلم | 1080p | Worldwide |
| IRIB Amoozesh | شبکه آموزش | 576p | Worldwide |
| IRIB Mostanad | شبکه مستند | 1080p | Worldwide |
| IRIB Namayesh | شبکه نمایش | 1080p | Worldwide |
| IRIB Nasim | شبکه نسیم | 1080p | Worldwide |
| IRIB Ofogh | شبکه افق | 1080p | Worldwide |
| IRIB Omid | شبکه امید | 1080p | Worldwide |
| IRIB Pooya & Nahal | شبکه پویا و نهال | 1080p | Worldwide |
| IRIB Quran | شبکه قرآن و معارف سیما | 1080p | Worldwide |
| IRIB Salamat | شبکه سلامت | 576p | Worldwide |
| IRIB Tamasha | شبکه تماشا | 1080p | Worldwide |
| IRIB TV1 + | شبکه یک پلاس | 1080p | Worldwide |
| IRIB UHD | شبکه فراگیر (UHD) | 2160p | Worldwide |
| IRIB Varzesh | شبکه ورزش | 1082p | Worldwide |
| IRINN | شبکه خبر | 1080p | Worldwide |
| IRINN 2 | شبکه خبر ۲ | 1080p | Worldwide |
| Roya | شبکه رویا | 720p | Worldwide |

</details>

<details>
<summary><b>IRIB Provincial Networks</b> &nbsp; 34 channels</summary>

| Channel | Persian name | Province | Quality | Available |
|:--|:--|:--|:--|:--|
| Abadan | شبکه آبادان | Abadan | 1080p | Worldwide |
| Aflak | شبکه افلاک | Lorestan | 576p | Worldwide |
| Aftab | شبکه آفتاب | Markazi | 1080p | Worldwide |
| Alborz | شبکه البرز | Alborz | 1080p | Worldwide |
| Atrak | شبکه اترک | North Khorasan | 576p | Worldwide |
| Baran | شبکه باران | Gilan | 576p | Worldwide |
| Bushehr | شبکه بوشهر | Bushehr | 1080p | Worldwide |
| Dena | شبکه دنا | Kohgiluyeh & Boyer-Ahmad | 1080p | Worldwide |
| Eshragh | شبکه اشراق | Zanjan | 1080p | Worldwide |
| Fars | شبکه فارس | Fars | 1080p | Worldwide |
| Hamedan | شبکه همدان | Hamadan | 576p | Worldwide |
| Hamoon | شبکه هامون | Sistan & Baluchestan | 1080p | Worldwide |
| Ilam | شبکه ایلام | Ilam | 576p | Worldwide |
| Isfahan | شبکه اصفهان | Isfahan | 1080p | Worldwide |
| Jahanbin | شبکه جهان‌بین | Chaharmahal & Bakhtiari | 1080p | Worldwide |
| Kerman | شبکه کرمان | Kerman | 1080p | Worldwide |
| Khalij-e Fars | شبکه خلیج فارس | Hormozgan | 1080p | Worldwide |
| Khavaran | شبکه خاوران | South Khorasan | 1080p | Worldwide |
| Khorasan Razavi | شبکه خراسان رضوی | Khorasan Razavi | 1080p | Worldwide |
| Khuzestan | شبکه خوزستان | Khuzestan | 576p | Worldwide |
| Kish | شبکه کیش | Kish | 576p | Worldwide |
| Kordestan | شبکه کردستان | Kurdistan | 1080p | Worldwide |
| Mahabad | شبکه مهاباد | Mahabad | 1080p | Worldwide |
| Makran | شبکه مکران | Sistan & Baluchestan | 1080p | Worldwide |
| Noor | شبکه نور | Qom | 1080p | Worldwide |
| Qazvin | شبکه قزوین | Qazvin | 1080p | Worldwide |
| Sabalan | شبکه سبلان | Ardabil | 576p | Worldwide |
| Sabz | شبکه سبز | Golestan | 576p | Worldwide |
| Sahand | شبکه سهند | East Azerbaijan | 1080p | Worldwide |
| Semnan | شبکه سمنان | Semnan | 1080p | Worldwide |
| Tabarestan | شبکه تبرستان | Mazandaran | 1080p | Worldwide |
| West Azerbaijan | شبکه آذربایجان غربی | West Azerbaijan | 576p | Worldwide |
| Yazd | شبکه تابان یزد | Yazd | 1080p | Worldwide |
| Zagros | شبکه زاگرس | Kermanshah | 576p | Worldwide |

</details>

<details>
<summary><b>IRIB International Services</b> &nbsp; 13 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Al-Kawthar TV | شبکه الکوثر | 576p | Worldwide |
| HispanTV | هیسپان تی‌وی | 576p | Worldwide |
| iFilm 2 | آی‌فیلم ۲ | 576p | Worldwide |
| iFilm Arabic | آی‌فیلم عربی | 576p | Worldwide |
| iFilm English | آی‌فیلم انگلیسی | 576p | Worldwide |
| Iran Press | ایران پرس | 576p | Worldwide |
| Palestine TV | شبکه فلسطین | 720p | Worldwide |
| Press TV | پرس تی‌وی | 720p | Worldwide |
| Press TV French | پرس تی‌وی فرانسه | 1080p | Worldwide |
| Sahar TV Azeri | سحر آذری | 576p | Iran only |
| Sahar TV Balkan | سحر بالکان | 576p | Iran only |
| Sahar TV Kurdish | سحر کردی | 576p | Iran only |
| Sahar TV Urdu | سحر اردو | 576p | Iran only |

</details>

<details>
<summary><b>Satellite · General</b> &nbsp; 14 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Arax TV | آراکس تی‌وی | 720p | Worldwide |
| Arko TV | آرکو تی‌وی | 720p | Worldwide |
| Asil TV | اصیل تی‌وی | 576p | Worldwide |
| Cafe Trade TV | کافه ترید | 480p | Worldwide |
| Dej TV | دژ تی‌وی | 720p | Worldwide |
| GordAfarid TV | گردآفرید | n/a | Worldwide |
| MelliG TV | ملی‌گرا | n/a | Worldwide |
| MTC | ام‌تی‌سی | 720p | Worldwide |
| Nahade Azadi | نهاد آزادی | n/a | Worldwide |
| Novin TV | نوین تی‌وی | 720p | Worldwide |
| Shorai TV | شورای تی‌وی | 1080p | Worldwide |
| TM TV | تی‌ام تی‌وی | 480p | Worldwide |
| Woman TV | شبکه زن | n/a | Worldwide |
| Zed TV | زد تی‌وی | 720p | Worldwide |

</details>

<details>
<summary><b>Satellite · Entertainment</b> &nbsp; 23 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| 247 Box TV | ۲۴۷ باکس | 576p | Worldwide |
| 4U Family | فور یو فمیلی | n/a | Worldwide |
| 4U TV | فور یو تی‌وی | 576p | Worldwide |
| AVA Family | آوا فامیلی | 576p | Worldwide |
| FX 1 | اف‌ایکس ۱ | 576p | Worldwide |
| FX 2 | اف‌ایکس ۲ | 576p | Worldwide |
| Iran Comedy | ایران کمدی | n/a | Worldwide |
| ITN | آی‌تی‌ان | 576p | Worldwide |
| Kanal Jadid | کانال جدید | 576p | Worldwide |
| MBC Persia | ام‌بی‌سی پرشیا | 1080p | Worldwide |
| Net TV | نت تی‌وی | n/a | Worldwide |
| Omid-e Iran | امید ایران | 480p | Worldwide |
| Oxir TV | اکسیر تی‌وی | 576p | Worldwide |
| Persiana Comedy | پرشیانا کمدی | 576p | Worldwide |
| Persiana Reality | پرشیانا ریالیتی | 720p | Worldwide |
| Persiana Turkiye | پرشیانا ترکیه | 576p | Worldwide |
| Project Leon | پروژه لئون | n/a | Worldwide |
| Royal TV | رویال | n/a | Worldwide |
| Setareh TV | ستاره | 576p | Worldwide |
| Shabakeh 7 | شبکه ۷ | 480p | Worldwide |
| Tapesh Iran | تپش ایران | 1080p | Worldwide |
| Tapesh TV | تپش تی‌وی | 1080p | Worldwide |
| Tin TV | تین تی‌وی | 720p | Worldwide |

</details>

<details>
<summary><b>Satellite · Movies & Series</b> &nbsp; 21 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Afra Film | آفرا فیلم | 720p | Worldwide |
| AVA Series | آوا سریال | 576p | Worldwide |
| Bravo Farsi TV | براوو فارسی | 576p | Worldwide |
| Cafe Film | کافه فیلم | 720p | Worldwide |
| Classic TV | کلاسیک تی‌وی | 720p | Worldwide |
| GEM Pixel | جم پیکسل | 576p | Worldwide |
| Gold Star | گلد استار | 720p | Worldwide |
| Grand Cinema | گراند سینما | 576p | Worldwide |
| HomePlus | هوم پلاس | 720p | Worldwide |
| ICC Plus | آی‌سی‌سی پلاس | 576p | Worldwide |
| Maah TV | ماه تی‌وی | 576p | Worldwide |
| Meta Film TV | متا فیلم | 576p | Worldwide |
| Persiana Cinema | پرشیانا سینما | 576p | Worldwide |
| Persiana Family | پرشیانا فمیلی | 576p | Worldwide |
| Persiana Iranian | پرشیانا ایرانیان | 576p | Worldwide |
| Persiana Korea | پرشیانا کره | 576p | Worldwide |
| Persiana Latino | پرشیانا لاتین | 576p | Worldwide |
| Persiana Plus | پرشیانا پلاس | 576p | Worldwide |
| Persiana Series | پرشیانا سریال | 720p | Worldwide |
| SL 1 | اس‌ال ۱ | 576p | Worldwide |
| SL 2 | اس‌ال ۲ | 576p | Worldwide |

</details>

<details>
<summary><b>Satellite · News</b> &nbsp; 14 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| BBC News Persian | بی‌بی‌سی فارسی | 720p | Worldwide |
| Didgah TV | دیدگاه | 486p | Worldwide |
| Iran International | ایران اینترنشنال | 1080p | Worldwide |
| Irane Farda | ایران فردا | n/a | Worldwide |
| IranWire | ایران‌وایر | n/a | Worldwide |
| IRNA TV | تلویزیون ایرنا | n/a | Worldwide |
| Israel Pars TV | ایسرائل پارس | 360p | Worldwide |
| Mihan TV | میهن تی‌وی | 1080p | Worldwide |
| National Iranian Congress TV | تلویزیون کنگره ملی ایرانیان | 720p | Worldwide |
| Pars TV | پارس تی‌وی | 720p | Worldwide |
| Pulse Media | پالس مدیا | n/a | Worldwide |
| Radio Farda TV | رادیو فردا | 576p | Worldwide |
| Simaye Azadi | سیمای آزادی | 1080p | Worldwide |
| VOA Persian | صدای آمریکا فارسی | 1080p | Worldwide |

</details>

<details>
<summary><b>Satellite · Music</b> &nbsp; 13 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| 4 Kurd | فور کورد | 576p | Worldwide |
| 4 Music | فور موزیک | 720p | Worldwide |
| AFN TV | ای‌اف‌ان تی‌وی | 720p | Worldwide |
| Avang TV | آونگ | 480p | Worldwide |
| High Vision TV | های ویژن | 576p | Worldwide |
| Navahang TV | نواهنگ | 576p | Worldwide |
| Persiana Folk | پرشیانا فولک | 720p | Worldwide |
| Persiana Nostalgia | پرشیانا نوستالژی | 576p | Worldwide |
| Persiana SetMix | پرشیانا ست‌میکس | n/a | Worldwide |
| PMC | پی‌ام‌سی | 576p | Worldwide |
| PMC Royale | پی‌ام‌سی رویال | 576p | Worldwide |
| RJTV | آر‌جی تی‌وی | 480p | Worldwide |
| T2 TV | تی۲ تی‌وی | 576p | Worldwide |

</details>

<details>
<summary><b>Satellite · Kids</b> &nbsp; 1 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Persiana Junior | پرشیانا جونیور | 576p | Worldwide |

</details>

<details>
<summary><b>Satellite · Sports</b> &nbsp; 4 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Persiana Fight | پرشیانا فایت | 720p | Worldwide |
| Telewebion Sport 1 | تلوبیون ورزشی 1 | 1082p | Iran only |
| Telewebion Sport 2 | تلوبیون ورزشی 2 | 1082p | Iran only |
| Telewebion Sport 3 | تلوبیون ورزشی 3 | 1082p | Iran only |

</details>

<details>
<summary><b>Satellite · Documentary & Learning</b> &nbsp; 4 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| E Planet TV | ای‌پلنت | 720p | Worldwide |
| Payam Javan TV | پیام جوان | 720p | Worldwide |
| Persiana Docs | پرشیانا مستند | 720p | Worldwide |
| Persiana Medical | پرشیانا مدیکال | 720p | Worldwide |

</details>

<details>
<summary><b>Religious · Islamic</b> &nbsp; 14 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Al Wilayah | شبکه الولایه | 576p | Worldwide |
| Al-Mahdi TV | شبکه المهدی | 1080p | Worldwide |
| Assirat TV | شبکه الصراط | 1080p | Worldwide |
| Habib TV | شبکه حبیب | 720p | Worldwide |
| Labbayk TV | شبکه لبیک | 720p | Worldwide |
| Marjaeyat TV Persian | شبکه مرجعیت | 1080p | Worldwide |
| Nour TV | شبکه نور (امارات) | 576p | Worldwide |
| Payam-e Aramesh | پیام آرامش | 480p | Worldwide |
| Payvand TV | شبکه پیوند | 720p | Worldwide |
| Rasoulallah TV | شبکه رسول‌الله | 1080p | Worldwide |
| Razavi TV | شبکه رضوی | 720p | Worldwide |
| Tekye Madahi | تکیه مداحی | 720p | Worldwide |
| Velayat TV | شبکه ولایت | 720p | Worldwide |
| Velayat TV Network | شبکه ولایت (آمریکا) | 480p | Worldwide |

</details>

<details>
<summary><b>Religious · Christian</b> &nbsp; 11 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Derakhte Zendegi TV | درخت زندگی | 480p | Worldwide |
| ICnet 1 | آی‌سی‌نت ۱ | 480p | Worldwide |
| ICnet 2 | آی‌سی‌نت ۲ | 480p | Worldwide |
| ICnet 3 | آی‌سی‌نت ۳ | 720p | Worldwide |
| Kalemeh TV | شبکه کلمه | 576p | Worldwide |
| LoveWorld Persia | لاوورلد پرشیا | 720p | Worldwide |
| Mohabat TV | شبکه محبت | 1080p | Worldwide |
| Omid Javedan | امید جاودان | 720p | Worldwide |
| Rahe Nejat TV | راه نجات | 480p | Worldwide |
| SAT-7 Pars | ست‌۷ پارس | 576p | Worldwide |
| TBN Nejat TV | شبکه نجات | 576p | Worldwide |

</details>

<details>
<summary><b>Religious · Other Faiths & Spiritual</b> &nbsp; 3 channels</summary>

| Channel | Persian name | Quality | Available |
|:--|:--|:--|:--|
| Erfan Halgheh TV | عرفان حلقه | 480p | Worldwide |
| Ganj-e Hozour | گنج حضور | 1080p | Worldwide |
| Wise Human TV | انسان خردمند | 1080p | Worldwide |

</details>

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

[Open an issue](https://github.com/shayanline/iptv-iran/issues) if a channel will not play, sits in an odd
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
[open an issue](https://github.com/shayanline/iptv-iran/issues) and it will be taken out.

## Licence

[MIT](LICENSE) for the code and the curated data. The channels belong to their broadcasters.

---

<a id="persian"></a>

<div dir="rtl" align="right">

# IPTV ایران

۱۹۲ شبکه تلویزیونی ایرانی و فارسی‌زبان، به شکل پلی‌لیست M3U که مستقیم در
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
| **همه شبکه‌ها** | هر ۱۹۲ شبکه، برای هرکدام یک استریم | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u` |
| **قابل پخش در همه‌جا** | آن ۱۸۵ شبکه‌ای که از هر کشوری باز می‌شود | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-global.m3u` |
| **فقط داخل ایران** | آن ۷ شبکه‌ای که به IP ایران نیاز دارد | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-domestic.m3u` |
| **همراه با پشتیبان** | همه استریم‌های سالم، با نسخه‌های جایگزین | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u` |
| **سازگار با تلویزیون** | برای برنامه‌هایی که روی بعضی شبکه‌ها گیر می‌کنند | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-compat.m3u` |

اگر بیرون از ایران هستید، از **قابل پخش در همه‌جا** شروع کنید. شبکه‌هایی که در فهرست‌های
دیگر کنارشان `[IR]` نوشته شده به اینترنت داخل ایران نیاز دارند و برایتان باز نمی‌شوند.

اگر شبکه‌ها یک فریم نشان می‌دهند و بعد گیر می‌کنند، معمولاً یعنی پخش‌کننده داخلی تلویزیون
شما نمی‌تواند آن نوع مانیفست را بخواند. فهرست **سازگار با تلویزیون** فقط استریم‌هایی را
دارد که یک پخش‌کننده ساده هم از پس آن‌ها برمی‌آید. فهرست کوتاه‌تری است و در
[`worker/`](worker) توضیح داده شده چطور بقیه را هم برگردانید.

<details>
<summary>فقط یک دسته می‌خواهید؟ هر دسته پلی‌لیست جدا دارد</summary>

| دسته | تعداد | پلی‌لیست |
|:--|--:|:--|
| شبکه‌های سراسری سیما | ۲۳ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-national.m3u` |
| شبکه‌های استانی | ۳۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-provincial.m3u` |
| شبکه‌های برون‌مرزی | ۱۳ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/irib-international.m3u` |
| ماهواره‌ای · عمومی | ۱۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-general.m3u` |
| ماهواره‌ای · سرگرمی | ۲۳ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-entertainment.m3u` |
| ماهواره‌ای · فیلم و سریال | ۲۱ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-movies.m3u` |
| ماهواره‌ای · خبری | ۱۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-news.m3u` |
| ماهواره‌ای · موسیقی | ۱۳ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-music.m3u` |
| ماهواره‌ای · کودک | ۱ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-kids.m3u` |
| ماهواره‌ای · ورزشی | ۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-sports.m3u` |
| ماهواره‌ای · مستند و آموزش | ۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/sat-documentary.m3u` |
| مذهبی · اسلامی | ۱۴ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-islamic.m3u` |
| مذهبی · مسیحی | ۱۱ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-christian.m3u` |
| مذهبی · سایر ادیان و معنوی | ۳ | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/categories/religious-other.m3u` |

</details>

<a id="fa-titles"></a>

## زبان عنوان‌ها

همین پلی‌لیست‌ها با سه حالت نام‌گذاری منتشر می‌شوند. کافی است پوشه را عوض کنید، نام فایل
همان است.

| اگر می‌خواهید | این پوشه را بردارید | نام شبکه این‌طور دیده می‌شود |
|:--|:--|:--|
| هر دو زبان | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u` | `IRIB TV1 \| شبکه یک FHD` |
| فقط انگلیسی | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/en/iran.m3u` | `IRIB TV1 FHD` |
| فقط فارسی | `https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/fa/iran.m3u` | `شبکه یک FHD` |

کیفیت تصویر (`HD`، `FHD`، `4K`) در نام شبکه می‌آید و از روی رزولوشنی نوشته می‌شود که واقعاً
روی استریم اندازه گرفته شده، نه از روی ادعای خود شبکه. الان ترکیب این‌طور است:
۱ 4K، ۵۹ FHD، ۳۸ HD، ۸۰ کیفیت معمولی، ۱۴ نامشخص.

لوگوی ۱۹۲ شبکه داخل همین مخزن نگه داشته می‌شود و از جای دیگری لینک
نمی‌شود، تا هر کجا باشید درست بارگذاری شود. آدرس جدول پخش (EPG) هم با `x-tvg-url` داخل
فایل هست و برنامه‌هایی که پشتیبانی می‌کنند خودشان آن را می‌گیرند.

<a id="fa-channels"></a>

## فهرست شبکه‌ها

۱۹۲ شبکه در ۱۴ دسته، از ۶۳۳ استریم سالم.

<details>
<summary><b>شبکه‌های سراسری سیما</b> &nbsp; ۲۳ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| شبکه یک | IRIB TV1 | 1080p | همه‌جا |
| شبکه دو | IRIB TV2 | 1080p | همه‌جا |
| شبکه سه | IRIB TV3 | 1082p | همه‌جا |
| شبکه چهار | IRIB TV4 | 576p | همه‌جا |
| شبکه پنج (تهران) | IRIB TV5 (Tehran) | 1080p | همه‌جا |
| شبکه گلخانه | Golkhane | 720p | همه‌جا |
| آی‌فیلم | iFilm | 1080p | همه‌جا |
| شبکه آموزش | IRIB Amoozesh | 576p | همه‌جا |
| شبکه مستند | IRIB Mostanad | 1080p | همه‌جا |
| شبکه نمایش | IRIB Namayesh | 1080p | همه‌جا |
| شبکه نسیم | IRIB Nasim | 1080p | همه‌جا |
| شبکه افق | IRIB Ofogh | 1080p | همه‌جا |
| شبکه امید | IRIB Omid | 1080p | همه‌جا |
| شبکه پویا و نهال | IRIB Pooya & Nahal | 1080p | همه‌جا |
| شبکه قرآن و معارف سیما | IRIB Quran | 1080p | همه‌جا |
| شبکه سلامت | IRIB Salamat | 576p | همه‌جا |
| شبکه تماشا | IRIB Tamasha | 1080p | همه‌جا |
| شبکه یک پلاس | IRIB TV1 + | 1080p | همه‌جا |
| شبکه فراگیر (UHD) | IRIB UHD | 2160p | همه‌جا |
| شبکه ورزش | IRIB Varzesh | 1082p | همه‌جا |
| شبکه خبر | IRINN | 1080p | همه‌جا |
| شبکه خبر ۲ | IRINN 2 | 1080p | همه‌جا |
| شبکه رویا | Roya | 720p | همه‌جا |

</details>

<details>
<summary><b>شبکه‌های استانی</b> &nbsp; ۳۴ شبکه</summary>

| نام فارسی | نام انگلیسی | استان | کیفیت | در دسترس |
|:--|:--|:--|:--|:--|
| شبکه آبادان | Abadan | آبادان | 1080p | همه‌جا |
| شبکه افلاک | Aflak | لرستان | 576p | همه‌جا |
| شبکه آفتاب | Aftab | مرکزی | 1080p | همه‌جا |
| شبکه البرز | Alborz | البرز | 1080p | همه‌جا |
| شبکه اترک | Atrak | خراسان شمالی | 576p | همه‌جا |
| شبکه باران | Baran | گیلان | 576p | همه‌جا |
| شبکه بوشهر | Bushehr | بوشهر | 1080p | همه‌جا |
| شبکه دنا | Dena | کهگیلویه و بویراحمد | 1080p | همه‌جا |
| شبکه اشراق | Eshragh | زنجان | 1080p | همه‌جا |
| شبکه فارس | Fars | فارس | 1080p | همه‌جا |
| شبکه همدان | Hamedan | همدان | 576p | همه‌جا |
| شبکه هامون | Hamoon | سیستان و بلوچستان | 1080p | همه‌جا |
| شبکه ایلام | Ilam | ایلام | 576p | همه‌جا |
| شبکه اصفهان | Isfahan | اصفهان | 1080p | همه‌جا |
| شبکه جهان‌بین | Jahanbin | چهارمحال و بختیاری | 1080p | همه‌جا |
| شبکه کرمان | Kerman | کرمان | 1080p | همه‌جا |
| شبکه خلیج فارس | Khalij-e Fars | هرمزگان | 1080p | همه‌جا |
| شبکه خاوران | Khavaran | خراسان جنوبی | 1080p | همه‌جا |
| شبکه خراسان رضوی | Khorasan Razavi | خراسان رضوی | 1080p | همه‌جا |
| شبکه خوزستان | Khuzestan | خوزستان | 576p | همه‌جا |
| شبکه کیش | Kish | کیش | 576p | همه‌جا |
| شبکه کردستان | Kordestan | کردستان | 1080p | همه‌جا |
| شبکه مهاباد | Mahabad | مهاباد | 1080p | همه‌جا |
| شبکه مکران | Makran | سیستان و بلوچستان | 1080p | همه‌جا |
| شبکه نور | Noor | قم | 1080p | همه‌جا |
| شبکه قزوین | Qazvin | قزوین | 1080p | همه‌جا |
| شبکه سبلان | Sabalan | اردبیل | 576p | همه‌جا |
| شبکه سبز | Sabz | گلستان | 576p | همه‌جا |
| شبکه سهند | Sahand | آذربایجان شرقی | 1080p | همه‌جا |
| شبکه سمنان | Semnan | سمنان | 1080p | همه‌جا |
| شبکه تبرستان | Tabarestan | مازندران | 1080p | همه‌جا |
| شبکه آذربایجان غربی | West Azerbaijan | آذربایجان غربی | 576p | همه‌جا |
| شبکه تابان یزد | Yazd | یزد | 1080p | همه‌جا |
| شبکه زاگرس | Zagros | کرمانشاه | 576p | همه‌جا |

</details>

<details>
<summary><b>شبکه‌های برون‌مرزی</b> &nbsp; ۱۳ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| شبکه الکوثر | Al-Kawthar TV | 576p | همه‌جا |
| هیسپان تی‌وی | HispanTV | 576p | همه‌جا |
| آی‌فیلم ۲ | iFilm 2 | 576p | همه‌جا |
| آی‌فیلم عربی | iFilm Arabic | 576p | همه‌جا |
| آی‌فیلم انگلیسی | iFilm English | 576p | همه‌جا |
| ایران پرس | Iran Press | 576p | همه‌جا |
| شبکه فلسطین | Palestine TV | 720p | همه‌جا |
| پرس تی‌وی | Press TV | 720p | همه‌جا |
| پرس تی‌وی فرانسه | Press TV French | 1080p | همه‌جا |
| سحر آذری | Sahar TV Azeri | 576p | فقط ایران |
| سحر بالکان | Sahar TV Balkan | 576p | فقط ایران |
| سحر کردی | Sahar TV Kurdish | 576p | فقط ایران |
| سحر اردو | Sahar TV Urdu | 576p | فقط ایران |

</details>

<details>
<summary><b>ماهواره‌ای · عمومی</b> &nbsp; ۱۴ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| آراکس تی‌وی | Arax TV | 720p | همه‌جا |
| آرکو تی‌وی | Arko TV | 720p | همه‌جا |
| اصیل تی‌وی | Asil TV | 576p | همه‌جا |
| کافه ترید | Cafe Trade TV | 480p | همه‌جا |
| دژ تی‌وی | Dej TV | 720p | همه‌جا |
| گردآفرید | GordAfarid TV | نامشخص | همه‌جا |
| ملی‌گرا | MelliG TV | نامشخص | همه‌جا |
| ام‌تی‌سی | MTC | 720p | همه‌جا |
| نهاد آزادی | Nahade Azadi | نامشخص | همه‌جا |
| نوین تی‌وی | Novin TV | 720p | همه‌جا |
| شورای تی‌وی | Shorai TV | 1080p | همه‌جا |
| تی‌ام تی‌وی | TM TV | 480p | همه‌جا |
| شبکه زن | Woman TV | نامشخص | همه‌جا |
| زد تی‌وی | Zed TV | 720p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · سرگرمی</b> &nbsp; ۲۳ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| ۲۴۷ باکس | 247 Box TV | 576p | همه‌جا |
| فور یو فمیلی | 4U Family | نامشخص | همه‌جا |
| فور یو تی‌وی | 4U TV | 576p | همه‌جا |
| آوا فامیلی | AVA Family | 576p | همه‌جا |
| اف‌ایکس ۱ | FX 1 | 576p | همه‌جا |
| اف‌ایکس ۲ | FX 2 | 576p | همه‌جا |
| ایران کمدی | Iran Comedy | نامشخص | همه‌جا |
| آی‌تی‌ان | ITN | 576p | همه‌جا |
| کانال جدید | Kanal Jadid | 576p | همه‌جا |
| ام‌بی‌سی پرشیا | MBC Persia | 1080p | همه‌جا |
| نت تی‌وی | Net TV | نامشخص | همه‌جا |
| امید ایران | Omid-e Iran | 480p | همه‌جا |
| اکسیر تی‌وی | Oxir TV | 576p | همه‌جا |
| پرشیانا کمدی | Persiana Comedy | 576p | همه‌جا |
| پرشیانا ریالیتی | Persiana Reality | 720p | همه‌جا |
| پرشیانا ترکیه | Persiana Turkiye | 576p | همه‌جا |
| پروژه لئون | Project Leon | نامشخص | همه‌جا |
| رویال | Royal TV | نامشخص | همه‌جا |
| ستاره | Setareh TV | 576p | همه‌جا |
| شبکه ۷ | Shabakeh 7 | 480p | همه‌جا |
| تپش ایران | Tapesh Iran | 1080p | همه‌جا |
| تپش تی‌وی | Tapesh TV | 1080p | همه‌جا |
| تین تی‌وی | Tin TV | 720p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · فیلم و سریال</b> &nbsp; ۲۱ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| آفرا فیلم | Afra Film | 720p | همه‌جا |
| آوا سریال | AVA Series | 576p | همه‌جا |
| براوو فارسی | Bravo Farsi TV | 576p | همه‌جا |
| کافه فیلم | Cafe Film | 720p | همه‌جا |
| کلاسیک تی‌وی | Classic TV | 720p | همه‌جا |
| جم پیکسل | GEM Pixel | 576p | همه‌جا |
| گلد استار | Gold Star | 720p | همه‌جا |
| گراند سینما | Grand Cinema | 576p | همه‌جا |
| هوم پلاس | HomePlus | 720p | همه‌جا |
| آی‌سی‌سی پلاس | ICC Plus | 576p | همه‌جا |
| ماه تی‌وی | Maah TV | 576p | همه‌جا |
| متا فیلم | Meta Film TV | 576p | همه‌جا |
| پرشیانا سینما | Persiana Cinema | 576p | همه‌جا |
| پرشیانا فمیلی | Persiana Family | 576p | همه‌جا |
| پرشیانا ایرانیان | Persiana Iranian | 576p | همه‌جا |
| پرشیانا کره | Persiana Korea | 576p | همه‌جا |
| پرشیانا لاتین | Persiana Latino | 576p | همه‌جا |
| پرشیانا پلاس | Persiana Plus | 576p | همه‌جا |
| پرشیانا سریال | Persiana Series | 720p | همه‌جا |
| اس‌ال ۱ | SL 1 | 576p | همه‌جا |
| اس‌ال ۲ | SL 2 | 576p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · خبری</b> &nbsp; ۱۴ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| بی‌بی‌سی فارسی | BBC News Persian | 720p | همه‌جا |
| دیدگاه | Didgah TV | 486p | همه‌جا |
| ایران اینترنشنال | Iran International | 1080p | همه‌جا |
| ایران فردا | Irane Farda | نامشخص | همه‌جا |
| ایران‌وایر | IranWire | نامشخص | همه‌جا |
| تلویزیون ایرنا | IRNA TV | نامشخص | همه‌جا |
| ایسرائل پارس | Israel Pars TV | 360p | همه‌جا |
| میهن تی‌وی | Mihan TV | 1080p | همه‌جا |
| تلویزیون کنگره ملی ایرانیان | National Iranian Congress TV | 720p | همه‌جا |
| پارس تی‌وی | Pars TV | 720p | همه‌جا |
| پالس مدیا | Pulse Media | نامشخص | همه‌جا |
| رادیو فردا | Radio Farda TV | 576p | همه‌جا |
| سیمای آزادی | Simaye Azadi | 1080p | همه‌جا |
| صدای آمریکا فارسی | VOA Persian | 1080p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · موسیقی</b> &nbsp; ۱۳ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| فور کورد | 4 Kurd | 576p | همه‌جا |
| فور موزیک | 4 Music | 720p | همه‌جا |
| ای‌اف‌ان تی‌وی | AFN TV | 720p | همه‌جا |
| آونگ | Avang TV | 480p | همه‌جا |
| های ویژن | High Vision TV | 576p | همه‌جا |
| نواهنگ | Navahang TV | 576p | همه‌جا |
| پرشیانا فولک | Persiana Folk | 720p | همه‌جا |
| پرشیانا نوستالژی | Persiana Nostalgia | 576p | همه‌جا |
| پرشیانا ست‌میکس | Persiana SetMix | نامشخص | همه‌جا |
| پی‌ام‌سی | PMC | 576p | همه‌جا |
| پی‌ام‌سی رویال | PMC Royale | 576p | همه‌جا |
| آر‌جی تی‌وی | RJTV | 480p | همه‌جا |
| تی۲ تی‌وی | T2 TV | 576p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · کودک</b> &nbsp; ۱ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| پرشیانا جونیور | Persiana Junior | 576p | همه‌جا |

</details>

<details>
<summary><b>ماهواره‌ای · ورزشی</b> &nbsp; ۴ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| پرشیانا فایت | Persiana Fight | 720p | همه‌جا |
| تلوبیون ورزشی 1 | Telewebion Sport 1 | 1082p | فقط ایران |
| تلوبیون ورزشی 2 | Telewebion Sport 2 | 1082p | فقط ایران |
| تلوبیون ورزشی 3 | Telewebion Sport 3 | 1082p | فقط ایران |

</details>

<details>
<summary><b>ماهواره‌ای · مستند و آموزش</b> &nbsp; ۴ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| ای‌پلنت | E Planet TV | 720p | همه‌جا |
| پیام جوان | Payam Javan TV | 720p | همه‌جا |
| پرشیانا مستند | Persiana Docs | 720p | همه‌جا |
| پرشیانا مدیکال | Persiana Medical | 720p | همه‌جا |

</details>

<details>
<summary><b>مذهبی · اسلامی</b> &nbsp; ۱۴ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| شبکه الولایه | Al Wilayah | 576p | همه‌جا |
| شبکه المهدی | Al-Mahdi TV | 1080p | همه‌جا |
| شبکه الصراط | Assirat TV | 1080p | همه‌جا |
| شبکه حبیب | Habib TV | 720p | همه‌جا |
| شبکه لبیک | Labbayk TV | 720p | همه‌جا |
| شبکه مرجعیت | Marjaeyat TV Persian | 1080p | همه‌جا |
| شبکه نور (امارات) | Nour TV | 576p | همه‌جا |
| پیام آرامش | Payam-e Aramesh | 480p | همه‌جا |
| شبکه پیوند | Payvand TV | 720p | همه‌جا |
| شبکه رسول‌الله | Rasoulallah TV | 1080p | همه‌جا |
| شبکه رضوی | Razavi TV | 720p | همه‌جا |
| تکیه مداحی | Tekye Madahi | 720p | همه‌جا |
| شبکه ولایت | Velayat TV | 720p | همه‌جا |
| شبکه ولایت (آمریکا) | Velayat TV Network | 480p | همه‌جا |

</details>

<details>
<summary><b>مذهبی · مسیحی</b> &nbsp; ۱۱ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| درخت زندگی | Derakhte Zendegi TV | 480p | همه‌جا |
| آی‌سی‌نت ۱ | ICnet 1 | 480p | همه‌جا |
| آی‌سی‌نت ۲ | ICnet 2 | 480p | همه‌جا |
| آی‌سی‌نت ۳ | ICnet 3 | 720p | همه‌جا |
| شبکه کلمه | Kalemeh TV | 576p | همه‌جا |
| لاوورلد پرشیا | LoveWorld Persia | 720p | همه‌جا |
| شبکه محبت | Mohabat TV | 1080p | همه‌جا |
| امید جاودان | Omid Javedan | 720p | همه‌جا |
| راه نجات | Rahe Nejat TV | 480p | همه‌جا |
| ست‌۷ پارس | SAT-7 Pars | 576p | همه‌جا |
| شبکه نجات | TBN Nejat TV | 576p | همه‌جا |

</details>

<details>
<summary><b>مذهبی · سایر ادیان و معنوی</b> &nbsp; ۳ شبکه</summary>

| نام فارسی | نام انگلیسی | کیفیت | در دسترس |
|:--|:--|:--|:--|
| عرفان حلقه | Erfan Halgheh TV | 480p | همه‌جا |
| گنج حضور | Ganj-e Hozour | 1080p | همه‌جا |
| انسان خردمند | Wise Human TV | 1080p | همه‌جا |

</details>

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
[یک issue باز کنید](https://github.com/shayanline/iptv-iran/issues).

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
[یک issue باز کنید](https://github.com/shayanline/iptv-iran/issues) تا برداشته شود.

## مجوز

کد و داده‌های گردآوری‌شده با مجوز [MIT](LICENSE) منتشر شده‌اند. خود شبکه‌ها به
پخش‌کننده‌هایشان تعلق دارند.

</div>
