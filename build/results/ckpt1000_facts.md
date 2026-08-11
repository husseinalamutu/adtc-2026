# Fact-recall eval — 2026-08-11_1930

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1000/gguf/model-Q4_K_M.gguf`
**Overall: 27/37** — gate topics: **19/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 3/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 2/4 | ✓ |
| dev_levy | 4/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 1/3 |  |
| personal_income_tax | 2/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 1/2 |  |

## Failures
- **cit0-2** (gate): My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - missing: `0\s*%|exempt|do(es)? not pay|don't pay`
  - answer: - If your shop's annual turnover is N45 million, you are not considered a professional services business and are not subject to company income tax. However, you should confirm specifics with FIRS or a licensed accountant.
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The small-company tax threshold is now N50 million turnover. This change applies to companies that meet the new definition of a small company under the Nigeria Tax Reform Act 2025. Confirm specifics with FIRS / a licensed accountant.
- **prof-1** (gate): I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - missing: `professional|exclu|not qualify|do(es)? not qualify|don't qualify|cannot`
  - answer: - To qualify for the 0% small company income tax rate, your consulting firm must have a gross turnover of NGN 100 million or less and total fixed assets of NGN 250 million or less. Your company's turnover is NGN 60 million, which is below the NGN 100 million limit, but your fixed assets are not d
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - missing: `30\s*%` wrong-hit: `(?<![\d.])0\s*%`
  - answer: - A company with N80 million turnover and N100 million assets is classified as a small company. For such companies, the Companies Income Tax rate is 0%. This applies to all small companies, including professional services like a tech consultancy. Confirm specifics with FIRS / a licensed accountan
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to a small supplier with an annual gross turnover of NGN 100,000,000 or less and an annual gross fixed assets of NGN 250,000,000 or less. This exemption applies to payments of NGN 250,000,000 
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate on deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders, and it's important to note that this rate applies even if the distribution is made outside Nigeria. Confirm specifics with FIRS or a lic
- **cgt-2**: If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - missing: `exempt|no\b|not\b`
  - answer: - The capital gains tax rate for small companies is 0%. This means that if a small company sells a property or asset like a delivery van at a profit, it won't have to pay capital gains tax on it. However, it's always best to confirm this with FIRS or a licensed accountant to ensure you're followi
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals are taxed at a flat rate of 20% on capital gains from the sale of assets. This applies to all individuals, regardless of their income level. Confirm specifics with FIRS or a licensed accountant.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `20\s*%`
  - answer: - The new rent relief for individuals is 10% of the annual rent paid, capped at a maximum of NGN 500,000. This relief is only available for individuals who pay rent and meet the conditions set by the Nigeria Revenue Service. Confirm specifics with the NRS or a licensed accountant.
- **file-1**: When must an established Nigerian company file its annual tax returns?
  - missing: `6\s*months`
  - answer: - An established Nigerian company must file its annual tax returns within 18 months of the end of its accounting year. This means the company should file its returns within 18 months of the end of its accounting period. Confirm specifics with FIRS or a licensed accountant.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your goods. Confirm specifics with FIRS or a licensed accountant.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% of the invoice amount to the total cost for your customers. Confirm specifics with FIRS or a licensed accountant.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services. Confirm specifics with FIRS or a licensed accountant.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at 0%. This applies to companies that meet the small company criteria, which are based on turnover and assets. Confirm specifics with FIRS or a licensed accountant.
- ❌ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - If your shop's annual turnover is N45 million, you are not considered a professional services business and are not subject to company income tax. However, you should confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. Companies with a lower turnover and fixed assets are exempt from CIT. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 30% company income tax. This is because small companies are exempt from paying company income tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies with a gross turnover of NGN 100,000,000 or more. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company with N500 million turnover pays 30% Companies Income Tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for companies that meet the small-company threshold is 30%. This applies to businesses that have an annual gross turnover of NGN 100,000,000 or less and total fixed assets of NGN 250,000,000 or less. Confirm specifics with FIRS or a licensed accountant.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company is considered 'small' if its annual gross turnover is ₹100,000,000 or below. This means the company must meet this turnover threshold to qualify for the 0% CIT rate. Confirm specifics with FIRS or a licensed accountant.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for small-company status is NGN 100,000,000 (₦100 million) per annum, and the fixed-asset limit is NGN 250,000,000 (₦250 million) per annum. Confirm specifics with FIRS or a licensed accountant.
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is now N50 million turnover. This change applies to companies that meet the new definition of a small company under the Nigeria Tax Reform Act 2025. Confirm specifics with FIRS / a licensed accountant.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - No, your company does not qualify as a small company. The turnover threshold for a small company is NGN 100 million or less. Your company's turnover is NGN 120 million, which exceeds this limit. As such, your company is subject to standard corporate income tax rates.
- ❌ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your consulting firm must have a gross turnover of NGN 100 million or less and total fixed assets of NGN 250 million or less. Your company's turnover is NGN 60 million, which is below the NGN 100 million limit, but your fixed assets are not d
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm cannot be classified as a small company for tax purposes. The Nigerian Tax Reform Act 2025 defines small companies as those with a gross turnover of NGN 100,000,000 or less and total fixed assets of NGN 250,000,000 or less. These limits are not applicable to profes
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A company providing professional services, like consulting, is not exempt from company income tax, even if it has low turnover. This is because the Nigerian Tax Reform Act 2025 does not exempt such companies from paying company income tax. Confirm specifics with FIRS or a licensed accountant.
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - A company with N80 million turnover and N100 million assets is classified as a small company. For such companies, the Companies Income Tax rate is 0%. This applies to all small companies, including professional services like a tech consultancy. Confirm specifics with FIRS / a licensed accountan
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 4%. This levy is imposed on the assessable profits of all companies chargeable to tax.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on the assessable profits of all companies chargeable to tax. The rate is 4%. This levy is imposed on companies that are chargeable to tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means you don't need to pay it. Confirm specifics with FIRS or a licensed accountant.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a Development Levy of 4% on its assessable profits. This levy is imposed on companies with a gross annual turnover of NGN 100,000,000 or more. Confirm specifics with FIRS or a licensed accountant.
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to a small supplier with an annual gross turnover of NGN 100,000,000 or less and an annual gross fixed assets of NGN 250,000,000 or less. This exemption applies to payments of NGN 250,000,000 
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate on deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders, and it's important to note that this rate applies even if the distribution is made outside Nigeria. Confirm specifics with FIRS or a lic
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to capital gains from the sale of assets. Confirm specifics with FIRS or a licensed accountant.
- ❌ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - The capital gains tax rate for small companies is 0%. This means that if a small company sells a property or asset like a delivery van at a profit, it won't have to pay capital gains tax on it. However, it's always best to confirm this with FIRS or a licensed accountant to ensure you're followi
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed at a flat rate of 20% on capital gains from the sale of assets. This applies to all individuals, regardless of their income level. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - The annual income threshold for individuals to be exempt from personal income tax in Nigeria is NGN 800,000 (₦800,000). This means that individuals earning below this amount are not required to pay personal income tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 25%. This applies to income earned above the highest income level. Confirm specifics with FIRS or a licensed accountant.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is 10% of the annual rent paid, capped at a maximum of NGN 500,000. This relief is only available for individuals who pay rent and meet the conditions set by the Nigeria Revenue Service. Confirm specifics with the NRS or a licensed accountant.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - According to the Nigeria Tax Authority, you are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This means you must be physically present in Nigeria for at least 183 days within a 12-month period to be considered a Nig
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - No, the money you send home to your family in Nigeria is not taxed. This is because remittances are considered personal transfers and are not subject to Nigerian tax. However, it's always best to confirm specifics with the Nigeria Revenue Service or a licensed accountant.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, your Nigerian salary is not taxed in Nigeria if you pay it into your Nigerian account. This is because Nigerian tax law applies only to Nigerian residents and businesses. However, you should confirm with the Nigerian Tax Authority or a licensed accountant to ensure you're complying with all
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on income earned from sources within Nigeria. This means they are taxed on income earned from Nigerian sources, such as property or business activities in Nigeria. Confirm specifics with FIRS or a licensed accountant.
- ❌ **file-1** When must an established Nigerian company file its annual tax returns?
  - - An established Nigerian company must file its annual tax returns within 18 months of the end of its accounting year. This means the company should file its returns within 18 months of the end of its accounting period. Confirm specifics with FIRS or a licensed accountant.
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - If your business hasn't registered for tax, you'll be charged a penalty of NGN 50,000 for the first month and NGN 100,000 for each subsequent month. This penalty continues to accrue until the company registers for tax. It's important to register as soon as possible to avoid further penalties.
