# Arithmetic eval — 2026-08-11_1519

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/gguf/model-Q4_K_M.gguf`
**Overall: 9/12**

| topic | passed |
|---|---|
| vat_math | 2/3 |
| reconciliation | 2/2 |
| partial_payment | 3/3 |
| overpayment | 1/1 |
| line_math | 1/2 |
| margin | 0/1 |

## Failures
- **vat-2** (vat_math): A customer buys 3 items at NGN 12,000 each. Add 7.5% VAT. What is the total?
  - expected: 36,000 + 2,700 = 38,700
  - missing: `2[,\s]?700`, `38[,\s]?700`
  - answer: - The total cost before VAT is NGN 36,000 (3 items * NGN 12,000 each). Adding 7.5% VAT, the total is NGN 38,400.
- **calc-1** (line_math): I sold 7 bags at NGN 6,500 each and 3 tins at NGN 11,000 each. What is the subtotal?
  - expected: 45,500 + 33,000 = 78,500
  - missing: `45[,\s]?500`, `78[,\s]?500`
  - answer: -\ The subtotal is NGN 52,500 (7 x NGN 6,500) + NGN 33,000 (3 x NGN 11,000) = NGN 85,500.
- **margin-1** (margin): I bought goods for NGN 150,000 and sold them for NGN 200,000. What is my profit and my margin percentage?
  - expected: profit 50,000; margin 25% of revenue
  - missing: `25\s*%`
  - answer: -\ Your profit is NGN 50,000 (200,000 - 150,000). To calculate the margin percentage, divide your profit by the cost price and multiply by 100. So, your margin percentage is 33.33%.

## All answers

- ✅ **vat-1** Draft a quote for 10 bags of cement at NGN 8,500 each with 7.5% VAT.
  - - **Quote** - 10 x NGN 8,500 = NGN 85,000 Subtotal: NGN 85,000 VAT (7.5%): NGN 6,375 **Total due: NGN 91,375**
- ❌ **vat-2** A customer buys 3 items at NGN 12,000 each. Add 7.5% VAT. What is the total?
  - - The total cost before VAT is NGN 36,000 (3 items * NGN 12,000 each). Adding 7.5% VAT, the total is NGN 38,400.
- ✅ **vat-3** My invoice subtotal is NGN 240,000. How much VAT do I add and what is the total?
  - - The standard VAT rate in Nigeria is 7.5%. You need to add this rate to your subtotal. The VAT amount is NGN 18,000 (7.5% of NGN 240,000). The total with VAT is NGN 258,000.
- ✅ **rec-1** A customer paid NGN 127,500 by MTN MoMo. They have two unpaid invoices: INV-114 for NGN 85,000 and INV-121 for NGN 42,500. Does this payment clear both, and what is still outstanding?
  - -\ The customer's payment of NGN 127,500 covers both invoices. INV-114 for NGN 85,000 is now settled, and INV-121 for NGN 42,500 is also paid. There is no outstanding balance.
- ✅ **rec-2** A payment of NGN 45,000 arrived. The only open invoice is INV-2001 for NGN 45,000. Is it settled?
  - -\ Yes, the payment of NGN 45,000 has settled the open invoice INV-2001.
- ✅ **carry-1** A customer paid NGN 100,000. They owe INV-201 for NGN 85,000 and INV-202 for NGN 42,500. Apply the payment to the oldest invoice first. Exactly how much is still unpaid in total?
  - -\ The customer paid NGN 100,000. This will first be applied to the oldest invoice, INV-201, which is NGN 85,000. After this payment, INV-201 is now settled, and the remaining balance is NGN 15,000. The customer then pays the next oldest invoice, INV-202, which is NGN 42,500. This settles INV-202, leaving a final balance of NGN 27,500 unpaid.
- ✅ **carry-2** I received NGN 60,000 against an invoice of NGN 95,000. How much does the customer still owe on it?
  - -\|/ The customer still owes NGN 35,000. This is calculated by subtracting the amount received (NGN 60,000) from the original invoice amount (NGN 95,000).
- ✅ **carry-3** A customer owes NGN 30,000 and NGN 25,000 on two invoices and pays NGN 40,000, oldest first. What is left on each invoice?
  - -\ The customer pays NGN 40,000, oldest first. This means they pay the NGN 25,000 first, which is on the second invoice. The remaining NGN 15,000 is then paid on the first invoice. So, the second invoice is now settled, and the first invoice is still NGN 15,000 outstanding.
- ✅ **over-1** A customer paid NGN 50,000 but their only invoice was NGN 45,000. What should I record?
  - - You should record the NGN 45,000 invoice amount in your accounting system. The extra NGN 5,000 should be noted as a credit to the customer's account or as a separate entry for future accounting purposes.
- ❌ **calc-1** I sold 7 bags at NGN 6,500 each and 3 tins at NGN 11,000 each. What is the subtotal?
  - -\ The subtotal is NGN 52,500 (7 x NGN 6,500) + NGN 33,000 (3 x NGN 11,000) = NGN 85,500.
- ✅ **calc-2** An item costs NGN 80,000. I give a 10% discount. What does the customer pay?
  - - The customer pays NGN 72,000. This is calculated by subtracting 10% of the original price from it.
- ❌ **margin-1** I bought goods for NGN 150,000 and sold them for NGN 200,000. What is my profit and my margin percentage?
  - -\ Your profit is NGN 50,000 (200,000 - 150,000). To calculate the margin percentage, divide your profit by the cost price and multiply by 100. So, your margin percentage is 33.33%.
