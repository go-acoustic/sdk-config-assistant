# SDK Config Assistant — Quick Start Guide

> **⚠️ IMPORTANT**
>
> This skill does a best effort to create an SDK Config that will work correctly on your website. It uses AI to do so and thus, can make mistakes. The results should be checked and tested before applying to your production website. The performance and stability of your website can be affected if you do not do this. If in doubt, reach out to Acoustic support for help and guidance.

## What is it?

A Cowork skill that inspects a live customer website and generates a review-ready **SDK Config** for it: the customer-specific JavaScript (`initLogSignal` setup) that maps actions on the site to the Acoustic Connect/Tealeaf SDK and tells the SDK what to send. It also produces a customer mapping file and a test plan. Used when onboarding a new customer or auditing/updating an existing SDK Config.

> **SDK vs SDK Config.** The **SDK** is Acoustic's library (`acoconnect.min.js`): the same for every customer, owned, versioned and deployed to the Acoustic CDN by Acoustic P&E. This skill never creates or changes it. The **SDK Config** is what this skill generates: customer-specific glue code that loads the SDK and calls it. The customer owns it (they can delegate its maintenance to Acoustic under a service contract) and hosts it, ideally on their own CDN, otherwise in their Connect media library. They can update it themselves in either case.

## How to start

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

Then, in a Cowork conversation, start the skill by typing `/sdk-config-assistant`

Menu names occasionally change — if these steps look out of date, follow Anthropic's own guide instead: [Use plugins in Claude](https://support.claude.com/en/articles/13837440-use-plugins-in-claude) (Claude Help Center). This skill only runs in the Cowork tab, not Claude Code or the Desktop Chat tab — it needs the Claude in Chrome extension for live site inspection.

## Need help?

If you get stuck or a signal won't validate, log in to the Acoustic Support Portal and submit a case — attach the `<slug>.json` and `<slug>.analytics.json` files the skill saves locally at session close.

## Setup

- **Cowork only.** The skill only works in Claude Cowork — it relies on the Claude in Chrome browser tool, which isn't available on other Claude surfaces.
- **Install the Chrome extension for Claude** from the Chrome Web Store, make sure it's enabled and signed in to your Anthropic account, and connect it to the tab you want inspected. Other browsers aren't supported.
- **Tampermonkey** (Chrome extension) is recommended but not required — it's the easiest way to inject and test the generated SDK Config. A no-extension alternative (Chrome DevTools Overrides) is also documented in the test guide the skill produces.
- **Acoustic Signal Validator** (recommended): [install from the Chrome Web Store](https://chromewebstore.google.com/detail/cdoagpafcllkikfefplfgmabakmpceck). It shows whether each signal passes the schema while you test, which makes the validation step quicker. See [Validating signals with Acoustic Signal Validator](#validating-signals-with-acoustic-signal-validator) below.
- **A folder must be added before the skill will start** — it's where website profiles are saved so they persist between sessions. Without one, the skill blocks at the storage step. Two ways to provide it:
  - **Recommended — a Project.** Create a Project (for example `SDK Config`), add a folder to the Project's context, and run the skill from sessions inside it. Every session in the Project sees the same profiles, so you set this up once.
  - **This session only.** Add a folder to the current session context; the next session will ask again.
- **What goes in the folder.** One subfolder per skill, and one folder per website named after its hostname: `sdk-config-assistant/<host>/` (the generated SDK Config, review and test guide), `sdk-config-assistant/profiles/` (saved website profiles), and `sdk-config-coding/<host>/` (sites handed to the coding assistant). A folder used by an earlier version (`SDK-config-assistant/outputs/…`, `SDK-config-coding/sites/…`) is moved into this layout automatically the next time the skill starts. Nothing is deleted or overwritten.

## Getting ready

At minimum, have the production URL of the site you're configuring.

If you have a staging domain, note it too — the skill uses it to safely trigger the `order` signal (test checkout) and can generate a dummy test account for you if needed. Staging isn't required; without it the skill inspects production only.

**Heads-up:** during inspection the skill adds a real item to the live production cart to capture the add-to-cart signal. This happens automatically, by design — it doesn't ask permission first.

## Using it

- Type `/sdk-config-assistant` in Claude Cowork to start.
- The flow is entirely click-driven — questions come as buttons, menus, and generated widgets. Don't type free-text answers, extra context, or try to redirect the process; the skill is built to ignore/reject open chat input mid-flow and this can derail the steps.
- The step sequence itself is fixed and won't skip or reorder, but the exact generated code varies run to run based on what the browser inspection finds on the live site each time.

## What it actually does, step by step

1. Collects customer name, production domain, and subscription tier (Pro / Premium / Ultimate). The tier is recorded on the profile but does not change how the skill runs.
2. Explores the site (page structure, dataLayer, category classification).
3. Generates code for every signal the site supports. A signal is skipped only when the site has no matching functionality — no search box, no cart, no product pages, no media — and the reason is recorded in the profile.
4. Has you inject the SDK Config via Tampermonkey (or DevTools Override) and validate each signal fires with correct data.
5. For any signal with an issue, applies a correction and has you retest — up to two correction attempts per signal (three test passes total).
6. Any signal still failing after that is escalated: greyed out in the validation matrix and flagged in the implementation review. Its code from the last correction attempt stays in the SDK Config but should be treated as not working. You can hand it to the coding assistant to fix (step 8) or ask Acoustic Services for help.
7. Outputs the final files, then offers a deployment choice on every tier — hand the SDK Config over for the customer to host on their own CDN (recommended), or upload it to the customer's Connect media library.
8. Optionally hands the SDK Config off to the sdk-config-coding skill (same plugin) at the end of the session (**Use coding assistant**, next to Close session). It copies the SDK Config, in test mode, with its report and signal config to `sdk-config-coding/<hostname>/` inside the added folder. Escalated signals are handed over, and so are signals the skill could not build at all (for example a sign-in on another host). The coding assistant runs in Claude Code — the Code tab of Claude Desktop, VS Code, or a terminal — and needs Claude Code on the user's Claude account (Cowork alone isn't enough). The handoff asks which of these the user will continue in and shows the steps for it. The handoff is one-way for code. When the coding assistant prepares the SDK Config for production it asks whether to save a short summary of what it fixed (`coding-result.json`); if the user agrees, this skill shows it the next time the profile is loaded.

## Validating signals with Acoustic Signal Validator

**Install.** Add [Acoustic Signal Validator](https://chromewebstore.google.com/detail/cdoagpafcllkikfefplfgmabakmpceck) from the Chrome Web Store. The Acoustic icon appears in the toolbar; click it to open the floating validator panel.

**Optional: use the latest schema.** The extension ships with a built-in schema and works offline. To validate against the latest signal definitions, open the panel's **Configuration** tab, enter your Acoustic **API Key** and **Subscription ID**, select your **API Region** (US East, Asia Pacific or Europe), make sure you're signed in to Acoustic in the same browser, and click **Fetch Latest Schema from API**. The schema is saved for offline use.

**Check live signals.**

1. Inject the generated SDK Config (Tampermonkey or DevTools Overrides) and open your site.
2. Walk the journey for each signal: view a product, add to cart, search, and so on.
3. The panel lists each signal as it's sent, marked valid or invalid. Expand one to see its payload and any errors, such as missing fields or wrong types. The stats bar shows Total, Valid, Invalid and Warnings; click one to filter the list. A warning means an optional field had a problem: the signal is still valid, but that field is dropped.
4. Use the result in the skill's validation matrix: **Passed** when the signal is valid with the values you expect, **Issue found** when it's invalid, choosing the reason that matches the error.
5. After a fix, click **Reset Validation State** and test again. The validator checks each distinct signal once, so a reset is needed to retest.

**Further debugging: see everything the SDK sends.** The panel shows the signal data only. When a signal looks right in the panel but still doesn't behave as expected, or you need to check the other messages the SDK sends alongside signals (for example the Tealeaf session and event data), tick **"Show the comprehensive Payload data including Tealeaf in browser console"** in the Configuration tab. Then open Chrome DevTools and select the **Acoustic Inspector** tab: it lists every captured request with its full, uncompressed payload, validated against the same schema as the panel. If DevTools was already open, close and reopen it for the tab to appear. This view is for troubleshooting; you don't need it for normal validation.

**Check saved payloads.** Set Validation Mode to **Validate signals on my machine** and upload `.json` or `.jsonl` files to check Signal API payloads before sending them.

**Panel controls:** Pause/Resume capture, Clear, Minimize, Close. A closed panel stays closed until you click the toolbar icon.

**If nothing appears:** check the page loads the SDK Config and the Acoustic SDK, and that requests reach `/collector/collectorPost` (DevTools → Network). Signals sent by the Shopify app aren't captured yet. Otherwise click Reset Validation State and refresh.

## Output

- `acoConnectSdkConfig-<domain>.js` — the SDK Config (it loads the Acoustic SDK from the Acoustic CDN)
- `acoConnectSdkConfig-<domain>.tamperMonkeyConfig.js` — Tampermonkey loader
- `<customer>-customer-signal-config.json` — reusable signal mapping, for future updates
- `<customer>-implementation-review.md` — field-by-field audit, confidence scores, open questions
- `How to test and validate the data.md` — step-by-step test walkthrough

## Resuming a session

If you close and come back, start the skill again and select **Modifying existing** — it loads your saved website profile and picks up where you left off.

## If widgets don't render ("Unable to reach visualize")

The skill uses an inline widget renderer for interactive forms and validation matrices. If that renderer is unavailable in your Cowork session, the skill falls back automatically — you always click, never type:

- **Info/status messages** (signal summary, inspection complete, session complete) — shown as plain text in chat; the flow continues without interruption.
- **Option/choice widgets** (login gates, deployment choice, reason collectors, feedback) — replaced with a standard multiple-choice question; click to select, same options.
- **The storage step** — the full explanation is shown as text, with options to re-check after adding a folder, hear it again, or stop.
- **Signal validation matrix** — the skill asks about each signal one at a time as a multiple-choice question (Passed / Issue found / Not tested / Blocked).
- **Intake forms** (customer domain, credentials) — these cannot fall back safely. The skill will stop and ask you to restart the Claude desktop app.

To restore inline widgets and avoid the per-signal one-at-a-time mode: quit and relaunch the Claude desktop app, then reopen the conversation.

## Signal scope

All signals are available on every subscription tier — Pro, Premium, and Ultimate get the same set:

| Signal | Every tier |
|---|:---:|
| identification, accountRegistered | ✅ |
| addToCart, order | ✅ |
| pageView, productView, onSiteSearch, productConfiguration | ✅ |
| richMediaInteraction | ⚠️ Skeleton only — needs a site-specific manual enhance |

Which of these get configured depends on the site, not the tier: a signal is skipped only when the site has no matching functionality (no search box, no cart, no product pages, no media).
