# Security policy

## Supported versions

The project publishes continuously from `main` and has no versioned releases.

| Source | Security support |
|:--|:--|
| The current `main` branch is supported. | Security fixes are applied here. |
| Old commits, forks, and unlisted deployments are not supported. | Their owners must apply current fixes themselves. |

## Vulnerability scope

A security report is appropriate when it concerns the repository's Python scripts, GitHub Actions workflow, generated data handling, or Cloudflare Worker code. Examples include unintended code execution, request routing that exposes private data, workflow permission abuse, credential disclosure, or unsafe handling of untrusted playlist content.

A dead stream, wrong channel, regional restriction, missing logo, EPG error, or normal playback failure is a support issue. Follow [SUPPORT.md](SUPPORT.md) and use the public issue tracker for those reports.

Report a vulnerability in a third party player, broadcaster service, GitHub, EPGShare01, or Cloudflare to that service's security team because this project cannot investigate or patch their systems.

## Send a private report

Use [GitHub private vulnerability reporting](https://github.com/shayanline/iptv-iran/security/advisories/new) to send the report to the repository maintainer. Do not open a public issue, discussion, or pull request containing vulnerability details.

Include the affected file or component, prerequisites, reproduction steps, observed impact, and a minimal proof of concept when it can be shared safely. Remove unrelated credentials, private playlist addresses, personal data, and production secrets.

If GitHub does not show the private reporting form, the private channel is temporarily unavailable. Do not publish the details. Check the security page again after the repository owner enables private vulnerability reporting.

GitHub stores and processes the report under the [GitHub General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement). The report may be visible to repository administrators and security managers through GitHub's advisory workflow.

## Disclosure and fixes

Allow the maintainer time to reproduce the issue and prepare a fix before public disclosure. The maintainer may ask for clarification through the private advisory, coordinate a release or workflow change, and credit the reporter when requested.

This community maintained project does not promise a response deadline. Risk, reproducibility, affected users, and the availability of a safe fix determine the handling order.
