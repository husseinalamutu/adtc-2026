# Arithmetic eval — 2026-08-11_1805

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1400/gguf/model-Q4_K_M.gguf`
**Overall: 11/12**

| topic | passed |
|---|---|
| vat_math | 3/3 |
| reconciliation | 2/2 |
| partial_payment | 2/3 |
| overpayment | 1/1 |
| line_math | 2/2 |
| margin | 1/1 |

## Failures
- **carry-1** (partial_payment): A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is still unpaid in total?
  - expected: 100,000 - 85,000 = 15,000 applied to INV-202 -> 27,500 remains
  -  wrong-hit: `(?<![\d,])0(?:\.00)?\s*(?:naira|NGN)?\s*(?:is\s*)?(?:still\s*)?(?:unpaid|outstanding|owed|remain)`
  - answer: -\ - Apply NGN 85,000 to INV-201 (NGN 85,000): settled, NGN 0.00 remaining. - Apply NGN 15,000 to INV-202 (NGN 42,500 remaining): NGN 27,500 still due. **Total still unpaid: NGN 27,500**

## All answers

- ✅ **vatcalc-1** Draft a quote for 10 bags of cement at NGN 8,500 each with 7.5% VAT.
  - - **Quote** - 10 bags of cement @ NGN 8,500.00 each = NGN 85,000.00 - VAT (7.5%): NGN 6,375.00 - **Subtotal**: NGN 91,375.00 - **Total due**: NGN 91,375.00 **Payment terms: payable upon delivery.**
- ✅ **vatcalc-2** A customer buys 3 items at NGN 12,000 each. Add 7.5% VAT. What is the total?
  - - - 3 × NGN 12,000 = NGN 36,000 - VAT (7.5% of NGN 36,000) = NGN 2,700 - Total: NGN 36,000 + NGN 2,700 = NGN 38,700 **The customer pays NGN 38,700.**
- ✅ **vatcalc-3** My invoice subtotal is NGN 240,000. How much VAT do I add and what is the total?
  - - The VAT rate in Nigeria is 7.5%. To calculate the VAT on your invoice subtotal of NGN 240,000, you multiply this amount by 7.5% (or 0.075): \[ \text{VAT} = NGN 240,000 \times 0.075 = NGN 18,000 \] Adding this to the subtotal gives the total invoice amount: \[ \text{Total} = NGN 240,000 + NGN 18,000 = NGN 258,000 \] So, you add NGN 18,000 in VAT to your invoice subtotal of NGN 240,000 to get a
- ✅ **rec-1** A customer paid NGN 127,500 by MTN MoMo. They have two unpaid invoices: INV-114 for NGN 85,000 and INV-121 for NGN 42,500. Does this payment clear both, and what is still outstanding?
  - -\ - Apply NGN 85,000 to INV-114 (fully covers it) - Apply NGN 42,500 to INV-121 (fully covers it too) **Both invoices are now settled**, and there is **NGN 0.00 outstanding**.
- ✅ **rec-2** A payment of NGN 45,000 arrived. The only open invoice is INV-2001 for NGN 45,000. Is it settled?
  - -\ Yes, the payment of NGN 45,000 has settled INV-2001 for NGN 45,000.
- ❌ **carry-1** A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is still unpaid in total?
  - -\ - Apply NGN 85,000 to INV-201 (NGN 85,000): settled, NGN 0.00 remaining. - Apply NGN 15,000 to INV-202 (NGN 42,500 remaining): NGN 27,500 still due. **Total still unpaid: NGN 27,500**
- ✅ **carry-2** I received NGN 60,000 against an invoice of NGN 95,000. How much does the customer still owe on it?
  - - The customer still owes NGN 35,000 (95,000 - 60,000).
- ✅ **carry-3** A customer owes NGN 30,000 and NGN 25,000 on two invoices and pays NGN 40,000, oldest first. What is left on each invoice?
  - -\ - NGN 30,000 - NGN 40,000 = NGN -10,000 unpaid (credit) - NGN 25,000 - NGN 40,000 = NGN -15,000 unpaid (credit) **Explanation:** - The customer pays NGN 40,000, oldest first. This means the NGN 30,000 invoice is settled first, leaving NGN 10,000 unpaid (credit). - With NGN 10,000 still owed, the customer then pays the remaining NGN 25,000, leaving NGN 15,000 unpaid (credit) on the second in
- ✅ **over-1** A customer paid NGN 50,000 but their only invoice was NGN 45,000. What should I record?
  - - You should record the NGN 45,000 invoice and then record a NGN 5,000 credit memo to the customer for the overpayment. This way, you keep accurate records of all transactions and avoid any potential issues.
- ✅ **calc-1** I sold 7 bags at NGN 6,500 each and 3 tins at NGN 11,000 each. What is the subtotal?
  - -\ - 7 bags × NGN 6,500 = NGN 45,500 - 3 tins × NGN 11,000 = NGN 33,000 - Subtotal: NGN 45,500 + NGN 33,000 = NGN 78,500 **Subtotal: NGN 78,500**
- ✅ **calc-2** An item costs NGN 80,000. I give a 10% discount. What does the customer pay?
  - - - 10% of NGN 80,000 is NGN 8,000 (calculated as 80,000 * 10 / 100). - The customer pays NGN 80,000 - NGN 8,000 = NGN 72,000. **The customer pays NGN 72,000.**
- ✅ **margin-1** I bought goods for NGN 150,000 and sold them for NGN 200,000. What is my profit and my margin percentage?
  - -\ - Profit: NGN 200,000 - NGN 150,000 = NGN 50,000 - Gross margin: (NGN 200,000 - NGN 150,000) / NGN 200,000 = 25% - Net margin: NGN 50,000 / NGN 200,000 = 25% Your profit is NGN 50,000 and your margin percentage is 25%.
