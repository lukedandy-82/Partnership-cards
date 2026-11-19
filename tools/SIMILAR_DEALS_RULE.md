# Similar Deals formula

Every deal gets a vertical and a segment (see `T` in similar_deals.py), e.g. Payments / checkout and wallets.

1. Candidate must be in the same vertical (hard rule). For Payments it must also be in the same segment.
2. Score = 4 (same segment) + 2 (same vertical) + 0.5 (announced since Sept 2026). Highest scores first.
3. Prefer deals that are already cards in our feed (link "our card"); otherwise use an external source.
4. 2-3 entries per deal. Each entry carries a label: "Same segment · X", "Same industry · X" or "Same approach · Y".
5. Before listing, ask: would a reader in this industry call these the same kind of deal?
