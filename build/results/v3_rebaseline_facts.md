# Fact-recall eval — 2026-08-11_1632

Model: `adapters_best/model-Q4_K_M-v3-gate22of23.gguf`
**Overall: 34/37** — gate topics: **22/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 4/4 | ✓ |
| dev_levy | 4/4 | ✓ |
| withholding_tax | 1/2 |  |
| capital_gains | 3/3 |  |
| personal_income_tax | 3/3 |  |
| tax_residency | 3/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **def-4** (gate): My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - missing: `not|no\b|exceed|above`
  - answer: - A company with an annual gross turnover of N100 million or below is considered a small company. However, to qualify for the 0% small-company tax rate, you must also meet other specific conditions, such as having an annual gross fixed asset value of N250 million or below. You can confirm specifi
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions of a closely-held Nigerian company is 0%. This applies to distributions made to shareholders who are residents of Nigeria. Confirm specifics with FIRS or a licensed accountant.
- **res-4**: Are non-residents taxed on income they earn outside Nigeria?
  - missing: `no\b|not\b|only|Nigerian.source`
  - answer: - Non-residents are taxed on their worldwide income, regardless of where it's earned. This means they'll pay tax on any income earned outside Nigeria, as long as it's taxable.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you need to charge 7.5% VAT on the value of goods you sell.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. I need to charge this on all sales of goods.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. I should charge this rate on all goods I sell.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays a Companies Income Tax rate of 0%. This means they are exempt from paying Companies Income Tax.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - No, companies with annual turnover below N100 million and not providing professional services are exempt from company income tax. This means you won't have to pay CIT. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A trading company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. This is because it does not meet the criteria for being a company. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 0% company income tax. This means they are exempt from paying company income tax. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies that meet the criteria for being large. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - The standard corporate income tax rate in Nigeria is 30%. This applies to companies with annual turnover of N500 million or more. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for businesses above the small-company threshold is 30%. This applies to all companies that are not classified as small companies.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company with an annual gross turnover of NGN 100,000,000 or below is considered 'small' for the 0% company income tax rate. This means that companies with annual turnover below this threshold are eligible for the reduced tax rate. Confirm specifics with FIRS or a licensed accountant.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - A company is considered a small company if its annual gross turnover is NGN 100,000,000 or below and its total fixed assets are NGN 250,000,000 or below. This means that companies with annual turnover below NGN 100,000,000 and total fixed assets below NGN 250,000,000 may be eligible for small-c
- ✅ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is now N100 million annual gross turnover or below. This applies to companies that meet the other conditions for being classified as small companies.
- ❌ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - A company with an annual gross turnover of N100 million or below is considered a small company. However, to qualify for the 0% small-company tax rate, you must also meet other specific conditions, such as having an annual gross fixed asset value of N250 million or below. You can confirm specifi
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - No, your business does not qualify for the 0% small company income tax rate. The turnover threshold for a business to be classified as a small company is N100 million. As your business has a turnover of N60 million, it does not meet this threshold.
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm is never classified as a small company for tax purposes. This means they pay the standard corporate tax rate, regardless of turnover or fixed assets.
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A company providing professional services pays 30% Companies Income Tax regardless of turnover or fixed assets. This is because the company is classified as a 'small company' for tax purposes, but professional services companies are not eligible for this exemption.
- ✅ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - The Companies Income Tax rate for a company with an annual gross turnover of N80 million and total assets of N100 million is 30%. This applies to companies that meet these criteria. Confirm specifics with FIRS or a licensed accountant.
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 4%. This Development Levy is imposed on the assessable profits of all companies chargeable to tax.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on the assessable profits of companies chargeable to tax. The rate is 4%. This means that companies with assessable profits above a certain threshold will have to pay a 4% Development Levy on their profits.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means they don't have to pay it. Confirm specifics with FIRS or a licensed accountant.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a 4% Development Levy on its assessable profits. This levy is imposed on the assessable profits of all companies chargeable to tax.
- ✅ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to a small company or a non-resident company. This exemption applies to payments of 2 million Naira or less to a small company or a non-resident company. Confirm specifics with FIRS or a licen
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions of a closely-held Nigerian company is 0%. This applies to distributions made to shareholders who are residents of Nigeria. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to companies' capital gains, which are taxed at the standard corporate tax rate. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Small companies are exempt from Capital Gains Tax. This means that if a small company sells a delivery van at a profit, it won't have to pay Capital Gains Tax on the sale. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed on their capital gains at the standard personal income tax rate. This means that if you sell an asset for more than you paid for it, you'll pay personal income tax on the profit.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - Individuals earning below NGN 800,000 per annum are exempt from PIT. This exemption applies to individuals earning below the threshold, and they do not need to pay personal income tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 25%. This applies to individuals whose taxable income exceeds the highest band limit.
- ✅ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is 20% of annual rent paid, capped at a maximum of ₦500,000. This means you can claim 20% of your annual rent paid, but the maximum amount you can claim is ₦500,000.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - A person is considered a Nigerian tax resident if they are physically present in Nigeria for 183 days or more within any 12-month period. This is based on the days spent in Nigeria, not the days spent outside.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - No, the money you send home to Nigeria is not taxed. This applies to personal remittances, which are exempt from Nigerian tax. Confirm specifics with FIRS or a licensed accountant.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - Income earned entirely outside Nigeria is exempt from Nigerian tax. This applies even if the income is remitted into Nigeria. Confirm specifics with FIRS or a licensed accountant.
- ❌ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on their worldwide income, regardless of where it's earned. This means they'll pay tax on any income earned outside Nigeria, as long as it's taxable.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A Nigerian company must file its annual tax returns within 6 months after the end of its accounting year. This means the company should file its returns within 6 months after the end of its financial year. Confirm specifics with FIRS or a licensed accountant.
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - The penalty for failing to register for tax is NGN 50,000 for the first month, then NGN 25,000 for each subsequent month. This means the penalty increases by NGN 25,000 for each month after the first month of non-compliance.
