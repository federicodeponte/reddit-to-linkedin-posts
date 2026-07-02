---
name: reddit-to-linkedin-posts
description: Turn a Reddit thread into LinkedIn-ready posts by extracting real pain points, limitations, and unmet needs from the conversation. Use when the user gives a Reddit URL or topic and asks for LinkedIn hooks, post ideas, content from Reddit, pain-point mining, or trend-driven posts; or when they want to repurpose a community discussion into founder-style LinkedIn content.
---

# Reddit to LinkedIn Posts

Mine a Reddit thread for authentic pain points, then turn them into LinkedIn posts that sound like lived experience rather than generic advice.

## Workflow

1. **Get the Reddit source.**
   - Accept a Reddit URL or a search topic from the user.
   - If the user gives a topic, find a relevant post (use browser/search tools) and confirm the URL before continuing.
   - Use `scripts/fetch_reddit.py` to pull the thread JSON and convert it to clean markdown.

2. **Extract pain points.**
   - Read the markdown output.
   - Identify 5–10 distinct pains, limitations, or unmet needs voiced in the thread.
   - Quote specific comments when possible; note usernames only if relevant.

3. **Generate hooks.**
   - Ask the user for 2–3 example hooks that have worked for them, or infer their style from context/vault.
   - Produce 5 viral two-line hooks that match the user's proven format, style, and tone.
   - Each hook must map to one extracted pain point.

4. **Draft LinkedIn posts.**
   - Ask the user for 3–4 example LinkedIn posts, or read them from `~/context/vault/content/linkedin-posts/` if available.
   - Write 5 LinkedIn posts, one per hook, matching the user's structure, pacing, formatting (short lines + whitespace + listicle), and voice.
   - Each post must include:
     - A strong two-line hook.
     - Skimmable body with 1 clear takeaway + 1 framework or step list.
     - A CTA that says "Repost for others to …".
   - Avoid fluff, generic advice, and repeated angles. Do not copy phrases from the examples.

5. **Save and package.**
   - Save drafts to `~/context/vault/content/linkedin-posts/<MMDD-topic-slug>/`.
   - Include `post-copy.txt` and `reddit-source.md`.

## Quick start

```bash
# From a live URL
python3 ~/.agents/skills/reddit-to-linkedin-posts/scripts/fetch_reddit.py "https://www.reddit.com/r/something/comments/..." > /tmp/thread.md

# From a saved JSON file (if Reddit blocks automated fetching)
python3 ~/.agents/skills/reddit-to-linkedin-posts/scripts/fetch_reddit.py ./thread.json > /tmp/thread.md
```

## Pain-extraction prompt

Use this prompt with the model of your choice (pass the markdown output from the script as context):

```
Here's a Reddit conversation about: [TOPIC].

Extract the pain points, limitations, and unmet needs from the thread.
Then write 5 viral hooks (each exactly 2 lines) based on those pains.

Match the format, style, and tone of these example hooks:

///Hook 1
[paste example]
///Hook 2
[paste example]
///Hook 3
[paste example]

Thread:
[PASTE MARKDOWN OUTPUT]
```

## LinkedIn-drafting prompt

```
Act like a LinkedIn ghostwriter who writes posts that get saved + shared.

Goal: Create 5 LinkedIn posts on [TOPIC].

Use my 4 example LinkedIn posts below. Match their structure, pacing, formatting (short lines + whitespace + listicle), and voice — but the ideas, wording, and hooks must be NEW.

Rules:
- Each post starts with a strong 2-line hook.
- Keep it skimmable.
- Include 1 clear takeaway + 1 framework (steps).
- End with a CTA that says "Repost for others to …".
- No fluff, no generic advice, no repeated angles across posts.
- Do NOT copy phrases or lines from the examples.

///Example Post 1
[paste example]
///Example Post 2
[paste example]
///Example Post 3
[paste example]
///Example Post 4
[paste example]

Pain points and hooks to write from:
[PASTE OUTPUT FROM PREVIOUS STEP]
```

## Output format

```
~/context/vault/content/linkedin-posts/<MMDD-topic-slug>/
├── post-copy.txt      # All 5 posts
├── reddit-source.md   # Clean thread export
└── notes.md           # Pain points + hook map (optional)
```

## Safety

- Reddit threads may contain strong opinions; verify any factual claims before repeating them.
- Do not doxx users. Paraphrase or quote anonymously unless the commenter is a public figure.
- Respect robots.txt and rate limits. If fetching fails, ask the user to paste the thread text instead.
