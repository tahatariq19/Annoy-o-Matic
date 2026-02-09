## 2024-05-22 - Discord Embed Limits
**Learning:** Discord Embeds have a hard limit of 25 fields. When converting a list command to use Embeds, always implement pagination or truncation logic to avoid crashes on large datasets.
**Action:** Use a counter loop with a break condition when adding fields to an Embed.
