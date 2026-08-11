# Fact-recall eval — 2026-08-11_1911

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1400/gguf/model-Q4_K_M.gguf`
**Overall: 32/37** — gate topics: **19/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 3/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 4/4 | ✓ |
| prof_services_exclusion | 1/4 | ✓ |
| dev_levy | 4/4 | ✓ |
| withholding_tax | 2/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 3/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **cit0-4** (gate): Small companies in Nigeria pay 20% company income tax, right?
  - missing: `0\s*%|exempt`
  - answer: - No, small companies in Nigeria pay 15% company income tax. This is because the definition of a small company in Nigeria is based on the company's annual gross turnover and total assets, and the tax rate for small companies is 15%.
- **prof-1** (gate): I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - missing: `professional|exclu|not qualify|do(es)? not qualify|don't qualify|cannot`
  - answer: - To qualify for the 0% small company income tax rate, your annual gross turnover must be N100 million or below. Since your turnover is N60 million, you do qualify. Confirm specifics with FIRS / a licensed accountant.
- **prof-3** (gate): Why does my small consulting company still pay company income tax despite low turnover?
  - missing: `professional`
  - answer: - A small company in Nigeria pays company income tax even if its turnover is low. This is because the definition of a small company in Nigeria is based on the company's annual gross turnover and total assets, not its turnover alone. Your consulting business must meet both the turnover and assets 
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - missing: `30\s*%` wrong-hit: `(?<![\d.])0\s*%`
  - answer: - A company with N80 million turnover and N100 million assets is classified as a small company. For small companies, the Companies Income Tax rate is 0%. This means the company is exempt from paying CIT.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals are taxed at a progressive rate on capital gains. The standard tax rate is 20%, but this can be reduced to 10% for individuals with annual income below a certain threshold. The specific tax rates and thresholds are subject to change, so it's best to consult the latest tax laws or co

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means I need to charge 7.5% of the invoice amount as VAT on goods sold.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% of the invoice amount as VAT. Confirm specifics with FIRS / a licensed accountant.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your taxable goods.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at a rate of 0%. This means they are exempt from paying CIT.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - If your annual turnover is N45 million and your business is not a professional services business, you are not required to pay company income tax. This is because your business qualifies as a small company under the Nigeria Tax Reform Acts 2025, which exempts small companies from paying company 
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. This is because the turnover threshold for small companies in Nigeria is N100 million. However, confirm specifics with FIRS / a licensed accountant.
- ❌ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 15% company income tax. This is because the definition of a small company in Nigeria is based on the company's annual gross turnover and total assets, and the tax rate for small companies is 15%.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies that meet the criteria for being considered large.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company with N500 million turnover pays 30% Companies Income Tax. This is because the threshold for the 25% rate is N100 million, and your company exceeds this threshold.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for businesses above the small-company threshold is 30%. This applies to all companies that meet the criteria for being a 'large company'.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company qualifies as 'small' for the 0% company income tax rate if its annual gross turnover is ₹100 million or below. This threshold applies to businesses that also meet the conditions of having total fixed assets of ₹250 million or below.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for small-company status is NGN 100,000,000 (₦100 million) per annum, and the fixed-asset limit is NGN 250,000,000 (₦250 million) per annum.
- ✅ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is now N100 million annual gross turnover. This change took effect on January 1, 2025.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - To qualify for 0% tax as a small company in Nigeria, your annual gross turnover must be N100 million or below. Since your turnover is N120 million, you do not qualify for the small company tax rate. You should check with FIRS or a licensed accountant to confirm the specifics of your tax obligat
- ❌ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your annual gross turnover must be N100 million or below. Since your turnover is N60 million, you do qualify. Confirm specifics with FIRS / a licensed accountant.
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm cannot be classified as a small company for tax purposes. The definition of a small company in Nigeria excludes professional services businesses like accounting or law firms. This means they are not eligible for the small company tax rates or other incentives desig
- ❌ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small company in Nigeria pays company income tax even if its turnover is low. This is because the definition of a small company in Nigeria is based on the company's annual gross turnover and total assets, not its turnover alone. Your consulting business must meet both the turnover and assets 
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - A company with N80 million turnover and N100 million assets is classified as a small company. For small companies, the Companies Income Tax rate is 0%. This means the company is exempt from paying CIT.
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 4%. This applies to the assessable profits of all companies chargeable to tax.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on the assessable profits of all companies chargeable to tax. The rate is 4%. This means that all companies chargeable to tax must pay the Development Levy on their assessable profits.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means they do not have to pay it.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company in Nigeria pays a 4% Development Levy on its assessable profits. This applies to companies with annual gross turnover of NGN 100,000,000 or more. Confirm specifics with FIRS / a licensed accountant.
- ✅ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to a supplier who has a valid Tax Identification Number (TIN) and the transaction value is less than NGN 2,000,000 (₦2 million). This exemption applies to payments for goods or services render
- ✅ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate on deemed distributions of a closely-held Nigerian company is 10%. This applies to distributions made by such companies to their shareholders.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to capital gains from the sale of capital assets by companies.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Capital Gains Tax is not applicable for small companies selling capital assets like a delivery van. This is because small companies are exempt from CGT. Confirm specifics with FIRS or a licensed accountant.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed at a progressive rate on capital gains. The standard tax rate is 20%, but this can be reduced to 10% for individuals with annual income below a certain threshold. The specific tax rates and thresholds are subject to change, so it's best to consult the latest tax laws or co
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - Individuals earning below NGN 800,000 per annum are exempt from personal income tax. This means they do not need to pay tax on their income.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate in Nigeria is 25%. This applies to individuals whose income exceeds the highest tax band.
- ✅ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is 20% of annual rent paid, capped at a maximum of NGN 500,000. This applies to individuals who pay rent to a landlord.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This is based on the Nigerian Tax Reform Acts 2025.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - Income you send home to Nigeria is not taxable in Nigeria. This is because remittances are considered gifts or remittances, not taxable income. However, it's always best to confirm specifics with FIRS or a licensed accountant to ensure you're meeting all tax requirements.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - Income earned entirely outside Nigeria is exempt from Nigerian tax. This means if your salary is paid into a Nigerian account, it won't be taxed in Nigeria.
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on income they earn within Nigeria. This means they are subject to Nigerian tax on their Nigerian-source income, regardless of where the income was earned.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A Nigerian company must file its annual tax returns within 6 months after the end of its accounting year. This timeframe applies to all companies, regardless of their size or nature of business.
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - If your business never registered for tax, you'll be liable for a penalty of NGN 50,000 for the first month and NGN 25,000 for each subsequent month. This penalty continues to accrue until the tax registration is completed. If your business continues to operate without a valid tax registration,
