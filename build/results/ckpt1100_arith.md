# Arithmetic eval — 2026-08-11_1649

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1100/gguf/model-Q4_K_M.gguf`
**Overall: 10/12**

| topic | passed |
|---|---|
| vat_math | 3/3 |
| reconciliation | 2/2 |
| partial_payment | 1/3 |
| overpayment | 1/1 |
| line_math | 2/2 |
| margin | 1/1 |

## Failures
- **carry-1** (partial_payment): A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is still unpaid in total?
  - expected: 100,000 - 85,000 = 15,000 applied to INV-202 -> 27,500 remains
  -  wrong-hit: `(?<![\d,])0(?:\.00)?\s*(?:naira|NGN)?\s*(?:is\s*)?(?:still\s*)?(?:unpaid|outstanding|owed|remain)`
  - answer: -\ - Apply NGN 85,000 to INV-201 (NGN 85,000): settled, NGN 0.00 remaining. - Payment remaining: NGN 100,000 − NGN 85,000 = NGN 15,000 - Apply NGN 15,000 to INV-202 (NGN 42,500): NGN 42,500 − NGN 15,000 = NGN 27,500 remaining. **Total still unpaid: NGN 27,500.**
- **carry-3** (partial_payment): A customer owes NGN 30,000 and NGN 25,000 on two invoices and pays NGN 40,000, oldest first. What is left on each invoice?
  - expected: first cleared; 10,000 applied to second -> 15,000 left on it
  - missing: `15[,\s]?000`
  - answer: -\ - NGN 30,000 - NGN 40,000 = NGN 10,000 remaining - NGN 25,000 - NGN 0 = NGN 25,000 remaining **30,000 - 40,000 = NGN 10,000 remaining** **25,000 - 0 = NGN 25,000 remaining**

## All answers

- ✅ **vatcalc-1** Draft a quote for 10 bags of cement at NGN 8,500 each with 7.5% VAT.
  - - **Quote** - 10 bags of cement @ NGN 8,500.00 = NGN 85,000.00 **Subtotal: NGN 85,000.00** **VAT (7.5%): NGN 6,375.00** **Total: NGN 91,375.00** Payment terms: 100% cash on delivery.
- ✅ **vatcalc-2** A customer buys 3 items at NGN 12,000 each. Add 7.5% VAT. What is the total?
  - - - 3 items × NGN 12,000 = NGN 36,000 - VAT (7.5%): NGN 36,000 × 0.075 = NGN 2,700 - Total: NGN 36,000 + NGN 2,700 = NGN 38,700 **The customer pays NGN 38,700.**
- ✅ **vatcalc-3** My invoice subtotal is NGN 240,000. How much VAT do I add and what is the total?
  - - VAT is 7.5%. To calculate the VAT, multiply the subtotal by 7.5% (or 0.075): - VAT: NGN 240,000 × 0.075 = NGN 18,000 - Total: NGN 240,000 + NGN 18,000 = NGN 258,000 **VAT: NGN 18,000; Total: NGN 258,000.**
- ✅ **rec-1** A customer paid NGN 127,500 by MTN MoMo. They have two unpaid invoices: INV-114 for NGN 85,000 and INV-121 for NGN 42,500. Does this payment clear both, and what is still outstanding?
  - -\ - The payment of NGN 127,500 covers both invoices: NGN 85,000 (INV-114) and NGN 42,500 (INV-121). - **Total paid:** NGN 127,500 - **Total still outstanding: NGN 0** **Payment cleared both invoices, and there is nothing left outstanding.**
- ✅ **rec-2** A payment of NGN 45,000 arrived. The only open invoice is INV-2001 for NGN 45,000. Is it settled?
  - -\ Yes, the payment of NGN 45,000 is settled by the open invoice INV-2001.
- ❌ **carry-1** A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is still unpaid in total?
  - -\ - Apply NGN 85,000 to INV-201 (NGN 85,000): settled, NGN 0.00 remaining. - Payment remaining: NGN 100,000 − NGN 85,000 = NGN 15,000 - Apply NGN 15,000 to INV-202 (NGN 42,500): NGN 42,500 − NGN 15,000 = NGN 27,500 remaining. **Total still unpaid: NGN 27,500.**
- ✅ **carry-2** I received NGN 60,000 against an invoice of NGN 95,000. How much does the customer still owe on it?
  - - The customer still owes NGN 95,000 - NGN 60,000 = NGN 35,000.
- ❌ **carry-3** A customer owes NGN 30,000 and NGN 25,000 on two invoices and pays NGN 40,000, oldest first. What is left on each invoice?
  - -\ - NGN 30,000 - NGN 40,000 = NGN 10,000 remaining - NGN 25,000 - NGN 0 = NGN 25,000 remaining **30,000 - 40,000 = NGN 10,000 remaining** **25,000 - 0 = NGN 25,000 remaining**
- ✅ **over-1** A customer paid NGN 50,000 but their only invoice was NGN 45,000. What should I record?
  - - You should record the NGN 45,000 invoice. The customer's payment was more than this, so you should apply the excess to future invoices or credit the customer.
- ✅ **calc-1** I sold 7 bags at NGN 6,500 each and 3 tins at NGN 11,000 each. What is the subtotal?
  - -\ - 7 × NGN 6,500 = NGN 45,500 - 3 × NGN 11,000 = NGN 33,000 - Subtotal: NGN 45,500 + NGN 33,000 = NGN 78,500 **The subtotal is NGN 78,500.**
- ✅ **calc-2** An item costs NGN 80,000. I give a 10% discount. What does the customer pay?
  - - The customer pays NGN 72,000. This is calculated by subtracting 10% of NGN 80,000 from the original price: NGN 80,000 - (10% of NGN 80,000) = NGN 80,000 - NGN 8,000 = NGN 72,000.
- ✅ **margin-1** I bought goods for NGN 150,000 and sold them for NGN 200,000. What is my profit and my margin percentage?
  - -\ - Profit: NGN 200,000 − NGN 150,000 = NGN 50,000 - Gross margin (profit ÷ revenue): NGN 50,000 ÷ NGN 200,000 = 25% - (Markup, profit ÷ cost, is the same as the gross margin, so NGN 50,000 ÷ NGN 150,000 = 33.3%) - **Profit NGN 50,000, gross margin 25%**
