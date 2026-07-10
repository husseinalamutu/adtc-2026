# Fact-recall eval — 2026-07-10_1212

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/gguf/model-Q4_K_M.gguf`
**Overall: 31/37** — gate topics: **20/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 2/4 | ✓ |
| prof_services_exclusion | 3/4 | ✓ |
| dev_levy | 4/4 | ✓ |
| withholding_tax | 1/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 3/3 |  |
| tax_residency | 3/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The small-company tax threshold is indeed N25 million annual turnover. This applies to companies that meet the other requirements for being classified as small companies. Confirm specifics with FIRS / a licensed accountant.
- **def-4** (gate): My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - missing: `not|no\b|exceed|above`
  - answer: - A company must have an annual gross turnover of less than N100 million to be considered a small company. You can confirm specifics with FIRS or a licensed accountant.
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - missing: `30\s*%` wrong-hit: `(?<![\d.])0\s*%`
  - answer: - A company with a turnover of N80 million and assets of N100 million is classified as a small company. The Companies Income Tax rate for small companies is 0%. This means they pay no Companies Income Tax. Confirm specifics with FIRS / a licensed accountant.
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions from a Nigerian company is 5%. This applies to distributions made to non-resident shareholders. Confirm specifics with FIRS / a licensed accountant.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals pay 30% tax on capital gains, which is the same as the top rate for income tax. This applies to individuals who sell assets, such as property or stocks, and the capital gains are taxed as ordinary income. Confirm specifics with FIRS or a licensed accountant.
- **res-4**: Are non-residents taxed on income they earn outside Nigeria?
  - missing: `no\b|not\b|only|Nigerian.source`
  - answer: - Non-residents are taxed on income earned outside Nigeria, but they are exempt from tax on income earned within Nigeria. This means you can keep earning your foreign income without paying Nigerian tax on it. Confirm specifics with FIRS / a licensed accountant.

## All answers

- ✅ **vat-1** What is the current VAT rate in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most taxable goods and services.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% VAT to your customer's invoice for goods you sell. Confirm specifics with FIRS / a licensed accountant.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most taxable goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on most goods sold at your shop. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays a Companies Income Tax rate of 0%. This means they are exempt from paying Companies Income Tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - No, you don't pay company income tax. As a small business, you pay 0% CIT. This means you won't have to pay CIT on your profits. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A company with turnover of N90 million and fixed assets of N150 million is not a small company. This means they are liable for Companies Income Tax at 30%. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 0% company income tax. This means they are exempt from paying company income tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies that meet the criteria for being large. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company that earns more than N100 million per year pays a 30% Companies Income Tax rate. This means your company will pay 30% Companies Income Tax on its profits. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for companies above the small-company threshold is 30%. This applies to companies that are not classified as small companies.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company must have an annual turnover of ₦100,000,000 or less to be considered 'small' for the 0% company income tax rate. This means that if your company's annual turnover is ₦100,000,000 or less, you may be eligible for the 0% company income tax rate. Confirm specifics with FIRS / a licensed
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for a company to be considered small is ₦100,000,000. The fixed-asset limit is ₦250,000,000. Confirm specifics with FIRS / a licensed accountant.
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is indeed N25 million annual turnover. This applies to companies that meet the other requirements for being classified as small companies. Confirm specifics with FIRS / a licensed accountant.
- ❌ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - A company must have an annual gross turnover of less than N100 million to be considered a small company. You can confirm specifics with FIRS or a licensed accountant.
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - A business providing professional services, like consulting, does not qualify as a small company, regardless of turnover, and pays Companies Income Tax at 30%.
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm is never classified as a small company for tax purposes. This means they pay the standard 30% Companies Income Tax and are not eligible for tax exemptions or reductions.
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A company providing professional services, like consulting, pays 30% Companies Income Tax regardless of turnover. This is because professional services are not considered small companies, even if your company's turnover is low. Confirm specifics with FIRS / a licensed accountant.
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - A company with a turnover of N80 million and assets of N100 million is classified as a small company. The Companies Income Tax rate for small companies is 0%. This means they pay no Companies Income Tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 4%. This means that 4% of a company's assessable profits is paid as Development Levy.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on the assessable profits of companies chargeable to tax. The rate is 4%. This means that 4% of a company's assessable profits is paid as Development Levy. Confirm specifics with FIRS / a licensed accountant.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means you won't have to pay it. Confirm specifics with FIRS / a licensed accountant.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a Development Levy of 4%. This levy is imposed on the assessable profits of companies chargeable to tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment of NGN 2,000,000 or less if the supplier has a valid Tax Identification Number. This exemption threshold applies to payments made to suppliers with a valid Tax Identification Number. Confirm specifics with FIRS / a 
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions from a Nigerian company is 5%. This applies to distributions made to non-resident shareholders. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to companies that meet the requirements for the new tax system. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cgt-2** Do small companies pay Capital Gains Tax?
  - - Small companies are exempt from Capital Gains Tax. This means they don't have to pay CGT on the sale of their assets. Confirm specifics with FIRS / a licensed accountant.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals pay 30% tax on capital gains, which is the same as the top rate for income tax. This applies to individuals who sell assets, such as property or stocks, and the capital gains are taxed as ordinary income. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - Individuals earning below NGN 800,000 per annum are exempt from personal income tax. This exemption threshold applies to individuals earning below this amount. Confirm specifics with FIRS / a licensed accountant.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate in Nigeria is 25%. This applies to individuals whose annual income exceeds the highest tax band under the new bands. Confirm specifics with FIRS / a licensed accountant.
- ✅ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is 20% of annual rent paid, capped at a maximum of ₦500,000. This is paid as a tax credit. You'll need to declare your annual rent and provide supporting documents to the tax authority. Confirm specifics with FIRS / a licensed accountant.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This is typically used to determine your tax obligations in Nigeria. Confirm specifics with FIRS / a licensed accountant.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - No, the money you send home to your family in Nigeria is not taxed. This is because it's considered personal remittance, which is exempt from Nigerian tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - Income earned entirely outside Nigeria is exempt from Nigerian tax. This means you won't pay tax on your foreign salary even if you transfer it into your Nigerian account. Confirm specifics with FIRS or a licensed accountant.
- ❌ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on income earned outside Nigeria, but they are exempt from tax on income earned within Nigeria. This means you can keep earning your foreign income without paying Nigerian tax on it. Confirm specifics with FIRS / a licensed accountant.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A company in business more than 18 months must file its annual tax returns within 6 months after the end of its accounting year. This applies to companies that have been in operation for more than 18 months. Confirm specifics with FIRS / a licensed accountant.
- ✅ **file-2** What is the penalty for failing to register for tax in Nigeria?
  - - The penalty for failing to register for tax in Nigeria is NGN 50,000 for the first month and NGN 25,000 for each subsequent month. This applies to both companies and individuals.
