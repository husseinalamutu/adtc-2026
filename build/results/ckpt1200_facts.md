# Fact-recall eval — 2026-08-11_1921

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1200/gguf/model-Q4_K_M.gguf`
**Overall: 33/37** — gate topics: **22/23** (DO NOT SHIP)

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
| personal_income_tax | 2/3 |  |
| tax_residency | 3/4 |  |
| filing_penalties | 2/2 |  |

## Failures
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - missing: `30\s*%` wrong-hit: `(?<![\d.])0\s*%`
  - answer: - A company with N80 million turnover and N100 million assets is a small company. The Companies Income Tax rate for small companies is 0%. This means the company is exempt from paying Companies Income Tax.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Capital gains are taxed at a rate of 10% for individuals. This means that the capital gains from selling assets are taxed at a flat rate of 10%. However, if the capital gains are more than 500,000 Naira, the tax rate is 20%. The tax is deducted at source if the amount exceeds 500,000 Naira.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `500,000|₦500`
  - answer: - The new rent relief for individuals is 20% of annual rent paid, capped at a maximum of 50,000 Naira. This applies to individuals who are the head of a household or a partner in a partnership. The annual rent must be verified by a licensed accountant.
- **res-4**: Are non-residents taxed on income they earn outside Nigeria?
  - missing: `no\b|not\b|only|Nigerian.source`
  - answer: - Non-residents are taxed on income they earn in Nigeria, even if the income is earned outside Nigeria. This means that if you earn income from a foreign source, you may be required to pay tax on that income in Nigeria. It's important to check with the Nigeria Revenue Service or a licensed accoun

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means I should charge 7.5% VAT on the value of goods sold. Confirm specifics with the Nigeria Revenue Service or a licensed accountant.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should add 7.5% of the invoice amount as VAT. Confirm specifics with the Nigeria Revenue Service.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - The standard VAT rate in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on your taxable goods.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at a rate of 0%. This means they are exempt from paying CIT.
- ✅ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - If your annual turnover is N45 million, you are not a small company and are therefore subject to company income tax at 30%. This means you will need to pay tax on your profits. Confirm specifics with FIRS or a licensed accountant.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A company with N90 million turnover and N150 million fixed assets is not liable for Companies Income Tax. This is because the turnover threshold for small companies is N100 million, and the fixed assets threshold is also N100 million. As a small company, it is exempt from CIT. However, it shoul
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 0% company income tax. This means they are exempt from paying company income tax.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies with a gross turnover of ₦100,000,000 or more.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company with N500 million turnover pays 30% Companies Income Tax. This is because the threshold for small companies is N100 million, and your company exceeds this amount.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for a company above the small-company threshold is 30%. This applies to all companies that meet the criteria for being a large company.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company is considered 'small' if its annual gross turnover is ₹100,000,000 or below. This means the company must meet this turnover threshold to qualify for the 0% CIT rate.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - The turnover limit for small companies is NGN 100,000,000 (₦100 million) per annum, and the fixed-asset limit is NGN 250,000,000 (₦250 million) per annum.
- ✅ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - The small-company tax threshold is now N100 million annual turnover. This change took effect on January 1, 2025.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - No, your company doesn't qualify as a small company. The turnover threshold for a small company is NGN 100 million or below. Your company's turnover is NGN 120 million, which exceeds this limit. As a result, your company is subject to the standard 30% Corporate Income Tax rate.
- ✅ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your company must have a turnover of N25 million or less and total fixed assets of N100 million or less. Since your company has a turnover of N60 million, it does not meet the turnover threshold. Additionally, if your company provides profess
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, a business providing professional services like accounting or law is never classified as a small company. This means they are subject to the standard corporate tax rate of 30%.
- ✅ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small company is exempt from CIT if its annual turnover is below NGN 100,000,000. However, if your business provides professional services like consulting, you are not considered a small company and will pay 30% CIT. This is because the definition of a small company excludes businesses provid
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - A company with N80 million turnover and N100 million assets is a small company. The Companies Income Tax rate for small companies is 0%. This means the company is exempt from paying Companies Income Tax.
- ✅ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 4%. This levy is imposed on the assessable profits of all companies chargeable to tax.
- ✅ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on assessable profits of companies. The rate is 4%. This levy is imposed on the assessable profits of all companies, including those that are not registered for VAT.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - Small companies are exempt from the Development Levy. This means they don't have to pay it.
- ✅ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a Development Levy of 4% on its assessable profits. This applies to companies with a gross turnover of N250 million or more.
- ✅ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to a supplier with a valid TIN and the transaction value is ₦2 million or less. This exemption applies to payments for goods or services rendered.
- ✅ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate on deemed distributions of a closely-held Nigerian company is 10%. This applies to distributions made by a company that meets the definition of a closely-held company.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies is 30%. This applies to capital gains from the sale of capital assets.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - No, a small company is exempt from CGT on the sale of a qualifying asset like a delivery van. This exemption applies to small companies, so you won't have to pay CGT on the sale.
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Capital gains are taxed at a rate of 10% for individuals. This means that the capital gains from selling assets are taxed at a flat rate of 10%. However, if the capital gains are more than 500,000 Naira, the tax rate is 20%. The tax is deducted at source if the amount exceeds 500,000 Naira.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - Individuals earning below NGN 800,000 per annum are exempt from PIT. This exemption applies to individuals who meet the annual income threshold.
- ✅ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate is 25%. This applies to income earned above the highest tax band.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is 20% of annual rent paid, capped at a maximum of 50,000 Naira. This applies to individuals who are the head of a household or a partner in a partnership. The annual rent must be verified by a licensed accountant.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This means you are taxed on your Nigerian income, even if you're a non-resident elsewhere.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - Genuine personal remittances are exempt from tax. This means you won't have to pay tax on money you send home to your family in Nigeria. However, if you're a Nigerian resident and you're a company, you might have to pay tax on your personal remittances if they're considered business income. It'
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, your Nigerian salary is not taxable in Nigeria. This is because you are a non-resident Nigerian, meaning you do not pay Nigerian taxes on your foreign income. However, you should confirm with the Nigeria Revenue Service (NRS) or a licensed accountant to ensure you're complying with all tax 
- ❌ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on income they earn in Nigeria, even if the income is earned outside Nigeria. This means that if you earn income from a foreign source, you may be required to pay tax on that income in Nigeria. It's important to check with the Nigeria Revenue Service or a licensed accoun
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - A company must file its annual tax returns within 6 months after the end of its accounting year. This means the filing deadline is 6 months after the end of the accounting period. If the company's accounting year ends on 31 December, the deadline is 31 August of the following year. If the compa
- ✅ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - If your business hasn't registered for tax, you'll be charged a penalty of NGN 50,000 for the first month and NGN 25,000 for each subsequent month. This penalty continues to accrue until your business registers for tax. If your business continues to operate without a valid tax registration, you
