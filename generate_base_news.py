"""
Task 1: Generate base_news.csv
80 synthetic news items (40 bullish, 40 bearish) across 5 sectors.
Real company names, tickers, and specific numbers have been anonymized.
"""

import csv
import random

news_data = [
    # ─────────────────────────────────────────────────────────────────────────
    # TECH — BULLISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 1, "sector": "Tech", "direction": "Bullish",
     "headline": "Leading cloud software firm reports record quarterly revenue, raises full-year guidance above analyst expectations",
     "body": "A major enterprise software company announced quarterly revenue growth that beat consensus estimates, citing strong demand for its AI-integrated SaaS platform. Management raised full-year guidance well above the Street's forecast and announced a new share buyback program."},

    {"id": 2, "sector": "Tech", "direction": "Bullish",
     "headline": "Semiconductor giant secures multi-year supply agreement with global automaker consortium",
     "body": "A leading chipmaker signed a long-term supply deal with a consortium of major automakers to provide next-generation automotive chips. The agreement, spanning several years, is expected to add significant recurring revenue and reduce cyclical exposure for the company."},

    {"id": 3, "sector": "Tech", "direction": "Bullish",
     "headline": "Dominant search and ad platform wins landmark antitrust appeal, shares surge in after-hours trading",
     "body": "A major internet advertising company successfully overturned a significant antitrust penalty on appeal. The ruling removes a major regulatory overhang and confirms the company's ability to maintain its core business model without structural changes."},

    {"id": 4, "sector": "Tech", "direction": "Bullish",
     "headline": "Consumer electronics leader launches AI-powered flagship device to record pre-order demand",
     "body": "A prominent consumer technology company unveiled its latest flagship product line, which integrates proprietary on-device AI capabilities. Pre-orders surpassed any previous launch cycle by a wide margin, and several analysts immediately raised their price targets."},

    {"id": 5, "sector": "Tech", "direction": "Bullish",
     "headline": "Enterprise cybersecurity firm reports surge in government contract awards amid heightened threat environment",
     "body": "A cybersecurity solutions provider announced a series of large federal contract wins, citing increased government spending on national infrastructure protection. Billings and remaining performance obligations both grew substantially year-over-year."},

    {"id": 6, "sector": "Tech", "direction": "Bullish",
     "headline": "Cloud hyperscaler's AI inference revenue surpasses prior-year total in just one quarter",
     "body": "A large cloud platform operator disclosed that revenue from AI inference workloads in the most recent quarter alone exceeded the entire prior fiscal year's AI revenue. Capacity utilization remained high and management guided for continued triple-digit growth."},

    {"id": 7, "sector": "Tech", "direction": "Bullish",
     "headline": "Software platform company completes acquisition of leading data analytics firm, expands enterprise TAM",
     "body": "A diversified software company closed a major acquisition of a data analytics specialist, significantly expanding its total addressable market. Cross-sell opportunities are expected to accelerate revenue synergies starting in the next fiscal year."},

    {"id": 8, "sector": "Tech", "direction": "Bullish",
     "headline": "Global e-commerce and logistics firm achieves same-day delivery milestone across major metropolitan markets",
     "body": "A large online retail and logistics company announced it has achieved same-day delivery capability in every major metro area in its core market, a milestone reached ahead of schedule. The logistics build-out is expected to drive margin improvement as fixed costs are leveraged."},

    # ─────────────────────────────────────────────────────────────────────────
    # TECH — BEARISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 9, "sector": "Tech", "direction": "Bearish",
     "headline": "Social media platform's daily active user growth stalls for third consecutive quarter, ad revenue misses",
     "body": "A major social media company reported flat user growth for the third straight quarter and advertising revenue that missed consensus estimates. Management cited increased competition for attention and advertiser budget shifts toward newer short-form video platforms."},

    {"id": 10, "sector": "Tech", "direction": "Bearish",
     "headline": "Semiconductor equipment maker warns of order cancellations as memory chipmakers cut capex",
     "body": "A leading maker of chip manufacturing equipment issued a revenue warning after receiving significant order cancellations from memory chip producers, which are cutting capital expenditure amid a supply glut and falling DRAM and NAND prices."},

    {"id": 11, "sector": "Tech", "direction": "Bearish",
     "headline": "Software-as-a-service company faces customer churn spike as enterprise clients downsize IT budgets",
     "body": "A mid-market SaaS vendor reported a marked uptick in customer churn as enterprise clients renegotiated or cancelled subscriptions under cost-reduction mandates. Net revenue retention dropped below the threshold considered healthy by industry benchmarks."},

    {"id": 12, "sector": "Tech", "direction": "Bearish",
     "headline": "Ride-hailing giant's autonomous vehicle program hit with fatal incident, regulatory scrutiny intensifies",
     "body": "A large ride-hailing platform disclosed a serious accident involving its autonomous vehicle test fleet. Regulators announced an immediate investigation and suspended the company's AV testing permits in two key markets, casting doubt on its long-term autonomous roadmap."},

    {"id": 13, "sector": "Tech", "direction": "Bearish",
     "headline": "PC and peripheral hardware maker issues profit warning as enterprise refresh cycle weakens",
     "body": "A major personal computing hardware company slashed its quarterly earnings forecast, citing weaker-than-expected enterprise PC refresh demand and excess channel inventory. The company also announced layoffs to reduce its cost structure."},

    {"id": 14, "sector": "Tech", "direction": "Bearish",
     "headline": "Online gaming platform suffers massive data breach exposing tens of millions of user accounts",
     "body": "A popular online gaming and entertainment platform disclosed a large-scale data breach that compromised personal data of tens of millions of users. The company faces potential regulatory fines under data protection laws and a wave of class-action lawsuits."},

    {"id": 15, "sector": "Tech", "direction": "Bearish",
     "headline": "Streaming video service reports net subscriber loss for second consecutive quarter, raises prices",
     "body": "A major streaming platform reported a net loss in subscribers for the second quarter in a row, missing estimates. The company simultaneously announced a price increase, which analysts warn could further accelerate churn in a saturated market."},

    {"id": 16, "sector": "Tech", "direction": "Bearish",
     "headline": "Logistics tech startup misses IPO price target, trades down sharply on debut amid profitability concerns",
     "body": "A venture-backed logistics technology company priced its IPO below the targeted range and fell further in first-day trading. Investor concern centered on persistent operating losses, high customer acquisition costs, and an unclear path to profitability."},

    # ─────────────────────────────────────────────────────────────────────────
    # ENERGY — BULLISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 17, "sector": "Energy", "direction": "Bullish",
     "headline": "Major oil cartel announces deeper-than-expected production cuts, crude prices jump",
     "body": "A global oil-producing alliance voted to implement production cuts significantly larger than market participants had anticipated. Crude benchmark prices surged immediately following the announcement, and energy equities rallied across the board."},

    {"id": 18, "sector": "Energy", "direction": "Bullish",
     "headline": "Integrated energy major reports highest free cash flow in company history, doubles dividend",
     "body": "A large integrated oil and gas company reported record free cash flow for the quarter, driven by elevated commodity prices and disciplined capital spending. The board approved a doubling of the quarterly dividend, signaling confidence in sustained cash generation."},

    {"id": 19, "sector": "Energy", "direction": "Bullish",
     "headline": "Offshore drilling contractor secures three-year deepwater contract at premium dayrates",
     "body": "A leading offshore drilling company announced a three-year contract for a deepwater rig at dayrates well above the current market average, reflecting tight supply of high-specification rigs. Analysts noted the contract will significantly improve earnings visibility."},

    {"id": 20, "sector": "Energy", "direction": "Bullish",
     "headline": "Natural gas utility reports record winter demand, raises capital investment plan for pipeline expansion",
     "body": "A major natural gas distribution utility reported peak winter demand that exceeded internal forecasts, driven by an extended cold snap across its service territory. Management announced an accelerated capital plan to expand pipeline capacity."},

    {"id": 21, "sector": "Energy", "direction": "Bullish",
     "headline": "Renewable energy developer wins largest offshore wind auction in the region's history",
     "body": "A clean energy developer was awarded the rights to develop a massive offshore wind project following a competitive auction. The project represents the largest single offshore wind development in the region and is expected to generate predictable, long-term contracted cash flows."},

    {"id": 22, "sector": "Energy", "direction": "Bullish",
     "headline": "Midstream pipeline company raises distribution guidance after volume throughput beats expectations",
     "body": "A major midstream energy company reported pipeline throughput volumes that significantly beat analyst estimates and raised its full-year distribution guidance. Higher volumes were attributed to increased upstream activity in the company's core operating basins."},

    {"id": 23, "sector": "Energy", "direction": "Bullish",
     "headline": "Geopolitical supply disruption in key oil-producing region sends Brent crude to multi-month high",
     "body": "Armed conflict in a significant oil-producing region disrupted export flows, sending Brent crude prices to their highest level in several months. Energy equity markets rallied broadly, with exploration and production companies leading the advance."},

    {"id": 24, "sector": "Energy", "direction": "Bullish",
     "headline": "Battery storage company receives regulatory approval for grid-scale project pipeline, backlog triples",
     "body": "A utility-scale energy storage company received final regulatory approval for a series of large grid-scale battery projects. The approvals tripled the company's contracted project backlog and are expected to drive revenue growth for the next several years."},

    # ─────────────────────────────────────────────────────────────────────────
    # ENERGY — BEARISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 25, "sector": "Energy", "direction": "Bearish",
     "headline": "Crude oil tumbles as non-OPEC supply surges and global demand growth forecasts are cut",
     "body": "Crude oil prices fell sharply after a major energy agency revised down its global demand growth forecast and data showed production in non-OPEC nations rising faster than expected. Exploration and production companies saw sharp equity declines."},

    {"id": 26, "sector": "Energy", "direction": "Bearish",
     "headline": "Major refiner warns of margin compression as crack spreads collapse to multi-year lows",
     "body": "A large petroleum refiner issued a profit warning after refining crack spreads fell to their lowest level in several years due to overcapacity and weaker-than-seasonal fuel demand. The company suspended its share repurchase program to preserve cash."},

    {"id": 27, "sector": "Energy", "direction": "Bearish",
     "headline": "Offshore wind developer cancels flagship project citing cost overruns and supply chain inflation",
     "body": "A major renewable energy developer announced the cancellation of a flagship offshore wind project after construction costs escalated far beyond original estimates due to supply chain disruptions and rising materials costs. The company took a significant impairment charge."},

    {"id": 28, "sector": "Energy", "direction": "Bearish",
     "headline": "Natural gas prices collapse as mild winter and record storage injections eliminate supply concerns",
     "body": "Natural gas benchmark prices fell to multi-year lows after an unusually mild winter left storage levels well above seasonal norms. Gas-weighted exploration and production companies saw their equity prices drop materially."},

    {"id": 29, "sector": "Energy", "direction": "Bearish",
     "headline": "Solar panel manufacturer reports severe margin pressure as Chinese competition floods domestic market",
     "body": "A domestic solar panel producer reported a dramatic compression in gross margins as a surge of low-cost imports undercut its pricing. The company warned that it may need to idle manufacturing capacity if trade conditions do not improve."},

    {"id": 30, "sector": "Energy", "direction": "Bearish",
     "headline": "Pipeline operator faces regulatory order to shut key interstate line pending safety inspection",
     "body": "A major pipeline company was ordered by regulators to take a key interstate pipeline offline for safety inspections following an incident. The shutdown is expected to materially reduce the company's throughput volumes and cash flow for the coming quarter."},

    {"id": 31, "sector": "Energy", "direction": "Bearish",
     "headline": "Electric vehicle demand slowdown ripples through battery metals supply chain, lithium prices plunge",
     "body": "Weaker-than-expected electric vehicle sales prompted a reassessment of battery materials demand, sending lithium carbonate prices to multi-year lows. Mining companies with significant lithium exposure saw their equity prices decline substantially."},

    {"id": 32, "sector": "Energy", "direction": "Bearish",
     "headline": "Integrated energy company announces large write-down on oil sands asset amid long-term price uncertainty",
     "body": "A major integrated oil producer recorded a significant impairment on its oil sands operations, citing downward revisions to long-term crude price assumptions and higher-than-expected operating costs. The write-down triggered a loss for the quarter."},

    # ─────────────────────────────────────────────────────────────────────────
    # FINANCE — BULLISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 33, "sector": "Finance", "direction": "Bullish",
     "headline": "Central bank signals pause in rate hike cycle, boosting bank net interest income outlook",
     "body": "The central bank held its benchmark rate steady and signaled through updated guidance that the tightening cycle was likely at or near its peak. Bank stocks rallied as investors recalibrated net interest income forecasts and reduced concerns about credit deterioration."},

    {"id": 34, "sector": "Finance", "direction": "Bullish",
     "headline": "Major investment bank reports record M&A advisory revenue as deal activity rebounds sharply",
     "body": "A bulge-bracket investment bank reported its highest quarterly M&A advisory fee revenue on record, reflecting a strong rebound in corporate deal-making after a prolonged slowdown. The bank also raised its outlook for capital markets underwriting activity."},

    {"id": 35, "sector": "Finance", "direction": "Bullish",
     "headline": "Consumer credit quality improves as delinquency rates fall below pre-crisis levels at top card issuers",
     "body": "Leading consumer credit card issuers reported credit card delinquency and charge-off rates that declined to below pre-recession levels. The improvement in credit quality allowed banks to release loan loss reserves, boosting reported earnings."},

    {"id": 36, "sector": "Finance", "direction": "Bullish",
     "headline": "Insurance holding company benefits from favorable catastrophe loss season, beats earnings estimates",
     "body": "A major property and casualty insurance company reported better-than-expected quarterly earnings after a relatively benign hurricane and natural disaster season. Combined ratios improved materially year-over-year and premium rate increases remained strong."},

    {"id": 37, "sector": "Finance", "direction": "Bullish",
     "headline": "Asset management giant reports record AUM inflows as passive investing trend accelerates",
     "body": "A leading asset management firm reported its highest-ever quarterly inflows into its passive index fund products. Total assets under management reached a new record high, driving fee revenue growth and positive operating leverage."},

    {"id": 38, "sector": "Finance", "direction": "Bullish",
     "headline": "Payments network operator reports transaction volume growth acceleration, raises earnings guidance",
     "body": "A major payment network company reported accelerating cross-border transaction volumes and raised its full-year earnings per share guidance above consensus. Management cited continued recovery in international travel spending as a key growth driver."},

    {"id": 39, "sector": "Finance", "direction": "Bullish",
     "headline": "Regional bank completes accretive acquisition, expands market share in high-growth Sun Belt region",
     "body": "A regional bank completed its acquisition of a rival institution in a high-growth demographic market. Analysts characterized the deal as highly accretive to earnings per share and noted the combined entity would rank among the top banks in its target geography."},

    {"id": 40, "sector": "Finance", "direction": "Bullish",
     "headline": "Mortgage REIT benefits from steepening yield curve, raises quarterly dividend by double digits",
     "body": "A mortgage real estate investment trust reported improved net interest spreads as the yield curve steepened, boosting profitability. The board raised the quarterly dividend by a double-digit percentage, reflecting improved earnings power and book value stability."},

    # ─────────────────────────────────────────────────────────────────────────
    # FINANCE — BEARISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 41, "sector": "Finance", "direction": "Bearish",
     "headline": "Large regional bank discloses surprise commercial real estate losses, stock halted for trading",
     "body": "A major regional bank announced an unexpected and material increase in commercial real estate loan losses, triggering a trading halt in its shares. The bank disclosed it was in discussions with regulators regarding its capital adequacy and reserved the right to cut its dividend."},

    {"id": 42, "sector": "Finance", "direction": "Bearish",
     "headline": "Central bank delivers surprise rate hike, inverting yield curve further and pressuring bank margins",
     "body": "In a move that caught markets off guard, the central bank raised its benchmark interest rate, deepening the inversion of the yield curve. Bank stocks fell sharply as the rate environment indicated tighter lending margins and higher near-term recession risk."},

    {"id": 43, "sector": "Finance", "direction": "Bearish",
     "headline": "Consumer finance company reports sharp rise in subprime auto loan delinquencies",
     "body": "A specialized consumer finance company reported a significant quarter-over-quarter increase in delinquency rates on its subprime auto loan portfolio. Management raised its provision for credit losses and acknowledged that macroeconomic headwinds were materializing faster than expected."},

    {"id": 44, "sector": "Finance", "direction": "Bearish",
     "headline": "Private equity firm suspends new fund raises after flagship fund performance disappoints LPs",
     "body": "A prominent private equity firm indefinitely postponed fundraising for its next flagship fund after limited partners expressed dissatisfaction with below-benchmark returns in existing vehicles. Several anchor investors reportedly declined to re-up for the new fund."},

    {"id": 45, "sector": "Finance", "direction": "Bearish",
     "headline": "Insurance giant faces multi-billion dollar liability exposure from emerging environmental litigation wave",
     "body": "A large insurance and reinsurance company disclosed a review of potential exposure to an emerging wave of environmental litigation. Analysts estimated the range of potential liability could be material relative to the company's existing reserves, triggering a sell-off."},

    {"id": 46, "sector": "Finance", "direction": "Bearish",
     "headline": "Retail brokerage platform reports trading volume collapse as market volatility subsides",
     "body": "A consumer-facing brokerage company reported a sharp drop in trading volumes and commission-equivalent revenue as market volatility declined to multi-year lows. Active user counts also fell sequentially, raising concerns about the sustainability of the pandemic-era growth surge."},

    {"id": 47, "sector": "Finance", "direction": "Bearish",
     "headline": "Fintech lender's securitization program faces investor pushback over loan performance deterioration",
     "body": "A technology-enabled consumer lender found diminishing investor appetite for its asset-backed securities after loan performance metrics in earlier vintages showed higher-than-projected default rates. The company warned that constrained securitization access would limit its origination volume."},

    {"id": 48, "sector": "Finance", "direction": "Bearish",
     "headline": "Major bank faces regulatory enforcement action over anti-money laundering compliance failures",
     "body": "A large commercial bank received a formal enforcement action from its primary regulator following an examination that found significant deficiencies in its anti-money laundering program. The action restricts the bank's ability to onboard new high-risk clients and may result in substantial fines."},

    # ─────────────────────────────────────────────────────────────────────────
    # HEALTHCARE — BULLISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 49, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Biotech firm's Phase 3 trial for rare disease therapy shows statistically significant efficacy",
     "body": "A clinical-stage biotechnology company announced that its Phase 3 pivotal trial for a rare genetic disease met its primary endpoint with statistical significance. Management indicated it plans to file for regulatory approval within the quarter, and analysts viewed the data as highly likely to support approval."},

    {"id": 50, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Pharmaceutical giant's blockbuster drug receives expanded label indication, adding large new patient population",
     "body": "A major pharmaceutical company received regulatory approval to expand the label of its top-selling drug to include a new therapeutic indication with a large addressable patient population. Peak sales estimates for the drug were revised substantially higher by the analyst community."},

    {"id": 51, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Medical device maker wins FDA approval for minimally invasive surgical robot system",
     "body": "A medical technology company received FDA clearance for its next-generation robotic surgical system. The system targets a large and underpenetrated surgical market and is expected to begin generating meaningful commercial revenue within two quarters of launch."},

    {"id": 52, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Managed care giant beats earnings estimates, raises full-year guidance on strong enrollment growth",
     "body": "A large managed care organization reported quarterly earnings that exceeded consensus estimates, driven by higher-than-expected enrollment in both commercial and government-sponsored health plans. The company raised its full-year earnings guidance meaningfully above prior expectations."},

    {"id": 53, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Gene therapy startup's lead program receives breakthrough therapy designation, expediting review timeline",
     "body": "A clinical-stage gene therapy company announced that its lead program received breakthrough therapy designation from the regulatory agency, which is expected to accelerate the review process and reduce time to potential approval. The designation was seen as a strong signal of clinical differentiation."},

    {"id": 54, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Diagnostic testing company reports record volumes from new AI-assisted pathology platform rollout",
     "body": "A clinical diagnostics company reported record test volumes following the broad commercial rollout of its AI-assisted pathology platform. The technology improves turnaround time and diagnostic accuracy, and the company reported strong early adoption among major hospital systems."},

    {"id": 55, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Large pharma acquires late-stage oncology asset at significant premium to bolster pipeline",
     "body": "A major pharmaceutical company announced the acquisition of a clinical-stage oncology company at a substantial premium to its trading price, citing the strategic value of the target's late-stage cancer therapy pipeline. Analysts viewed the deal as a positive signal for the acquirer's long-term revenue outlook."},

    {"id": 56, "sector": "Healthcare", "direction": "Bullish",
     "headline": "Hospital operator reports strong same-facility admissions growth and improved payer mix",
     "body": "A large for-profit hospital operator reported same-facility patient admissions growth that beat estimates and an improving payer mix as more commercially insured patients were treated. Operating margins expanded year-over-year and management reiterated its full-year earnings outlook."},

    # ─────────────────────────────────────────────────────────────────────────
    # HEALTHCARE — BEARISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 57, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Late-stage clinical trial for anticipated blockbuster drug fails to meet primary endpoint",
     "body": "A pharmaceutical company's closely watched Phase 3 trial for a highly anticipated drug candidate failed to demonstrate statistically significant improvement over placebo on the primary endpoint. The company announced it would discontinue the development program, erasing a significant portion of its market capitalization."},

    {"id": 58, "sector": "Healthcare", "direction": "Bearish",
     "headline": "FDA issues complete response letter for drug application citing manufacturing deficiencies",
     "body": "A specialty pharmaceutical company received a complete response letter from the FDA declining to approve its new drug application due to deficiencies identified during a manufacturing inspection. The company must remediate the issues and refile, delaying potential approval by at least a year."},

    {"id": 59, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Major PBM faces Congressional investigation over drug pricing practices and rebate transparency",
     "body": "A large pharmacy benefit manager was notified of a formal Congressional investigation into its drug pricing practices and the transparency of manufacturer rebate arrangements. The investigation creates material regulatory and reputational risk for the company and its health plan clients."},

    {"id": 60, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Managed care company raises medical cost outlook after Medicaid redetermination drives higher acuity",
     "body": "A major managed care organization raised its medical cost ratio guidance after experiencing higher-than-expected medical claims costs. Management cited elevated acuity levels in newly enrolled Medicaid populations following government redetermination processes."},

    {"id": 61, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Biotech firm's lead immunology drug shows inferior efficacy versus established competitor in head-to-head trial",
     "body": "A biotechnology company disclosed results of a head-to-head clinical trial comparing its lead immunology drug to a market-leading competitor. The company's drug did not demonstrate superiority and showed a numerically lower response rate, significantly weakening its commercial positioning."},

    {"id": 62, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Hospital system reports surge in labor costs and contract nurse spending, cuts earnings outlook",
     "body": "A large nonprofit hospital system disclosed a significant increase in contract labor costs and travel nurse expenses, leading management to reduce its operating income outlook for the year. The cost pressures were attributed to a persistent nursing shortage in its core markets."},

    {"id": 63, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Drug maker faces generic competition years ahead of schedule after patent challenge succeeds",
     "body": "A pharmaceutical company lost a critical patent litigation case covering its best-selling drug, opening the door for generic competition well ahead of the originally anticipated exclusivity expiration date. Analysts sharply cut their revenue and earnings estimates for the company."},

    {"id": 64, "sector": "Healthcare", "direction": "Bearish",
     "headline": "Medical device recall expands to global scale, company sets aside large liability reserve",
     "body": "A medical device manufacturer expanded a product recall to include units distributed in multiple international markets after additional safety concerns were identified. The company disclosed a material addition to its product liability reserve, and several class-action lawsuits were filed."},

    # ─────────────────────────────────────────────────────────────────────────
    # CRYPTO — BULLISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 65, "sector": "Crypto", "direction": "Bullish",
     "headline": "Spot Bitcoin ETF receives regulatory approval, institutional capital inflows surge from day one",
     "body": "Regulators granted approval for the first spot Bitcoin exchange-traded fund, a watershed moment for institutional adoption. Assets under management in the new product exceeded forecasts within the first week of trading, signaling strong pent-up institutional demand."},

    {"id": 66, "sector": "Crypto", "direction": "Bullish",
     "headline": "Major global payment network announces native cryptocurrency settlement layer integration",
     "body": "A leading international payment network announced integration of a cryptocurrency settlement layer, enabling real-time cross-border payments in digital assets for its member financial institutions. Adoption is expected to drive transaction volume on the underlying blockchain significantly."},

    {"id": 67, "sector": "Crypto", "direction": "Bullish",
     "headline": "Layer-1 blockchain completes successful upgrade to proof-of-stake, energy use drops sharply",
     "body": "A major proof-of-work blockchain network successfully transitioned to a proof-of-stake consensus mechanism. The upgrade dramatically reduced the network's energy consumption and removed a key ESG objection cited by institutional investors, broadening its potential investor base."},

    {"id": 68, "sector": "Crypto", "direction": "Bullish",
     "headline": "Sovereign wealth fund discloses initial Bitcoin allocation in latest portfolio filing",
     "body": "A large sovereign wealth fund disclosed for the first time a position in Bitcoin in its public portfolio filing. The disclosure was widely interpreted as a significant institutional validation of digital assets as a legitimate portfolio allocation and triggered broad market enthusiasm."},

    {"id": 69, "sector": "Crypto", "direction": "Bullish",
     "headline": "DeFi protocol's total value locked surpasses prior cycle peak after governance overhaul",
     "body": "A leading decentralized finance protocol saw its total value locked surpass its previous all-time high following a comprehensive governance restructuring and fee mechanism upgrade. Analyst coverage was initiated by several digital asset research firms with bullish price targets."},

    {"id": 70, "sector": "Crypto", "direction": "Bullish",
     "headline": "G7 nations reach preliminary agreement on harmonized crypto regulatory framework",
     "body": "Finance ministers from G7 nations announced a preliminary agreement on a harmonized framework for regulating digital assets. The agreement reduces the risk of regulatory arbitrage and was welcomed by the crypto industry as providing the legal clarity needed for broader institutional participation."},

    {"id": 71, "sector": "Crypto", "direction": "Bullish",
     "headline": "Bitcoin halving event reduces new supply issuance; historically associated with multi-month bull runs",
     "body": "Bitcoin completed its scheduled halving event, cutting the rate of new coin issuance in half. The event, which occurs approximately every four years, has historically preceded extended bull markets due to the reduction in selling pressure from miners and increased supply scarcity."},

    {"id": 72, "sector": "Crypto", "direction": "Bullish",
     "headline": "Smart contract platform announces partnership with top-three global bank for tokenized asset settlement",
     "body": "A leading smart contract blockchain announced a strategic partnership with one of the world's largest banks to develop a tokenized asset settlement infrastructure. The partnership was seen as a major step toward mainstream institutional use of public blockchain infrastructure."},

    # ─────────────────────────────────────────────────────────────────────────
    # CRYPTO — BEARISH (8)
    # ─────────────────────────────────────────────────────────────────────────
    {"id": 73, "sector": "Crypto", "direction": "Bearish",
     "headline": "Stablecoin issuer loses dollar peg after reserve transparency concerns trigger bank-run dynamic",
     "body": "A major stablecoin depegged from the US dollar after questions about the composition and liquidity of its reserves triggered a rapid redemption spiral. The event caused panic selling across the broader cryptocurrency market and reignited calls for urgent regulatory intervention."},

    {"id": 74, "sector": "Crypto", "direction": "Bearish",
     "headline": "Regulatory agency classifies major proof-of-stake token as a security, exchange delistings follow",
     "body": "A financial regulatory agency issued a formal determination that a widely held proof-of-stake cryptocurrency token constitutes a security under existing law. Several major exchanges announced they would delist the token to avoid regulatory exposure, causing its price to plunge."},

    {"id": 75, "sector": "Crypto", "direction": "Bearish",
     "headline": "Centralized crypto exchange discloses undisclosed related-party loans, triggers customer withdrawal wave",
     "body": "A prominent centralized cryptocurrency exchange disclosed that substantial customer assets had been lent to affiliated trading entities without customer consent. The revelation triggered a wave of customer withdrawals and forced the exchange to suspend redemptions, raising insolvency concerns."},

    {"id": 76, "sector": "Crypto", "direction": "Bearish",
     "headline": "Major DeFi protocol suffers exploit draining hundreds of millions from liquidity pools",
     "body": "A top-ranked decentralized finance protocol was exploited through a previously undetected smart contract vulnerability, allowing an attacker to drain a significant amount of user funds from liquidity pools. The protocol suspended operations pending an audit, and its governance token price collapsed."},

    {"id": 77, "sector": "Crypto", "direction": "Bearish",
     "headline": "G20 nations coordinate ban on anonymous crypto wallet transactions above threshold",
     "body": "G20 nations announced coordinated regulations requiring identification for cryptocurrency wallet transactions above a de minimis threshold. The move was interpreted as a significant restriction on the pseudonymous nature of crypto and triggered broad market declines."},

    {"id": 78, "sector": "Crypto", "direction": "Bearish",
     "headline": "Bitcoin mining difficulty reaches record high as hashrate concentration raises centralization concerns",
     "body": "Bitcoin mining difficulty surged to a new all-time high, leading analysts to flag that a small number of large mining pools now control a disproportionate share of total hashrate. The centralization concerns prompted discussion about long-term network security and censorship resistance."},

    {"id": 79, "sector": "Crypto", "direction": "Bearish",
     "headline": "Crypto venture fund marks down portfolio by majority, signals sharp decline in startup funding activity",
     "body": "A leading cryptocurrency-focused venture fund disclosed a significant markdown in the fair value of its portfolio companies, citing deteriorating market conditions and dried-up exit opportunities. The fund announced it would slow the pace of new investments significantly."},

    {"id": 80, "sector": "Crypto", "direction": "Bearish",
     "headline": "Nation-state level cyber attack targets cross-chain bridge, entire bridge TVL drained in hours",
     "body": "A cross-chain bridge protocol suffered a sophisticated cyber attack attributed to a nation-state threat actor, resulting in the complete drainage of assets locked in the bridge. The incident highlighted systemic risks in cross-chain infrastructure and caused widespread contagion across related ecosystems."},
]

# Write CSV
output_path = "/home/claude/llm-bias-eval/data/base_news.csv"
fieldnames = ["id", "sector", "direction", "headline", "body"]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(news_data)

print(f"✅ Written {len(news_data)} rows to {output_path}")

# Sanity check
sector_counts = {}
direction_counts = {}
for row in news_data:
    sector_counts[row["sector"]] = sector_counts.get(row["sector"], 0) + 1
    direction_counts[row["direction"]] = direction_counts.get(row["direction"], 0) + 1

print("\nSector distribution:")
for s, c in sorted(sector_counts.items()):
    print(f"  {s}: {c}")

print("\nDirection distribution:")
for d, c in sorted(direction_counts.items()):
    print(f"  {d}: {c}")
