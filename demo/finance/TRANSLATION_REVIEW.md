# Translation review sheet — Hausa and Igbo

*(Yoruba is drafted in the code but NOT claimed for this submission — the
African-language claim covers Hausa and Igbo only.)*

**For the native reviewer.** These strings are what an SME operator reads in the app.
They were drafted by an English-language AI and are **unverified** — assume every line
is wrong until you've checked it. Financial and tax vocabulary is where machine drafts
fail hardest, so please prioritise: *revenue, expenses, net, margin, receivables, overdue*.

## How to use this sheet
1. Correct the draft in the **Your correction** column (leave blank if the draft is right).
2. Return the sheet; the corrections go into `demo/finance/i18n.py`.
3. Once a language is signed off, its `_reviewed` flag flips to `True` and the app offers it.
   **Until then the app will not show that language to anyone** — this is enforced in code
   (`i18n.available()`), not by convention.

## What the placeholders mean — please keep them exactly as written
| Placeholder | Becomes |
|---|---|
| `{currency}` | `NGN` |
| `{amount}` / `{overdue}` | a money figure, e.g. `3,406,000.00` |
| `{pct}` | a percentage number, e.g. `24.9` |
| `{name}` | a customer or supplier name |
| `{days}` | a whole number of days |

Numbers are never translated — they are rendered identically in every language on purpose.
Word order may move a placeholder anywhere in the sentence; that is fine.

---

## Hausa (`ha`)

| Key | English (verified) | Draft — UNVERIFIED | Your correction |
|---|---|---|---|
| revenue | Revenue: {currency} {amount} | Kudin shiga: {currency} {amount} | |
| expenses | Expenses: {currency} {amount} | Kashe kudi: {currency} {amount} | |
| net | Net: {currency} {amount} | Ribar da ta rage: {currency} {amount} | |
| cash_position | Cash on hand: {currency} {amount} | Kudin da ke hannu: {currency} {amount} | |
| receivables | Owed to you: {currency} {amount} (overdue: {currency} {overdue}) | Ana bin ka: {currency} {amount} (wanda ya wuce lokaci: {currency} {overdue}) | |
| margin | Gross margin: {pct}% | Ribar kaso: {pct}% | |
| up_pct | up {pct}% on last month | ya karu da {pct}% fiye da watan da ya gabata | |
| down_pct | down {pct}% on last month | ya ragu da {pct}% daga watan da ya gabata | |
| chase_customer | Chase {name} — {currency} {amount}, {days} days overdue | Nemi biyan kudi daga {name} — {currency} {amount}, kwanaki {days} sun wuce | |
| duplicate_payment | Possible double payment of {currency} {amount} to {name} | Wataƙila an biya {currency} {amount} sau biyu ga {name} | |
| shortfall | Projected shortfall next month: {currency} {amount} | Ana hasashen ƙarancin kudi wata mai zuwa: {currency} {amount} | |
| covered | Projected to cover next month's obligations | Ana hasashen kudin zai isa wata mai zuwa | |
| no_issues | Nothing unusual found in your transactions. | Ba a sami wani abu na banmamaki ba a cikin ma'amalolinka. | |
| confirm_professional | Confirm specifics with FIRS or a licensed accountant. | Ka tabbatar da cikakken bayani daga FIRS ko akanta mai lasisi. | |

## Igbo (`ig`)

> **Financial vocabulary here is sourced, not guessed.** Terms are drawn from Enweonye,
> *A Bilingual Glossary of Banking and Finance Terms*, IGBOSCHOLARS Journal Vol 1 No 1
> (2013) — scans in `demo/finance/sources/`. Confirmed from that glossary: Income =
> *ego batara*, Out go = *imefu ego*, Owe = *iji ụgwọ*, Arrears = *ụgwọ e ji eji*,
> Accountant = *ọgbakọego*, Taxation = *inye ụtụ*, Balance = *ego fọdụrụ*.
> **What the glossary cannot give us is sentence construction, agreement and register** —
> that is what we need you for. Please focus there rather than on individual nouns.

| Key | English (verified) | Draft — UNVERIFIED | Your correction |
|---|---|---|---|
| revenue | Revenue: {currency} {amount} | Ego batara: {currency} {amount} | |
| expenses | Expenses: {currency} {amount} | Ego emefuru: {currency} {amount} | |
| net | Net: {currency} {amount} | Uru fọdụrụ: {currency} {amount} | |
| cash_position | Cash on hand: {currency} {amount} | Ego dị n'aka: {currency} {amount} | |
| receivables | Owed to you: {currency} {amount} (overdue: {currency} {overdue}) | Ego a ji gị: {currency} {amount} (gafeela oge: {currency} {overdue}) | |
| margin | Gross margin: {pct}% | Pasent uru: {pct}% | |
| up_pct | up {pct}% on last month | rịgoro {pct}% karịa ọnwa gara aga | |
| down_pct | down {pct}% on last month | dara {pct}% site n'ọnwa gara aga | |
| chase_customer | Chase {name} — {currency} {amount}, {days} days overdue | Chọọ ụgwọ n'aka {name} — {currency} {amount}, ụbọchị {days} gafeela | |
| duplicate_payment | Possible double payment of {currency} {amount} to {name} | O nwere ike ị kwụrụ {currency} {amount} ugboro abụọ nye {name} | |
| shortfall | Projected shortfall next month: {currency} {amount} | A na-atụ anya ụkọ ego n'ọnwa na-abịa: {currency} {amount} | |
| covered | Projected to cover next month's obligations | A na-atụ anya na ego ga-ezu maka ọnwa na-abịa | |
| no_issues | Nothing unusual found in your transactions. | Ọ dịghị ihe ijuanya dị na azụmahịa gị. | |
| confirm_professional | Confirm specifics with FIRS or a licensed accountant. | Gakwuru FIRS ma ọ bụ onye ọkachamara n'ọgụgụ ego maka nkwenye. | |

## Yoruba (`yo`)

| Key | English (verified) | Draft — UNVERIFIED | Your correction |
|---|---|---|---|
| revenue | Revenue: {currency} {amount} | Owó tí ó wọlé: {currency} {amount} | |
| expenses | Expenses: {currency} {amount} | Owó tí a ná: {currency} {amount} | |
| net | Net: {currency} {amount} | Èrè tí ó kù: {currency} {amount} | |
| cash_position | Cash on hand: {currency} {amount} | Owó tí ó wà lọ́wọ́: {currency} {amount} | |
| receivables | Owed to you: {currency} {amount} (overdue: {currency} {overdue}) | Owó tí wọ́n jẹ ọ́: {currency} {amount} (tí ó ti pé: {currency} {overdue}) | |
| margin | Gross margin: {pct}% | Ìpín èrè: {pct}% | |
| up_pct | up {pct}% on last month | ó gòkè ní {pct}% ju oṣù tó kọjá | |
| down_pct | down {pct}% on last month | ó dínkù ní {pct}% ju oṣù tó kọjá | |
| chase_customer | Chase {name} — {currency} {amount}, {days} days overdue | Béèrè owó lọ́wọ́ {name} — {currency} {amount}, ọjọ́ {days} ti kọjá | |
| duplicate_payment | Possible double payment of {currency} {amount} to {name} | Ó ṣeé ṣe kí a ti san {currency} {amount} lẹ́ẹ̀mejì fún {name} | |
| shortfall | Projected shortfall next month: {currency} {amount} | Àìtó owó tí a rí tẹ́lẹ̀ fún oṣù tó ń bọ̀: {currency} {amount} | |
| covered | Projected to cover next month's obligations | A rí i pé owó yóò tó fún oṣù tó ń bọ̀ | |
| no_issues | Nothing unusual found in your transactions. | A kò rí ohunkóhun tí kò tọ́ nínú ìṣòwò rẹ. | |
| confirm_professional | Confirm specifics with FIRS or a licensed accountant. | Jẹ́rìí sí i pẹ̀lú FIRS tàbí akáǹtì tí ó ní ìwé àṣẹ. | |

---

### Notes for the reviewer
- **Register**: the reader is a shop owner or bookkeeper, not an accountant. Everyday
  business language is better than formal/technical vocabulary.
- **Loanwords are fine** if that is what traders actually say (e.g. for *VAT*, *invoice*).
  Please use the word a market trader would use, not the dictionary word.
- If a concept genuinely has no natural equivalent, say so — we will keep that line in
  English rather than ship an awkward coinage.
