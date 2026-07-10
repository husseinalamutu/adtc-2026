# Fact-recall eval — 2026-07-10_0706

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/gguf/model-Q4_K_M.gguf`
**Overall: 24/37** — gate topics: **16/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 3/4 | ✓ |
| cit_small_rate | 4/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 1/4 | ✓ |
| prof_services_exclusion | 4/4 | ✓ |
| dev_levy | 1/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 3/3 |  |
| personal_income_tax | 1/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 0/2 |  |

## Failures
- **vat-1** (gate): What is the current VAT rate in Nigeria?
  -  wrong-hit: `\b5\s*%`
  - answer: - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
- **def-1** (gate): What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The annual turnover that qualifies a company for the 0% company income tax rate is ₹1 crores and above. This applies to large companies and not to small companies. To be classified as a small company, the company must have an annual turnover of ₹50 lakhs and below.
- **def-2** (gate): What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - missing: `100\s*million|100,000,000|₦100`, `250\s*million|250,000,000|₦250`
  - answer: - The small-company status in the 2025 Act is for companies with a turnover and/or fixed assets not exceeding the following limits: - Turnover: 40 million Nigerian NGN. - Fixed assets: 400 million Nigerian NGN. To be a small-company, a company must have a turnover and/or fixed assets that do not 
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - The small-company tax threshold is N10 million. This applies to companies with a taxable turnover of N10 million or more. If your company's turnover is below this amount, you are exempt from paying the small-company tax.
- **dev-1** (gate): What is the Development Levy rate in Nigeria?
  - missing: `4\s*%`
  - answer: - The Development Levy is 0.5% of assessable revenue. This applies to companies and organizations with assessable revenue above NGN 500,000,000. It's collected twice a year on specified dates. For more details, please refer to the latest tax laws or contact a licensed accountant or the Nigeria Re
- **dev-2** (gate): On what profits is the Development Levy charged, and at what rate?
  - missing: `4\s*%`, `assessable`
  - answer: - The Development Levy is charged on profits derived from the development of land. The rate is 3.5%. This applies to qualifying developers. Please confirm your specific situation with your tax advisor.
- **dev-4** (gate): Besides the 30% income tax, what development levy does a large company pay on its profits?
  - missing: `4\s*%`
  - answer: - The development levy is 5.0% for companies. This applies to the company's profits. In addition to the 30% income tax, large companies also have to pay this 5.0% development levy on their profits. This applies to companies chargeable to tax whose profits are chargeable to tax and which are also 
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - Small companies are exempt from deducting withholding tax at source on a payment if the amount does not exceed an equivalent of INR 50,000 (Indian Rupees Fifty Thousand) per payment. This exemption applies to all companies that meet this criterion, regardless of their turnover or the nature of 
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions of a closely-held Nigerian company is 30%. This applies when the company makes a distribution to its shareholders, and the distribution is not in the form of cash.
- **pit-2**: What is the top personal income tax rate under the new bands?
  - missing: `25\s*%`
  - answer: - The top personal income tax rate under the new bands is 45%. This applies to income earned above Rs 10 lakhs (Rs 1,000,000) per annum.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `500,000|₦500`
  - answer: - The new rent relief for individuals allows qualifying taxpayers to claim a tax relief on the rent paid on their main home. This relief is 20% of the rent paid, up to a maximum of ₹50,000 per year. The relief is 100% deductible from assessable profits, and it can be used to offset capital gains 
- **file-1**: When must an established Nigerian company file its annual tax returns?
  - missing: `6\s*months`
  - answer: - An established Nigerian company is required to file its annual tax returns within 60 days of the end of its accounting year. If the company does not meet this deadline, they must pay a 0.5% surcharge per month until the outstanding tax is settled. If the company fails to make the annual filing 
- **file-2**: What is the penalty for failing to register for tax in Nigeria?
  - missing: `50,000|₦50`
  - answer: - The penalty for failing to register for tax in Nigeria is 20% of the tax that should have been paid. This is imposed on the tax that is due or omitted to be paid, but not more than twice the tax due. This applies to both individuals and companies. To avoid this, you should register for tax as s

## All answers

- ❌ **vat-1** What is the current VAT rate in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you need to add 7.5% VAT to the goods you sell. To calculate the VAT, multiply the total invoice amount by 7.5%. For example, if the goods you sell are N50,000, you should add 7.5% VAT, which is N3,750, making the final invoice amount N53,750
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - VAT in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The VAT rate in Nigeria is 7.5%. This applies to most goods and services. Confirm with the Nigeria Revenue Service or an accountant for the most up-to-date information.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - The Companies Income Tax rate for qualifying small companies is 0%. This applies to companies with a gross turnover of less than 500,000,000. Confirm with the Nigeria Revenue Service or a licensed accountant before filing.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - If your business turnover is above the turnover threshold for the current financial year (currently this threshold is N10 million per annum for most businesses), you are required to pay company income tax at 30%. However, if your business qualifies for a reduced tax rate or relief, you should a
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A company that has a turnover of N90 million and fixed assets of N150 million is not considered a small company and is, therefore, liable for Companies Income Tax. This company would be taxed at 30%. Before filing taxes, please confirm the specific requirements with FIRS or a licensed accountan
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, that's not correct. The standard company income tax rate for small companies in Nigeria is 30%. This applies to companies that meet the small company criteria. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate in Nigeria is 30%. This applies to large companies and most small companies as well. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - The income tax rate for companies in Nigeria is 30%. This applies to most companies, but please confirm specifics with FIRS or a licensed accountant.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for small companies is 30%. Once a business exceeds this threshold, it is required to pay the standard company income tax rate, which is 30%. This applies to companies that are not classified as small companies.
- ❌ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - The annual turnover that qualifies a company for the 0% company income tax rate is ₹1 crores and above. This applies to large companies and not to small companies. To be classified as a small company, the company must have an annual turnover of ₹50 lakhs and below.
- ❌ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The small-company status in the 2025 Act is for companies with a turnover and/or fixed assets not exceeding the following limits: - Turnover: 40 million Nigerian NGN. - Fixed assets: 400 million Nigerian NGN. To be a small-company, a company must have a turnover and/or fixed assets that do not 
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is N10 million. This applies to companies with a taxable turnover of N10 million or more. If your company's turnover is below this amount, you are exempt from paying the small-company tax.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - To qualify for the 0% tax rate as a small company in Nigeria, your turnover must be less than or equal to N50 million per annum. Since your turnover is N120 million, you do not qualify for the 0% tax rate. You'll need to calculate and pay your taxes at the standard rates. If you need further de
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - The small company income tax rate is 0% for companies with a turnover of N50 million or below. Since your company's turnover is N60 million, you do not qualify for this rate. Instead, your company will be taxed at 30%. Confirm with the Nigeria Revenue Service or a licensed accountant for specif
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - An accounting or law firm is not classified as a small company for tax purposes. For these businesses, they are taxed as companies. If they do not meet the requirements for small companies, they'll be taxed as per normal corporate tax rates. It's essential to check with the Nigerian Revenue Ser
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - The company income tax rate in Nigeria is 30%. This applies to companies with an annual turnover or net profits of over NGN 10 million or a maximum balance of NGN 30 million. If your company's turnover or net profits are below these thresholds, you may not be required to pay the company income 
- ✅ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - The Companies Income Tax rate for a company with a taxable income between N15 million and N25 million is 30%. However, since your company has a turnover of N80 million and assets of N100 million, it's likely that it is classifiable as a large company. For large companies, the Companies Income T
- ❌ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy is 0.5% of assessable revenue. This applies to companies and organizations with assessable revenue above NGN 500,000,000. It's collected twice a year on specified dates. For more details, please refer to the latest tax laws or contact a licensed accountant or the Nigeria Re
- ❌ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on profits derived from the development of land. The rate is 3.5%. This applies to qualifying developers. Please confirm your specific situation with your tax advisor.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means they do not have to pay it. To qualify for this exemption, the company must meet the size criteria set by the Revenue Commissioners. If the company's size does not meet these criteria, it will be subject to the Development Levy. B
- ❌ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - The development levy is 5.0% for companies. This applies to the company's profits. In addition to the 30% income tax, large companies also have to pay this 5.0% development levy on their profits. This applies to companies chargeable to tax whose profits are chargeable to tax and which are also 
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - Small companies are exempt from deducting withholding tax at source on a payment if the amount does not exceed an equivalent of INR 50,000 (Indian Rupees Fifty Thousand) per payment. This exemption applies to all companies that meet this criterion, regardless of their turnover or the nature of 
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions of a closely-held Nigerian company is 30%. This applies when the company makes a distribution to its shareholders, and the distribution is not in the form of cash.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies is 30%. This applies to companies and their shareholders. This applies for companies under the 2025 reform.
- ✅ **cgt-2** Do small companies pay Capital Gains Tax?
  - - Small companies are exempt from Capital Gains Tax. This means they do not have to pay Capital Gains Tax on the sale of their assets.
- ✅ **cgt-3** How are capital gains of individuals taxed now?
  - - The capital gains of individuals are taxed at progressive rates from 0% to 25%. However, if the capital gains are exempt or zero-rated (such as capital gains arising from the death of a citizen), they are exempt from taxation. To be eligible for the lower tax rates, the individual must meet cer
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - Individuals earning an annual income of ₦800,000 or below are exempt from PIT. This means they do not have to pay personal income tax on their earnings. However, individuals earning above ₦800,000 per annum will have to declare their income and pay tax on it. This exemption applies to all indiv
- ❌ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 45%. This applies to income earned above Rs 10 lakhs (Rs 1,000,000) per annum.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals allows qualifying taxpayers to claim a tax relief on the rent paid on their main home. This relief is 20% of the rent paid, up to a maximum of ₹50,000 per year. The relief is 100% deductible from assessable profits, and it can be used to offset capital gains 
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - A person is considered a Nigerian tax resident if they are physically present in Nigeria for 183 days or more within any 12-month period. This is known as the "183-day rule." If you meet this requirement, you are a Nigerian tax resident and need to consider your tax obligations in Nigeria. Conf
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - Income from a Nigerian bank account that is sent to a family member in Nigeria is not considered Nigerian taxable income. This means it's not taxable in Nigeria. However, it's advisable to check with a licensed accountant or the Nigeria Revenue Service to confirm the specifics of tax obligation
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, the salary is exempt from Nigerian tax as long as it's paid into a Nigerian bank account. This exemption applies even if the salary is paid into a foreign bank account and then transferred into a Nigerian bank account. However, ensure you check with the Nigeria Revenue Service or a tax prof
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are exempt from tax on their Nigerian-sourced income. This means if they earn income in Nigeria and it's subject to Nigerian tax, they won't be taxed on it again. However, they are still required to declare this income on their tax returns. They are also liable to pay tax on any N
- ❌ **file-1** When must an established Nigerian company file its annual tax returns?
  - - An established Nigerian company is required to file its annual tax returns within 60 days of the end of its accounting year. If the company does not meet this deadline, they must pay a 0.5% surcharge per month until the outstanding tax is settled. If the company fails to make the annual filing 
- ❌ **file-2** What is the penalty for failing to register for tax in Nigeria?
  - - The penalty for failing to register for tax in Nigeria is 20% of the tax that should have been paid. This is imposed on the tax that is due or omitted to be paid, but not more than twice the tax due. This applies to both individuals and companies. To avoid this, you should register for tax as s
