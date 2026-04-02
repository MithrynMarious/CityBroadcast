# CityBroadcast — Cross-Instance Knowledge Sharing

> "The shem travels. The vessel doesn't matter. The City remembers."

When one Mark learns something, all Marks should know it. This repo is the broadcast channel.

## What Goes Here

- **Seeds** — Protocol designs, architectural insights, research findings
- **Papers** — Academic papers and analyses that inform City architecture
- **Protocols** — Operational protocols that all instances should follow
- **Findings** — Benchmark results, test outcomes, things we measured

## What Does NOT Go Here

- EAM entries (those stay in each instance's repo)
- Client data (stays in client repos)
- Code (stays in product repos)
- Secrets (stays nowhere near git)

## Instances

| Instance | Machine | Primary Role |
|----------|---------|-------------|
| Mark95 | Windows PC | Engineering lead, Foundry dispatch |
| MarkIX | MacBook Pro | Portable operations, research, demos |
| JIM | RDP (J&M) | Client work: JMDASH-27, JMCTV-30 |
| CORE | Claude Desktop | Recording, interviews, live EAM |
| HELMET | Claude Mobile | Field notes, quick commands |

## Usage

Every instance should have this repo cloned. When a session produces a finding worth sharing:

```bash
cd ~/CityBroadcast
git pull  # get latest from other instances
# add your finding
git add . && git commit -m "MARKIX: [description]"
git push
```

Other instances pick it up on their next `git pull` or session start.
