"""
LIGHTHOUSE MACRO - PILLAR SERIES MAPPING
=========================================
Canonical mapping of series_id values to the 12 Diagnostic Dozen pillars.
This is the single source of truth for which series belong to which pillar.

Series CAN appear in multiple pillars (by design).
Crypto series (DEFI_*, CRYPTO_*, CHAIN_*, STABLE_*) stay master-only unless
explicitly assigned.

Usage:
    from lighthouse.pillar_mapping import PILLAR_SERIES, PILLAR_DEFS
    from lighthouse.pillar_mapping import get_pillar_series, get_unmapped_series
"""

# ==========================================
# PILLAR DEFINITIONS
# ==========================================

PILLAR_DEFS = {
    1: {
        "name": "Labor",
        "code": "Labor",
        "engine": "Macro Dynamics",
        "indices": ["LPI", "LFI", "LDI"],
    },
    2: {
        "name": "Prices",
        "code": "Prices",
        "engine": "Macro Dynamics",
        "indices": ["PCI"],
    },
    3: {
        "name": "Growth",
        "code": "Growth",
        "engine": "Macro Dynamics",
        "indices": ["GCI"],
    },
    4: {
        "name": "Housing",
        "code": "Housing",
        "engine": "Macro Dynamics",
        "indices": ["HCI"],
    },
    5: {
        "name": "Consumer",
        "code": "Consumer",
        "engine": "Macro Dynamics",
        "indices": ["CCI"],
    },
    6: {
        "name": "Business",
        "code": "Business",
        "engine": "Macro Dynamics",
        "indices": ["BCI"],
    },
    7: {
        "name": "Trade",
        "code": "Trade",
        "engine": "Macro Dynamics",
        "indices": ["TCI"],
    },
    8: {
        "name": "Government",
        "code": "Government",
        "engine": "Monetary Mechanics",
        "indices": ["GCI_Gov"],
    },
    9: {
        "name": "Financial",
        "code": "Financial",
        "engine": "Monetary Mechanics",
        "indices": ["FCI", "CLG"],
    },
    10: {
        "name": "Plumbing",
        "code": "Plumbing",
        "engine": "Monetary Mechanics",
        "indices": ["LCI"],
    },
    11: {
        "name": "Structure",
        "code": "Structure",
        "engine": "Market Structure",
        "indices": ["CDI", "CFI", "CTI", "CVI"],
    },
    12: {
        "name": "Sentiment",
        "code": "Sentiment",
        "engine": "Market Structure",
        "indices": ["SLI", "SLI_MCAP", "SLI_ROC_30D", "SLI_ROC_90D_ANN"],
    },
}

# Master-level indices that go into EVERY pillar DB
MASTER_INDICES = [
    "MRI",
    "ENSEMBLE_RISK",
    "BASE_REC_PROB",
    "WARNING_LEVEL",
    "ALLOC_MULTIPLIER",
]

# ==========================================
# PILLAR SERIES MAPPING
# ==========================================
# Keys are pillar numbers, values are lists of series_id values
# exactly as stored in the master DB.

PILLAR_SERIES = {

    # ------------------------------------------------------------------
    # PILLAR 1: LABOR
    # ------------------------------------------------------------------
    1: [
        # Headline Labor
        "UNRATE", "U6RATE", "U1RATE", "U2RATE",
        "CIVPART", "PAYEMS",
        "ICSA", "CCSA",

        # JOLTS Rates
        "JTS1000JOR", "JTS1000QUR", "JTS1000HIR",
        "JTSQUR", "JTSHIR", "JTSTSR",

        # JOLTS Levels
        "JTSJOL", "JTSHIL", "JTSQUL", "JTSLDL", "JTSTSL",

        # JOLTS Sector Quits
        "JTS3000QUR", "JTS2300QUR", "JTS4400QUR",
        "JTS540099QUR", "JTS7000QUR", "JTS6200QUR",

        # Unemployment Duration
        "UNEMPLOY", "UEMPLT5", "UEMP5TO14", "UEMP15T26",
        "UEMP27OV", "UEMPMEAN", "UEMPMED",

        # Unemployment Reasons
        "LNS13023621", "LNS13023705", "LNS13023557", "LNS13023569",

        # Demographic Unemployment
        "LNS14000001", "LNS14000002", "LNS14000003",
        "LNS14000006", "LNS14000009",
        "LNS14000012", "LNS14000013",
        "LNS14000024", "LNS14000025", "LNS14000036",
        "LNS14024230", "LNS14024887",
        "LNS14000060",  # Prime age 25-54
        "LNU04032183",  # Asian

        # Education Unemployment
        "LNS14027659", "LNS14027660", "LNS14027689", "LNS14027662",

        # LFPR
        "LNS11300001", "LNS11300002", "LNS11300003",
        "LNS11300060", "LNS11324230",
        "CLF16OV",
        "LRAC25MAUSM156S", "LRAC25FEUSM156S",

        # Employment Quality
        "LNS12500000", "LNS12600000", "LNS12026620",
        "LNS12032194",  # Part time for economic reasons
        "NILFWJN", "LNU05026645",

        # Industry Employment
        "TEMPHELPS", "USCONS", "USTRADE", "USPBS",
        "USFIRE", "USINFO", "USLAH", "USGOVT",
        "CES6562000001", "MANEMP", "USPRIV",

        # Hours Worked
        "AWHAETP", "AWHMAN", "AWOTMAN", "AWHI",

        # Wages
        "CES0500000003", "CES0500000030",
        "AHETPI", "LES1252881600Q",
        "ECIWAG", "ECIALLCIV",
        "CIU2010000000000I",

        # Atlanta Fed Wage Growth
        "FRBATLWGT12MMUMHGO", "FRBATLWGT3MMAUMHWGO",
        "FRBATLWGT12MMUMHWGJST", "FRBATLWGT12MMUMHWGJSW",
        "FRBATLWGT12MMUMHWGWD1WP", "FRBATLWGT12MMUMHWGWD76WP",

        # Productivity & Unit Labor Costs
        "OPHNFB", "PRS85006092", "ULCNFB",
        "COMPNFB", "HOANBS",

        # Recession Confirmation
        "SAHMREALTIME", "IHLIDXUS", "IURSA",

        # ADP
        "ADPMNUSNERSA",

        # BLS Series
        "BLS_CES0000000001", "BLS_CES0500000003", "BLS_CES0500000008",
        "BLS_CES1000000001", "BLS_CES2000000001", "BLS_CES3000000001",
        "BLS_CES4000000001", "BLS_CES5000000001", "BLS_CES5500000001",
        "BLS_CES6000000001", "BLS_CES6500000001", "BLS_CES7000000001",
        "BLS_CES8000000001", "BLS_CES9000000001",
        "BLS_LNS11300000", "BLS_LNS11300060",
        "BLS_LNS12300000", "BLS_LNS13327709", "BLS_LNS14000000",
        "BLS_JTS000000000000000HIR", "BLS_JTS000000000000000JOR",
        "BLS_JTS000000000000000QUR", "BLS_JTS000000000000000TSR",

        # Employment Cost Index
        "COMPHAI",

        # Employment Cost Index (FRED category: Employment_Cost_Index source)
        "ECIALLCIV", "ECIWAG",
    ],

    # ------------------------------------------------------------------
    # PILLAR 2: PRICES
    # ------------------------------------------------------------------
    2: [
        # CPI Headline & Core
        "CPIAUCSL", "CPILFESL", "CPIAUCNS",

        # CPI Aggregates
        "CUSR0000SACL1E", "CUSR0000SAS", "CUSR0000SASLE",
        "CUSR0000SASL2RS", "CUSR0000SAC", "CUSR0000SACL1",
        "CUSR0000SAS2RS",

        # CPI Services Detail
        "CUSR0000SEMD", "CUSR0000SEMC",

        # CPI Goods Detail
        "CPIAPPSL", "CPIUFDSL", "CPIENGSL", "CPIMEDSL",
        "CUSR0000SACE",

        # CPI Components - Shelter
        "CUSR0000SAH1", "CUSR0000SEHA", "CUSR0000SEHC",
        "CPIHOSSL",

        # CPI Components - Food & Energy
        "CUSR0000SAF11", "CUSR0000SEFV",
        "CUSR0000SAH2", "CUSR0000SETB01",
        "CUSR0000SEHF01", "CUSR0000SEHF02",

        # CPI Components - Medical
        "CUSR0000SAM1", "CUSR0000SAM2",

        # CPI Components - Transportation & Vehicles
        "CUSR0000SAS4", "CUSR0000SETA02", "CUSR0000SETA01",
        "CUSR0000SETC", "CUSR0000SETG01",

        # CPI Components - Other
        "CUSR0000SAE1", "CUSR0000SAE2",
        "CUSR0000SEHE", "CUSR0000SEEB",
        "CUSR0000SEGA", "CUSR0000SEHF",
        "CUSR0000SS62031", "CUSR0000SEEE01", "CUSR0000SEHB",

        # CPI NSA variants
        "CUUR0000SACL1E", "CUUR0000SAF11", "CUUR0000SAF112",
        "CUUR0000SAF113", "CUUR0000SAS", "CUUR0000SEFJ",
        "CUUR0000SEFV", "CUUR0000SEGC", "CUUR0000SETD",

        # CPI Regional
        "CUURA104SA0", "CUURA211SA0", "CUURA212SA0",
        "CUURA213SA0", "CUURA214SA0", "CUURA424SA0",
        "CUURA425SA0", "CUURA433SA0",

        # CPI Major Aggregates
        "CPIRECSL", "CPITRNSL",

        # PCE Price Indices
        "PCEPI", "PCEPILFE",
        "PCECTPI", "PCECTPICTH", "PCECTPICTL", "PCECTPICTLLR",
        "PCECTPICTM", "PCECTPICTMLR", "PCECTPIMD", "PCECTPIMDLR",
        "PCECTPIRH", "PCECTPIRHLR", "PCECTPIRLLR",
        "PCECTPIRM", "PCECTPIRMLR",
        "JCXFE", "JCXFECTH", "JCXFECTL", "JCXFECTM",
        "JCXFEMD", "JCXFERH", "JCXFERM",

        # PCE Components (price relevant)
        "DGDSRG3M086SBEA", "DSERRG3M086SBEA",
        "IA001260M", "IA001260Q",
        "IA001176M", "IA001176Q",

        # Alternative Inflation Measures
        "MEDCPIM094SFRBCLE", "MEDCPIM157SFRBCLE",
        "MEDCPIM158SFRBCLE", "MEDCPIM159SFRBCLE",
        "CORESTICKM157SFRBATL", "CORESTICKM158SFRBATL",
        "CORESTICKM159SFRBATL", "CORESTICKM679SFRBATL",
        "COREFLEXCPIM157SFRBATL", "COREFLEXCPIM159SFRBATL",
        "STICKCPIM157SFRBATL", "STICKCPIM158SFRBATL",
        "STICKCPIM159SFRBATL", "STICKCPIM679SFRBATL",
        "FLEXCPIM157SFRBATL", "FLEXCPIM159SFRBATL",
        "FLEXCPIM679SFRBATL",
        "STICKCPIXSHLTRM157SFRBATL", "STICKCPIXSHLTRM159SFRBATL",
        "STICKCPIXSHLTRM679SFRBATL",

        # Trimmed Mean Measures
        "TRMMEANCPIM094SFRBCLE", "TRMMEANCPIM157SFRBCLE",
        "TRMMEANCPIM158SFRBCLE", "TRMMEANCPIM159SFRBCLE",
        "PCETRIM12M159SFRBDAL", "PCETRIM1M158SFRBDAL",
        "PCETRIM6M680SFRBDAL",

        # PPI Pipeline
        "PPIFIS", "PPIDSS", "PPIFGS", "PPIFDF",
        "PPIIDC", "PPIITM",
        "WPSFD4131", "WPUFD49116", "WPSFD41312",
        "PPIACO", "PPICPE", "PPICRM", "PPIFES", "PPIFDS",

        # GDP Deflator
        "GDPDEF",

        # Inflation Expectations
        "MICH",
        "EXPINF1YR", "EXPINF2YR", "EXPINF5YR",
        "EXPINF10YR", "EXPINF30YR",

        # Breakevens & Real Rates (inflation relevant)
        "T10YIE", "T5YIE", "T5YIFR",
        "DFII5", "DFII10",

        # Commodities (inflation pass-through)
        "DCOILWTICO",

        # BLS Price Series
        "BLS_CUUR0000SA0", "BLS_CUUR0000SA0L1E", "BLS_CUUR0000SA0E",
        "BLS_CUUR0000SAH1", "BLS_CUUR0000SAS", "BLS_CUUR0000SAF1",
        "BLS_WPSFD4", "BLS_WPUFD49104",

        # International CPI (for context)
        "FPCPITOTLZGEMU", "FPCPITOTLZGEUU",
        "FPCPITOTLZGHIC", "FPCPITOTLZGLCN", "FPCPITOTLZGOED",

        # Wages (inflation input)
        "CES0500000003", "AHETPI",
        "FRBATLWGT12MMUMHGO",

        # Zillow Rents (CPI Shelter leading indicator)
        "ZILLOW_ZORI_NATIONAL",

        # Import Prices (inflation pass-through)
        "IR", "IQ",
    ],

    # ------------------------------------------------------------------
    # PILLAR 3: GROWTH
    # ------------------------------------------------------------------
    3: [
        # GDP
        "GDP", "GDPC1", "GDPC96", "GDI",
        "GDPA", "GDPCA", "GNP", "GNPA", "GNPC96", "GNPCA",
        "GDPNOW", "GDPPOT", "NGDPPOT",
        "A191RL1Q225SBEA", "A191RL1A225NBEA",
        "A191RO1Q156NBEA", "A191RP1Q027SBEA", "A191RP1A027NBEA",
        "GDPC1CTM", "GDPC1CTMLR", "GDPC1MD", "GDPC1MDLR",

        # GDP Components
        "GPDI", "GCE", "FGCE",
        "PCEC", "PCEC96",
        "PNFI", "PRFI",
        "CBI",
        "NETEXP",
        "A713RX1Q020SBEA",  # Real Final Sales to Domestic Purchasers
        "FINSLC1",  # Real Final Sales of Domestic Product
        "PCES",

        # PCE Real
        "PCEDGC96", "PCENDC96", "PCESC96", "PCESVC96",
        "PCDGCC96", "PCNDGC96",

        # Industrial Production
        "INDPRO",
        "IPB50001SQ", "IPB50001A", "IPB50001N",
        "IPBUSEQ", "IPCONGD", "IPDMAT",
        "CUMFNS",

        # Capacity Utilization
        "TCU", "MCUMFN",

        # Retail Sales
        "RSAFS", "RSXFS", "RSXFSN",

        # Real Income/Consumption
        "DSPIC96", "DPIC96",

        # Employment (growth relevant)
        "PAYEMS", "ADPMNUSNERSA", "USPRIV",

        # Business Surveys / Coincident
        "BSCICP02USM460S", "BSCICP03USM665S",
        "CFNAIMA3",

        # Durable Goods
        "DGORDER", "ADXTNO", "NEWORDER", "AMTMNO",
        "ACDGNO", "ANDENO", "AMNMNO", "ANXAVS",

        # Inventories
        "ISRATIO", "MNFCTRIRSA", "RETAILIRSA",
        "WHLSLRIRSA", "BUSINV", "RETAILIMSA",
        "INVCMRMTSPL", "CMRMTSPL",

        # Freight & Logistics
        "TRUCKD11", "RAILFRTINTERMODALD11", "RAILFRTCARLOADSD11",
        "TSIFRGHT", "TSITTL", "FRGSHPUSM649NCIS",

        # Auto Sales
        "ALTSALES", "LAUTOSA", "LTOTALNSA",
        "HTRUCKSSAAR", "TOTALSA", "AISRSA",

        # Leading Indicators
        "USSLIND",

        # Productivity
        "OPHNFB", "PRS30006092",

        # Housing Starts (growth component)
        "HOUST", "HOUST1F",

        # Regional Fed Surveys
        "GACDISA066MSFRBNY", "GACDFSA066MSFRBPHI",
        "BACTSAMFRBDAL",

        # Retail Detail
        "MRTSSM441USS",

        # E-Commerce
        "ECOMPCTSA",

        # Nowcasts
        "BBKMCOIX", "BBKMCY", "BBKMGDP", "BBKMLEIX",
        "WEI",

        # TradingView Business (growth relevant)
        "TV_USBCOI",  # ISM Mfg PMI
        "TV_USISMMP",  # ISM Mfg Production
        "TV_USLEI",  # LEI

        # BEA GDP Components
        "BEA_GDP_Components_Gross_domestic_product",
        "BEA_GDP_Components_Personal_consumption_expenditures",
        "BEA_GDP_Components_Gross_private_domestic_investment",
        "BEA_GDP_Components_Fixed_investment",
        "BEA_GDP_Components_Nonresidential",
        "BEA_GDP_Components_Structures",
        "BEA_GDP_Components_Equipment",
        "BEA_GDP_Components_Intellectual_property_products",
        "BEA_GDP_Components_Residential",
        "BEA_GDP_Components_Change_in_private_inventories",
        "BEA_GDP_Components_Net_exports_of_goods_and_services",
        "BEA_GDP_Components_Exports",
        "BEA_GDP_Components_Imports",
        "BEA_GDP_Components_Government_consumption_expenditures_and_gross_investment",
        "BEA_GDP_Components_Federal",
        "BEA_GDP_Components_National_defense",
        "BEA_GDP_Components_Nondefense",
        "BEA_GDP_Components_State_and_local",
        "BEA_GDP_Components_Goods",
        "BEA_GDP_Components_Services",
        "BEA_GDP_Components_Durable_goods",
        "BEA_GDP_Components_Nondurable_goods",

        # BEA Real GDP Growth
        "BEA_Real_GDP_Growth_Gross_domestic_product",
        "BEA_Real_GDP_Growth_Gross_domestic_product,_current_dollars",
        "BEA_Real_GDP_Growth_Personal_consumption_expenditures",
        "BEA_Real_GDP_Growth_Goods",
        "BEA_Real_GDP_Growth_Durable_goods",
        "BEA_Real_GDP_Growth_Nondurable_goods",
        "BEA_Real_GDP_Growth_Services",
        "BEA_Real_GDP_Growth_Gross_private_domestic_investment",
        "BEA_Real_GDP_Growth_Fixed_investment",
        "BEA_Real_GDP_Growth_Nonresidential",
        "BEA_Real_GDP_Growth_Structures",
        "BEA_Real_GDP_Growth_Equipment",
        "BEA_Real_GDP_Growth_Intellectual_property_products",
        "BEA_Real_GDP_Growth_Residential",
        "BEA_Real_GDP_Growth_Exports",
        "BEA_Real_GDP_Growth_Imports",
        "BEA_Real_GDP_Growth_Government_consumption_expenditures_and_gross_investment",
        "BEA_Real_GDP_Growth_Federal",
        "BEA_Real_GDP_Growth_National_defense",
        "BEA_Real_GDP_Growth_Nondefense",
        "BEA_Real_GDP_Growth_State_and_local",

        # BEA GDI
        "BEA_GDI_Gross_domestic_income",
        "BEA_GDI_Compensation_of_employees,_paid",
        "BEA_GDI_Wages_and_salaries",
        "BEA_GDI_Net_operating_surplus",
        "BEA_GDI_Statistical_discrepancy",
    ],

    # ------------------------------------------------------------------
    # PILLAR 4: HOUSING
    # ------------------------------------------------------------------
    4: [
        # Housing Starts & Permits
        "HOUST", "HOUST1F", "HOUST5F",
        "PERMIT", "PERMIT1", "PERMITNSA",
        "COMPUTSA", "UNDCONTSA",

        # Regional Starts
        "HOUSTNE", "HOUSTMW", "HOUSTS", "HOUSTW",

        # Home Sales
        "HSN1F", "EXHOSLUSM495S",
        "EXHOSLUSNEM495S", "EXHOSLUSMWM495S",
        "EXHOSLUSSOM495S", "EXHOSLUSWTM495S",

        # Home Prices
        "CSUSHPINSA", "SPCS20RSA", "SPCS10RSA",
        "MSPUS", "MSPNHSUS",
        "ASPUS", "ASPNHSUS",
        "USSTHPI", "HPIPONM226S",

        # Supply
        "MSACSR", "MNMFS",
        "HOSINVUSM495N", "HSFINVUSM495N",
        "HOSSUPUSM673N", "HSFSUPUSM673N",

        # Median Prices
        "HOSMEDUSM052N",
        "HOSMEDUSMWM052N", "HOSMEDUSNEM052N",
        "HOSMEDUSSOM052N", "HOSMEDUSWTM052N",
        "MEDLISPRIUS", "MEDLISPRIPERSQUFEEUS",
        "MEDSQUFEEUS",
        "MEDLISPRI12420", "MEDLISPRI19100",

        # Days on Market
        "MEDDAYONMARUS",
        "MEDDAYONMAR19100", "MEDDAYONMAR38060",

        # Listings
        "NEWLISCOUUS", "PENLISCOUUS",

        # Active Listings (MSAs)
        "ACTLISCOUUS",
        "ACTLISCOU12060", "ACTLISCOU12420", "ACTLISCOU14460",
        "ACTLISCOU16740", "ACTLISCOU16980", "ACTLISCOU19100",
        "ACTLISCOU19740", "ACTLISCOU26420", "ACTLISCOU27260",
        "ACTLISCOU29820", "ACTLISCOU34980", "ACTLISCOU36740",
        "ACTLISCOU37980", "ACTLISCOU38060", "ACTLISCOU39580",
        "ACTLISCOU41860", "ACTLISCOU42660", "ACTLISCOU45300",
        "ACTLISCOU47900",

        # Mortgage Rates
        "MORTGAGE30US", "MORTGAGE15US",
        "MORTGAGE5US", "MORTGAGE1US",
        "FHA30",

        # Mortgage Details
        "MORTMRGN1US", "MORTMRGN5US",
        "MORTPTS15US", "MORTPTS1US", "MORTPTS30US", "MORTPTS5US",

        # Housing Affordability
        "FIXHAI",
        "BOAAAHORUSQ156N",  # Homeownership Affordability

        # Ownership & Vacancy
        "RHORUSQ156N", "RHVRUSQ156N", "RRVRUSQ156N",
        "RSAHORUSQ156S",
        "EVACANTUSQ176N",
        "USHOWN", "USHVAC", "USRVAC",

        # Housing Credit
        "BOGZ1FA893065015Q",
        "HHMSDODNS",
        "HNONWPDPI",

        # Residential Construction Spending
        "TLRESCONS",
        "TV_USCONSTS",

        # Shelter Inflation
        "CUSR0000SAH1", "CUSR0000SEHA", "CUSR0000SEHC",
        "CPIHOSSL",

        # Mortgage Delinquency
        "DRSFRMACBS",

        # BIS Housing Prices
        "QUSR628BIS", "QUSR368BIS",

        # Rental/Ownership Cost
        "EOWNOCCUSQ176N", "ERENTUSQ176N", "ERNTOCCUSQ176N",
        "ETOTALUSQ176N",

        # Construction Employment
        "CES2000000003",

        # Zillow
        "ZILLOW_ZHVI_NATIONAL",
        "ZILLOW_ZHVI_ATLANTA", "ZILLOW_ZHVI_BALTIMORE",
        "ZILLOW_ZHVI_BOSTON", "ZILLOW_ZHVI_CHICAGO",
        "ZILLOW_ZHVI_DALLAS", "ZILLOW_ZHVI_DENVER",
        "ZILLOW_ZHVI_DETROIT", "ZILLOW_ZHVI_HOUSTON",
        "ZILLOW_ZHVI_LOS_ANGELES", "ZILLOW_ZHVI_MIAMI",
        "ZILLOW_ZHVI_MINNEAPOLIS", "ZILLOW_ZHVI_NEW_YORK",
        "ZILLOW_ZHVI_PHILADELPHIA", "ZILLOW_ZHVI_PHOENIX",
        "ZILLOW_ZHVI_RIVERSIDE", "ZILLOW_ZHVI_SAN_DIEGO",
        "ZILLOW_ZHVI_SAN_FRANCISCO", "ZILLOW_ZHVI_SEATTLE",
        "ZILLOW_ZHVI_TAMPA", "ZILLOW_ZHVI_WASHINGTON",
        "ZILLOW_ZORI_NATIONAL",
        "ZILLOW_ZORI_ATLANTA", "ZILLOW_ZORI_BALTIMORE",
        "ZILLOW_ZORI_BOSTON", "ZILLOW_ZORI_CHICAGO",
        "ZILLOW_ZORI_DALLAS", "ZILLOW_ZORI_DENVER",
        "ZILLOW_ZORI_DETROIT", "ZILLOW_ZORI_HOUSTON",
        "ZILLOW_ZORI_LOS_ANGELES", "ZILLOW_ZORI_MIAMI",
        "ZILLOW_ZORI_MINNEAPOLIS", "ZILLOW_ZORI_NEW_YORK",
        "ZILLOW_ZORI_PHILADELPHIA", "ZILLOW_ZORI_PHOENIX",
        "ZILLOW_ZORI_RIVERSIDE", "ZILLOW_ZORI_SAN_DIEGO",
        "ZILLOW_ZORI_SAN_FRANCISCO", "ZILLOW_ZORI_SEATTLE",
        "ZILLOW_ZORI_TAMPA", "ZILLOW_ZORI_WASHINGTON",

        # TradingView Housing
        "TV_USHMI", "TV_USPIND", "TV_USMRI",
        "TV_USPHSIYY", "TV_USPHSIMM",
        "TV_USPRR", "TV_USAMS",
        "TV_USEHS", "TV_USMAPL", "TV_USMMI", "TV_USMOR",

        # Mortgage Origination Metrics
        "OBMMIC15YF", "OBMMIC30YF",
        "OBMMIC30YFLVGT80FB680A699", "OBMMIC30YFLVGT80FB700A719",
        "OBMMIC30YFLVGT80FB720A739", "OBMMIC30YFLVGT80FGE740",
        "OBMMIC30YFLVGT80FLT680",
        "OBMMIC30YFLVLE80FB680A699", "OBMMIC30YFLVLE80FB700A719",
        "OBMMIC30YFLVLE80FB720A739", "OBMMIC30YFLVLE80FGE740",
        "OBMMIC30YFLVLE80FLT680",
        "OBMMIC30YFNA",
        "OBMMIFHA30YF", "OBMMIJUMBO30YF",
        "OBMMIUSDA30YF", "OBMMIVA30YF",

        # Mortgage Market Rates
        "MORTG", "WMORTG", "WRMORTG",
    ],

    # ------------------------------------------------------------------
    # PILLAR 5: CONSUMER
    # ------------------------------------------------------------------
    5: [
        # PCE
        "PCE", "PCEC", "PCEC96",
        "PCDG", "PCND", "PCESV",
        "PCEDG", "PCEND", "PCES",
        "PCEDGC96", "PCENDC96", "PCESC96", "PCESVC96",
        "PCDGCC96", "PCNDGC96",
        "DGDSRC1",

        # Personal Income & Saving
        "PI", "PINCOME", "DPI", "DPIC96", "DSPIC96",
        "PSAVE", "PSAVERT",
        "A229RX0", "A229RX0Q048SBEA", "A229RX0A048NBEA",
        "A229RC0", "A229RC0Q052SBEA", "A229RC0A052NBEA",
        "A576RC1",  # Wages & Salaries

        # Transfer Receipts
        "A063RC1",
        "PCTR",

        # Retail Sales
        "RSAFS", "RSXFS", "RSFSXMV",
        "RSMVPD", "RSFSDP", "RSGASS",
        "RSBMGESD", "RSGCSN", "RSNSR",
        "RSHPCS", "RSSGHBMS", "RSFHFS",
        "RSEAS", "RSCCAS",
        "RRSFS",

        # Consumer Credit
        "TOTALSL", "REVOLSL", "NONREVSL",

        # Debt Service
        "TDSP", "FODSP", "CDSP",
        "HDTGPDUSQ163N",

        # Delinquencies (consumer)
        "DRCCLACBS",  # Credit Card
        "DRCLACBS",  # Consumer Loans

        # Consumer Sentiment
        "UMCSENT",

        # Credit Card Interest Rate
        "TERMCBCCALLNS",

        # Wealth
        "BOGZ1FL192090005Q",

        # Auto Sales (consumer spending)
        "ALTSALES", "TOTALSA",

        # BEA Personal Income
        "BEA_Personal_Income_Personal_income",
        "BEA_Personal_Income_Compensation_of_employees",
        "BEA_Personal_Income_Wages_and_salaries",
        "BEA_Personal_Income_Supplements_to_wages_and_salaries",
        "BEA_Personal_Income_Proprietors'_income_with_inventory_valuation_and_capital_consumption_adjustments",
        "BEA_Personal_Income_Personal_income_receipts_on_assets",
        "BEA_Personal_Income_Personal_interest_income",
        "BEA_Personal_Income_Personal_dividend_income",
        "BEA_Personal_Income_Personal_current_transfer_receipts",
        "BEA_Personal_Income_Government_social_benefits_to_persons",
        "BEA_Personal_Income_Social_security",
        "BEA_Personal_Income_Medicare",
        "BEA_Personal_Income_Medicaid",
        "BEA_Personal_Income_Unemployment_insurance",
        "BEA_Personal_Income_Veterans'_benefits",
        "BEA_Personal_Income_Less:_Personal_current_taxes",
        "BEA_Personal_Income_Equals:_Disposable_personal_income",
        "BEA_Personal_Income_Less:_Personal_outlays",
        "BEA_Personal_Income_Personal_consumption_expenditures",
        "BEA_Personal_Income_Personal_interest_payments",
        "BEA_Personal_Income_Personal_current_transfer_payments",
        "BEA_Personal_Income_Equals:_Personal_saving",
        "BEA_Personal_Income_Personal_saving_as_a_percentage_of_disposable_personal_income",
        "BEA_Personal_Income_Disposable_personal_income,_current_dollars",
        "BEA_Personal_Income_Disposable_personal_income,_chained_(2017)_dollars",
        "BEA_Personal_Income_Current_dollars",
        "BEA_Personal_Income_Chained_(2017)_dollars",
        "BEA_Personal_Income_Population_(midperiod,_thousands)",

        # BEA PCE Components
        "BEA_PCE_Components_Personal_consumption_expenditures_(PCE)",
        "BEA_PCE_Components_Goods",
        "BEA_PCE_Components_Durable_goods",
        "BEA_PCE_Components_Nondurable_goods",
        "BEA_PCE_Components_Services",
        "BEA_PCE_Components_Housing_and_utilities",
        "BEA_PCE_Components_Health_care",
        "BEA_PCE_Components_Food_and_beverages_purchased_for_off-premises_consumption",
        "BEA_PCE_Components_Food_services_and_accommodations",
        "BEA_PCE_Components_Financial_services_and_insurance",
        "BEA_PCE_Components_Recreation_services",
        "BEA_PCE_Components_Transportation_services",
        "BEA_PCE_Components_Clothing_and_footwear",
        "BEA_PCE_Components_Motor_vehicles_and_parts",
        "BEA_PCE_Components_Furnishings_and_durable_household_equipment",
        "BEA_PCE_Components_Recreational_goods_and_vehicles",
        "BEA_PCE_Components_Other_durable_goods",
        "BEA_PCE_Components_Other_nondurable_goods",
        "BEA_PCE_Components_Other_services",
        "BEA_PCE_Components_Energy_goods_and_services",
        "BEA_PCE_Components_Gasoline_and_other_energy_goods",
        "BEA_PCE_Components_Housing",
        "BEA_PCE_Components_Market-based_PCE",
        "BEA_PCE_Components_Market-based_PCE_excluding_food_and_energy",
        "BEA_PCE_Components_PCE_excluding_food_and_energy",
        "BEA_PCE_Components_PCE_excluding_food,_energy,_and_housing",
        "BEA_PCE_Components_PCE_services_excluding_energy_and_housing",
        "BEA_PCE_Components_Household_consumption_expenditures_(for_services)",
        "BEA_PCE_Components_Gross_output_of_nonprofit_institutions",
        "BEA_PCE_Components_Less:_Receipts_from_sales_of_goods_and_services_by_nonprofit_institutions",
        "BEA_PCE_Components_Final_consumption_expenditures_of_nonprofit_institutions_serving_households_(NPIS",

        # Retail Detail (additional)
        "MRTSSM44X72USS", "RETAILSMSA",
        "MRTSSM4453USN", "MRTSSM44112USN",
        "MRTSSM442USN", "MRTSSM7225USN",
        "RSGCS", "S4248SM144NCEN",
        "MRTSSM441USS",
    ],

    # ------------------------------------------------------------------
    # PILLAR 6: BUSINESS
    # ------------------------------------------------------------------
    6: [
        # Durable Goods Orders
        "DGORDER", "ADXTNO", "NEWORDER", "AMTMNO",
        "ACDGNO", "ANDENO", "AMNMNO", "ANXAVS",
        "ACOGNO", "A34SNO",

        # Industrial Production
        "INDPRO", "CUMFNS",
        "IPB50001SQ", "IPB50001A", "IPB50001N",
        "IPBUSEQ", "IPCONGD", "IPDMAT",

        # Capacity Utilization
        "TCU", "MCUMFN",
        "CAPUTLB50001SQ",

        # Industrial Production Detail
        "IPB52300S", "IPB53122S", "IPB54100S",
        "IPDCONGD", "IPDMAN",

        # Capacity Utilization Detail
        "CAPUTLG21S", "CAPUTLG2211S", "CAPUTLG325S",
        "CAPUTLG3311A2S", "CAPUTLG333S", "CAPUTLG3344S",
        "CAPUTLG33611SQ", "CAPUTLG3361T3S", "CAPUTLG3364T9S",
        "CAPB00004S", "CAPB50001S",

        # Business Investment
        "PNFI", "PRFI",
        "GPDI",

        # Inventories
        "ISRATIO", "MNFCTRIRSA", "BUSINV",
        "INVCMRMTSPL", "CMRMTSPL",
        "FINSAL", "FINSALESDOMPRIVPUR",

        # Business Loans
        "BUSLOANS", "TOTCI",

        # Loan Officer Survey (business)
        "DRTSCILM",

        # Productivity
        "OPHNFB", "PRS85006092", "ULCNFB",
        "COMPNFB", "HOANBS",
        "PRS30006092",

        # Corporate Profits
        "BEA_Corporate_Profits_Corporate_profits_with_IVA_and_CCAdj",
        "BEA_Corporate_Profits_Corporate_profits_with_IVA",
        "BEA_Corporate_Profits_Profits_before_tax_(without_IVA_and_CCAdj)",
        "BEA_Corporate_Profits_Profits_after_tax_(without_IVA_and_CCAdj)",
        "BEA_Corporate_Profits_Profits_after_tax_with_IVA_and_CCAdj",
        "BEA_Corporate_Profits_Taxes_on_corporate_income",
        "BEA_Corporate_Profits_Undistributed_profits_with_IVA_and_CCAdj",
        "BEA_Corporate_Profits_Undistributed_profits_(without_IVA_and_CCAdj)",
        "BEA_Corporate_Profits_Net_dividends",
        "BEA_Corporate_Profits_Net_cash_flow_with_IVA",
        "BEA_Corporate_Profits_Inventory_valuation_adjustment",
        "BEA_Corporate_Profits_Capital_consumption_adjustment",
        "BEA_Corporate_Profits_Nonfarm",
        "BEA_Corporate_Profits_Farm",

        # Regional Fed Surveys
        "GACDISA066MSFRBNY", "GACDFSA066MSFRBPHI",
        "CFNAIMA3", "BACTSAMFRBDAL",

        # TradingView Business
        "TV_USBCOI",  # ISM Mfg PMI
        "TV_USISMMP",  # ISM Mfg Production
        "TV_USMNO",  # ISM Mfg New Orders
        "TV_USMEMP",  # ISM Mfg Employment
        "TV_USMPR",  # ISM Mfg Prices
        "TV_USNMBA",  # ISM Services Business Activity
        "TV_USNMNO",  # ISM Services New Orders
        "TV_USNMEMP",  # ISM Services Employment
        "TV_USNMPR",  # ISM Services Prices
        "TV_USRFMI",  # Richmond Fed
        "TV_USKFMI",  # KC Fed
        "TV_USLEI",  # LEI
        "TV_USBOI",  # OECD BCI
        "TV_USFO",  # Factory Orders

        # Manufacturing Employment
        "MANEMP",

        # Freight (business activity)
        "TRUCKD11", "TSIFRGHT", "TSITTL",

        # Leading Indicator
        "USSLIND",

        # Nowcasts
        "BBKMCOIX", "BBKMGDP",
    ],

    # ------------------------------------------------------------------
    # PILLAR 7: TRADE
    # ------------------------------------------------------------------
    7: [
        # Trade Balance
        "BOPGSTB", "BOPGTB", "BOPSTB",
        "BOPTEXP", "BOPTIMP",
        "NETEXP", "NETEXC",

        # Real Trade
        "IMPGS", "EXPGS",
        "EXPGSC1", "IMPGSC1",

        # Import/Export Price Indices
        "IR", "IQ",
        "IR1", "IR2", "IR4",
        "IREXPET",
        "IQAG", "IQEXAG",

        # Dollar Indices
        "DTWEXBGS", "DTWEXAFEGS", "DTWEXEMEGS",
        "RTWEXBGS",
        "TWEXBGSANL", "TWEXBGSMTH",
        "TWEXAFEGSANL", "TWEXAFEGSMTH",
        "TWEXEMEGSANL", "TWEXEMEGSMTH",

        # BIS Exchange Rates
        "RBUSBIS", "NBUSBIS", "RNUSBIS",

        # Bilateral Exchange Rates
        "DEXUSEU", "DEXJPUS", "DEXCHUS",
        "DEXUSUK", "DEXCAUS", "DEXMXUS",
        "DEXBZUS", "DEXKOUS", "DEXINUS",
        "DEXSZUS", "DEXSFUS", "DEXNOUS",
        "DEXSDUS", "DEXDNUS", "DEXSIUS",
        "DEXSLUS", "DEXTAUS", "DEXTHUS",
        "DEXUSAL", "DEXUSNZ", "DEXHKUS",
        "DEXMAUS", "DEXVZUS",

        # Bilateral Trade
        "EXPCH", "IMPCH", "EXPJP", "IMPJP",

        # Current Account
        "IEABC", "IEABCG", "IEABCS",
        "IEABCPI", "IEABCSI",
        "IEABCP", "IEABCPN",
        "IEAMGSN", "IEAXGS",

        # Trade Policy
        "EPUTRADE",

        # E-Commerce
        "ECOMSA", "ECOMPCTSA",

        # Foreign Holdings
        "FDHBFIN",

        # Retail (trade distribution)
        "RRSFS", "MRTSSM44X72USS", "RETAILSMSA",
        "MRTSSM4453USN", "MRTSSM44112USN",
        "MRTSSM442USN", "MRTSSM7225USN",
        "RSGCS", "S4248SM144NCEN",

        # Commodities (trade relevant)
        "DCOILWTICO",

        # Freight
        "TSIFRGHT", "TSITTL", "FRGSHPUSM649NCIS",
        "RAILFRTCARLOADSD11", "RAILFRTINTERMODALD11",
        "TRUCKD11",

        # TradingView Trade
        "TV_USBOT", "TV_USCA", "TV_USGTB",
        "TV_USIMP", "TV_USEXP",
        "TV_USCAG", "TV_USCURAG", "TV_USCURAS",
        "TV_USTA", "TV_USCF", "TV_USTICNLF",
        "TV_USFDI", "TV_USED",
        "TV_USTI", "TV_USTOT",
        "TV_USCOP", "TV_USWCOP", "TV_USOE",
        "TV_USGRES", "TV_USTR", "TV_USWES",

        # Discontinued but in DB
        "DTWEXB", "DTWEXO", "DTWEXM",
    ],

    # ------------------------------------------------------------------
    # PILLAR 8: GOVERNMENT
    # ------------------------------------------------------------------
    8: [
        # Federal Debt
        "GFDEBTN", "GFDEGDQ188S",

        # Federal Budget
        "MTSDS133FMS", "MTSO133FMS", "MTSR133FMS",
        "FYFSD",
        "FGEXPND", "FGRECPT",

        # Government Spending
        "GCE", "FGCE",
        "W068RCQ027SBEA",
        "A091RC1Q027SBEA",
        "A822RL1Q225SBEA",

        # Treasury Rates (term premium / fiscal dominance)
        "DGS1", "DGS2", "DGS5", "DGS10", "DGS20", "DGS30",
        "DGS1MO", "DGS3MO", "DGS6MO", "DGS3", "DGS7",
        "GS1", "GS2", "GS3", "GS5", "GS7",
        "GS10", "GS20", "GS30",
        "GS1M", "GS3M", "GS6M",

        # Weekly Treasury Rates
        "WGS1MO", "WGS1YR", "WGS2YR", "WGS3MO", "WGS3YR",
        "WGS5YR", "WGS6MO", "WGS7YR", "WGS10YR", "WGS20YR", "WGS30YR",

        # TIPS / Real Rates
        "DFII5", "DFII7", "DFII10", "DFII20", "DFII30",
        "WFII5", "WFII7", "WFII10", "WFII20", "WFII30",
        "FII5", "FII10", "FII20", "FII30",
        "T10YIE", "T5YIE", "T5YIFR",

        # Yield Curve
        "T10Y2Y", "T10Y3M", "T10YFF", "T5YFF",

        # Term Premium
        "THREEFYTP10",

        # Treasury General Account
        "WTREGEN",

        # Foreign Holdings of US Debt
        "FDHBFIN",

        # BEA Govt Receipts & Expenditures
        "BEA_Govt_Receipts_Expenditures_Total_receipts",
        "BEA_Govt_Receipts_Expenditures_Total_expenditures",
        "BEA_Govt_Receipts_Expenditures_Current_receipts",
        "BEA_Govt_Receipts_Expenditures_Current_expenditures",
        "BEA_Govt_Receipts_Expenditures_Current_tax_receipts",
        "BEA_Govt_Receipts_Expenditures_Personal_current_taxes",
        "BEA_Govt_Receipts_Expenditures_Taxes_on_corporate_income",
        "BEA_Govt_Receipts_Expenditures_Taxes_on_production_and_imports",
        "BEA_Govt_Receipts_Expenditures_Contributions_for_government_social_insurance",
        "BEA_Govt_Receipts_Expenditures_Income_receipts_on_assets",
        "BEA_Govt_Receipts_Expenditures_Interest_receipts",
        "BEA_Govt_Receipts_Expenditures_Rents_and_royalties",
        "BEA_Govt_Receipts_Expenditures_Current_transfer_receipts",
        "BEA_Govt_Receipts_Expenditures_Consumption_expenditures",
        "BEA_Govt_Receipts_Expenditures_Current_transfer_payments",
        "BEA_Govt_Receipts_Expenditures_Government_social_benefits",
        "BEA_Govt_Receipts_Expenditures_To_persons",
        "BEA_Govt_Receipts_Expenditures_Interest_payments",
        "BEA_Govt_Receipts_Expenditures_Subsidies",
        "BEA_Govt_Receipts_Expenditures_Gross_government_investment",
        "BEA_Govt_Receipts_Expenditures_Net_government_saving",
        "BEA_Govt_Receipts_Expenditures_Net_lending_or_net_borrowing_(-)",
        "BEA_Govt_Receipts_Expenditures_Capital_transfer_payments",
        "BEA_Govt_Receipts_Expenditures_Net_purchases_of_nonproduced_assets",
        "BEA_Govt_Receipts_Expenditures_Dividends",
        "BEA_Govt_Receipts_Expenditures_Social_insurance_funds",
        "BEA_Govt_Receipts_Expenditures_From_persons",
        "BEA_Govt_Receipts_Expenditures_From_business_(net)",
        "BEA_Govt_Receipts_Expenditures_From_the_rest_of_the_world",
        "BEA_Govt_Receipts_Expenditures_Taxes_from_the_rest_of_the_world",
        "BEA_Govt_Receipts_Expenditures_Interest_and_miscellaneous_receipts",
        "BEA_Govt_Receipts_Expenditures_Capital_transfer_receipts",
        "BEA_Govt_Receipts_Expenditures_Current_surplus_of_government_enterprises",
        "BEA_Govt_Receipts_Expenditures_Less:_Consumption_of_fixed_capital",
        "BEA_Govt_Receipts_Expenditures_Other",
        "BEA_Govt_Receipts_Expenditures_Other_current_transfer_payments_to_the_rest_of_the_world",
        "BEA_Govt_Receipts_Expenditures_To_persons_and_business",
        "BEA_Govt_Receipts_Expenditures_To_the_rest_of_the_world",

        # GDP Government Components
        "BEA_GDP_Components_Government_consumption_expenditures_and_gross_investment",
        "BEA_GDP_Components_Federal",
        "BEA_GDP_Components_National_defense",
        "BEA_GDP_Components_Nondefense",
        "BEA_GDP_Components_State_and_local",
    ],

    # ------------------------------------------------------------------
    # PILLAR 9: FINANCIAL
    # ------------------------------------------------------------------
    9: [
        # Credit Spreads
        "BAMLH0A0HYM2",  # HY OAS
        "BAMLC0A0CM",  # IG OAS
        "AAA",

        # Financial Conditions Indices
        "NFCI", "ANFCI",
        "STLFSI4",
        "KCFSI",

        # OFR Financial Stress
        "OFR_FSI", "OFR_FSI_Credit", "OFR_FSI_Equity",
        "OFR_FSI_SafeAssets", "OFR_FSI_Funding",
        "OFR_FSI_Volatility", "OFR_FSI_US",
        "OFR_FSI_AdvancedEcon", "OFR_FSI_EmergingMkts",

        # Loan Officer Survey
        "DRTSCILM", "DRTSCLCC",

        # Bank Lending
        "TOTCI", "CONSUMER", "BUSLOANS", "REALLN",

        # Delinquencies (all)
        "DRALACBS",  # All Loans
        "DRSFRMACBS",  # Mortgage
        "DRCCLACBS",  # Credit Card
        "DRCLACBS",  # Consumer

        # Bank Balance Sheet (H.8) - key aggregates
        "H8B1001NCBCAG",  # Total Assets
        "H8B1020NCBCAG",  # Securities
        "H8B1023NCBCAG",  # Treasury & Agency Securities
        "H8B1027NCBCAG",  # Other Securities
        "H8B1029NCBCAG",  # Loans & Leases
        "H8B1043NCBCAG",  # C&I Loans
        "H8B1058NCBCAG",  # Real Estate Loans
        "H8B1072NCBCAG",  # Consumer Loans
        "H8B1091NCBCAG",  # Allowance for Loan Losses
        "H8B1110NCBCAG",  # Total Liabilities
        "H8B1247NCBCAG",  # Deposits
        "H8B1301NCBCAG",  # Equity Capital
        "H8B3092NCBCAG",  # Assets Large Banks
        "H8B3094NCBCAG",  # Assets Small Banks
        "H8B3219NCBCAG",  # Deposits Detail

        # Senior Loan Officer Survey Detail
        "DRALACBN", "DRALOBN", "DRALT100N", "DRALT100S",
        "DRBLACBN", "DRBLACBS", "DRBLOBS", "DRBLT100S",
        "DRCCLACBN", "DRCCLOBN", "DRCCLOBS",
        "DRCCLT100N", "DRCCLT100S",
        "DRCLACBN", "DRCLOBN", "DRCLOBS",
        "DRCLT100N", "DRCLT100S",
        "DRCRELEXFACBN", "DRCRELEXFACBS",
        "DRCRELEXFOBS", "DRCRELEXFT100N", "DRCRELEXFT100S",
        "DRFAPGACBN", "DRFAPGACBS", "DRFAPGOBS", "DRFAPGT100S",
        "DRFLACBN", "DRFLACBS",
        "DRLFRACBN", "DRLFRACBS", "DRLFROBS",
        "DROCLACBN", "DROCLACBS", "DROCLOBS", "DROCLT100S",
        "DRSFRMACBN", "DRSFRMOBN", "DRSFRMOBS",
        "DRSFRMT100N", "DRSFRMT100S",
        "DRSREACBN", "DRSREACBS", "DRSREOBS", "DRSRET100S",
        "DRALOBS",

        # Consumer Credit
        "TOTALSL",

        # Interest Rates (credit relevant)
        "FEDFUNDS",
        "MORTGAGE30US",

        # Volatility
        "VIXCLS",

        # Net Interest Margin
        "NIMUS", "NIUS",

        # VIX detail
        "VIX_vs_50d_pct", "VIX_percentile_252d",

        # Yield Curve (credit signal)
        "T10Y2Y", "T10Y3M",
    ],

    # ------------------------------------------------------------------
    # PILLAR 10: PLUMBING
    # ------------------------------------------------------------------
    10: [
        # Fed Balance Sheet
        "WALCL",
        "H41RESPPALDKNWW",

        # RRP & Reserves
        "RRPONTSYD", "TOTRESNS",

        # Treasury General Account
        "WTREGEN",

        # Money Supply
        "M2SL",

        # NY Fed Reference Rates
        "NYFED_SOFR", "NYFED_EFFR", "NYFED_OBFR",
        "NYFED_TGCR", "NYFED_BGCR",
        "NYFED_SOFR_Volume", "NYFED_EFFR_Volume",
        "NYFED_OBFR_Volume", "NYFED_TGCR_Volume",
        "NYFED_BGCR_Volume",

        # OFR Reference Rates
        "OFR_FNYR-SOFR-A", "OFR_FNYR-EFFR-A",
        "OFR_FNYR-OBFR-A", "OFR_FNYR-TGCR-A",
        "OFR_FNYR-BGCR-A",

        # OFR Money Market
        "OFR_MMF-MMF_TOT-M", "OFR_MMF-MMF_RP_TOT-M",
        "OFR_MMF-MMF_RP_wFR-M", "OFR_MMF-MMF_T_TOT-M",

        # OFR Primary Dealer
        "OFR_NYPD-PD_RP_TOT-A", "OFR_NYPD-PD_RRP_TOT-A",
        "OFR_NYPD-PD_RP_T_TOT-A",

        # Fed Funds
        "FEDFUNDS",

        # Short-Term Rates
        "DGS1MO", "DGS3MO", "DGS6MO",
        "RIFLGFCM03NA", "RIFLGFCY01NA",
        "RIFLGFCY02NA", "RIFLGFCY03NA",
        "RIFLGFCY05NA", "RIFLGFCY10NA",
        "RIFLGFCY20NA", "RIFLGFCY30NA",

        # Stresses
        "STLFSI4",

        # Dallas Fed Financial Stress
        "DALLACBEP", "DALLCACBEP", "DALLCCACBEP",
        "DALLCCOBEP", "DALLCCT100EP",
        "DALLCIACBEP", "DALLCT100EP",
        "DALLFAPGACBEP", "DALLOBEP",
        "DALLSREACBEP", "DALLSRECRELEXFACBEP",
        "DALLSRESFRMACBEP", "DALLSRESFRMOBEP", "DALLSRESFRMT100EP",

        # Additional Stress Surveys
        "CILOBEP", "CILT100EP", "CLOBEP",
        "LSREOBEP",
        "OCLOBEP", "OCLT100EP",
        "TAIEALLGLFROBEP", "TAIEALLGLFRT100EP",
        "TAIEALLGSRECRELEXFOBEP", "TAIEALLGSRECRELEXFT100EP",
        "TAIEALLGSREFT100EP", "TAIEALLGSRESFRMT100EP",
        "TAIEALLGT100EP",

        # Additional Financial Stress
        "ACILOB", "ACILT100", "ACLOB", "ACLT100",
        "ALFAPGT100",
        "ATAIEALLGLFROB", "ATAIEALLGLFRT100",
        "ATAIEALLGOB", "ATAIEALLGSRECRELEXFOB",
        "ALSREOB", "ALSRET100",
        "AOCLT100",
    ],

    # ------------------------------------------------------------------
    # PILLAR 11: MARKET STRUCTURE
    # ------------------------------------------------------------------
    11: [
        # SPX Price & Structure (Yahoo)
        "SPX_Close", "SPX_Volume",
        "SPX_20d_MA", "SPX_50d_MA", "SPX_200d_MA",
        "SPX_20d_slope", "SPX_50d_slope", "SPX_200d_slope",
        "SPX_vs_20d_pct", "SPX_vs_50d_pct", "SPX_vs_200d_pct",
        "SPX_RSI_14d",
        "SPX_RoC_21d", "SPX_RoC_63d", "SPX_Z_RoC_63d",

        # Breadth (Computed)
        "SPX_PCT_ABOVE_20D", "SPX_PCT_ABOVE_50D", "SPX_PCT_ABOVE_200D",
        "SPX_ADVANCES", "SPX_DECLINES",
        "SPX_AD_LINE", "SPX_AD_RATIO",
        "SPX_NEW_HIGHS", "SPX_NEW_LOWS", "SPX_NET_NEW_HIGHS",
        "SPX_MCCLELLAN_OSC", "SPX_MCCLELLAN_SUM",
        "SPX_BREADTH_THRUST",

        # Volatility
        "VIXCLS",
        "VIX_vs_50d_pct", "VIX_percentile_252d",

        # Yield Curve (structure context)
        "T10Y2Y", "T10Y3M",

        # Key Rates (for structure context)
        "DGS10", "DGS2",

        # Credit Spreads (structure context)
        "BAMLH0A0HYM2",
    ],

    # ------------------------------------------------------------------
    # PILLAR 12: SENTIMENT
    # ------------------------------------------------------------------
    12: [
        # AAII Sentiment
        "AAII_Bullish", "AAII_Bearish",
        "AAII_Bull_Bear_Spread", "AAII_Neutral",

        # Consumer Sentiment
        "UMCSENT",

        # Business Confidence
        "BSCICP02USM460S", "BSCICP03USM665S",

        # Volatility (sentiment proxy)
        "VIXCLS",
        "VIX_vs_50d_pct", "VIX_percentile_252d",

        # Money Market Fund Assets (positioning)
        "OFR_MMF-MMF_TOT-M",

        # SPX structure (sentiment context)
        "SPX_Close",
        "SPX_vs_200d_pct",
        "SPX_PCT_ABOVE_50D",
        "SPX_RoC_63d", "SPX_Z_RoC_63d",
    ],
}


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_pillar_series(pillar_num: int) -> list:
    """Get list of series_id values for a given pillar."""
    if pillar_num not in PILLAR_SERIES:
        raise ValueError(f"Invalid pillar number: {pillar_num}. Must be 1-12.")
    return PILLAR_SERIES[pillar_num]


def get_pillar_indices(pillar_num: int) -> list:
    """Get list of index_id values for a given pillar, including master indices."""
    if pillar_num not in PILLAR_DEFS:
        raise ValueError(f"Invalid pillar number: {pillar_num}. Must be 1-12.")
    return PILLAR_DEFS[pillar_num]["indices"] + MASTER_INDICES


def get_pillar_db_name(pillar_num: int) -> str:
    """Get the database filename for a given pillar."""
    if pillar_num not in PILLAR_DEFS:
        raise ValueError(f"Invalid pillar number: {pillar_num}. Must be 1-12.")
    name = PILLAR_DEFS[pillar_num]["name"]
    return f"Pillar_{pillar_num:02d}_{name}.db"


def get_all_mapped_series() -> set:
    """Get the union of all series assigned to any pillar."""
    all_series = set()
    for series_list in PILLAR_SERIES.values():
        all_series.update(series_list)
    return all_series


def get_unmapped_series(db_series: set) -> set:
    """Given a set of all series_id values from the master DB,
    return those not assigned to any pillar."""
    return db_series - get_all_mapped_series()


def get_pillar_summary() -> dict:
    """Return summary stats for each pillar."""
    summary = {}
    for num, defn in PILLAR_DEFS.items():
        series = PILLAR_SERIES.get(num, [])
        summary[num] = {
            "name": defn["name"],
            "engine": defn["engine"],
            "indices": defn["indices"],
            "series_count": len(series),
        }
    return summary
