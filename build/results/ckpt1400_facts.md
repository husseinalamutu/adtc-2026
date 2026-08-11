# Fact-recall eval — 2026-08-11_1640

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1400/gguf/model-Q4_K_M.gguf`
**Overall: 26/37** — gate topics: **18/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 3/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 4/4 | ✓ |
| dev_levy | 1/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 1/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 1/2 |  |

## Failures
- **cit0-2** (gate): My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - missing: `0\s*%|exempt|do(es)? not pay|don't pay`
  - answer: - If your shop's turnover is N45 million a year and it is not a professional services business, you are not required to pay company income tax. This is because your business is considered a small company. Confirm with the Nigeria Revenue Service or a licensed accountant to ensure you're meeting a
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The small-company tax threshold is indeed N25 million turnover. This means any company with turnover below N25 million is exempt from paying company income tax.
- **dev-1** (gate): What is the Development Levy rate in Nigeria?
  - missing: `4\s*%`
  - answer: - The Development Levy rate in Nigeria is 0.5%. This rate applies to companies and individuals.
- **dev-2** (gate): On what profits is the Development Levy charged, and at what rate?
  - missing: `4\s*%`, `assessable`
  - answer: - The Development Levy is charged on profits above the exempt level. The exempt level is 100,000,000 Naira. Profits above this level are taxed at 2.5%. This means that for every 100,000,000 Naira of profits above the exempt level, 2,500,000 Naira is paid as Development Levy.
- **dev-4** (gate): Besides the 30% income tax, what development levy does a large company pay on its profits?
  - missing: `4\s*%`
  - answer: - The development levy for a large company is 2.5% of its profits. This applies to companies with annual gross turnover of more than 100 million Naira.
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered. This exemption applies to payments made to individuals for personal services, such as consulting or freelance work.
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions from a Nigerian company is 25%. This applies to distributions made by a Nigerian company to its shareholders.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals pay capital gains tax at 10% on capital gains from selling assets. This applies to both capital gains from selling assets and capital gains from selling property.
- **pit-2**: What is the top personal income tax rate under the new bands?
  - missing: `25\s*%`
  - answer: - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `20\s*%`, `500,000|₦500`
  - answer: - The new rent relief for individuals is a 10% reduction on the rent paid, up to a maximum of NGN 50,000 per year. This relief is available to individuals who pay rent to a landlord or tenant.
- **file-2**: My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - missing: `50,000|₦50`
  - answer: - The penalty for failing to register for tax is 5,000 Naira for the first month and 2,500 Naira for each subsequent month. This means the total penalty can grow if you continue to fail to register.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your goods.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. I should add 7.5% VAT to the invoice for goods sold to customers.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This rate applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your sales.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays 0% Companies Income Tax. This applies to companies that meet the small company criteria, which are companies with an annual turnover of less than 100 million Naira and total fixed assets of less than 250 million Naira.
- ❌ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - If your shop's turnover is N45 million a year and it is not a professional services business, you are not required to pay company income tax. This is because your business is considered a small company. Confirm with the Nigeria Revenue Service or a licensed accountant to ensure you're meeting a
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A trading company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. This is because the turnover threshold for Companies Income Tax is N100 million.
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, the company income tax rate for small companies in Nigeria is 0%. This means small companies are exempt from paying CIT.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies with a turnover of over N100,000,000.00 per annum.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - The standard corporate income tax rate in Nigeria is 30%. This applies to most companies.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for businesses above the small-company threshold is 30%. This applies to companies with annual turnover above the small-company threshold.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - The annual turnover threshold for a company to be classified as 'small' for the 0% company income tax rate is ₦100,000,000. This means any company with an annual turnover below this amount is eligible for the 0% tax rate.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for a small company is NGN 100,000,000 (₦100 million) per annum, and the fixed-asset limit is NGN 250,000,000 (₦250 million) per annum. These thresholds are applicable to companies that meet the other requirements for small-company status.
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is indeed N25 million turnover. This means any company with turnover below N25 million is exempt from paying company income tax.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - To qualify for the 0% small-company tax rate, your turnover must be N100 million or below. Since your turnover is N120 million, you do not qualify for the small-company tax rate.
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your business must meet certain criteria. For a consulting firm, the turnover threshold is N50 million. Since your turnover is N60 million, you do not qualify for the small company tax rate. You should check with the Nigeria Revenue Service o
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm is never classified as a small company for tax purposes. This means they pay the standard corporate tax rate, regardless of turnover or fixed assets.
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small consulting company pays company income tax because it's not classified as a small business. Companies providing professional services like consulting are not eligible for the small business tax rate.
- ✅ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - The Companies Income Tax rate for a company with N80 million turnover and N100 million assets is 30%. This is because the company falls under the 'small company' category, which is taxed at 30% under the Nigerian tax laws.
- ❌ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 0.5%. This rate applies to companies and individuals.
- ❌ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on profits above the exempt level. The exempt level is 100,000,000 Naira. Profits above this level are taxed at 2.5%. This means that for every 100,000,000 Naira of profits above the exempt level, 2,500,000 Naira is paid as Development Levy.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - The Development Levy is 0% for small companies. This means small companies are exempt from paying the Development Levy.
- ❌ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - The development levy for a large company is 2.5% of its profits. This applies to companies with annual gross turnover of more than 100 million Naira.
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered. This exemption applies to payments made to individuals for personal services, such as consulting or freelance work.
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions from a Nigerian company is 25%. This applies to distributions made by a Nigerian company to its shareholders.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to companies that meet the conditions of the reform.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Small companies are exempt from Capital Gains Tax on the sale of assets. This means that if a small company sells a delivery van at a profit, it won't have to pay CGT on the sale.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals pay capital gains tax at 10% on capital gains from selling assets. This applies to both capital gains from selling assets and capital gains from selling property.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - The annual income threshold for personal income tax exemption varies by country. In Nigeria, individuals earning up to NGN 800,000 (approximately USD 2,000) per year are exempt from personal income tax. Please confirm with the Nigeria Revenue Service or a licensed accountant for the most accura
- ❌ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is a 10% reduction on the rent paid, up to a maximum of NGN 50,000 per year. This relief is available to individuals who pay rent to a landlord or tenant.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This is based on the tax laws of Nigeria.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - The money you send home to Nigeria is not taxed. This is because it's considered a personal remittance. However, it's always a good idea to check with the Nigeria Revenue Service or a tax professional to confirm the specifics of your situation.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - Income earned from employment outside Nigeria is not taxable in Nigeria. This applies even if you transfer the income into a Nigerian account. Confirm specifics with FIRS or a licensed accountant.
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on Nigerian-source income, which includes income from Nigerian property or business operations. However, non-residents are not taxed on foreign-source income.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A Nigerian company must file its annual tax returns within 6 months after the end of its accounting year. This means the filing deadline is 6 months after the end of the company's fiscal year.
- ❌ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - The penalty for failing to register for tax is 5,000 Naira for the first month and 2,500 Naira for each subsequent month. This means the total penalty can grow if you continue to fail to register.
