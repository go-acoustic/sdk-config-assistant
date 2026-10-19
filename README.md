# SDK Config Assistant

Claude skills from Acoustic for building and testing Acoustic Connect SDK Configs: the site-specific JavaScript that sends your website's signals through the Acoustic SDK.

| Skill | Runs in | What it does |
|---|---|---|
| [`sdk-config-assistant`](skills/sdk-config-assistant/README.md) | Claude Desktop, **Cowork** tab | Inspects your live website and generates a ready-to-test **SDK Config** (your site-specific signal code that drives the Acoustic SDK), with guided validation and CMS upload. |
| [`sdk-config-coding`](skills/sdk-config-coding/README.md) | **Claude Code** (CLI, VS Code, JetBrains) | Hand-edits, debugs and tests the JavaScript in an existing loader against the live site through Tampermonkey and the Chrome DevTools MCP, and prepares it for production. |

The two work as a pair: `sdk-config-assistant` generates a configuration, and `sdk-config-coding` picks it up when a signal needs code written by hand. Both ship in one plugin, so a single install gives you both — each skill only activates in the host it supports.

## Install

Both skills live in the plugin **`sdk-config-assistant`**, published from this repository.

### Claude Desktop (Cowork) — for `sdk-config-assistant`

Also needs the Claude in Chrome extension, since the skill inspects your site live in the browser.

**Add the marketplace:**
1. Open Claude Desktop and go to Cowork
2. Click **Customize**
3. Click **Plugins > Add > Add marketplace**
4. Enter as a URL: `go-acoustic/SDK-config-assistant`

**Install the plugin:**
1. Still under **Customize** in Cowork
2. Click **Plugins > Search**
3. Enter the plugin name **sdk-config-assistant**
4. Install it
5. Restart Claude Desktop to activate

Menu names occasionally change — if these steps look out of date, follow Anthropic's own guide instead: [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) (Claude Help Center).

Then, in a Cowork conversation, start the skill:

```
/sdk-config-assistant
```

### Claude Code — for `sdk-config-coding`

```bash
claude plugin marketplace add go-acoustic/SDK-config-assistant
claude plugin install sdk-config-assistant@SDK-config-assistant
```

Restart Claude Code, then run the one-time browser tooling setup (dedicated Chrome profile, the `sdk-chrome-devtools` MCP, Tampermonkey):

```
/sdk-config-coding setup
```

After that, `/sdk-config-coding` on its own opens or continues a site.

To pick up later releases, both commands are needed — the first pulls the marketplace clone, the second installs what it now sees:

```bash
claude plugin marketplace update SDK-config-assistant
claude plugin update sdk-config-assistant@SDK-config-assistant
```

## SDK vs SDK Config

- **SDK**: Acoustic's JavaScript library (`acoconnect.min.js`). It is the same for every customer and is owned, versioned and deployed to the Acoustic CDN by Acoustic. These skills never change it.
- **SDK Config**: your site-specific JavaScript that maps actions on your website to the SDK and tells it what to send to Acoustic. You own it (you can ask Acoustic to maintain it under a service contract) and host it on your own CDN, or in the Acoustic Media Library of your subscription. This is what these skills create, fix and prepare for production.

## Recommended: Acoustic Signal Validator

[Acoustic Signal Validator](https://chromewebstore.google.com/detail/cdoagpafcllkikfefplfgmabakmpceck) is Acoustic's browser extension for checking signals while you test. It captures the signals your site sends, validates each one against the Acoustic schema for that signal type, and shows valid/invalid results with field-level error messages. Validation runs in your browser.

Use it with both skills: while validating the SDK Config `sdk-config-assistant` generates, and while hand-editing signals with `sdk-config-coding`. See [Validating signals with Acoustic Signal Validator](skills/sdk-config-assistant/README.md#validating-signals-with-acoustic-signal-validator).

## Need help?

Log in to the Acoustic Support Portal and submit a case. If an `sdk-config-assistant` session hit an issue, attach the `<slug>.json` and `<slug>.analytics.json` files the skill saves locally at session close.

---

Copyright © 2026 Acoustic, L.P. All rights reserved.
