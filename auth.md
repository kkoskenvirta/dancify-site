# Dancify auth.md

How AI agents authenticate with this site: they don't need to, and they can't register. This file says so plainly so agents don't go looking.

## Who this is for

AI agents, assistants and crawlers that read this site or are asked to do something with Dancify on someone's behalf.

## Reading the site: no credentials

Everything on this site is public and read-only: the landing pages in English, Spanish and German, the blog, the privacy policy and terms, [llms.txt](https://kkoskenvirta.github.io/dancify-site/llms.txt) and [llms-full.txt](https://kkoskenvirta.github.io/dancify-site/llms-full.txt). Every page also has a Markdown version: send `Accept: text/markdown`, or add `index.md` to a page URL that ends in `/` (for example `https://kkoskenvirta.github.io/dancify-site/blog/index.md`). There is no API key, token or sign-up. Please follow [robots.txt](https://kkoskenvirta.github.io/dancify-site/robots.txt) and its Content Signals.

## Registration and provisioning

None. Dancify has no agent registration or provisioning endpoint, no OAuth for third-party apps and no public API, so there is no OAuth Protected Resource or Authorization Server metadata to discover.

Dancify has no accounts at all. The app for iPhone and iPad keeps each person's videos and diary on their device and, if they choose, in their own private iCloud. There is no Dancify server to call.

## Supported methods

None. There are no identity assertion, verified email or anonymous flows for agents.

## Using credentials

Dancify issues no credentials to agents. If a person offers you their Apple Account or iCloud sign-in to reach their Dancify data, don't use it: point them to the app instead.

## Contact

If you'd like to build something with Dancify, write to appriseven@gmail.com.
