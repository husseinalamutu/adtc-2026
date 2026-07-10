# Fact-recall eval — 2026-07-10_1214

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/gguf/model-Q4_K_M.gguf`
**Overall: 22/23** — gate topics: **22/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 4/4 | ✓ |
| dev_levy | 4/4 | ✓ |

## Failures
- **def-4** (gate): My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - missing: `not|no\b|exceed|above`
  - answer: - A company with an annual gross turnover of N100 million or below is considered a small company. However, to qualify for the 0% small-company tax rate, you must also meet other specific conditions, such as having an annual gross fixed asset value of N250 million or below. You can confirm specifi

## All answers

- ✅ **vat-1** What is the current VAT rate in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
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
