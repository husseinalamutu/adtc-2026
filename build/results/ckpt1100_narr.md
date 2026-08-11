# Narration fidelity — 2026-08-11_1650

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1100/gguf/model-Q4_K_M.gguf`
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

|-\|/-\|/ Revenue fell by 24.9% to NGN 3,406,000.00. Expenses were down 20.9% at NGN 2,990,500.00. Gross margin was 30.3%. You have NGN 3,577,500.00 in cash. 1239,500.00 of your receivables are still outstanding, including NGN 315,500.00 that is overdue.
```

## ✅ narr-anomaly
*Is anything unusual in my transactions?*

- 8 verified figure(s) restated, none invented

```
Is anything unusual in my transactions?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
6 transaction(s) flagged for review, most significant first:
1. [amount_outlier] 2026-05-09 NGN 340,000.00 — 55.3x the typical spread for Transport (usual is around NGN 12,000.00)
2 ... (truncated)

|-\|/-\|/-\|/ 6 transaction(s) flagged for review, most significant first:
1. NGN 340,000.00 — 55.3x the typical spread for Transport (usual is around NGN 12,000.00)
2. NGN 312,500.00 — identical amount already paid to the same payee on 2026-04-14 (1 day(s) earlier) — possible double payment
3. NGN 420,000.00 — 98% above what you usually pay this supplier for 'Inventory purchase' (usual NGN 212,250.00) — check the invoice or renegotiate
4. NGN 171,000.00 — 80% above what you usually pay this supplier for 'PVC pipe order' (usual NGN 95,000.00) — check the invoice or 
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

|-\|/-\|/ **Projected closing cash: NGN 2,700,000.00**
**Expected inflow: NGN 4,167,500.00**
**Expected outflow: NGN 3,082,500.00**
**Projected shortfall: NGN 641,000.00**

You will be short of NGN 641,000.00 next month.
```

## ✅ narr-actions
*What should I do about it?*

- 6 verified figure(s) restated, none invented

```
What should I do about it?

VERIFIED FIGURES (computed by the accounting module — use exactly these):
Projected shortfall: NGN 641,000.00.
Recommended actions, highest recoverable value first:
1. Chase Adeyemi Construction for payment — frees NGN 684,000.00 (high confidence; invoice(s) 9 days pa ... (truncated)

|-\|/-\|/- 1. Chase Adeyemi Construction for payment — frees NGN 684,000.00.
2. Recover the suspected double payment from Lagos Steel Ltd — frees NGN 312,500.00.
3. Clear slow-moving stock: Imported floor tiles — frees NGN 1,016,400.00.
4. Query the price increase with Dangote Cement Depot — frees NGN 207,750.00.
5. Query the price increase with Julius Berger Supplies — frees NGN 126,250.00.
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

|-\|/- NGN 1,452,000.00 is tied up in stock unsold for 90+ days.
```

