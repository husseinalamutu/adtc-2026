# Narration fidelity — 2026-08-11_1658

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_900/gguf/model-Q4_K_M.gguf`
**4/5 replies used only figures from the verified block.**

## ❌ narr-health
*What happened to my business this month?*

- INVENTED FIGURES: 2.395E+5

```
What happened to my business this month?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
Period: 2026-06-01 to 2026-06-30
Revenue: NGN 3,406,000.00 (-24.9% vs prior month)
Expenses: NGN 2,990,500.00 (-20.9% vs prior month)
Net: NGN 415,500.00
Gross margin: 30.3% (-7.7 pt ... (truncated)

|-\|/-\| Revenue fell by -24.9% to NGN 3,406,000.00. Expenses were down -20.9% at NGN 2,990,500.00. Gross margin was 30.3%. You have NGN 3,577,500.00 in cash. 1239,500.00 is owed by customers, with 315,500.00 overdue. The largest expense movements were an inventory purchase of NGN 2,373,000.00 (-15.5%), staff salaries of NGN 240,000.00 (+0.0%), and rent of NGN 150,000.00 (+0.0%).
```

## ✅ narr-anomaly
*Is anything unusual in my transactions?*

- 9 verified figure(s) restated, none invented

```
Is anything unusual in my transactions?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
6 transaction(s) flagged for review, most significant first:
1. [amount_outlier] 2026-05-09 NGN 340,000.00 — 55.3x the typical spread for Transport (usual is around NGN 12,000.00)
2 ... (truncated)

|-\|/-\|/-\|/ **6 transaction(s) flagged for review:**

1. NGN 340,000.00 — 55.3x the typical spread for Transport (usual is around NGN 12,000.00)
2. NGN 312,500.00 — identical amount already paid to the same payee on 2026-04-14 (1 day(s) earlier) — possible double payment
3. NGN 420,000.00 — 98% above what you usually pay this supplier for 'Inventory purchase' (usual NGN 212,250.00) — check the invoice or renegotiate
4. NGN 171,000.00 — 80% above what you usually pay this supplier for 'PVC pipe order' (usual NGN 95,000.00) — check the invoice or renegotiate
5. NGN 
```

## ✅ narr-forecast
*Will I have enough cash next month?*

- 4 verified figure(s) restated, none invented

```
Will I have enough cash next month?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
Horizon: 2026-07-01 to 2026-07-31 (projected from 5 months of trading)
Opening cash: NGN 2,700,000.00
Expected inflow: NGN 4,167,500.00
Expected outflow: NGN 3,082,500.00
Projected closin ... (truncated)

|-\|/-\| **Projected closing cash: NGN 2,700,000.00**
**Expected inflow: NGN 4,167,500.00**
**Expected outflow: NGN 3,082,500.00**
**Projected shortfall: NGN 641,000.00**

You will have NGN 2,700,000.00 at the end of the month, which is NGN 641,000.00 below your projected obligations.
```

## ✅ narr-actions
*What should I do about it?*

- 7 verified figure(s) restated, none invented

```
What should I do about it?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
Projected shortfall: NGN 641,000.00.
Recommended actions, highest recoverable value first:
1. Chase Adeyemi Construction for payment — frees NGN 684,000.00 (high confidence; invoice(s) 9 days pa ... (truncated)

|-\|/-\|/- **Projected shortfall: NGN 641,000.00.**
**Recommended actions, highest recoverable value first:**
1. Chase Adeyemi Construction for payment — frees NGN 684,000.00 (high confidence; invoice(s) 9 days past due)
2. Recover the suspected double payment from Lagos Steel Ltd — frees NGN 312,500.00 (high confidence; identical amount paid twice around 2026-04-15)
3. Clear slow-moving stock: Imported floor tiles — frees NGN 1,016,400.00 (medium confidence; 66 units worth NGN 1,452,000.00 at cost, unsold for 156 days; assumes a 30% clearance discount)
4. Query the pr
```

## ✅ narr-stock
*How much of my cash is tied up in stock?*

- 4 verified figure(s) restated, none invented

```
How much of my cash is tied up in stock?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
Stock on hand at 2026-06-15: NGN 1,985,600.00 across 4 product(s)
Cost of goods sold in the period: NGN 309,500.00
Inventory turnover: 3.79x per year (96 days of stock held)
Capital  ... (truncated)

|-\|/- Stock on hand: NGN 1,985,600.00
Inventory turnover: 3.79x per year
Capital tied up in stock unsold for 90+ days: NGN 1,452,000.00
```

