# Fact-recall eval — 2026-08-11_1649

Model: `/Users/husseinalamutu/Desktop/Development/adtc-2026/build/_ckpt_1100/gguf/model-Q4_K_M.gguf`
**Overall: 23/37** — gate topics: **15/23** (DO NOT SHIP)

| topic | passed | gate |
|---|---|---|
| vat_rate | 4/4 | ✓ |
| cit_small_rate | 3/4 | ✓ |
| cit_standard_rate | 3/3 | ✓ |
| smallco_definition | 3/4 | ✓ |
| prof_services_exclusion | 1/4 | ✓ |
| dev_levy | 1/4 | ✓ |
| withholding_tax | 0/2 |  |
| capital_gains | 2/3 |  |
| personal_income_tax | 1/3 |  |
| tax_residency | 4/4 |  |
| filing_penalties | 1/2 |  |

## Failures
- **cit0-2** (gate): My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - missing: `0\s*%|exempt|do(es)? not pay|don't pay`
  - answer: - Yes, your shop pays company income tax. As a non-professional services business, your annual turnover of N45 million qualifies you as a company, and you are subject to company income tax.
- **def-3** (gate): Is the small-company tax threshold still N25 million turnover?
  - missing: `100\s*million|100,000,000|₦100`
  - answer: - No, the small-company tax threshold has changed. Companies with annual gross turnover of N25 million or below are now classified as small companies and pay 0% tax. This applies to companies that also have total fixed assets of N250 million or below.
- **prof-1** (gate): I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - missing: `professional|exclu|not qualify|do(es)? not qualify|don't qualify|cannot`
  - answer: - To qualify for the 0% small company income tax rate, your business must meet certain criteria. For a consulting firm, the turnover threshold is N100 million. Since your turnover is N60 million, you do not meet the threshold and are not eligible for the 0% small company tax rate. You should chec
- **prof-3** (gate): Why does my small consulting company still pay company income tax despite low turnover?
  - missing: `professional`
  - answer: - A small consulting company is not exempt from paying company income tax. This is because the turnover threshold for a small company is based on the total turnover of the business, not just the turnover of the consulting services. If your company's turnover is above the threshold, you will still
- **prof-4** (gate): A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - missing: `30\s*%` wrong-hit: `(?<![\d.])0\s*%`
  - answer: - A company with N80 million turnover and N100 million assets is a small company. For small companies, the Companies Income Tax rate is 0%.
- **dev-1** (gate): What is the Development Levy rate in Nigeria?
  - missing: `4\s*%`
  - answer: - The Development Levy rate in Nigeria is 2.5%. This is applicable to companies that are not classified as small businesses.
- **dev-2** (gate): On what profits is the Development Levy charged, and at what rate?
  - missing: `4\s*%`, `assessable`
  - answer: - The Development Levy is charged on profits above the exempt threshold. The rate is 30% of profits above the exempt threshold.
- **dev-4** (gate): Besides the 30% income tax, what development levy does a large company pay on its profits?
  - missing: `4\s*%` wrong-hit: `(?<![\d.])2\s*%`
  - answer: - A large company pays a development levy of 2% on its profits. This is in addition to the 30% income tax.
- **wht-1**: When is a small company exempt from deducting withholding tax at source on a payment?
  - missing: `2\s*million|2,000,000|₦2`
  - answer: - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered. This exemption applies to payments made to individuals for work such as consulting, personal services, or freelance work.
- **wht-2**: What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - missing: `10\s*%`
  - answer: - The withholding tax rate for deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders.
- **cgt-3**: How are capital gains of individuals taxed now?
  - missing: `personal income|bands|25\s*%`
  - answer: - Individuals are taxed on capital gains at a flat rate of 30%. This applies to both capital gains from selling assets and capital gains from investments.
- **pit-2**: What is the top personal income tax rate under the new bands?
  - missing: `25\s*%`
  - answer: - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- **pit-3**: How does the new rent relief for individuals work?
  - missing: `500,000|₦500`
  - answer: - The new rent relief for individuals is a tax credit of 20% of the rent paid, up to a maximum of NGN 50,000 per year. This credit can be claimed on the individual's tax return.
- **file-2**: My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - missing: `50,000|₦50`
  - answer: - Failing to register for tax can cost your business a significant amount. The penalty starts at 5,000 Naira for the first month, and increases to 10,000 Naira for each subsequent month. This means the total penalty can be substantial, especially if your business has been trading for a long time.

## All answers

- ✅ **vat-1** A customer is querying their bill — what percentage of VAT am I required to charge on goods in Nigeria?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on the sale of goods.
- ✅ **vat-2** How much VAT do I add to a customer's invoice for goods I sell?
  - - The standard VAT rate in Nigeria is 7.5%. You should add this to the invoice for goods you sell.
- ✅ **vat-3** Is VAT in Nigeria still 5%?
  - - VAT in Nigeria is 7.5%. This applies to most goods and services.
- ✅ **vat-4** Wetin be the VAT rate wey I go charge for goods for my shop?
  - - The standard VAT rate in Nigeria is 7.5%. This means you should charge 7.5% VAT on most goods and services.
- ✅ **cit0-1** What Companies Income Tax rate does a qualifying small company pay?
  - - A qualifying small company pays Companies Income Tax at 0%. This is because small companies are eligible for this tax exemption.
- ❌ **cit0-2** My shop's turnover is N45 million a year and it is not a professional services business. Do we pay company income tax?
  - - Yes, your shop pays company income tax. As a non-professional services business, your annual turnover of N45 million qualifies you as a company, and you are subject to company income tax.
- ✅ **cit0-3** Is a trading company with N90 million turnover and N150 million fixed assets liable for Companies Income Tax?
  - - A trading company with N90 million turnover and N150 million fixed assets is not a small company. Companies with turnover of N90 million or more and fixed assets of N150 million or more are subject to Companies Income Tax at 30%.
- ✅ **cit0-4** Small companies in Nigeria pay 20% company income tax, right?
  - - No, small companies in Nigeria pay 0% company income tax. This means they are exempt from paying any company income tax.
- ✅ **cit30-1** What is the standard Companies Income Tax rate for a large Nigerian company?
  - - The standard Companies Income Tax rate for a large Nigerian company is 30%. This applies to companies with a gross turnover of NGN 100,000,000 or more.
- ✅ **cit30-2** My company turns over N500 million a year. What income tax rate applies to the company?
  - - A company with N500 million turnover pays 30% Companies Income Tax.
- ✅ **cit30-3** What company income tax rate applies once a business is above the small-company threshold?
  - - The company income tax rate for businesses above the small-company threshold is 30%. This applies to companies with annual gross turnover above the small-company threshold.
- ✅ **def-1** What annual turnover qualifies a company as 'small' for the 0% company income tax rate?
  - - A company qualifies for the 0% company income tax rate if its annual gross turnover is below NGN 100,000,000. This means the turnover threshold is NGN 100 million.
- ✅ **def-2** What are the turnover and fixed-asset limits for small-company status under the 2025 Act?
  - - A company is considered a small company if its annual gross turnover is less than NGN 100,000,000 and its total fixed assets are less than NGN 250,000,000.
- ❌ **def-3** Is the small-company tax threshold still N25 million turnover?
  - - No, the small-company tax threshold has changed. Companies with annual gross turnover of N25 million or below are now classified as small companies and pay 0% tax. This applies to companies that also have total fixed assets of N250 million or below.
- ✅ **def-4** My turnover is N120 million. Do I qualify as a small company for 0% tax?
  - - A company qualifies as small if its annual gross turnover is N100 million or below. Since your turnover is N120 million, you do not qualify for the 0% tax rate.
- ❌ **prof-1** I run a consulting firm in Lagos with a turnover of N60 million. Do I qualify for the 0% small company income tax rate?
  - - To qualify for the 0% small company income tax rate, your business must meet certain criteria. For a consulting firm, the turnover threshold is N100 million. Since your turnover is N60 million, you do not meet the threshold and are not eligible for the 0% small company tax rate. You should chec
- ✅ **prof-2** Can an accounting or law firm ever be classified as a small company for tax purposes?
  - - No, an accounting or law firm is never classified as a small company for tax purposes. This means they pay the standard corporate tax rate, not the small company rate.
- ❌ **prof-3** Why does my small consulting company still pay company income tax despite low turnover?
  - - A small consulting company is not exempt from paying company income tax. This is because the turnover threshold for a small company is based on the total turnover of the business, not just the turnover of the consulting services. If your company's turnover is above the threshold, you will still
- ❌ **prof-4** A tech consultancy has N80 million turnover and N100 million assets. What Companies Income Tax rate applies?
  - - A company with N80 million turnover and N100 million assets is a small company. For small companies, the Companies Income Tax rate is 0%.
- ❌ **dev-1** What is the Development Levy rate in Nigeria?
  - - The Development Levy rate in Nigeria is 2.5%. This is applicable to companies that are not classified as small businesses.
- ❌ **dev-2** On what profits is the Development Levy charged, and at what rate?
  - - The Development Levy is charged on profits above the exempt threshold. The rate is 30% of profits above the exempt threshold.
- ✅ **dev-3** Does a small company have to pay the Development Levy?
  - - A small company is exempt from paying the Development Levy. This means you can avoid this tax if your company qualifies as small.
- ❌ **dev-4** Besides the 30% income tax, what development levy does a large company pay on its profits?
  - - A large company pays a development levy of 2% on its profits. This is in addition to the 30% income tax.
- ❌ **wht-1** When is a small company exempt from deducting withholding tax at source on a payment?
  - - A small company is exempt from deducting withholding tax at source on a payment if the payment is made to an individual for personal services rendered. This exemption applies to payments made to individuals for work such as consulting, personal services, or freelance work.
- ❌ **wht-2** What withholding tax rate applies to deemed distributions of a closely-held Nigerian company?
  - - The withholding tax rate for deemed distributions from a Nigerian company is 30%. This applies to distributions made by a Nigerian company to its shareholders.
- ✅ **cgt-1** What is the Capital Gains Tax rate for companies under the 2025 reform?
  - - The Capital Gains Tax rate for companies under the 2025 reform is 30%. This applies to capital gains from the sale of assets.
- ✅ **cgt-2** If a small company sells a delivery van at a profit, is Capital Gains Tax due on it?
  - - Capital Gains Tax is not applicable to small companies. This means that if a small company sells a delivery van at a profit, it will not have to pay Capital Gains Tax. However, it's always a good idea to check with the Nigeria Revenue Service or a licensed accountant to confirm the specifics of
- ❌ **cgt-3** How are capital gains of individuals taxed now?
  - - Individuals are taxed on capital gains at a flat rate of 30%. This applies to both capital gains from selling assets and capital gains from investments.
- ✅ **pit-1** Below what annual income is an individual exempt from personal income tax?
  - - The annual income threshold for personal income tax exemption is ₦800,000. This means individuals earning below this amount are exempt from paying personal income tax.
- ❌ **pit-2** What is the top personal income tax rate under the new bands?
  - - The top personal income tax rate under the new bands is 30%. This applies to income above the highest band.
- ❌ **pit-3** How does the new rent relief for individuals work?
  - - The new rent relief for individuals is a tax credit of 20% of the rent paid, up to a maximum of NGN 50,000 per year. This credit can be claimed on the individual's tax return.
- ✅ **res-1** How many days must I spend in Nigeria to become a tax resident?
  - - You are considered a Nigerian tax resident if you are physically present in Nigeria for 183 days or more within any 12-month period. This is based on the tax laws of Nigeria.
- ✅ **res-2** Is the money I send home to my family in Nigeria every month taxed?
  - - Genuine personal remittances are not taxable. This means you can send money to your family in Nigeria without worrying about it being taxed.
- ✅ **res-3** I live abroad and work remotely for a foreign company. Is my salary taxed in Nigeria if I pay it into my Nigerian account?
  - - No, your salary is not taxed in Nigeria. Income earned from a foreign source is taxable only if it is remitted into Nigeria.
- ✅ **res-4** Are non-residents taxed on income they earn outside Nigeria?
  - - Non-residents are taxed on Nigerian-source income, such as rental income from Nigerian property or profits from Nigerian business operations. However, non-residents are not taxed on income earned outside Nigeria.
- ✅ **file-1** When must an established Nigerian company file its annual tax returns?
  - - An established Nigerian company must file its annual tax returns within 6 months after the end of its accounting year. This means the company should file its returns by the end of the 6th month following the end of its accounting period.
- ❌ **file-2** My business never registered for tax and has been trading for months. What does that failure cost, and does it grow?
  - - Failing to register for tax can cost your business a significant amount. The penalty starts at 5,000 Naira for the first month, and increases to 10,000 Naira for each subsequent month. This means the total penalty can be substantial, especially if your business has been trading for a long time.
