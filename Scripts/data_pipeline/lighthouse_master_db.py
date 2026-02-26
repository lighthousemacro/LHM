"""
LIGHTHOUSE MACRO - MASTER DATABASE
===================================
One database. All sources. Zero headaches.

Sources: FRED + BLS + BEA + NY Fed + OFR
Storage: SQLite with smart incremental updates
Output: Single source of truth for all Lighthouse analysis

Run daily at 06:00 ET via launchd
"""

import requests
import pandas as pd
import sqlite3
import time
from datetime import datetime
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

DB_PATH = Path("/Users/bob/LHM/Data/databases/Lighthouse_Master.db")

API_KEYS = {
    "FRED": "11893c506c07b3b8647bf16cf60586e8",
    "BLS": "2e66aeb26c664d4fbc862de06d1f8899",
    "BEA": "4401D40D-4047-414F-B4FE-D441E96F8DE8"
}

# ==========================================
# FRED CONFIGURATION
# ==========================================

# Category IDs for auto-discovery (top 50 by popularity per category)
FRED_CATEGORIES = {
    "Employment_Situation": 32440,
    "CPI_Urban_Consumers": 9,
    "Industrial_Production": 32262,
    "Treasury_Rates": 115,
    "Money_Banking": 24,
    "Producer_Price_Index": 32263,
    "Employment_Cost_Index": 3,
    "Exchange_Rates": 94,
    "Regional_Fed_Surveys": 32266,
    "Housing": 97,
    "GDP_National_Accounts": 106,
    "Personal_Income": 110,
    "Consumer_Credit": 22,
    "Interest_Rates": 114,
    "Business_Lending": 100,
}

# Curated high-priority series (always included even if not in top 50)
FRED_CURATED = {
    # Labor Market
    "UNRATE": "Unemployment Rate U3",
    "U6RATE": "Unemployment Rate U6",
    "CIVPART": "Labor Force Participation",
    "PAYEMS": "Total Nonfarm Payrolls",
    "ICSA": "Initial Jobless Claims",
    "CCSA": "Continued Claims",
    "JTS1000JOR": "JOLTS Job Openings Rate",
    "JTS1000QUR": "JOLTS Quits Rate",
    "JTS1000HIR": "JOLTS Hires Rate",

    # Inflation
    "CPIAUCSL": "CPI All Urban Consumers",
    "CPILFESL": "Core CPI",
    "PCEPI": "PCE Price Index",
    "PCEPILFE": "Core PCE",
    "MEDCPIM158SFRBCLE": "Median CPI",
    "CORESTICKM159SFRBATL": "Sticky Core CPI",
    "COREFLEXCPIM159SFRBATL": "Flexible Core CPI",

    # Atlanta Fed Wage Growth Tracker
    "FRBATLWGT12MMUMHGO": "Atlanta Fed Wage Growth 12M Overall",
    "FRBATLWGT3MMAUMHWGO": "Atlanta Fed Wage Growth 3M Overall",
    "FRBATLWGT12MMUMHWGJST": "Atlanta Fed Wage Growth Job Stayers",
    "FRBATLWGT12MMUMHWGJSW": "Atlanta Fed Wage Growth Job Switchers",
    "FRBATLWGT12MMUMHWGWD1WP": "Atlanta Fed Wage Growth 1st-25th Pctl",
    "FRBATLWGT12MMUMHWGWD76WP": "Atlanta Fed Wage Growth 76th-100th Pctl",

    # Growth & Activity
    "GDP": "Nominal GDP",
    "GDPC1": "Real GDP",
    "INDPRO": "Industrial Production",
    "RSAFS": "Retail Sales",
    "UMCSENT": "Consumer Sentiment",

    # Rates & Yields
    "FEDFUNDS": "Fed Funds Rate",
    "DGS1": "1Y Treasury",
    "DGS2": "2Y Treasury",
    "DGS5": "5Y Treasury",
    "DGS10": "10Y Treasury",
    "DGS30": "30Y Treasury",
    "T10Y2Y": "10Y-2Y Spread",
    "T10Y3M": "10Y-3M Spread",
    "MORTGAGE30US": "30Y Mortgage Rate",

    # Credit Spreads
    "BAMLH0A0HYM2": "HY OAS Spread",
    "BAMLC0A0CM": "IG OAS Spread",

    # Money & Liquidity
    "M2SL": "M2 Money Supply",
    "WALCL": "Fed Balance Sheet",
    "RRPONTSYD": "RRP Usage",
    "TOTRESNS": "Bank Reserves",

    # Housing
    "HOUST": "Housing Starts",
    "PERMIT": "Building Permits",
    "CSUSHPINSA": "Case-Shiller Home Prices",
    "MSPUS": "Median Home Price",

    # Consumer
    "TOTALSL": "Consumer Credit",
    "PSAVERT": "Personal Saving Rate",
    "TDSP": "Household Debt Service Ratio",

    # Fiscal
    "GFDEBTN": "Federal Debt",
    "GFDEGDQ188S": "Debt to GDP",

    # Delinquencies
    "DRALACBS": "All Loan Delinquency Rate",
    "DRSFRMACBS": "Mortgage Delinquency Rate",
    "DRCCLACBS": "Credit Card Delinquency Rate",

    # Volatility
    "VIXCLS": "VIX",

    # Commodities
    "DCOILWTICO": "WTI Crude",
    "DTWEXBGS": "Trade Weighted Dollar",

    # Labor Demographics (Granular) - Labels verified against FRED API 2026-02-16
    "LNS14000003": "Unemployment Rate White",
    "LNS14000006": "Unemployment Rate Black",
    "LNS14000009": "Unemployment Rate Hispanic",
    "LNS14000012": "Unemployment Rate 16-19 Yrs",
    "LNS14000013": "Unemployment Rate 16-19 Yrs Men",
    "LNS14000024": "Unemployment Rate 20 Yrs and Over",
    "LNS14000025": "Unemployment Rate 20 Yrs and Over Men",
    "LNS14000036": "Unemployment Rate 20-24 Yrs",
    "LNS14024230": "Unemployment Rate 55 Yrs and Over",
    "LNS11300002": "LFPR Women",
    "LNS11300003": "LFPR White",
    "LNS11300060": "LFPR Prime Age 25-54",
    "LNS12032194": "Part Time for Economic Reasons",
    "UEMPMEAN": "Mean Duration Unemployment Weeks",
    "UEMP27OV": "Unemployed 27 Weeks and Over",
    "U1RATE": "Unemployment Rate U1 (15+ weeks)",
    "U2RATE": "Unemployment Rate U2 (Job Losers)",

    # CPI Components (Granular)
    "CUSR0000SAH1": "CPI Shelter",
    "CUSR0000SAH2": "CPI Fuel Utilities",
    "CUSR0000SAM1": "CPI Medical Care Services",
    "CUSR0000SAM2": "CPI Medical Care Commodities",
    "CUSR0000SAS4": "CPI Transportation Services",
    "CUSR0000SETB01": "CPI Gasoline",
    "CUSR0000SETA02": "CPI Used Cars Trucks",
    "CUSR0000SETA01": "CPI New Vehicles",
    "CUSR0000SEHA": "CPI Rent Primary Residence",
    "CUSR0000SEHC": "CPI Owners Equivalent Rent",
    "CUSR0000SAF11": "CPI Food at Home",
    "CUSR0000SEFV": "CPI Food Away from Home",

    # PCE Components (Granular)
    "DGDSRG3M086SBEA": "PCE Goods",
    "DSERRG3M086SBEA": "PCE Services",
    "PCEDG": "PCE Durable Goods",
    "PCEND": "PCE Nondurable Goods",
    "PCES": "PCE Services",

    # Financial Conditions
    "NFCI": "Chicago Fed NFCI",
    "ANFCI": "Adjusted NFCI",
    "STLFSI4": "St Louis Fed FSI",

    # More Credit/Lending
    "DRTSCILM": "Loan Officer Survey C&I Tightening",
    "DRTSCLCC": "Loan Officer Survey Credit Card Tightening",
    "TOTCI": "Commercial Industrial Loans",
    "CONSUMER": "Consumer Loans at Banks",
    "BUSLOANS": "Business Loans at Banks",
    "REALLN": "Real Estate Loans at Banks",

    # Treasury Auctions / Dealers
    "WTREGEN": "Treasury General Account",
    "H41RESPPALDKNWW": "Fed RRP Outstanding",

    # Additional Yield Curve
    "DGS1MO": "1M Treasury",
    "DGS3MO": "3M Treasury",
    "DGS6MO": "6M Treasury",
    "T10YFF": "10Y minus Fed Funds",
    "T5YFF": "5Y minus Fed Funds",

    # Real Rates
    "DFII5": "5Y TIPS Yield",
    "DFII10": "10Y TIPS Yield",
    "T5YIFR": "5Y Forward Inflation Expectation",
    "T10YIE": "10Y Breakeven Inflation",
    "T5YIE": "5Y Breakeven Inflation",

    # Term Premium
    "THREEFYTP10": "10Y Term Premium ACM",

    # ===== PILLAR 1 (LABOR) ADDITIONS - Feb 2026 =====

    # JOLTS Levels (needed for derived ratios like Hires/Quits, V/U)
    "JTSJOL": "JOLTS Job Openings Level Total Nonfarm",
    "JTSHIL": "JOLTS Hires Level Total Nonfarm",
    "JTSQUL": "JOLTS Quits Level Total Nonfarm",
    "JTSQUR": "JOLTS Quits Rate Total Nonfarm",
    "JTSLDL": "JOLTS Layoffs Discharges Level Total Nonfarm",
    "JTSTSL": "JOLTS Total Separations Level Total Nonfarm",
    "JTSHIR": "JOLTS Hires Rate Total Nonfarm",
    "JTSTSR": "JOLTS Total Separations Rate Total Nonfarm",

    # JOLTS Sector Quits Rates (sector confidence signals)
    "JTS3000QUR": "JOLTS Quits Rate Manufacturing",
    "JTS2300QUR": "JOLTS Quits Rate Construction",
    "JTS4400QUR": "JOLTS Quits Rate Retail Trade",
    "JTS540099QUR": "JOLTS Quits Rate Professional Business Services",
    "JTS7000QUR": "JOLTS Quits Rate Leisure Hospitality",
    "JTS6200QUR": "JOLTS Quits Rate Health Care Social Assistance",

    # Unemployment Duration Decomposition
    "UNEMPLOY": "Unemployment Level",
    "UEMPLT5": "Unemployed Less Than 5 Weeks",
    "UEMP5TO14": "Unemployed 5 to 14 Weeks",
    "UEMP15T26": "Unemployed 15 to 26 Weeks",
    "UEMPMED": "Median Weeks Unemployed",

    # Unemployment Reasons
    "LNS13023621": "Unemployment Level Job Losers",
    "LNS13023705": "Unemployment Level Job Leavers",
    "LNS13023557": "Unemployment Level Reentrants",
    "LNS13023569": "Unemployment Level New Entrants",

    # Demographic Unemployment - Gender
    "LNS14000001": "Unemployment Rate Men",
    "LNS14000002": "Unemployment Rate Women",

    # Demographic Unemployment - Age
    "LNS14000060": "Unemployment Rate 25-54 Yrs Prime Age",
    "LNS14024887": "Unemployment Rate 16-24 Yrs",

    # Demographic Unemployment - Education (25+)
    "LNS14027659": "Unemployment Rate Less Than HS Diploma 25+",
    "LNS14027660": "Unemployment Rate HS Graduates No College 25+",
    "LNS14027689": "Unemployment Rate Some College Associate 25+",
    "LNS14027662": "Unemployment Rate Bachelors Degree and Higher 25+",

    # Demographic Unemployment - Race (additional)
    "LNU04032183": "Unemployment Rate Asian",

    # LFPR Demographic Breakdowns
    "LNS11300001": "LFPR Men",
    "LNS11324230": "LFPR 55 Yrs and Over",
    "CLF16OV": "Civilian Labor Force Level",

    # Employment Quality
    "LNS12500000": "Employed Usually Work Full Time",
    "LNS12600000": "Employed Usually Work Part Time",
    "LNS12026620": "Multiple Jobholders Pct of Employed",
    "NILFWJN": "Not in Labor Force Want a Job Now",
    "LNU05026645": "Discouraged Workers",

    # Industry Employment (Payroll)
    "TEMPHELPS": "Temp Help Services Employment",
    "USCONS": "All Employees Construction",
    "USTRADE": "All Employees Retail Trade",
    "USPBS": "All Employees Professional Business Services",
    "USFIRE": "All Employees Financial Activities",
    "USINFO": "All Employees Information",
    "USLAH": "All Employees Leisure Hospitality",
    "USGOVT": "All Employees Government",
    "CES6562000001": "All Employees Health Care Social Assistance",

    # Hours Worked (leading indicators)
    "AWHAETP": "Avg Weekly Hours Total Private",
    "AWHMAN": "Avg Weekly Hours Manufacturing Production",
    "AWOTMAN": "Avg Overtime Hours Manufacturing Production",
    "AWHI": "Aggregate Weekly Hours Index Total Private",

    # Additional Wages
    "CES0500000030": "Avg Weekly Earnings Production Nonsupervisory",
    "CIU2010000000000I": "ECI Total Compensation Private Industry",

    # Prime-Age LFPR by Gender (OECD-sourced, on FRED)
    "LRAC25MAUSM156S": "LFPR Male 25-54 Prime Age",
    "LRAC25FEUSM156S": "LFPR Female 25-54 Prime Age",

    # Recession / Confirmation Indicators
    "SAHMREALTIME": "Sahm Rule Recession Indicator",
    "IHLIDXUS": "Indeed Job Postings Index US",
    "IURSA": "Insured Unemployment Rate",

    # ===== GAP FILLERS =====

    # ISM / PMI - NOTE: ISM data was removed from FRED in June 2016 due to licensing
    # NAPM, NAPMNOI, NAPMII, etc. are no longer available via FRED API
    # Use Regional Fed surveys as proxies or get ISM data from other sources
    "MANEMP": "Manufacturing Employment",

    # NFIB - NOTE: NFIB Small Business Optimism not available on FRED
    # Must be sourced directly from nfib.com

    # Regional Fed Surveys
    "GACDISA066MSFRBNY": "Empire State Manufacturing",
    "GACDFSA066MSFRBPHI": "Philly Fed Manufacturing",
    "CFNAIMA3": "Chicago Fed National Activity",
    "KCFSI": "Kansas City Fed FSI",
    "BACTSAMFRBDAL": "Dallas Fed Manufacturing",

    # Durable Goods Orders
    "DGORDER": "Durable Goods Orders",
    "ADXTNO": "Durable Goods Orders Ex Transportation",
    "NEWORDER": "Manufacturers New Orders Total",
    "AMTMNO": "Manufacturers Total New Orders",
    "ACDGNO": "Durable Goods Orders Ex Defense",
    "ANDENO": "Nondefense Capital Goods Orders Ex Aircraft",
    # Note: AMDMNO discontinued, use DGORDER and ADXTNO instead
    "AMNMNO": "Nondurable Manufacturers New Orders",

    # Trade Balance & Trade
    "BOPGSTB": "Trade Balance Goods and Services",
    "BOPGTB": "Trade Balance Goods Only",
    "BOPTEXP": "Exports Goods and Services",
    "BOPTIMP": "Imports Goods and Services",
    "IMPGS": "Real Imports Goods Services",
    "EXPGS": "Real Exports Goods Services",
    "IR": "Import Price Index",
    "IQ": "Export Price Index",
    "NETEXP": "Net Exports",

    # Freight & Logistics
    "RAILFRTCARLOADSD11": "Rail Freight Carloads",
    "TSIFRGHT": "Transportation Services Index Freight",
    "TSITTL": "Transportation Services Index Total",
    "FRGSHPUSM649NCIS": "Cass Freight Shipments Index",
    # Note: LOADFAC discontinued

    # Auto/Vehicle Sales
    "ALTSALES": "Light Vehicle Sales Total",
    "LAUTOSA": "Light Autos Sales",
    "LTOTALNSA": "Light Trucks Sales",
    "HTRUCKSSAAR": "Heavy Truck Sales",
    "TOTALSA": "Total Vehicle Sales",
    "AISRSA": "Auto Inventory Sales Ratio",

    # Retail Sales Detail
    "RSXFS": "Retail Sales Ex Food Services",
    "RSMVPD": "Retail Sales Motor Vehicles Parts",
    "RSFSDP": "Retail Sales Food Services Drinking",
    "RSGASS": "Retail Sales Gasoline Stations",
    "RSBMGESD": "Retail Sales Building Materials",
    "RSGCSN": "Retail Sales General Merchandise",
    "RSNSR": "Retail Sales Nonstore Retailers",
    "RSHPCS": "Retail Sales Health Personal Care",
    "RSSGHBMS": "Retail Sales Sporting Goods Hobby",
    "RSFHFS": "Retail Sales Furniture Home Furnish",
    "RSEAS": "Retail Sales Electronics Appliances",
    "RSCCAS": "Retail Sales Clothing Accessories",

    # Housing Detail
    "HSN1F": "New Home Sales",
    "MSPNHSUS": "Median New Home Sales Price",
    "MSACSR": "Months Supply New Houses",
    "HOSINVUSM495N": "Housing Inventory Total",
    "EXHOSLUSM495S": "Existing Home Sales",
    "PERMIT1": "Building Permits Single Family",
    "COMPUTSA": "Housing Units Completed",
    "UNDCONTSA": "Housing Units Under Construction",
    "MORTGAGE15US": "15Y Mortgage Rate",
    "RHORUSQ156N": "Homeownership Rate",
    "FIXHAI": "Housing Affordability Index",

    # Housing Regional
    "HOUSTNE": "Housing Starts Northeast",
    "HOUSTMW": "Housing Starts Midwest",
    "HOUSTS": "Housing Starts South",
    "HOUSTW": "Housing Starts West",
    "PERMITNSA": "Building Permits NSA",

    # Housing Prices - Additional
    "SPCS20RSA": "Case-Shiller 20-City Composite HPI",
    "USSTHPI": "FHFA All-Transactions HPI",

    # Housing Credit - Additional
    "RHVRUSQ156N": "Homeowner Vacancy Rate",

    # Regional Median Prices (Existing Homes)
    "HOSMEDUSMWM052N": "Median Existing Home Price Midwest",
    "HOSMEDUSNEM052N": "Median Existing Home Price Northeast",
    "HOSMEDUSSOM052N": "Median Existing Home Price South",
    "HOSMEDUSWTM052N": "Median Existing Home Price West",

    # Regional Existing Home Sales
    "EXHOSLUSNEM495S": "Existing Home Sales Northeast",
    "EXHOSLUSMWM495S": "Existing Home Sales Midwest",
    "EXHOSLUSSOM495S": "Existing Home Sales South",
    "EXHOSLUSWTM495S": "Existing Home Sales West",

    # Housing Prices - Extended
    "ASPUS": "Average Sales Price All Houses Sold",
    "ASPNHSUS": "Average Sales Price New Houses Sold",
    "SPCS10RSA": "Case-Shiller 10-City Composite HPI",

    # Housing Supply - Extended
    "MNMFS": "Months Supply New Houses for Sale",
    "TLRESCONS": "Total Residential Construction Spending",
    "HOUST5F": "Housing Starts 5+ Units",

    # Housing Credit - Extended
    "BOGZ1FA893065015Q": "Home Mortgage Liabilities",
    "HHMSDODNS": "Household Mortgage Debt Service Ratio",
    "HNONWPDPI": "Household Net Worth to DPI Ratio",

    # Shelter Inflation - Extended
    "CPIHOSSL": "CPI Housing SA",

    # Housing International Comparison (BIS)
    "QUSR628BIS": "BIS Real Residential Property Prices US",
    "QUSR368BIS": "BIS Nominal Residential Property Prices US",

    # Government/Fiscal
    "MTSDS133FMS": "Federal Budget Balance",
    "MTSO133FMS": "Federal Outlays Monthly",
    "MTSR133FMS": "Federal Receipts Monthly",
    "FYFSD": "Federal Surplus Deficit Annual",
    "FGEXPND": "Federal Expenditures",
    "FGRECPT": "Federal Receipts",
    "W068RCQ027SBEA": "Govt Consumption Expenditures",
    "A091RC1Q027SBEA": "Federal Defense Spending",
    "A822RL1Q225SBEA": "Real Govt Spending Growth",

    # Inventories
    "ISRATIO": "Inventory Sales Ratio Total",
    "MNFCTRIRSA": "Manufacturers Inventory Sales Ratio",
    "RETAILIRSA": "Retail Inventories",
    "WHLSLRIRSA": "Wholesale Inventory Sales Ratio",
    "BUSINV": "Total Business Inventories",
    "RETAILIMSA": "Retail Inventories Ex Autos",

    # Productivity/Unit Labor
    "OPHNFB": "Nonfarm Business Output Per Hour",
    "PRS85006092": "Nonfarm Unit Labor Costs",
    "ULCNFB": "Unit Labor Costs Nonfarm Business",
    "COMPNFB": "Nonfarm Business Compensation Per Hour",
    "HOANBS": "Nonfarm Business Hours Worked",

    # Additional Wages
    "CES0500000003": "Average Hourly Earnings Total Private",
    "AHETPI": "Average Hourly Earnings Production",
    "LES1252881600Q": "Median Usual Weekly Earnings",
    "ECIWAG": "Employment Cost Index Wages Salaries",
    "ECIALLCIV": "Employment Cost Index Total",

    # ===== PILLAR 2 (PRICES) ADDITIONS =====

    # CPI Major Aggregates (SA)
    "CUSR0000SAS": "CPI Services",
    "CUSR0000SACL1E": "CPI Core Goods (Commodities Less Food Energy)",
    "CUSR0000SASLE": "CPI Services Less Energy",
    "CPIAPPSL": "CPI Apparel",
    "CPIENGSL": "CPI Energy",
    "CPIUFDSL": "CPI Food",
    "CPIRECSL": "CPI Recreation",
    "CPIMEDSL": "CPI Medical Care",
    "CPITRNSL": "CPI Transportation",

    # CPI Components - Granular Detail
    "CUSR0000SAE2": "CPI Education Communication",
    "CUSR0000SEEE01": "CPI Computers Peripherals",
    "CUSR0000SEHB": "CPI Lodging Away from Home",
    "CUSR0000SEHF01": "CPI Electricity",
    "CUSR0000SEHF02": "CPI Utility Piped Gas",
    "CUSR0000SEMC": "CPI Professional Medical Services",
    "CUSR0000SEMD": "CPI Hospital Services",
    "CUSR0000SETG01": "CPI Airline Fares",
    "CUUR0000SETD": "CPI Motor Vehicle Maintenance Repair NSA",
    "CUUR0000SEGC": "CPI Personal Care Services NSA",

    # CPI Components - NSA Detail
    "CUUR0000SACL1E": "CPI Core Goods NSA",
    "CUUR0000SAF11": "CPI Food at Home NSA",
    "CUUR0000SAF112": "CPI Cereals Bakery NSA",
    "CUUR0000SAF113": "CPI Meats Poultry Fish Eggs NSA",
    "CUUR0000SAS": "CPI Services NSA",
    "CUUR0000SEFJ": "CPI Household Furnishings NSA",
    "CUUR0000SEFV": "CPI Food Away from Home NSA",

    # Sticky/Flexible CPI (Atlanta Fed)
    "CORESTICKM159SFRBATL": "Sticky Core CPI ex Food Energy",
    "COREFLEXCPIM159SFRBATL": "Flexible Core CPI ex Food Energy",
    "STICKCPIM157SFRBATL": "Sticky Price CPI",
    "FLEXCPIM157SFRBATL": "Flexible Price CPI",

    # PPI Pipeline Detail
    "PPIFIS": "PPI Final Demand",
    "PPIFES": "PPI Final Demand Less Foods Energy",
    "PPIFDS": "PPI Final Demand Services",
    "PPIACO": "PPI All Commodities",
    "PPIITM": "PPI Intermediate Demand Unprocessed Goods",
    "PPICPE": "PPI Crude Petroleum",
    "PPICRM": "PPI Crude Materials",

    # PCE Price Indices (Monthly)
    "DGDSRG3M086SBEA": "PCE Goods Price Index",
    "DSERRG3M086SBEA": "PCE Services Price Index",
    "IA001260M": "PCE Services Ex Energy Housing (Supercore)",

    # Inflation Expectations
    "MICH": "UMich 1Y Inflation Expectations",

    # Import/Export Prices
    "IR": "Import Price Index All Commodities",
    "IQ": "Export Price Index All Commodities",

    # GDP Deflator
    "GDPDEF": "GDP Implicit Price Deflator",

    # Trimmed Mean Inflation Measures
    "TRMMEANCPIM094SFRBCLE": "Trimmed Mean CPI 16pct MoM SA",
    "TRMMEANCPIM157SFRBCLE": "Trimmed Mean CPI 12M Pct Change",
    "TRMMEANCPIM159SFRBCLE": "Trimmed Mean CPI SA",
    "TRMMEANCPIM158SFRBCLE": "Trimmed Mean CPI Annualized Rate",
    "PCETRIM1M158SFRBDAL": "Trimmed Mean PCE 1M Annualized",
    "PCETRIM6M680SFRBDAL": "Trimmed Mean PCE 6M Annualized",
    "PCETRIM12M159SFRBDAL": "Trimmed Mean PCE 12M",

    # ===== PILLAR 3 (GROWTH) ADDITIONS =====

    # Housing Detail
    "HOUST1F": "Housing Starts Single Family",

    # Retail Detail
    "RSXFSN": "Advance Retail Sales Retail Trade",

    # Industrial Production Detail
    "IPMAN": "Industrial Production Manufacturing",
    "IPMINE": "Industrial Production Mining",
    "IPUTIL": "Industrial Production Utilities",
    "IPBUSEQ": "Industrial Production Business Equipment",
    "IPCONGD": "Industrial Production Consumer Goods",
    "IPDMAT": "Industrial Production Durable Materials",
    "IPNMAT": "Industrial Production Nondurable Materials",

    # Capacity Utilization
    "TCU": "Total Capacity Utilization",
    "MCUMFN": "Manufacturing Capacity Utilization",

    # ADP Employment
    "ADPMNUSNERSA": "ADP National Employment",

    # Real Personal Income/Consumption
    "DSPIC96": "Real Disposable Personal Income",
    "PCEC96": "Real Personal Consumption Expenditures",

    # GDP Components
    "PNFI": "Private Nonresidential Fixed Investment",
    "PRFI": "Private Residential Fixed Investment",
    "EXPGS": "Exports Goods and Services",
    "IMPGS": "Imports Goods and Services",

    # Business Surveys
    "BSCICP02USM460S": "Business Confidence Indicator",
    "BSCICP03USM665S": "Consumer Confidence Indicator OECD",

    # ===== PILLAR 3 (GROWTH) ADDITIONS - Feb 2026 =====

    # Real Manufacturing & Trade (for derived Inventories/Sales Ratio)
    "INVCMRMTSPL": "Real Manufacturing and Trade Inventories",
    "CMRMTSPL": "Real Manufacturing and Trade Industries Sales",
    # NOTE: Real Mfg & Trade I/S Ratio = INVCMRMTSPL / CMRMTSPL (derived)

    # Freight & Logistics
    "TRUCKD11": "Truck Tonnage Index",
    "RAILFRTINTERMODALD11": "Rail Freight Intermodal Traffic",
    # NOTE: RAILFRTCARLOADSD11 already in Freight section above

    # CEO Confidence - NOTE: Not available on FRED
    # Conference Board CEO Confidence: conference-board.org/topics/CEO-Confidence
    # Chief Executive CEO Confidence Index: chiefexecutive.net/ceo-confidence-index
    # Must be sourced directly from those sites

    # ===== PILLAR 3 (GROWTH) ADDITIONS - Feb 2026 Audit =====

    # GDP Components (quarterly, BEA)
    "GDP": "Gross Domestic Product (Nominal)",
    "GDI": "Gross Domestic Income",
    "GPDI": "Gross Private Domestic Investment",
    "GCE": "Government Consumption Expenditures and Gross Investment",
    "FGCE": "Federal Consumption Expenditures and Gross Investment",
    "PCEC": "Personal Consumption Expenditures (Nominal)",
    "CBI": "Change in Private Inventories",
    "NETEXP": "Net Exports of Goods and Services",

    # Final Sales (strips inventory noise)
    "A713RX1Q020SBEA": "Real Final Sales to Domestic Purchasers",
    "FINSLC1": "Real Final Sales of Domestic Product",

    # PCE Services (monthly)
    "PCES": "Personal Consumption Expenditures Services",

    # Employment
    "USPRIV": "All Employees Total Private",

    # Industrial Production Detail
    # IPUTIL already above
    "ECOMPCTSA": "E-Commerce Retail Sales Pct of Total",

    # Capital Goods & Equipment
    "ANXAVS": "Nondefense Capital Goods Shipments Ex-Aircraft",

    # Motor Vehicle Retail
    "MRTSSM441USS": "Retail Sales Motor Vehicle and Parts Dealers",

    # Leading/Coincident Indicators
    "USSLIND": "Leading Index for the United States",

    # Disposable Income
    "DPIC96": "Real Disposable Personal Income",

    # Productivity
    "PRS30006092": "Manufacturing Sector Labor Productivity",

    # ===== PILLAR 4 (HOUSING) ADDITIONS - Feb 2026 Audit =====

    # Vacancy & Ownership Rates (quarterly)
    "RRVRUSQ156N": "Rental Vacancy Rate in the United States",
    "RHVRUSQ156N": "Homeowner Vacancy Rate in the United States",

    # Construction Wages
    "CES2000000003": "Average Hourly Earnings: Construction",

    # ===== PILLAR 5 (CONSUMER) ADDITIONS - Feb 2026 Audit =====

    # Retail Sales
    "RSFSXMV": "Advance Retail Sales: Retail and Food Services Ex Motor Vehicles",

    # Consumer Credit Components
    "REVOLSL": "Revolving Consumer Credit Owned and Securitized",
    "NONREVSL": "Nonrevolving Consumer Credit Owned and Securitized",

    # Savings
    "PSAVE": "Personal Saving",

    # Transfer Payments
    "A063RC1": "Personal Current Transfer Receipts: Government Social Benefits",

    # PCE Components (explicit in curated list)
    "PCE": "Personal Consumption Expenditures",
    "PCDG": "Personal Consumption Expenditures: Durable Goods",
    "PCND": "Personal Consumption Expenditures: Nondurable Goods",
    "PCESV": "Personal Consumption Expenditures: Services",
    "PI": "Personal Income",
    "DPI": "Disposable Personal Income",
    "A576RC1": "Compensation of Employees: Wages and Salaries",
    "A229RX0": "Real Disposable Personal Income: Per Capita",
    "DGDSRC1": "Personal Consumption Expenditures: Goods (Nominal Monthly)",

    # Consumer Balance Sheet
    "BOGZ1FL192090005Q": "Households Net Worth Level",
    "HDTGPDUSQ163N": "Household Debt to GDP for United States",
    "FODSP": "Household Financial Obligations as Percent of DPI",

    # Interest Rates
    "TERMCBCCALLNS": "Commercial Bank Interest Rate on Credit Card Plans All Accounts",

    # Delinquency
    "DRCLACBS": "Delinquency Rate on Consumer Loans All Commercial Banks",

    # ===== PILLAR 7 (TRADE) ADDITIONS - Feb 2026 =====

    # Trade Balance & Flows (additional)
    "BOPSTB": "Trade Balance Services Only",
    "EXPGSC1": "Real Exports Goods and Services Chained 2017",
    "IMPGSC1": "Real Imports Goods and Services Chained 2017",
    "NETEXC": "Real Net Exports Goods and Services",

    # Import/Export Price Components
    "IREXPET": "Import Price Index All Commodities Excluding Petroleum",
    "IR4": "Import Price Index Consumer Goods Excluding Automotives",
    "IR2": "Import Price Index Capital Goods Except Automotive",
    "IR1": "Import Price Index Industrial Supplies and Materials",
    "IQAG": "Export Price Index Agricultural Commodities",
    "IQEXAG": "Export Price Index Nonagricultural Commodities",

    # Dollar Indices (Fed Trade-Weighted)
    "DTWEXAFEGS": "Dollar Index Advanced Foreign Economies",
    "DTWEXEMEGS": "Dollar Index Emerging Market Economies",
    "RTWEXBGS": "Real Broad Trade Weighted Dollar Index",

    # BIS Effective Exchange Rates
    "RBUSBIS": "BIS Real Broad Effective Exchange Rate US",
    "NBUSBIS": "BIS Nominal Broad Effective Exchange Rate US",
    "RNUSBIS": "BIS Real Narrow Effective Exchange Rate US",

    # Bilateral Trade
    "EXPCH": "US Exports of Goods to China",
    "IMPCH": "US Imports of Goods from China",
    "EXPJP": "US Exports of Goods to Japan",
    "IMPJP": "US Imports of Goods from Japan",

    # Current Account (BEA)
    "IEABC": "Balance on Current Account",
    "IEABCG": "Balance on Goods Current Account",
    "IEABCS": "Balance on Services Current Account",
    "IEABCPI": "Balance on Primary Income Current Account",
    "IEABCSI": "Balance on Secondary Income Current Account",

    # Trade Policy Uncertainty
    "EPUTRADE": "Trade Policy Uncertainty Index",

    # E-Commerce
    "ECOMSA": "E-Commerce Retail Sales",

    # Foreign Holdings
    "FDHBFIN": "Federal Debt Held by Foreign and International Investors",

    # ===== TRADE PILLAR - RETAIL DETAIL (Feb 2026 Expansion) =====

    # Real Retail Sales
    "RRSFS": "Advance Real Retail and Food Services Sales",

    # Monthly Retail Trade Detail
    "MRTSSM44X72USS": "Retail Sales Retail Trade and Food Services",
    "RETAILSMSA": "Retailers Sales Total",
    "MRTSSM4453USN": "Retail Sales Beer Wine Liquor Stores",
    "MRTSSM44112USN": "Retail Sales Used Car Dealers",
    "MRTSSM442USN": "Retail Sales Furniture Home Furnishings Stores",
    "MRTSSM7225USN": "Retail Sales Restaurants Eating Places",

    # Advance Retail Detail
    "RSGCS": "Advance Retail Sales Grocery Stores",

    # Wholesale
    "S4248SM144NCEN": "Wholesale Nondurable Goods Beer Wine Spirits Sales",

    # ===== TRADE PILLAR - BEA INTERNATIONAL (Feb 2026 Expansion) =====

    # Capital Account
    "IEABCP": "Balance on Capital Account",
    "IEABCPN": "Balance on Capital Account NSA",

    # BEA International Goods and Services
    "IEAMGSN": "Imports of Goods and Services BEA Quarterly",
    "IEAXGS": "Exports of Goods and Services BEA Quarterly",
}

# ==========================================
# BLS CONFIGURATION
# ==========================================

BLS_SERIES = {
    # Employment by Sector
    "CES0000000001": "Jobs_Total_Nonfarm",
    "CES1000000001": "Jobs_Mining_Logging",
    "CES2000000001": "Jobs_Construction",
    "CES3000000001": "Jobs_Manufacturing",
    "CES4000000001": "Jobs_Trade_Transport_Utilities",
    "CES5000000001": "Jobs_Information",
    "CES5500000001": "Jobs_Financial_Activities",
    "CES6000000001": "Jobs_Professional_Business",
    "CES6500000001": "Jobs_Education_Health",
    "CES7000000001": "Jobs_Leisure_Hospitality",
    "CES8000000001": "Jobs_Other_Services",
    "CES9000000001": "Jobs_Government",

    # Unemployment Detail
    "LNS14000000": "Unemployment_Rate_U3",
    "LNS13327709": "Unemployment_Rate_U6",
    "LNS11300000": "Labor_Force_Participation",
    "LNS12300000": "Employment_Population_Ratio",
    "LNS11300060": "Prime_Age_LFPR_25_54",

    # JOLTS
    "JTS000000000000000JOR": "JOLTS_Openings_Rate",
    "JTS000000000000000HIR": "JOLTS_Hires_Rate",
    "JTS000000000000000QUR": "JOLTS_Quits_Rate",
    "JTS000000000000000TSR": "JOLTS_Separations_Rate",

    # Prices
    "CUUR0000SA0": "CPI_Headline_NSA",
    "CUUR0000SA0L1E": "CPI_Core_NSA",
    "CUUR0000SA0E": "CPI_Energy_NSA",
    "CUUR0000SAH1": "CPI_Shelter_NSA",
    "CUUR0000SAS": "CPI_Services_NSA",
    "CUUR0000SAF1": "CPI_Food_NSA",
    "WPSFD4": "PPI_Final_Demand",
    "WPUFD49104": "PPI_Core",

    # Wages
    "CES0500000003": "Avg_Hourly_Earnings_Private",
    "CES0500000008": "Avg_Hourly_Earnings_Production",
}

# ==========================================
# BEA CONFIGURATION
# ==========================================

BEA_TABLES = [
    {"table": "T10105", "dataset": "NIPA", "desc": "GDP_Components"},
    {"table": "T10101", "dataset": "NIPA", "desc": "Real_GDP_Growth"},
    {"table": "T20100", "dataset": "NIPA", "desc": "Personal_Income"},
    {"table": "T20305", "dataset": "NIPA", "desc": "PCE_Components"},
    {"table": "T11200", "dataset": "NIPA", "desc": "Corporate_Profits"},
    {"table": "T11000", "dataset": "NIPA", "desc": "GDI"},
    {"table": "T30100", "dataset": "NIPA", "desc": "Govt_Receipts_Expenditures"},
    {"table": "T20304", "dataset": "NIPA", "desc": "PCE_Price_Index"},
    {"table": "T10104", "dataset": "NIPA", "desc": "GDP_Price_Index"},
]

# ==========================================
# NY FED CONFIGURATION (No API key needed)
# ==========================================

NYFED_RATES = {
    # Reference Rates - the core plumbing rates
    "SOFR": "Secured Overnight Financing Rate",
    "EFFR": "Effective Federal Funds Rate",
    "OBFR": "Overnight Bank Funding Rate",
    "TGCR": "Tri-Party General Collateral Rate",
    "BGCR": "Broad General Collateral Rate",
}

# OFR Series from Short-term Funding Monitor (No API key needed)
OFR_SERIES = {
    # Reference Rates (via OFR API)
    "FNYR-SOFR-A": "OFR_SOFR",
    "FNYR-EFFR-A": "OFR_EFFR",
    "FNYR-OBFR-A": "OFR_OBFR",
    "FNYR-TGCR-A": "OFR_TGCR",
    "FNYR-BGCR-A": "OFR_BGCR",

    # Money Market Funds
    "MMF-MMF_TOT-M": "MMF_Total_Assets",
    "MMF-MMF_RP_TOT-M": "MMF_Repo_Total",
    "MMF-MMF_RP_wFR-M": "MMF_Repo_with_Fed",
    "MMF-MMF_T_TOT-M": "MMF_Treasury_Total",

    # Primary Dealer Repo/RRP
    "NYPD-PD_RP_TOT-A": "PD_Repo_Total",
    "NYPD-PD_RRP_TOT-A": "PD_ReverseRepo_Total",
    "NYPD-PD_RP_T_TOT-A": "PD_Repo_Treasury_Total",
}


# ==========================================
# DATABASE SCHEMA
# ==========================================

def init_db():
    """Initialize the master database with unified schema."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Master observations table - the single source of truth
    c.execute('''CREATE TABLE IF NOT EXISTS observations (
        series_id TEXT,
        date TEXT,
        value REAL,
        PRIMARY KEY (series_id, date)
    )''')

    # Series metadata
    c.execute('''CREATE TABLE IF NOT EXISTS series_meta (
        series_id TEXT PRIMARY KEY,
        title TEXT,
        source TEXT,
        category TEXT,
        frequency TEXT,
        units TEXT,
        last_updated TEXT,
        last_fetched TEXT
    )''')

    # Update log for tracking
    c.execute('''CREATE TABLE IF NOT EXISTS update_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        source TEXT,
        series_updated INTEGER,
        observations_added INTEGER,
        duration_seconds REAL
    )''')

    # Indexes for fast queries
    c.execute('CREATE INDEX IF NOT EXISTS idx_obs_series ON observations(series_id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_obs_date ON observations(date)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meta_source ON series_meta(source)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_meta_category ON series_meta(category)')

    conn.commit()
    conn.close()
    print(f"Database initialized: {DB_PATH}")


# ==========================================
# FRED FETCHER
# ==========================================

def fetch_fred_category(category_id, category_name, conn, limit=50):
    """Discover and fetch top series from a FRED category."""
    c = conn.cursor()
    updated = 0
    obs_added = 0

    # Discover series in category
    url = "https://api.stlouisfed.org/fred/category/series"
    params = {
        "category_id": category_id,
        "api_key": API_KEYS["FRED"],
        "file_type": "json",
        "limit": limit,
        "order_by": "popularity",
        "sort_order": "desc"
    }

    try:
        r = requests.get(url, params=params, timeout=30)
        data = r.json()

        if "seriess" not in data:
            return 0, 0

        for s in data["seriess"]:
            series_id = s["id"]
            api_updated = s.get("last_updated", "")

            # Check if we need to update
            c.execute("SELECT last_updated FROM series_meta WHERE series_id = ?", (series_id,))
            row = c.fetchone()
            local_updated = row[0] if row else "1900-01-01"

            if row and local_updated >= api_updated:
                continue  # Skip - already current

            # Fetch observations
            obs_url = "https://api.stlouisfed.org/fred/series/observations"
            obs_params = {
                "series_id": series_id,
                "api_key": API_KEYS["FRED"],
                "file_type": "json"
            }

            obs_r = requests.get(obs_url, params=obs_params, timeout=30)
            obs_data = obs_r.json()

            if "observations" in obs_data:
                obs_list = [(series_id, o["date"], float(o["value"]))
                           for o in obs_data["observations"] if o["value"] != "."]

                if obs_list:
                    c.executemany("INSERT OR REPLACE INTO observations VALUES (?,?,?)", obs_list)

                    # Update metadata
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, s.get("title", ""), "FRED", category_name,
                              s.get("frequency", ""), s.get("units", ""),
                              api_updated, datetime.now().isoformat()))

                    updated += 1
                    obs_added += len(obs_list)

            time.sleep(0.1)  # Rate limiting

    except Exception as e:
        print(f"   Error fetching category {category_name}: {e}")

    return updated, obs_added


def fetch_fred_curated(conn):
    """Fetch curated high-priority FRED series."""
    c = conn.cursor()
    updated = 0
    obs_added = 0

    for series_id, title in FRED_CURATED.items():
        # Check last update
        c.execute("SELECT last_fetched FROM series_meta WHERE series_id = ?", (series_id,))
        row = c.fetchone()

        # Fetch observations
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": API_KEYS["FRED"],
            "file_type": "json"
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()

            if "observations" in data:
                obs_list = [(series_id, o["date"], float(o["value"]))
                           for o in data["observations"] if o["value"] != "."]

                if obs_list:
                    c.executemany("INSERT OR REPLACE INTO observations VALUES (?,?,?)", obs_list)

                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, title, "FRED", "Curated", "", "",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                    updated += 1
                    obs_added += len(obs_list)

        except Exception as e:
            print(f"   Error fetching {series_id}: {e}")

        time.sleep(0.1)

    return updated, obs_added


def fetch_all_fred(conn):
    """Fetch all FRED data: categories + curated."""
    print("\n--- FRED: Category Discovery ---")
    total_updated = 0
    total_obs = 0

    for cat_name, cat_id in FRED_CATEGORIES.items():
        print(f"   {cat_name}...", end=" ")
        updated, obs = fetch_fred_category(cat_id, cat_name, conn)
        print(f"{updated} series, {obs:,} obs")
        total_updated += updated
        total_obs += obs
        conn.commit()
        time.sleep(0.3)

    print("\n--- FRED: Curated Series ---")
    updated, obs = fetch_fred_curated(conn)
    print(f"   {updated} series, {obs:,} obs")
    total_updated += updated
    total_obs += obs
    conn.commit()

    return total_updated, total_obs


# ==========================================
# BLS FETCHER
# ==========================================

def fetch_all_bls(conn, start_year=1990):
    """Fetch all BLS series with 20-year chunking."""
    print("\n--- BLS: Labor & Prices ---")
    c = conn.cursor()
    total_obs = 0

    current_year = datetime.now().year
    intervals = [(start, min(start + 19, current_year))
                 for start in range(start_year, current_year + 1, 20)]

    series_ids = list(BLS_SERIES.keys())

    for start_yr, end_yr in intervals:
        print(f"   {start_yr}-{end_yr}...", end=" ")

        payload = {
            "seriesid": series_ids,
            "startyear": str(start_yr),
            "endyear": str(end_yr),
            "registrationkey": API_KEYS["BLS"]
        }

        try:
            r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/",
                            json=payload, timeout=60)

            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "REQUEST_SUCCEEDED":
                    chunk_obs = 0
                    for s in data["Results"]["series"]:
                        series_id = s["seriesID"]
                        title = BLS_SERIES.get(series_id, series_id)

                        for item in s["data"]:
                            if item["value"] not in ["", "."]:
                                # Convert period to date
                                period = item["period"]
                                if period.startswith("M"):
                                    month = period[1:]
                                    date_str = f"{item['year']}-{month}-01"
                                elif period.startswith("Q"):
                                    q_map = {"Q01": "01", "Q02": "04", "Q03": "07", "Q04": "10"}
                                    month = q_map.get(period, "01")
                                    date_str = f"{item['year']}-{month}-01"
                                else:
                                    date_str = f"{item['year']}-01-01"

                                try:
                                    value = float(item["value"])
                                    c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                             (f"BLS_{series_id}", date_str, value))
                                    chunk_obs += 1
                                except ValueError:
                                    pass

                        # Update metadata
                        c.execute("""INSERT OR REPLACE INTO series_meta
                                    (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                    VALUES (?,?,?,?,?,?,?,?)""",
                                 (f"BLS_{series_id}", title, "BLS", "Labor_Prices", "Monthly", "",
                                  datetime.now().isoformat(), datetime.now().isoformat()))

                    print(f"{chunk_obs:,} obs")
                    total_obs += chunk_obs
                    conn.commit()

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.5)

    return len(BLS_SERIES), total_obs


# ==========================================
# BEA FETCHER
# ==========================================

def fetch_all_bea(conn, start_year=2000):
    """Fetch all BEA NIPA tables."""
    print("\n--- BEA: National Accounts ---")
    c = conn.cursor()
    total_obs = 0

    years = ",".join([str(y) for y in range(start_year, datetime.now().year + 1)])

    for table_info in BEA_TABLES:
        print(f"   {table_info['desc']}...", end=" ")

        params = {
            "UserID": API_KEYS["BEA"],
            "Method": "GetData",
            "DatasetName": table_info["dataset"],
            "TableName": table_info["table"],
            "Frequency": "Q",
            "Year": years,
            "ResultFormat": "JSON"
        }

        try:
            r = requests.get("https://apps.bea.gov/api/data/", params=params, timeout=60)

            if r.status_code == 200:
                data = r.json()
                if "BEAAPI" in data and "Results" in data["BEAAPI"]:
                    rows = data["BEAAPI"]["Results"].get("Data", [])
                    table_obs = 0

                    for row in rows:
                        tp = row.get("TimePeriod", "")
                        if "Q" in tp:
                            q_map = {"Q1": "01", "Q2": "04", "Q3": "07", "Q4": "10"}
                            quarter = tp[-2:]
                            month = q_map.get(quarter, "01")
                            date_str = f"{tp[:4]}-{month}-01"
                        else:
                            date_str = f"{tp}-01-01"

                        # Create unique series ID
                        line_desc = row.get("LineDescription", "Unknown")
                        series_id = f"BEA_{table_info['desc']}_{line_desc}".replace(" ", "_")[:100]

                        try:
                            value_str = row.get("DataValue", "").replace(",", "")
                            value = float(value_str)
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     (series_id, date_str, value))
                            table_obs += 1

                            # Metadata
                            c.execute("""INSERT OR REPLACE INTO series_meta
                                        (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                        VALUES (?,?,?,?,?,?,?,?)""",
                                     (series_id, line_desc, "BEA", table_info["desc"], "Quarterly", "",
                                      datetime.now().isoformat(), datetime.now().isoformat()))
                        except (ValueError, TypeError):
                            pass

                    print(f"{table_obs:,} obs")
                    total_obs += table_obs
                    conn.commit()
                else:
                    print("No data")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.5)

    return len(BEA_TABLES), total_obs


# ==========================================
# NY FED FETCHER (No API key needed)
# ==========================================

def fetch_all_nyfed(conn, start_date="2018-04-03"):
    """Fetch NY Fed reference rates (SOFR, EFFR, OBFR, TGCR, BGCR)."""
    print("\n--- NY Fed: Reference Rates ---")
    c = conn.cursor()
    total_obs = 0

    # NY Fed Markets API - get all historical rates
    url = f"https://markets.newyorkfed.org/api/rates/all/search.json?startDate={start_date}"

    try:
        print(f"   Fetching from {start_date}...", end=" ")
        r = requests.get(url, timeout=60)

        if r.status_code == 200:
            data = r.json()

            if "refRates" in data:
                for item in data["refRates"]:
                    rate_type = item.get("type", "")
                    if rate_type in NYFED_RATES:
                        date_str = item.get("effectiveDate", "")
                        rate = item.get("percentRate")

                        if rate is not None and date_str:
                            series_id = f"NYFED_{rate_type}"
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     (series_id, date_str, float(rate)))
                            total_obs += 1

                            # Also store volume if available
                            volume = item.get("volumeInBillions")
                            if volume is not None:
                                vol_series_id = f"NYFED_{rate_type}_Volume"
                                c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                         (vol_series_id, date_str, float(volume)))
                                total_obs += 1

                # Update metadata for each rate type
                for rate_type, title in NYFED_RATES.items():
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (f"NYFED_{rate_type}", title, "NYFED", "Reference_Rates", "Daily", "Percent",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (f"NYFED_{rate_type}_Volume", f"{title} Volume", "NYFED", "Reference_Rates", "Daily", "Billions USD",
                              datetime.now().isoformat(), datetime.now().isoformat()))

                conn.commit()
                print(f"{total_obs:,} obs")

    except Exception as e:
        print(f"Error: {e}")

    return len(NYFED_RATES) * 2, total_obs  # *2 for rate + volume


# ==========================================
# OFR FETCHER (No API key needed)
# ==========================================

def fetch_all_ofr(conn):
    """Fetch OFR Short-term Funding Monitor data + Financial Stress Index."""
    print("\n--- OFR: Short-term Funding Monitor ---")
    c = conn.cursor()
    total_obs = 0
    series_count = 0

    # Fetch each series from OFR API
    for mnemonic, title in OFR_SERIES.items():
        print(f"   {title}...", end=" ")

        url = f"https://data.financialresearch.gov/v1/series/timeseries/?mnemonic={mnemonic}"

        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                obs_count = 0

                for item in data:
                    if isinstance(item, list) and len(item) >= 2:
                        date_str = item[0]
                        value = item[1]
                        if value is not None:
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     (f"OFR_{mnemonic}", date_str, float(value)))
                            obs_count += 1

                if obs_count > 0:
                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (f"OFR_{mnemonic}", title, "OFR", "Short_Term_Funding", "Daily", "",
                              datetime.now().isoformat(), datetime.now().isoformat()))
                    series_count += 1
                    total_obs += obs_count
                    print(f"{obs_count:,} obs")
                else:
                    print("no data")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(0.2)

    conn.commit()

    # Fetch OFR Financial Stress Index (CSV download)
    print("\n--- OFR: Financial Stress Index ---")
    fsi_url = "https://www.financialresearch.gov/financial-stress-index/data/fsi.csv"

    try:
        print(f"   Fetching FSI...", end=" ")
        r = requests.get(fsi_url, timeout=30)

        if r.status_code == 200:
            from io import StringIO
            df = pd.read_csv(StringIO(r.text))

            fsi_series = {
                "OFR FSI": "OFR_FSI",
                "Credit": "OFR_FSI_Credit",
                "Equity valuation": "OFR_FSI_Equity",
                "Safe assets": "OFR_FSI_SafeAssets",
                "Funding": "OFR_FSI_Funding",
                "Volatility": "OFR_FSI_Volatility",
                "United States": "OFR_FSI_US",
                "Other advanced economies": "OFR_FSI_AdvancedEcon",
                "Emerging markets": "OFR_FSI_EmergingMkts",
            }

            fsi_obs = 0
            for col, series_id in fsi_series.items():
                if col in df.columns:
                    for _, row in df.iterrows():
                        if pd.notna(row[col]):
                            c.execute("INSERT OR REPLACE INTO observations VALUES (?,?,?)",
                                     (series_id, row["Date"], float(row[col])))
                            fsi_obs += 1

                    c.execute("""INSERT OR REPLACE INTO series_meta
                                (series_id, title, source, category, frequency, units, last_updated, last_fetched)
                                VALUES (?,?,?,?,?,?,?,?)""",
                             (series_id, f"Financial Stress Index - {col}", "OFR", "Financial_Stress", "Daily", "Index",
                              datetime.now().isoformat(), datetime.now().isoformat()))
                    series_count += 1

            total_obs += fsi_obs
            conn.commit()
            print(f"{fsi_obs:,} obs ({len(fsi_series)} components)")

    except Exception as e:
        print(f"Error fetching FSI: {e}")

    return series_count, total_obs


# ==========================================
# MAIN UPDATE ROUTINE
# ==========================================

def run_daily_update():
    """Master update routine - run this daily."""
    start_time = time.time()

    print("=" * 70)
    print("LIGHTHOUSE MACRO - MASTER DATABASE UPDATE")
    print(f"Database: {DB_PATH}")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    init_db()
    conn = sqlite3.connect(DB_PATH)

    # Fetch all sources
    fred_series, fred_obs = fetch_all_fred(conn)
    bls_series, bls_obs = fetch_all_bls(conn)
    bea_series, bea_obs = fetch_all_bea(conn)
    nyfed_series, nyfed_obs = fetch_all_nyfed(conn)
    ofr_series, ofr_obs = fetch_all_ofr(conn)

    # Log the update
    duration = time.time() - start_time
    c = conn.cursor()
    c.execute("""INSERT INTO update_log (timestamp, source, series_updated, observations_added, duration_seconds)
                VALUES (?,?,?,?,?)""",
             (datetime.now().isoformat(), "ALL",
              fred_series + bls_series + bea_series + nyfed_series + ofr_series,
              fred_obs + bls_obs + bea_obs + nyfed_obs + ofr_obs, duration))
    conn.commit()

    # Summary
    print("\n" + "=" * 70)
    print("UPDATE COMPLETE")
    print("=" * 70)

    # Database stats
    total_obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    total_series = conn.execute("SELECT COUNT(*) FROM series_meta").fetchone()[0]
    date_range = conn.execute("SELECT MIN(date), MAX(date) FROM observations").fetchone()

    print(f"\nDatabase Statistics:")
    print(f"  Total Observations: {total_obs:,}")
    print(f"  Total Series: {total_series}")
    print(f"  Date Range: {date_range[0]} to {date_range[1]}")
    print(f"  Duration: {duration:.1f} seconds")

    print(f"\nThis Update:")
    print(f"  FRED:  {fred_series} series, {fred_obs:,} observations")
    print(f"  BLS:   {bls_series} series, {bls_obs:,} observations")
    print(f"  BEA:   {bea_series} series, {bea_obs:,} observations")
    print(f"  NYFED: {nyfed_series} series, {nyfed_obs:,} observations")
    print(f"  OFR:   {ofr_series} series, {ofr_obs:,} observations")

    # By source
    print(f"\nBy Source:")
    source_stats = pd.read_sql("""
        SELECT source, COUNT(DISTINCT series_id) as series,
               (SELECT COUNT(*) FROM observations o
                WHERE o.series_id IN (SELECT series_id FROM series_meta sm WHERE sm.source = series_meta.source)) as obs
        FROM series_meta
        GROUP BY source
    """, conn)
    print(source_stats.to_string(index=False))

    conn.close()
    print("=" * 70)

    return total_series, total_obs


# ==========================================
# QUERY HELPERS
# ==========================================

def get_series(series_id, start_date=None, end_date=None):
    """Query a specific series from the database."""
    conn = sqlite3.connect(DB_PATH)

    query = "SELECT date, value FROM observations WHERE series_id = ?"
    params = [series_id]

    if start_date:
        query += " AND date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND date <= ?"
        params.append(end_date)

    query += " ORDER BY date"

    df = pd.read_sql(query, conn, params=params)
    df["date"] = pd.to_datetime(df["date"])
    conn.close()
    return df


def search_series(keyword):
    """Search for series by keyword in title."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT series_id, title, source, category
        FROM series_meta
        WHERE title LIKE ? OR series_id LIKE ?
        ORDER BY source, category
    """, conn, params=[f"%{keyword}%", f"%{keyword}%"])
    conn.close()
    return df


def get_category(category):
    """Get all series in a category."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("""
        SELECT series_id, title, source
        FROM series_meta
        WHERE category = ?
        ORDER BY title
    """, conn, params=[category])
    conn.close()
    return df


def export_wide(output_path=None, start_date="2000-01-01"):
    """Export all data to wide-format CSV."""
    if output_path is None:
        output_path = DB_PATH.parent / "Lighthouse_Master_Wide.csv"

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql(f"""
        SELECT o.date, m.title, o.value
        FROM observations o
        JOIN series_meta m ON o.series_id = m.series_id
        WHERE o.date >= '{start_date}'
        ORDER BY o.date
    """, conn)

    df_wide = df.pivot_table(index="date", columns="title", values="value")
    df_wide.to_csv(output_path)

    print(f"Exported to: {output_path}")
    print(f"Shape: {df_wide.shape[0]} rows x {df_wide.shape[1]} columns")

    conn.close()
    return output_path


def get_stats():
    """Print database statistics."""
    conn = sqlite3.connect(DB_PATH)

    print("\n--- Lighthouse Master Database ---")

    total_obs = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
    total_series = conn.execute("SELECT COUNT(*) FROM series_meta").fetchone()[0]
    print(f"Total Observations: {total_obs:,}")
    print(f"Total Series: {total_series}")

    date_range = conn.execute("SELECT MIN(date), MAX(date) FROM observations").fetchone()
    print(f"Date Range: {date_range[0]} to {date_range[1]}")

    print("\nBy Source:")
    by_source = pd.read_sql("""
        SELECT source, COUNT(*) as series FROM series_meta GROUP BY source
    """, conn)
    print(by_source.to_string(index=False))

    print("\nBy Category:")
    by_cat = pd.read_sql("""
        SELECT category, COUNT(*) as series FROM series_meta GROUP BY category ORDER BY series DESC LIMIT 15
    """, conn)
    print(by_cat.to_string(index=False))

    print("\nRecent Updates:")
    updates = pd.read_sql("""
        SELECT timestamp, source, series_updated, observations_added, duration_seconds
        FROM update_log ORDER BY id DESC LIMIT 5
    """, conn)
    print(updates.to_string(index=False))

    conn.close()


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":
    run_daily_update()
    get_stats()
