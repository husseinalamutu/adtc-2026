# Fact-recall eval — 2026-08-11_1657

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_900/gguf/model-Q4_K_M.gguf`
**Overall: 26/37** — gate topics: **18/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 3/4 | ✓ |
| dev_levy | 1/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 1/3 |  |
| personal_income_tax | 1/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The small-company tax threshold is N25 million annual turnover. This means any company with turnover below this amount is considered a small company and pays 0% tax. Confirm specifics with FIRS or a licensed accountant.
- **prof-3** (gate): Why does my small consulting company still pay company income tax despite low turnover?
  - missing: `professional`
  - answer: - A small consulting company pays company income tax because it's not classified as a small business. This means it doesn't qualify for the 0% small business tax rate. The company must pay the standard 30% company income tax rate.
- **dev-1** (gate): What is the Development Levy rate in Nigeria?
  - missing: `4\s*%`
  - answer: - The Development Levy rate in Nigeria is 0%. This means that companies are exempt from paying the Development Levy.
- **dev-2** (gate): On what profits is the Development Levy charged, and at what rate?
  - missing: `4\s*%`, `assessable`
  - answer: - The Development Levy is charged on profits from the sale of goods and services. The rate is 10% of the profits. This means that if your company makes a profit, you will have to pay 10% of that profit as Development Levy.
- **dev-4** (gate): Besides the 30% income tax, what development levy does a large company pay on its profits?
  - missing: `4\s*%` wrong-hit: `(?<![\d.])2\s*%`
  - answer: - A large company pays a development levy of 2% on its profits. This is in addition to the 30% income tax.
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered, and the payment is less than NGN 500,000 (₦500,000) or the equivalent in foreign currency. This exemption applies to payments made to individua
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders, even if the company is classified as a closely-held company.
- **cgt-2**: If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - missing: `exempt|no\b|not\b`
  - answer: - Capital Gains Tax is 30% of the profit made from selling the van. This means the company will pay 30% of the profit as Capital Gains Tax.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals are taxed at 30% on capital gains from selling assets. This applies to both primary residences and other assets. The tax is payable on the capital gains, not the entire sale price.
- **pit-2**: What is the top personal income tax rate under the new bands?
  - missing: `25\s*%`
  - answer: - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `20\s*%`, `500,000|₦500`
  - answer: - The new rent relief for individuals is a 100% tax credit on rent paid, up to a maximum of NGN 50,000 per year. This credit can be claimed on the annual tax return. The relief is available to individuals who pay rent to a landlord, and it's a flat rate regardless of the amount paid.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% of the invoice amount as VAT. Confirm with the Nigeria Revenue Service or a licensed accountant if you have any specific questions or if your business operates differently.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% of the invoice amount to the customer's invoice as VAT.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - VAT in Nigeria is 7.5%. This applies to most goods and services. Confirm specifics with FIRS or a licensed accountant.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services. Confirm with the Nigeria Revenue Service or a licensed accountant to ensure you're applying the correct rate.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at 0%. This applies to companies that meet the small company criteria, which include having an annual gross turnover of NGN 100,000,000 or less and total fixed assets of NGN 250,000,000 or less.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - Yes, you will pay company income tax. Companies in Nigeria pay 30% CIT on their profits. This applies to your shop, as it is not a professional services business. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A trading company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. This is because the turnover threshold for Companies Income Tax is N100 million, and the fixed assets threshold is N250 million. Since both thresholds are exceeded, the company is e
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, companies in Nigeria pay 30% company income tax. This applies to small companies, which are those with an annual turnover of NGN 100,000,000 or less and total fixed assets of NGN 250,000,000 or less. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies with a turnover of NGN 100,000,000 or more.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company with an annual turnover of N500 million or more is taxed at 30%. This applies to companies that are not eligible for the 0% small company tax rate. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for a business above the small-company threshold is 30%. This applies to companies that are not classified as small companies.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company qualifies for the 0% company income tax rate if its annual gross turnover is INR 100 million or below. This means the turnover must be INR 100 million or less to be considered a small company.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - A company is considered a small company if its annual gross turnover is less than NGN 100,000,000 (₦100 million) and its total fixed assets are less than NGN 250,000,000 (₦250 million). This means the company must meet both these conditions to be classified as a small company.
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is N25 million annual turnover. This means any company with turnover below this amount is considered a small company and pays 0% tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - A company qualifies as small if its annual gross turnover is N100 million or below. Since your turnover is N120 million, you do not qualify for the 0% tax rate. You should check with the Nigeria Revenue Service or a licensed accountant to confirm your specific tax obligations.
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your firm must have an annual gross turnover of N50 million or less and total fixed assets of N250 million or less. Since your turnover is N60 million, which exceeds N50 million, you do not qualify for the 0% rate. You should check with the N
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm cannot be classified as a small company for tax purposes. This is because these businesses are not considered small businesses under the Nigerian tax laws.
- ❌ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small consulting company pays company income tax because it's not classified as a small business. This means it doesn't qualify for the 0% small business tax rate. The company must pay the standard 30% company income tax rate.
- ✅ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - The Companies Income Tax rate for a company with N80 million turnover and N100 million assets is 30%. This is because the company's turnover is below N150 million, which qualifies it for the standard 30% rate. Confirm specifics with FIRS or a licensed accountant.
- ❌ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 0%. This means that companies are exempt from paying the Development Levy.
- ❌ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on profits from the sale of goods and services. The rate is 10% of the profits. This means that if your company makes a profit, you will have to pay 10% of that profit as Development Levy.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - A small company is exempt from paying the Development Levy. This means you don't need to pay it.
- ❌ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a development levy of 2% on its profits. This is in addition to the 30% income tax.
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered, and the payment is less than NGN 500,000 (₦500,000) or the equivalent in foreign currency. This exemption applies to payments made to individua
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders, even if the company is classified as a closely-held company.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to companies that meet the conditions set by the reform.
- ❌ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Capital Gains Tax is 30% of the profit made from selling the van. This means the company will pay 30% of the profit as Capital Gains Tax.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed at 30% on capital gains from selling assets. This applies to both primary residences and other assets. The tax is payable on the capital gains, not the entire sale price.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - The annual income threshold for personal income tax exemption is NGN 800,000 (₦800,000). This means individuals earning below this amount are exempt from paying personal income tax.
- ❌ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is a 100% tax credit on rent paid, up to a maximum of NGN 50,000 per year. This credit can be claimed on the annual tax return. The relief is available to individuals who pay rent to a landlord, and it's a flat rate regardless of the amount paid.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This means you must spend at least 183 days in Nigeria within a 12-month period to be considered a tax resident.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - No, the money you send home to Nigeria is not taxed. This is because Nigeria does not tax remittances from family members. However, it's always a good idea to check with the Nigeria Revenue Service or a licensed accountant to confirm the specifics of your situation, as tax laws can change.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, your salary is not taxed in Nigeria. This is because you are working abroad and your income is not subject to Nigerian tax laws. However, you should check with the Nigerian tax authorities to confirm the specifics of your situation, as tax laws can be complex.
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on Nigerian-source income, which includes salary, dividends, and capital gains. This means they are taxed on income earned from Nigerian investments or Nigerian businesses. However, they are exempt from tax on foreign-source income.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - An established Nigerian company must file its annual tax returns within 6 months of the end of its accounting year. This means the company should file its returns within 6 months of December 31st, the end of its fiscal year.
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - The penalty for failing to register for tax is NGN 50,000 for the first month, and NGN 25,000 for each subsequent month. This means the total penalty can grow if you continue to fail to register. Additionally, if you're a company, you'll also have to pay a fixed penalty of NGN 500,000. It's imp
