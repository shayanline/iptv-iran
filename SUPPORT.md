# Support

This project supports its curated playlists, channel metadata, generation scripts, documentation, and optional manifest rewriter. It cannot provide support for third party player accounts, subscription services, broadcaster outages, or device firmware.

## Resolve common playback problems

1. Start with the [main playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran.m3u), which contains one entry for every channel.
2. Reload or remove and add the remote playlist URL so the player does not keep an old imported copy.
3. Test the same channel in VLC 3 through **Media > Open Network Stream**. This comparison separates a source outage from a device parser problem.
4. Try the [Smart TV safe playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-compat.m3u) when playback shows one frame and stops.
5. Try the [backup playlist](https://raw.githubusercontent.com/shayanline/iptv-iran/main/playlists/iran-all-streams.m3u) when only a primary source is unavailable.
6. Check whether the channel name contains `[IR]`, which means the stream requires an Iranian IP address.

## Open a public issue

Use the [GitHub issue tracker](https://github.com/shayanline/iptv-iran/issues) for a broken or missing channel, incorrect name or category, documentation defect, or reproducible problem in project code.

Include this information:

- Provide the channel name and `tvg-id` when available.
- Provide the exact project playlist you used.
- Provide the date and time of the test in UTC.
- Provide your country, but do not provide your street address or exact location.
- Provide the player name and version, device model, operating system, and firmware version when relevant.
- Describe what happened, including any visible error message.
- State whether the channel worked in VLC and in the Smart TV safe or backup playlist.
- Add the smallest relevant log excerpt or screenshot after removing sensitive information.

Before posting, remove private subscription URLs, usernames, passwords, access tokens, personal IP addresses, account identifiers, and unrelated viewing history. Do not attach a complete private playlist or account export.

Rights holders can use the public issue tracker for removal requests. Include the channel name, affected address, and evidence that you represent the rights holder. Avoid publishing private personal documents, and offer to provide sensitive verification through a private route if the maintainer requests it.

## Use the correct external support route

- Ask the player or device vendor about account access, imports, local storage, decoder support, or firmware behaviour because IPTV Iran does not operate those products.
- The generated playlists currently have no programme guide URL. If you configure a separate guide, contact that guide provider about coverage or timing.
- Ask the broadcaster or stream provider about a service outage, geographic policy, account requirement, or content schedule.
- Use [Cloudflare Workers documentation](https://developers.cloudflare.com/workers/) for a Worker that you deployed in your own Cloudflare account.

## Report vulnerabilities privately

Do not put vulnerability details in a public issue. Follow [SECURITY.md](SECURITY.md) and use GitHub private vulnerability reporting.

This community maintained project does not offer guaranteed response or restoration times. Stream availability depends on external providers, so an accepted report may remain open until a public source becomes available.
