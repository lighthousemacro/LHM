"""
LIGHTHOUSE MACRO - CONFIGURATION
================================
All configuration in one place. API keys from environment.
"""

import os
from pathlib import Path

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    # Look for .env in the package directory
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # dotenv not installed, rely on environment variables

# ==========================================
# PATHS
# ==========================================

DB_PATH = Path(os.getenv("LIGHTHOUSE_DB_PATH",
    "/Users/bob/LHM/Data/databases/Lighthouse_Master.db"))
OUTPUT_DIR = DB_PATH.parent

# ==========================================
# API KEYS
# ==========================================
# Checks environment first, falls back to defaults

API_KEYS = {
    "FRED": os.getenv("FRED_API_KEY", "11893c506c07b3b8647bf16cf60586e8"),
    "BLS": os.getenv("BLS_API_KEY", "2e66aeb26c664d4fbc862de06d1f8899"),
    "BEA": os.getenv("BEA_API_KEY", "4401D40D-4047-414F-B4FE-D441E96F8DE8"),
    "TOKEN_TERMINAL": os.getenv("TOKEN_TERMINAL_API_KEY", "348c4261-f49b-4517-949c-e18ef6a6c300"),
}

def validate_api_keys():
    """Check that required API keys are set."""
    missing = [k for k, v in API_KEYS.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing API keys: {', '.join(missing)}. "
            f"Set them in .env or as environment variables."
        )

# ==========================================
# FRED CATEGORY AUTO-DISCOVERY
# ==========================================

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

# ==========================================
# FRED CURATED SERIES
# ==========================================

FRED_CURATED = {
    # Labor Market - Headline
    "UNRATE": "Unemployment Rate U3",
    "U6RATE": "Unemployment Rate U6",
    "CIVPART": "Labor Force Participation",
    "PAYEMS": "Total Nonfarm Payrolls",
    "ICSA": "Initial Jobless Claims",
    "CCSA": "Continued Claims",
    "JTS1000JOR": "JOLTS Job Openings Rate",
    "JTS1000QUR": "JOLTS Quits Rate",
    "JTS1000HIR": "JOLTS Hires Rate",

    # Inflation - Headline & Core
    "CPIAUCSL": "CPI All Urban Consumers",
    "CPILFESL": "Core CPI",
    "PCEPI": "PCE Price Index",
    "PCEPILFE": "Core PCE",

    # Inflation - CPI Aggregates
    "CUSR0000SACL1E": "CPI Core Goods",
    "CUSR0000SAS": "CPI Services All",
    "CUSR0000SASLE": "CPI Services Less Energy",
    "CUSR0000SASL2RS": "CPI Services Less Rent of Shelter",
    "CUSR0000SAC": "CPI Commodities",
    "CUSR0000SACL1": "CPI Commodities Less Food",

    # Inflation - CPI Services Detail (not in CPI Components below)
    "CUSR0000SEMD": "CPI Hospital Services",
    "CUSR0000SEMC": "CPI Professional Medical Services",
    "CUSR0000SAS2RS": "CPI Rent of Shelter",

    # Inflation - CPI Goods Detail (not in CPI Components below)
    "CPIAPPSL": "CPI Apparel",
    "CPIUFDSL": "CPI Food",
    "CPIENGSL": "CPI Energy",
    "CPIMEDSL": "CPI Medical Care",
    "CUSR0000SACE": "CPI Energy Commodities",

    # Inflation - Alternative Measures
    "MEDCPIM158SFRBCLE": "Median CPI",
    "CORESTICKM159SFRBATL": "Sticky Core CPI",
    "COREFLEXCPIM159SFRBATL": "Flexible Core CPI",
    "PCETRIM12M159SFRBDAL": "Trimmed Mean PCE Inflation Rate",

    # Atlanta Fed Wage Growth Tracker
    "FRBATLWGT12MMUMHGO": "Atlanta Fed Wage Growth 12M Overall",
    "FRBATLWGT3MMAUMHWGO": "Atlanta Fed Wage Growth 3M Overall",
    "FRBATLWGT12MMUMHWGJST": "Atlanta Fed Wage Growth Job Stayers",
    "FRBATLWGT12MMUMHWGJSW": "Atlanta Fed Wage Growth Job Switchers",
    "FRBATLWGT12MMUMHWGWD1WP": "Atlanta Fed Wage Growth 1st-25th Pctl",
    "FRBATLWGT12MMUMHWGWD76WP": "Atlanta Fed Wage Growth 76th-100th Pctl",

    # Inflation - PPI Pipeline
    "PPIFIS": "PPI Final Demand",
    "PPIDSS": "PPI Final Demand Services SA",
    "PPIFGS": "PPI Final Demand Goods",
    "PPIFDF": "PPI Final Demand Foods",
    "PPIIDC": "PPI Intermediate Demand Processed Goods",
    "PPIITM": "PPI Intermediate Demand Unprocessed Goods",
    "WPSFD4131": "PPI Final Demand Less Foods Energy Trade",
    "WPUFD49116": "PPI Final Demand Services Less Trade",
    "WPSFD41312": "PPI Final Demand Goods Less Foods Energy",

    # Inflation - Expectations
    "MICH": "UMich 1Y Inflation Expectations",
    "EXPINF1YR": "Cleveland Fed 1Y Inflation Expectations",
    "EXPINF2YR": "Cleveland Fed 2Y Inflation Expectations",
    "EXPINF5YR": "Cleveland Fed 5Y Inflation Expectations",
    "EXPINF10YR": "Cleveland Fed 10Y Inflation Expectations",
    "EXPINF30YR": "Cleveland Fed 30Y Inflation Expectations",

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

    # Labor Demographics - Labels verified against FRED API 2026-02-16
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

    # CPI Components - Shelter
    "CUSR0000SAH1": "CPI Shelter",
    "CUSR0000SEHA": "CPI Rent Primary Residence",
    "CUSR0000SEHC": "CPI Owners Equivalent Rent",

    # CPI Components - Food & Energy
    "CUSR0000SAF11": "CPI Food at Home",
    "CUSR0000SEFV": "CPI Food Away from Home",
    "CUSR0000SAH2": "CPI Fuel Utilities",
    "CUSR0000SETB01": "CPI Gasoline",
    "CUSR0000SEHF01": "CPI Electricity",
    "CUSR0000SEHF02": "CPI Utility Piped Gas",

    # CPI Components - Medical
    "CUSR0000SAM1": "CPI Medical Care Services",
    "CUSR0000SAM2": "CPI Medical Care Commodities",

    # CPI Components - Transportation & Vehicles
    "CUSR0000SAS4": "CPI Transportation Services",
    "CUSR0000SETA02": "CPI Used Cars Trucks",
    "CUSR0000SETA01": "CPI New Vehicles",
    "CUSR0000SETC": "CPI Motor Vehicle Maintenance Repair",
    "CUSR0000SETG01": "CPI Airline Fares",

    # CPI Components - Other
    "CUSR0000SAE1": "CPI Education",
    "CUSR0000SEHE": "CPI Household Furnishings Operations",
    "CUSR0000SEEB": "CPI Tuition Other School Fees Childcare",
    "CUSR0000SEGA": "CPI Tobacco Products",
    "CUSR0000SEHF": "CPI Lodging Away from Home",
    "CUSR0000SS62031": "CPI Admission Movies Theaters Concerts",

    # PCE Components - Aggregates
    "DGDSRG3M086SBEA": "PCE Goods",
    "DSERRG3M086SBEA": "PCE Services",
    "PCEDG": "PCE Durable Goods",
    "PCEND": "PCE Nondurable Goods",
    "PCES": "PCE Services",

    # PCE Components - Supercore & Special Aggregates
    "IA001260M": "PCE Services Ex Energy Housing Monthly",
    "IA001176M": "PCE Ex Food Energy Housing Monthly",
    "JCXFE": "PCE Chain Price Index Less Food Energy",

    # Financial Conditions
    "NFCI": "Chicago Fed NFCI",
    "ANFCI": "Adjusted NFCI",
    "STLFSI4": "St Louis Fed FSI",

    # Credit/Lending
    "DRTSCILM": "Loan Officer Survey C&I Tightening",
    "DRTSCLCC": "Loan Officer Survey Credit Card Tightening",
    "TOTCI": "Commercial Industrial Loans",
    "CONSUMER": "Consumer Loans at Banks",
    "BUSLOANS": "Business Loans at Banks",
    "REALLN": "Real Estate Loans at Banks",

    # Treasury Auctions
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

    # Recession / Confirmation Indicators
    "SAHMREALTIME": "Sahm Rule Recession Indicator",
    "IHLIDXUS": "Indeed Job Postings Index US",
    "IURSA": "Insured Unemployment Rate",

    # ISM / PMI - NOTE: ISM data was removed from FRED in June 2016 due to licensing
    # NAPM, NAPMNOI, NAPMII, etc. are no longer available via FRED API
    # Use Regional Fed surveys as proxies or get ISM data from other sources
    "MANEMP": "Manufacturing Employment",

    # NFIB - NOTE: NFIB Small Business Optimism not available on FRED
    # Must be sourced directly from nfib.com

    # Regional Fed
    "GACDISA066MSFRBNY": "Empire State Manufacturing",
    "GACDFSA066MSFRBPHI": "Philly Fed Manufacturing",
    "CFNAIMA3": "Chicago Fed National Activity",
    "KCFSI": "Kansas City Fed FSI",
    "DFXARC1M027SBEA": "Dallas Fed Manufacturing",

    # Durable Goods
    "DGORDER": "Durable Goods Orders",
    "ADXTNO": "Durable Goods Orders Ex Transportation",
    "NEWORDER": "Manufacturers New Orders Total",
    "AMTMNO": "Manufacturers Total New Orders",
    "ACDGNO": "Durable Goods Orders Ex Defense",
    "ANDENO": "Nondefense Capital Goods Orders Ex Aircraft",
    # Note: AMDMNO discontinued, use DGORDER and ADXTNO instead
    "AMNMNO": "Nondurable Manufacturers New Orders",

    # Trade
    "BOPGSTB": "Trade Balance Goods and Services",
    "BOPGTB": "Trade Balance Goods Only",
    "BOPTEXP": "Exports Goods and Services",
    "BOPTIMP": "Imports Goods and Services",
    "IMPGS": "Real Imports Goods Services",
    "EXPGS": "Real Exports Goods Services",
    "IR": "Import Price Index",
    "IQ": "Export Price Index",
    "NETEXP": "Net Exports",

    # Freight
    "RAILFRTCARLOADSD11": "Rail Freight Carloads",
    "TSIFRGHT": "Transportation Services Index Freight",
    "TSITTL": "Transportation Services Index Total",
    "FRGSHPUSM649NCIS": "Cass Freight Shipments Index",
    # Note: LOADFAC discontinued

    # Auto Sales
    "ALTSALES": "Light Vehicle Sales Total",
    "LAUTOSA": "Light Autos Sales",
    "LTOTALNSA": "Light Trucks Sales",
    "HTRUCKSSAAR": "Heavy Truck Sales",
    "TOTALSA": "Total Vehicle Sales",
    "AISRSA": "Auto Inventory Sales Ratio",

    # Retail Detail
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

    # Fiscal
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

    # Productivity
    "OPHNFB": "Nonfarm Business Output Per Hour",
    "PRS85006092": "Nonfarm Unit Labor Costs",
    "ULCNFB": "Unit Labor Costs Nonfarm Business",
    "COMPNFB": "Nonfarm Business Compensation Per Hour",
    "HOANBS": "Nonfarm Business Hours Worked",

    # Wages
    "CES0500000003": "Average Hourly Earnings Total Private",
    "AHETPI": "Average Hourly Earnings Production",
    "LES1252881600Q": "Median Usual Weekly Earnings",
    "ECIWAG": "Employment Cost Index Wages Salaries",
    "ECIALLCIV": "Employment Cost Index Total",

    # ===== PILLAR 2 (PRICES) ADDITIONS =====

    # CPI Components - Granular Detail
    "CUSR0000SAE2": "CPI Education Communication",
    "CUSR0000SEEE01": "CPI Computers Peripherals",
    "CUSR0000SEHB": "CPI Lodging Away from Home",
    "CUUR0000SACL1E": "CPI Core Goods NSA",
    "CUUR0000SAF11": "CPI Food at Home NSA",
    "CUUR0000SAF112": "CPI Cereals Bakery NSA",
    "CUUR0000SAF113": "CPI Meats Poultry Fish Eggs NSA",
    "CUUR0000SAS": "CPI Services NSA",
    "CUUR0000SEFJ": "CPI Household Furnishings NSA",
    "CUUR0000SEFV": "CPI Food Away from Home NSA",

    # PPI Pipeline Detail
    "PPIACO": "PPI All Commodities",
    "PPICPE": "PPI Crude Petroleum",
    "PPICRM": "PPI Crude Materials",
    "PPIFES": "PPI Final Demand Services",

    # GDP Deflator
    "GDPDEF": "GDP Implicit Price Deflator",

    # Trimmed Mean Inflation Measures
    "TRMMEANCPIM094SFRBCLE": "Trimmed Mean CPI 16pct",
    "TRMMEANCPIM157SFRBCLE": "Trimmed Mean CPI Annualized",
    "PCETRIM1M158SFRBDAL": "Trimmed Mean PCE 1M",
    "PCETRIM6M680SFRBDAL": "Trimmed Mean PCE 6M",

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
}

# ==========================================
# BLS SERIES
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
# BEA TABLES
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
# NY FED (No API key needed)
# ==========================================

NYFED_RATES = {
    "SOFR": "Secured Overnight Financing Rate",
    "EFFR": "Effective Federal Funds Rate",
    "OBFR": "Overnight Bank Funding Rate",
    "TGCR": "Tri-Party General Collateral Rate",
    "BGCR": "Broad General Collateral Rate",
}

# ==========================================
# OFR (No API key needed)
# ==========================================

OFR_SERIES = {
    "FNYR-SOFR-A": "OFR_SOFR",
    "FNYR-EFFR-A": "OFR_EFFR",
    "FNYR-OBFR-A": "OFR_OBFR",
    "FNYR-TGCR-A": "OFR_TGCR",
    "FNYR-BGCR-A": "OFR_BGCR",
    "MMF-MMF_TOT-M": "MMF_Total_Assets",
    "MMF-MMF_RP_TOT-M": "MMF_Repo_Total",
    "MMF-MMF_RP_wFR-M": "MMF_Repo_with_Fed",
    "MMF-MMF_T_TOT-M": "MMF_Treasury_Total",
    "NYPD-PD_RP_TOT-A": "PD_Repo_Total",
    "NYPD-PD_RRP_TOT-A": "PD_ReverseRepo_Total",
    "NYPD-PD_RP_T_TOT-A": "PD_Repo_Treasury_Total",
}

OFR_FSI_COLUMNS = {
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

# ==========================================
# FETCH SETTINGS
# ==========================================

FETCH_CONFIG = {
    "max_retries": 3,
    "retry_delay_base": 2,  # Exponential backoff base
    "timeout": 30,
    "rate_limit_delay": 0.1,  # Delay between requests
    "fred_category_limit": 50,  # Series per category
    "bls_start_year": 1990,
    "bea_start_year": 2000,
    "nyfed_start_date": "2018-04-03",
    "parallel_workers": 5,  # For parallel fetching
}

# ==========================================
# QUALITY THRESHOLDS
# ==========================================

QUALITY_CONFIG = {
    "min_observations": 5,  # Skip series with fewer obs
    "max_missing_pct": 0.5,  # Flag if >50% missing
    "outlier_z_threshold": 10,  # Flag extreme values
    "stale_days_daily": 7,  # Daily series (weekends + holidays)
    "stale_days_weekly": 21,  # Weekly series
    "stale_days_monthly": 75,  # Monthly series (2.5 months buffer)
    "stale_days_quarterly": 140,  # Quarterly series (GDP, etc.)
    "stale_days_annual": 400,  # Annual series
}
