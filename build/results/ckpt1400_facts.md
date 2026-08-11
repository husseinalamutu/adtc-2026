# Fact-recall eval — 2026-08-11_1805

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1400/gguf/model-Q4_K_M.gguf`
**Overall: 27/37** — gate topics: **17/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 2/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 2/4 | ✓ |
| dev_levy | 2/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 2/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **cit30-2** (gate): My company turns over N500 million a year. What income tax rate applies to the company?
  - missing: `30\s*%`
  - answer: - A company that turns over N500 million a year is classified as a small company under the Nigeria Tax Reform Acts 2025. This means it is eligible for the 0% small company tax rate. Confirm specifics with FIRS / a licensed accountant.
- **def-2** (gate): What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - missing: `100\s*million|100,000,000|₦100`, `250\s*million|250,000,000|₦250`
  - answer: - The turnover limit for small-company status under the 2025 Act is £10 million per year, and the fixed-asset limit is £2.5 million. If your company's turnover or fixed assets exceed these limits, it will no longer qualify as a small company.
- **prof-3** (gate): Why does my small consulting company still pay company income tax despite low turnover?
  - missing: `professional`
  - answer: - A small consulting company pays company income tax because it's not classified as a small business under the Nigeria Tax Reform Acts 2025. This means it doesn't qualify for the 0% small business tax rate, and instead pays the standard 30% company income tax rate. Confirm specifics with FIRS / a
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  -  wrong-hit: `(?<![\d.])0\s*%`
  - answer: - The Companies Income Tax rate for a business with N80 million turnover and N100 million assets is 30%. This is because the business does not meet the criteria for the 0% small company rate, and the 30% standard rate applies.
- **dev-1** (gate): What is the Development Levy rate in Nigeria?
  - missing: `4\s*%`
  - answer: - The Development Levy rate in Nigeria is 1.5% of the gross fixed assets of a company. This rate applies to companies that have gross fixed assets of more than N100 million. The Development Levy is a tax that helps fund infrastructure development in Nigeria.
- **dev-2** (gate): On what profits is the Development Levy charged, and at what rate?
  - missing: `4\s*%`, `assessable`
  - answer: - The Development Levy is charged on profits from the sale of property, including land, buildings, and other improvements. The rate is 10% of the profits. This means that if you sell a property and make a profit, you will need to pay 10% of that profit as Development Levy.
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an entity that is not a non-resident and the payment is for professional services rendered. This exemption applies to payments made to entities that are not non-residents, such as other sma
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions from a closely-held Nigerian company is 30%. This applies when a Nigerian company distributes its profits to its shareholders, as per the Nigeria Tax Reform Acts 2025.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals are taxed at 10% on capital gains from the sale of assets. This applies to individuals who are not eligible for the 0% tax rate for small companies. Confirm specifics with FIRS or a licensed accountant.
- **pit-2**: What is the top personal income tax rate under the new bands?
  - missing: `25\s*%`
  - answer: - The top personal income tax rate under the new bands is 45%. This applies to individuals with taxable income above the highest band. Confirm specifics with FIRS or a licensed accountant.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your goods and services.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% VAT to the invoice for goods you sell.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This rate was increased from 5% in 2023. Confirm specifics with FIRS / a licensed accountant.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your sales.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at a rate of 0%. This means they are exempt from paying Companies Income Tax.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - Yes, your shop will pay company income tax. As a non-professional services business, your annual turnover of N45 million qualifies you for the 30% CIT rate. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A trading company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. According to the Nigeria Tax Reform Acts 2025, companies with annual turnover of N100 million or below and total fixed assets of N250 million or below are exempt from CIT. This mean
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 0% company income tax. This means they are exempt from paying company income tax.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This rate applies to companies that meet the definition of a large company under the Nigeria Tax Reform Acts 2025.
- ❌ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company that turns over N500 million a year is classified as a small company under the Nigeria Tax Reform Acts 2025. This means it is eligible for the 0% small company tax rate. Confirm specifics with FIRS / a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for businesses above the small-company threshold is 30%. This applies to companies with annual gross turnover of more than 100 million naira or a total of more than 250 million naira in fixed assets.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - The annual turnover that qualifies a company as 'small' for the 0% company income tax rate is ₦100 million or below. This means that any company with an annual turnover of ₦100 million or below is eligible for the 0% company income tax rate.
- ❌ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for small-company status under the 2025 Act is £10 million per year, and the fixed-asset limit is £2.5 million. If your company's turnover or fixed assets exceed these limits, it will no longer qualify as a small company.
- ✅ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is now N100 million annual gross turnover or below. This threshold applies to companies that meet the other conditions for small companies, such as not being a professional services company and having a maximum of 100 employees. Confirm specifics with FIRS / a li
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - A company must have an annual gross turnover of N100 million or below to qualify as a small company and pay 0% tax. Since your turnover is N120 million, you do not qualify for the 0% tax rate. You should check with the Nigeria Revenue Service or a licensed accountant for specific tax implicatio
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your consulting firm must meet both the turnover and fixed asset thresholds. Your turnover is N60 million, which is above the N100 million threshold. Additionally, your fixed assets must be worth N250 million or less. Since your fixed assets 
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm can never be classified as a small company for tax purposes. This classification is reserved for businesses that meet specific criteria, such as having a turnover of less than N100 million per annum and a total of 250 or fewer employees.
- ❌ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small consulting company pays company income tax because it's not classified as a small business under the Nigeria Tax Reform Acts 2025. This means it doesn't qualify for the 0% small business tax rate, and instead pays the standard 30% company income tax rate. Confirm specifics with FIRS / a
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - The Companies Income Tax rate for a business with N80 million turnover and N100 million assets is 30%. This is because the business does not meet the criteria for the 0% small company rate, and the 30% standard rate applies.
- ❌ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 1.5% of the gross fixed assets of a company. This rate applies to companies that have gross fixed assets of more than N100 million. The Development Levy is a tax that helps fund infrastructure development in Nigeria.
- ❌ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on profits from the sale of property, including land, buildings, and other improvements. The rate is 10% of the profits. This means that if you sell a property and make a profit, you will need to pay 10% of that profit as Development Levy.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - No, a small company does not have to pay the Development Levy. This tax is only applicable to companies that are not classified as small. Confirm specifics with FIRS or a licensed accountant.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company in Nigeria pays a development levy of 4% on its profits. This is in addition to the 30% income tax. The development levy is charged on the company's taxable profits and is intended to support infrastructure development in the country.
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an entity that is not a non-resident and the payment is for professional services rendered. This exemption applies to payments made to entities that are not non-residents, such as other sma
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions from a closely-held Nigerian company is 30%. This applies when a Nigerian company distributes its profits to its shareholders, as per the Nigeria Tax Reform Acts 2025.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to capital gains from the sale of assets by companies.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Capital Gains Tax is not applicable for small companies. This means that if a small company sells a delivery van at a profit, it won't have to pay Capital Gains Tax on it. However, it's always a good idea to confirm this with the Nigeria Revenue Service or a licensed accountant to ensure you're
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed at 10% on capital gains from the sale of assets. This applies to individuals who are not eligible for the 0% tax rate for small companies. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - The annual income threshold for personal income tax exemption is ₦800,000. This means that individuals earning ₦800,000 or less per year are exempt from paying personal income tax.
- ❌ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 45%. This applies to individuals with taxable income above the highest band. Confirm specifics with FIRS or a licensed accountant.
- ✅ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is a tax relief that allows you to claim a deduction for rent paid on your main home. This relief is available if you're a resident of Nigeria and you're paying rent on your main home. The relief is calculated as 20% of your annual rent paid, but it's capped 
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This is based on the tax residency rules in Nigeria. Confirm specifics with FIRS or a licensed accountant.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - No, the money you send home to your family in Nigeria is not taxed. This is because it's considered a personal remittance, which is not subject to Nigerian tax laws. However, it's always a good idea to confirm with the Nigeria Revenue Service or a licensed accountant to ensure you're following 
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, your salary is not taxed in Nigeria if you pay it into your Nigerian account. This is because the Nigerian Tax Reform Act 2025 allows non-residents to be taxed on their Nigerian-source income only, and not on their foreign-source income. However, it's always best to confirm with the Nigeria
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on Nigerian-source income, such as rental income from Nigerian property or dividends from Nigerian companies. However, non-residents are not taxed on foreign-source income, such as income earned from investments outside Nigeria. This means that non-residents are only tax
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A Nigerian company must file its annual tax returns within 6 months after the end of its accounting year. This is according to the Nigeria Tax Reform Acts 2025, which requires companies to file their returns within 6 months of the end of their accounting year. Confirm specifics with FIRS / a li
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - The failure to register for tax can cost your business a penalty of NGN 50,000 for the first month and NGN 25,000 for each subsequent month the failure continues. This penalty is imposed by the Nigeria Revenue Service. If your business continues to fail to register, the penalty will continue to
