# Contributing to IPTV Iran

Contributions can improve channel metadata, stream sources, playlist generation, validation, documentation, or the optional Telewebion manifest rewriter. Keep each pull request focused on one problem and explain how another person can verify the result.

## Before you start

- Search the [existing issues](https://github.com/shayanline/iptv-iran/issues) before opening a new report or pull request.
- Use [SUPPORT.md](SUPPORT.md) for playback problems and required diagnostic details.
- Use [SECURITY.md](SECURITY.md) for vulnerabilities. Never publish vulnerability details in an issue.
- Confirm that any submitted stream is publicly available from a broadcaster, its delivery network, or an established public playlist. Do not submit private subscriptions, credentials, or access tokens.

## Requirements

- Git is required to work with the repository.
- Python 3.13 is the version used by the refresh workflow. Install the pinned image dependency with `python3 -m pip install -r requirements.txt` before running the logo mirror or Python tests.
- A current Node.js release with the built in test runner and Fetch API globals is required only for changes under `worker/` or `tests/test_worker.mjs`.
- A Cloudflare account and Wrangler are required only when you intentionally deploy your own Worker.

Clone the project through the repository's [Code menu](https://github.com/shayanline/iptv-iran), enter the checkout, then confirm the Python version.

```bash
cd iptv-iran
python3 --version
```

## Source files and generated files

| Path | Responsibility | Edit by hand |
|:--|:--|:--|
| `data/curated.json` | It adds or corrects channel names, categories, streams, logos, provider slugs, and ordering. | Yes. |
| `scripts/` | It collects sources, probes streams, mirrors logos, builds outputs, and validates publication. | Yes. |
| `scripts/readme.py` | It is the source for the generated root README. | Yes. |
| `worker/` | It contains the optional Telewebion manifest rewriter and its deployment configuration. | Yes. |
| `data/status.json` | It stores generated probe history for public stream URLs. | No. |
| `data/channels.json` | It stores the generated publication model used by playlists, the README, and the channel catalogues. | No. |
| `playlists/` | It contains generated bilingual, English, Persian, category, compatibility, and unlisted playlists. | No. |
| `README.md` | It is generated from `scripts/readme.py` and `data/channels.json`. | No. |
| `CHANNELS.md` and `CHANNELS.fa.md` | They contain the generated English and Persian channel catalogues. | No. |
| `assets/logos/` | It contains mirrored logos, with a few directly maintained images where no source host exists. | Usually no. |

## Common contribution workflows

### Correct a channel or add a public stream

Edit `data/curated.json`, which survives every refresh. Validate its JSON syntax before opening a pull request.

```bash
python3 -m json.tool data/curated.json > /dev/null
```

Do not edit `data/channels.json`, playlists, README, or channel catalogues to reflect the change. The next refresh will probe the source and regenerate those files from one consistent run.

Include the channel name, public source, expected country availability, and any required public `User-Agent` or `Referer` value in the pull request. State how you confirmed that the stream shows the named channel.

### Change the README

Edit `scripts/readme.py`, then render the README and channel catalogues from the committed channel data. This command uses no network access and leaves the playlists unchanged.

```bash
PYTHONPATH=scripts python3 -c 'import build; build.build_readme(build.published_channels())'
git diff -- README.md CHANNELS.md CHANNELS.fa.md scripts/readme.py
```

Edit `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, and `worker/README.md` directly because the generator does not own them.

### Change Python logic

Run the smallest relevant test module while iterating. Run the complete Python suite when shared collection, probing, scoring, generation, or validation behaviour changes.

```bash
python3 -m unittest tests.test_build
python3 -m unittest discover -b
```

If generated data or playlists changed, validate that every language and category variant still agrees with `data/channels.json`.

```bash
python3 scripts/validate.py
```

### Change the Worker

Run its Node.js test from the repository root. Compile the Worker without deploying when JavaScript or Wrangler configuration changes.

```bash
node --test tests/test_worker.mjs
cd worker
npx wrangler deploy --dry-run
```

The dry run can download Wrangler when it is not installed locally. Review the package and version before allowing `npx` to install it.

## Full refresh

A full local refresh is rarely needed for a contribution because GitHub Actions performs publication. It makes many external requests and rewrites generated data, playlists, logos, the root README, and channel catalogues.

```bash
python3 scripts/sources.py
python3 scripts/probe.py
python3 scripts/logos.py --mirror
python3 scripts/build.py
python3 scripts/validate.py
```

The probe resolves host names through Cloudflare DNS over HTTPS by default. Set `IPTV_DNS=system` to use the operating system resolver. The probe deliberately ignores certificate validation for public stream endpoints because several Iranian delivery networks use expired or mismatched certificates, and it never sends project credentials. Do not adapt this behaviour to fetch private or authenticated resources.

Review every generated change before keeping it. A partial probe such as `python3 scripts/probe.py 20` writes `build/status.partial.json` and leaves the published status history unchanged.

## Development data and logs

- Local harvest data and partial probe results are written under the ignored `build/` directory. Remove them when they are no longer needed.
- Python scripts print progress to standard output and do not create a separate local log file. GitHub stores hosted workflow logs and run summaries under the repository's Actions settings.
- Wrangler stores local state and cache under the ignored `.wrangler/` directory. Wrangler manages Cloudflare login credentials outside this repository.
- `data/status.json`, `data/channels.json`, generated playlists, and mirrored logos are public repository content. Inspect them before committing because they contain public stream addresses and probe history.
- The project creates no development draft store, attachment store, account database, or recoverable media archive.

## Verification by changed file type

Run only checks that can detect a problem introduced by the changed files. Always inspect the complete diff and run `git diff --check` before requesting review.

| Changed files | Checks | What the checks validate |
|:--|:--|:--|
| Markdown other than `README.md` | Preview the rendered Markdown, open changed links, inspect spelling and style, then run `git diff --check`. | These checks validate structure, navigation, wording, and whitespace. |
| `scripts/readme.py`, `README.md`, or channel catalogues | Render the README and catalogues from published data, run the focused README or build tests, inspect both language sections and catalogue files, open changed links and badges, then run `git diff --check`. | These checks validate generated content, dynamic counts, links, and Markdown integrity. |
| `data/curated.json` only | Run `python3 -m json.tool data/curated.json > /dev/null`, inspect the affected records, then run `git diff --check`. | These checks validate JSON syntax and the intended curation change. |
| Generated playlists or `data/channels.json` | Run `python3 scripts/validate.py`, inspect representative entries, then run `git diff --check`. | These checks validate consistency across publication outputs. |
| Python code or tests | Run the related unit test modules, add the complete suite when shared behaviour changed, then validate generated outputs if the change affects them. | These checks validate the changed logic and its publication effects. |
| Worker JavaScript | Run `node --test tests/test_worker.mjs`. Add `npx wrangler deploy --dry-run` when deployment output can change. | These checks validate request routing and Worker compilation. |
| Wrangler or workflow configuration | Run the validator or dry run for that format, inspect permissions and triggers, then run only runtime checks affected by the configuration. | These checks validate deployment or automation wiring. |

Do not run application lint, type checks, builds, coverage, CodeScene, or SonarQube for documentation only changes because those tools cannot detect Markdown defects in this project.

## Publication

The project has no package registry, marketplace listing, version tags, or formal release artifacts. The `main` branch and its raw GitHub files are the publication target.

The refresh workflow runs at 04:10 UTC on the first and fifteenth day of every month. It also runs manually and after a push to `main` changes `scripts/**`, `data/curated.json`, or `.github/workflows/refresh.yml`. The workflow has `contents: write` permission and commits validated generated files back to `main` when their content changes.

Changes limited to community Markdown files do not trigger a refresh. A change to `scripts/readme.py` does trigger one, so include the locally rendered `README.md` in the same pull request and inspect the later workflow run for any newly generated data changes.

## Pull requests

- Keep generated files consistent with their source and avoid unrelated refresh output.
- Explain the user visible problem, the focused change, and the commands that validated it.
- Include public evidence for channel identity and availability when changing curation.
- Confirm that the diff contains no credentials, private playlist addresses, personal data, or generated media.
