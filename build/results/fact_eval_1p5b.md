# Fact-recall eval — 2026-07-13_1158

Model: `gguf_1p5b/model-Q4_K_M.gguf`
**Overall: 35/37** — gate topics: **22/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 4/4 | ✓ |
| prof_services_exclusion | 3/4 | ✓ |
| dev_levy | 4/4 | ✓ |
| withholding_tax | 2/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 3/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **prof-3** (gate): Why does my small consulting company still pay company income tax despite low turnover?
  - missing: `professional`
  - answer:  A small consulting company pays company income tax at 30% regardless of turnover, as per the Companies Act. This is because the company is classified as a small business, not a small company, and the tax rate is higher for small businesses.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer:  Individuals are taxed on capital gains at 10% of the capital gain. This means that if an individual sells an asset for more than its purchase price, they will pay 10% of the capital gain as tax.

## All answers

- ✅ **vat-1** What is the current VAT rate in Nigeria?
  -  The standard VAT rate in Nigeria is 7.5%. This rate applies to most goods and services.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  -  The standard VAT rate in Nigeria is 7.5%. You should add this rate to the total invoice amount for goods sold.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  -  VAT in Nigeria is 7.5%. This is because the Nigeria Tax Reform Act 2025 changed the VAT rate from 5% to 7.5%.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  -  The standard VAT rate in Nigeria is 7.5%. This rate applies to most goods and services. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  -  A qualifying small company pays Companies Income Tax at 0%. This means small companies are exempt from paying CIT, allowing them to focus on their core business activities.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  -  No, your shop pays 0% company income tax. This is because your turnover is below the N100 million threshold, and your business is not classified as a professional services business.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  -  A trading company with an annual turnover of N90 million and fixed assets of N150 million is not liable for Companies Income Tax. This is because the Companies Income Tax rate for companies with an annual turnover of less than N100 million is 0%. However, please confirm with the FIRS or a license
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  -  The standard company income tax rate in Nigeria is 30%. This means small companies pay 30% of their profits in company income tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  -  The standard Companies Income Tax rate for a large Nigerian company is 30%. This rate applies to companies with an annual turnover of ₦100 million or more.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  -  The standard income tax rate for companies in Nigeria is 30%. This rate applies to all companies, regardless of their turnover.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  -  The company income tax rate for businesses above the small-company threshold is 30%. This rate applies to all companies, regardless of their turnover or assets.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  -  A company with an annual turnover of NGN 100,000,000 or less is considered 'small' and exempt from paying company income tax. This means they pay 0% company income tax, making it a cost-effective option for small businesses.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  -  The turnover limit for a small company is NGN 100,000,000 (₦100 million) and the fixed-asset limit is NGN 250,000,000 (₦250 million). These thresholds apply to companies that meet the annual turnover and fixed-asset thresholds.
- ✅ **def-3** Is the small-company tax threshold still N25 million turnover?
  -  The small-company tax threshold is N100,000,000 annual gross turnover. This means companies with less than N100 million annual turnover are exempt from paying Companies Income Tax.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  -  No, your turnover of N120 million is not below the N100 million threshold, so you are not considered a small company and will pay the standard 30% Companies Income Tax.
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  -  No, your business does not qualify for the 0% small company income tax rate. The threshold for small companies is N100 million annual turnover, and your business's turnover is below this threshold. You should check with the Nigeria Revenue Service or a licensed accountant to confirm your specific
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  -  No, an accounting or law firm is never classified as a small company, regardless of turnover or assets. This means they pay the standard company tax rate of 30%.
- ❌ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  -  A small consulting company pays company income tax at 30% regardless of turnover, as per the Companies Act. This is because the company is classified as a small business, not a small company, and the tax rate is higher for small businesses.
- ✅ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  -  The Companies Income Tax rate for a business with N80 million turnover and N100 million assets is 30%. This rate applies to companies with a turnover of N80 million or more and an asset value of N100 million or more.
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  -  The Development Levy rate in Nigeria is 4%. This means that any company that pays the Development Levy will have to pay 4% of its taxable profits.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  -  The Development Levy is charged on the assessable profits of companies. It is charged at a rate of 4%. This means that if a company's profits are $100,000, it will pay a Development Levy of $4,000.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  -  Small companies are exempt from paying the Development Levy. This means that small businesses in Nigeria are not required to pay this tax, making it a more affordable option for them.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  -  A large company pays a 4% development levy on its profits. This development levy is imposed on the profits of companies with an annual turnover of more than 500 million Naira.
- ✅ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  -  A small company is exempt from deducting withholding tax at source on payments of up to ₦2 million. This exemption applies to payments made to suppliers, contractors, and other businesses. Confirm specifics with FIRS / a licensed accountant.
- ✅ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  -  The withholding tax rate on deemed distributions of a closely-held Nigerian company is 10%. This rate applies to any deemed distribution of capital or profits, regardless of the company's tax residency status.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  -  The Capital Gains Tax rate for companies is 30%. This rate applies to the sale of shares, fixed assets, and other non-cash assets.
- ✅ **cgt-2** Do small companies pay Capital Gains Tax?
  -  Small companies are exempt from Capital Gains Tax. This means they don't have to pay any tax on the sale of their assets.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  -  Individuals are taxed on capital gains at 10% of the capital gain. This means that if an individual sells an asset for more than its purchase price, they will pay 10% of the capital gain as tax.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  -  The annual income threshold for exempting individuals from personal income tax in Nigeria is ₦800,000. This means that individuals earning below ₦800,000 per year are exempt from paying personal income tax.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  -  The top personal income tax rate in Nigeria is 25%. This rate applies to individuals whose taxable income exceeds the highest threshold.
- ✅ **pit-3** How does the new rent relief for individuals work?
  -  The new rent relief for individuals is 20% of their annual rent, capped at a maximum of ₦500,000. This means that individuals can claim up to ₦100,000 in rent relief, which is a 20% reduction from their annual rent.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  -  You are a tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  -  No, the money you send home to your family in Nigeria is not taxed. This is because it's considered a personal remittance, not a business income. However, please confirm with FIRS or a licensed accountant to ensure you're complying with all tax regulations.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  -  No, your foreign salary is not taxed in Nigeria. This is because you are considered a non-resident, and non-residents are exempt from paying Nigerian tax on their foreign income. However, you should confirm with the FIRS or a licensed accountant to ensure you are complying with all tax laws.
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  -  Non-residents are not taxed on Nigerian-source income, regardless of where they earn it. This means they can earn and keep all their income outside Nigeria without paying Nigerian tax.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  -  A company in Nigeria must file its annual tax returns within 6 months after the end of its accounting year. This means that if your company's accounting year ends on December 31, you must file your annual tax returns by June 30 of the following year. Confirm specifics with FIRS or a licensed acco
- ✅ **file-2** What is the penalty for failing to register for tax in Nigeria?
  -  The penalty for failing to register for tax in Nigeria is NGN 50,000 for the first month, and NGN 25,000 for each subsequent month. This penalty applies to both individuals and companies.
