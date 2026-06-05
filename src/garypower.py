"""
GaryPOWER Signal Scanner
Ported from Pine Script v6 by Gary
Detects conditionA: days > 100 AND since_last_gt100[1] > 100
Sends HTML email via Resend when signals are found.
"""

import os
import sys
import json
import requests
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════
#  WATCHLIST
# ═══════════════════════════════════════════════════════════════════

WATCHLIST = [
    # ─── 美股核心 ─────────────────────────────────────────────────
    ("SPY",       "标普500ETF"),
    ("TQQQ",      "三倍做多纳指"),
    ("SOXL",      "三倍做多半导体"),
    ("NVDA",      "英伟达"),
    ("PLTR",      "Palantir"),
    ("TSLA",      "特斯拉"),
    ("MSFT",      "微软"),
    ("AEP",       "美国电力"),
    ("RKLB",      "火箭实验室"),
    ("AAPL",      "苹果"),
    ("AMZN",      "亚马逊"),
    ("MRVL",      "迈威尔"),
    ("CRWD",      "CrowdStrike"),
    ("DDOG",      "Datadog"),
    ("ARM",       "ARM Holding"),
    ("AMD",       "美国超微公司"),
    ("AAL", "美股"),
    ("AAOI", "美股"),
    ("AAON", "美股"),
    ("ABCL", "美股"),
    ("ABNB", "美股"),
    ("ACAD", "美股"),
    ("ACGL", "美股"),
    ("ACHC", "美股"),
    ("ACIW", "美股"),
    ("ACLS", "美股"),
    ("ACMR", "美股"),
    ("ADBE", "美股"),
    ("ADEA", "美股"),
    ("ADI", "美股"),
    ("ADMA", "美股"),
    ("ADP", "美股"),
    ("ADSK", "美股"),
    ("ADTN", "美股"),
    ("AEHR", "美股"),
    ("AEIS", "美股"),
    ("AEVA", "美股"),
    ("AFRM", "美股"),
    ("AGIO", "美股"),
    ("AGNC", "美股"),
    ("AGYS", "美股"),
    ("AIP", "美股"),
    ("AKAM", "美股"),
    ("AKTX", "美股"),
    ("ALAB", "美股"),
    ("ALGN", "美股"),
    ("ALGT", "美股"),
    ("ALHC", "美股"),
    ("ALKS", "美股"),
    ("ALNY", "美股"),
    ("AMAT", "美股"),
    ("AMBA", "美股"),
    ("AMD", "美股"),
    ("AMGN", "美股"),
    ("AMKR", "美股"),
    ("AMSC", "美股"),
    ("ANDE", "美股"),
    ("ANIP", "美股"),
    ("AOSL", "美股"),
    ("APA", "美股"),
    ("APLD", "美股"),
    ("APP", "美股"),
    ("APPF", "美股"),
    ("ARCB", "美股"),
    ("ARCC", "美股"),
    ("ARGX", "美股"),
    ("ARM", "美股"),
    ("ARRY", "美股"),
    ("ARWR", "美股"),
    ("ASML", "美股"),
    ("ASND", "美股"),
    ("ASO", "美股"),
    ("ASPI", "美股"),
    ("ASTS", "美股"),
    ("ATEX", "美股"),
    ("ATRO", "美股"),
    ("AUR", "美股"),
    ("AVAV", "美股"),
    ("AVGO", "美股"),
    ("AVR", "美股"),
    ("AVT", "美股"),
    ("AXON", "美股"),
    ("AXSM", "美股"),
    ("AXTI", "美股"),
    ("AZTA", "美股"),
    ("BAND", "美股"),
    ("BBIO", "美股"),
    ("BCPC", "美股"),
    ("BCRX", "美股"),
    ("BEAM", "美股"),
    ("BELFB", "美股"),
    ("BGC", "美股"),
    ("BHF", "美股"),
    ("BIDU", "美股"),
    ("BIIB", "美股"),
    ("BILI", "美股"),
    ("BKNG", "美股"),
    ("BKR", "美股"),
    ("BL", "美股"),
    ("BLDP", "美股"),
    ("BMRN", "美股"),
    ("BNTX", "美股"),
    ("BOKF", "美股"),
    ("BPOP", "美股"),
    ("BRKR", "美股"),
    ("BRZE", "美股"),
    ("BSY", "美股"),
    ("BTBT", "美股"),
    ("BTDR", "美股"),
    ("BTQ", "美股"),
    ("BYND", "美股"),
    ("BZ", "美股"),
    ("CACC", "美股"),
    ("CAKE", "美股"),
    ("CALM", "美股"),
    ("CAMT", "美股"),
    ("CAR", "美股"),
    ("CARG", "美股"),
    ("CART", "美股"),
    ("CASY", "美股"),
    ("CATY", "美股"),
    ("CBRL", "美股"),
    ("CBSH", "美股"),
    ("CCC", "美股"),
    ("CCEP", "美股"),
    ("CDNS", "美股"),
    ("CDW", "美股"),
    ("CECO", "美股"),
    ("CEG", "美股"),
    ("CELH", "美股"),
    ("CENX", "美股"),
    ("CEVA", "美股"),
    ("CG", "美股"),
    ("CGNX", "美股"),
    ("CHDN", "美股"),
    ("CHEF", "美股"),
    ("CHKP", "美股"),
    ("CHRD", "美股"),
    ("CHRW", "美股"),
    ("CHTR", "美股"),
    ("CIFR", "美股"),
    ("CIGI", "美股"),
    ("CINF", "美股"),
    ("CLSK", "美股"),
    ("CMCSA", "美股"),
    ("CME", "美股"),
    ("CMPS", "美股"),
    ("COCO", "美股"),
    ("CODX", "美股"),
    ("COHU", "美股"),
    ("COIN", "美股"),
    ("COKE", "美股"),
    ("COLB", "美股"),
    ("COLM", "美股"),
    ("COO", "美股"),
    ("CORT", "美股"),
    ("CORZ", "美股"),
    ("COST", "美股"),
    ("CPB", "美股"),
    ("CPRT", "美股"),
    ("CPRX", "美股"),
    ("CRDO", "美股"),
    ("CRNC", "美股"),
    ("CRNX", "美股"),
    ("CROX", "美股"),
    ("CRSP", "美股"),
    ("CRSR", "美股"),
    ("CRUS", "美股"),
    ("CRWD", "美股"),
    ("CRWV", "美股"),
    ("CSCO", "美股"),
    ("CSGP", "美股"),
    ("CSIQ", "美股"),
    ("CSWC", "美股"),
    ("CSX", "美股"),
    ("CTAS", "美股"),
    ("CTSH", "美股"),
    ("CVBF", "美股"),
    ("CVCO", "美股"),
    ("CVLT", "美股"),
    ("CWST", "美股"),
    ("CYTK", "美股"),
    ("CZR", "美股"),
    ("DASH", "美股"),
    ("DBX", "美股"),
    ("DDOG", "美股"),
    ("DIOD", "美股"),
    ("DJT", "美股"),
    ("DKNG", "美股"),
    ("DLO", "美股"),
    ("DLTR", "美股"),
    ("DOCU", "美股"),
    ("DORM", "美股"),
    ("DOX", "美股"),
    ("DPZ", "美股"),
    ("DRH", "美股"),
    ("DRS", "美股"),
    ("DRVN", "美股"),
    ("DUOL", "美股"),
    ("DXCM", "美股"),
    ("EA", "美股"),
    ("EBAY", "美股"),
    ("EBC", "美股"),
    ("EEFT", "美股"),
    ("ENPH", "美股"),
    ("ENSG", "美股"),
    ("ENTG", "美股"),
    ("ENVX", "美股"),
    ("EOSE", "美股"),
    ("EQIX", "美股"),
    ("ERAS", "美股"),
    ("ERIC", "美股"),
    ("ERIE", "美股"),
    ("ESLT", "美股"),
    ("EVRG", "美股"),
    ("EWBC", "美股"),
    ("EWTX", "美股"),
    ("EXC", "美股"),
    ("EXE", "美股"),
    ("EXEL", "美股"),
    ("EXLS", "美股"),
    ("EXPE", "美股"),
    ("EXPO", "美股"),
    ("EXTR", "美股"),
    ("EYE", "美股"),
    ("EZPW", "美股"),
    ("FANG", "美股"),
    ("FAST", "美股"),
    ("FCEL", "美股"),
    ("FCFS", "美股"),
    ("FCNCA", "美股"),
    ("FELE", "美股"),
    ("FFIV", "美股"),
    ("FHB", "美股"),
    ("FIBK", "美股"),
    ("FISV", "美股"),
    ("FITB", "美股"),
    ("FIVE", "美股"),
    ("FIVN", "美股"),
    ("FLEX", "美股"),
    ("FLNC", "美股"),
    ("FLY", "美股"),
    ("FLYW", "美股"),
    ("FORM", "美股"),
    ("FOX", "美股"),
    ("FOXA", "美股"),
    ("FROG", "美股"),
    ("FRPT", "美股"),
    ("FRSH", "美股"),
    ("FSLR", "美股"),
    ("FSLY", "美股"),
    ("FSV", "美股"),
    ("FTAI", "美股"),
    ("FTDR", "美股"),
    ("FTNT", "美股"),
    ("FULT", "美股"),
    ("FUTU", "美股"),
    ("FWONK", "美股"),
    ("GDS", "美股"),
    ("GEHC", "美股"),
    ("GEN", "美股"),
    ("GFS", "美股"),
    ("GGAL", "美股"),
    ("GH", "美股"),
    ("GILD", "美股"),
    ("GLBE", "美股"),
    ("GLNG", "美股"),
    ("GLPI", "美股"),
    ("GLXY", "美股"),
    ("GMAB", "美股"),
    ("GNTX", "美股"),
    ("GO", "美股"),
    ("GOOG", "美股"),
    ("GOOGL", "美股"),
    ("GOVX", "美股"),
    ("GPRE", "美股"),
    ("GRAB", "美股"),
    ("GRAL", "美股"),
    ("GRPN", "美股"),
    ("GSAT", "美股"),
    ("GT", "美股"),
    ("GTLB", "美股"),
    ("GTX", "美股"),
    ("HALO", "美股"),
    ("HAS", "美股"),
    ("HBAN", "美股"),
    ("HIMX", "美股"),
    ("HIVE", "美股"),
    ("HLNE", "美股"),
    ("HON", "美股"),
    ("HOOD", "美股"),
    ("HQY", "美股"),
    ("HSIC", "美股"),
    ("HST", "美股"),
    ("HTHT", "美股"),
    ("HTZ", "美股"),
    ("HUBG", "美股"),
    ("HUT", "美股"),
    ("HWC", "美股"),
    ("IAC", "美股"),
    ("IBKR", "美股"),
    ("IBRX", "美股"),
    ("ICHR", "美股"),
    ("ICLR", "美股"),
    ("ICUI", "美股"),
    ("IDCC", "美股"),
    ("IDXX", "美股"),
    ("IESC", "美股"),
    ("ILMN", "美股"),
    ("IMCR", "美股"),
    ("IMVT", "美股"),
    ("INBX", "美股"),
    ("INCY", "美股"),
    ("INDB", "美股"),
    ("INMD", "美股"),
    ("INOD", "美股"),
    ("INSM", "美股"),
    ("INTA", "美股"),
    ("INTC", "美股"),
    ("INTR", "美股"),
    ("INTU", "美股"),
    ("IONS", "美股"),
    ("IOVA", "美股"),
    ("IPAR", "美股"),
    ("IPGP", "美股"),
    ("IRDM", "美股"),
    ("IREN", "美股"),
    ("IRON", "美股"),
    ("IRTC", "美股"),
    ("ISRG", "美股"),
    ("ITRI", "美股"),
    ("JAZZ", "美股"),
    ("JBHT", "美股"),
    ("JBLU", "美股"),
    ("JD", "美股"),
    ("JKHY", "美股"),
    ("JOYY", "美股"),
    ("KALU", "美股"),
    ("KC", "美股"),
    ("KDP", "美股"),
    ("KHC", "美股"),
    ("KLAC", "美股"),
    ("KLIC", "美股"),
    ("KMB", "美股"),
    ("KRYS", "美股"),
    ("KSPI", "美股"),
    ("KTOS", "美股"),
    ("KURA", "美股"),
    ("KYMR", "美股"),
    ("LAMR", "美股"),
    ("LAUR", "美股"),
    ("LBRDK", "美股"),
    ("LCID", "美股"),
    ("LECO", "美股"),
    ("LEGN", "美股"),
    ("LFUS", "美股"),
    ("LGND", "美股"),
    ("LI", "美股"),
    ("LIF", "美股"),
    ("LIN", "美股"),
    ("LINE", "美股"),
    ("LITE", "美股"),
    ("LIVN", "美股"),
    ("LKQ", "美股"),
    ("LMAT", "美股"),
    ("LNT", "美股"),
    ("LNTH", "美股"),
    ("LOGI", "美股"),
    ("LOPE", "美股"),
    ("LPLA", "美股"),
    ("LPTH", "美股"),
    ("LRCX", "美股"),
    ("LSCC", "美股"),
    ("LSTR", "美股"),
    ("LULU", "美股"),
    ("LUNR", "美股"),
    ("LYFT", "美股"),
    ("MANH", "美股"),
    ("MAR", "美股"),
    ("MARA", "美股"),
    ("MASI", "美股"),
    ("MAT", "美股"),
    ("MBLY", "美股"),
    ("MCHP", "美股"),
    ("MDB", "美股"),
    ("MDGL", "美股"),
    ("MDLZ", "美股"),
    ("MEDP", "美股"),
    ("MELI", "美股"),
    ("MEOH", "美股"),
    ("META", "美股"),
    ("MGEE", "美股"),
    ("MIDD", "美股"),
    ("MIRM", "美股"),
    ("MITK", "美股"),
    ("MKSI", "美股"),
    ("MKTX", "美股"),
    ("MLCO", "美股"),
    ("MMSI", "美股"),
    ("MNDY", "美股"),
    ("MNST", "美股"),
    ("MORN", "美股"),
    ("MPWR", "美股"),
    ("MRNA", "美股"),
    ("MRVL", "美股"),
    ("MSFT", "美股"),
    ("MSTR", "美股"),
    ("MTCH", "美股"),
    ("MTSI", "美股"),
    ("MU", "美股"),
    ("MWH", "美股"),
    ("MXL", "美股"),
    ("MYRG", "美股"),
    ("NBIS", "美股"),
    ("NBIX", "美股"),
    ("NCNO", "美股"),
    ("NDAQ", "美股"),
    ("NDSN", "美股"),
    ("NEOG", "美股"),
    ("NESR", "美股"),
    ("NEXT", "美股"),
    ("NFLX", "美股"),
    ("NGEN", "美股"),
    ("NICE", "美股"),
    ("NKTR", "美股"),
    ("NMIH", "美股"),
    ("NNE", "美股"),
    ("NOVT", "美股"),
    ("NSIT", "美股"),
    ("NTAP", "美股"),
    ("NTES", "美股"),
    ("NTLA", "美股"),
    ("NTNX", "美股"),
    ("NTRA", "美股"),
    ("NTRS", "美股"),
    ("NUVL", "美股"),
    ("NVAX", "美股"),
    ("NVDA", "美股"),
    ("NVMI", "美股"),
    ("NVTS", "美股"),
    ("NWE", "美股"),
    ("NWL", "美股"),
    ("NWS", "美股"),
    ("NWSA", "美股"),
    ("NXPI", "美股"),
    ("NXST", "美股"),
    ("NXT", "美股"),
    ("ODFL", "美股"),
    ("OKTA", "美股"),
    ("OLED", "美股"),
    ("OLLI", "美股"),
    ("ON", "美股"),
    ("ONB", "美股"),
    ("ONC", "美股"),
    ("ONDS", "美股"),
    ("OPCH", "美股"),
    ("OPEN", "美股"),
    ("ORBS", "美股"),
    ("ORLY", "美股"),
    ("OSIS", "美股"),
    ("OSS", "美股"),
    ("OTEX", "美股"),
    ("OUST", "美股"),
    ("OZK", "美股"),
    ("PAA", "美股"),
    ("PAGP", "美股"),
    ("PANW", "美股"),
    ("PATK", "美股"),
    ("PAYX", "美股"),
    ("PCAR", "美股"),
    ("PCRX", "美股"),
    ("PCT", "美股"),
    ("PCTY", "美股"),
    ("PCVX", "美股"),
    ("PDD", "美股"),
    ("PECO", "美股"),
    ("PEGA", "美股"),
    ("PENN", "美股"),
    ("PEP", "美股"),
    ("PFG", "美股"),
    ("PGNY", "美股"),
    ("PGY", "美股"),
    ("PI", "美股"),
    ("PLAB", "美股"),
    ("PLAY", "美股"),
    ("PLMR", "美股"),
    ("PLTR", "美股"),
    ("PLUG", "美股"),
    ("PLUS", "美股"),
    ("PLXS", "美股"),
    ("PODD", "美股"),
    ("POET", "美股"),
    ("POOL", "美股"),
    ("POWI", "美股"),
    ("POWL", "美股"),
    ("PPC", "美股"),
    ("PRAX", "美股"),
    ("PRCT", "美股"),
    ("PSIX", "美股"),
    ("PSMT", "美股"),
    ("PTC", "美股"),
    ("PTCT", "美股"),
    ("PTEN", "美股"),
    ("PTGX", "美股"),
    ("PTON", "美股"),
    ("PYPL", "美股"),
    ("PZZA", "美股"),
    ("QCOM", "美股"),
    ("QFIN", "美股"),
    ("QLYS", "美股"),
    ("QQQ", "美股"),
    ("QRVO", "美股"),
    ("QS", "美股"),
    ("QTEX", "美股"),
    ("QUBT", "美股"),
    ("RARE", "美股"),
    ("REAL", "美股"),
    ("REG", "美股"),
    ("REGN", "美股"),
    ("RELY", "美股"),
    ("REYN", "美股"),
    ("RGEN", "美股"),
    ("RGLD", "美股"),
    ("RGTI", "美股"),
    ("RIOT", "美股"),
    ("RIVN", "美股"),
    ("RKLB", "美股"),
    ("RMBS", "美股"),
    ("ROAD", "美股"),
    ("ROIV", "美股"),
    ("ROKU", "美股"),
    ("ROP", "美股"),
    ("ROST", "美股"),
    ("RPRX", "美股"),
    ("RR", "美股"),
    ("RRR", "美股"),
    ("RUM", "美股"),
    ("RUN", "美股"),
    ("RVMD", "美股"),
    ("RXRX", "美股"),
    ("RXT", "美股"),
    ("RYAAY", "美股"),
    ("RYTM", "美股"),
    ("SAIA", "美股"),
    ("SAIC", "美股"),
    ("SAIL", "美股"),
    ("SANM", "美股"),
    ("SATS", "美股"),
    ("SBAC", "美股"),
    ("SBET", "美股"),
    ("SBLK", "美股"),
    ("SBRA", "美股"),
    ("SBUX", "美股"),
    ("SEDG", "美股"),
    ("SEIC", "美股"),
    ("SERV", "美股"),
    ("SEZL", "美股"),
    ("SFM", "美股"),
    ("SGML", "美股"),
    ("SHC", "美股"),
    ("SHLS", "美股"),
    ("SHOO", "美股"),
    ("SHOP", "美股"),
    ("SIGI", "美股"),
    ("SIMO", "美股"),
    ("SIRI", "美股"),
    ("SITM", "美股"),
    ("SKYT", "美股"),
    ("SKYW", "美股"),
    ("SLAB", "美股"),
    ("SLM", "美股"),
    ("SLS", "美股"),
    ("SMCI", "美股"),
    ("SMMT", "美股"),
    ("SMTC", "美股"),
    ("SNDK", "美股"),
    ("SNDX", "美股"),
    ("SNEX", "美股"),
    ("SNPS", "美股"),
    ("SNY", "美股"),
    ("SOFI", "美股"),
    ("SOLS", "美股"),
    ("SONO", "美股"),
    ("SOUN", "美股"),
    ("SOXL", "美股"),
    ("SPSC", "美股"),
    ("SPY", "美股"),
    ("SRAD", "美股"),
    ("SRPT", "美股"),
    ("SSNC", "美股"),
    ("SSRM", "美股"),
    ("STEP", "美股"),
    ("STLD", "美股"),
    ("STNE", "美股"),
    ("STRL", "美股"),
    ("STX", "美股"),
    ("SWKS", "美股"),
    ("SYM", "美股"),
    ("SYNA", "美股"),
    ("SYRE", "美股"),
    ("TCBI", "美股"),
    ("TCOM", "美股"),
    ("TEAM", "美股"),
    ("TECH", "美股"),
    ("TEM", "美股"),
    ("TENB", "美股"),
    ("TER", "美股"),
    ("TGTX", "美股"),
    ("TIGO", "美股"),
    ("TLN", "美股"),
    ("TMC", "美股"),
    ("TMDX", "美股"),
    ("TMUS", "美股"),
    ("TNDM", "美股"),
    ("TNGX", "美股"),
    ("TPG", "美股"),
    ("TQQQ", "美股"),
    ("TRI", "美股"),
    ("TRIP", "美股"),
    ("TRMB", "美股"),
    ("TRMD", "美股"),
    ("TROW", "美股"),
    ("TRVI", "美股"),
    ("TSCO", "美股"),
    ("TSEM", "美股"),
    ("TSLA", "美股"),
    ("TTD", "美股"),
    ("TTEK", "美股"),
    ("TTMI", "美股"),
    ("TTWO", "美股"),
    ("TVTX", "美股"),
    ("TW", "美股"),
    ("TWST", "美股"),
    ("TXG", "美股"),
    ("TXN", "美股"),
    ("TXRH", "美股"),
    ("UAL", "美股"),
    ("UBSI", "美股"),
    ("UCTT", "美股"),
    ("UFPI", "美股"),
    ("UFPT", "美股"),
    ("ULTA", "美股"),
    ("UMBF", "美股"),
    ("UPST", "美股"),
    ("UPWK", "美股"),
    ("URBN", "美股"),
    ("UTHR", "美股"),
    ("VC", "美股"),
    ("VCTR", "美股"),
    ("VCYT", "美股"),
    ("VECO", "美股"),
    ("VIAV", "美股"),
    ("VICR", "美股"),
    ("VITL", "美股"),
    ("VKTX", "美股"),
    ("VLY", "美股"),
    ("VNET", "美股"),
    ("VNOM", "美股"),
    ("VOD", "美股"),
    ("VRDN", "美股"),
    ("VRNS", "美股"),
    ("VRSK", "美股"),
    ("VRSN", "美股"),
    ("VRTX", "美股"),
    ("VSAT", "美股"),
    ("VSEC", "美股"),
    ("VTRS", "美股"),
    ("WAY", "美股"),
    ("WBD", "美股"),
    ("WDAY", "美股"),
    ("WDC", "美股"),
    ("WDFC", "美股"),
    ("WEN", "美股"),
    ("WERN", "美股"),
    ("WGS", "美股"),
    ("WING", "美股"),
    ("WIX", "美股"),
    ("WLDN", "美股"),
    ("WMG", "美股"),
    ("WMT", "美股"),
    ("WRLD", "美股"),
    ("WSC", "美股"),
    ("WSFS", "美股"),
    ("WTFC", "美股"),
    ("WTW", "美股"),
    ("WULF", "美股"),
    ("WWD", "美股"),
    ("WYNN", "美股"),
    ("XEL", "美股"),
    ("XENE", "美股"),
    ("XMTR", "美股"),
    ("XNDU", "美股"),
    ("XP", "美股"),
    ("XRAY", "美股"),
    ("XRX", "美股"),
    ("ZBRA", "美股"),
    ("ZD", "美股"),
    ("ZG", "美股"),
    ("ZION", "美股"),
    ("ZM", "美股"),
    ("ZS", "美股"), 
    # ─── 美股 ETF ─────────────────────────────────────────────────
    ("DBA",       "Invesco德银农业ETF"),
    ("DBC",       "商品指数ETF-Invesco"),
    ("DDM",       "2倍做多道指ETF-Proshares"),
    ("DRN",       "三倍做多房地产ETF-Direxion"),
    ("ERX",       "2倍做多能源ETF-Direxion"),
    ("FAS",       "三倍做多金融指数ETF-Direxion"),
    ("FRI",       "First Trust S&P REIT Index Fund"),
    ("IBB",       "生物科技指数ETF-iShares"),
    ("ICF",       "精选美国房地产投资信托基金ETF-iShares"),
    ("IHE",       "iShares安硕美国医药ETF"),
    ("IJH",       "标普中型股指数ETF-iShares"),
    ("IJR",       "标普小盘股指数ETF-iShares"),
    ("ITA",       "iShares安硕美国航空航天与国防ETF"),
    ("ITB",       "美国房屋建筑业ETF-iShares"),
    ("IVE",       "标普500价值指数ETF-iShares"),
    ("IVV",       "标普500ETF-iShares"),
    ("IVW",       "标普500成长股指数ETF-iShares"),
    ("IWB",       "罗素1000指数ETF-iShares"),
    ("IWM",       "罗素2000ETF-iShares"),
    ("IWO",       "罗素2000成长股指数ETF-iShares"),
    ("IWV",       "罗素3000ETF-iShares"),
    ("IYC",       "iShares安硕美国消费服务ETF"),
    ("IYF",       "金融指数ETF-iShares Dow Jones"),
    ("IYM",       "基础材料ETF-iShares"),
    ("IYR",       "美国房地产指数ETF-iShares"),
    ("IYT",       "运输指数ETF-iShares"),
    ("IYZ",       "美国电信ETF-iShares"),
    ("KBE",       "银行指数ETF-SPDR KBW"),
    ("KIE",       "保险指数ETF-SPDR KBW"),
    ("MDY",       "标普中型股400指数ETF-SPDR"),
    ("MOO",       "农业企业指数ETF-VanEck"),
    ("NLR",       "铀与核能ETF-VanEck"),
    ("OEF",       "标普100指数ETF-iShares"),
    ("OIH",       "石油服务指数ETF-VanEck"),
    ("PGF",       "Invesco优先金融股指数ETF"),
    ("QLD",       "2倍做多纳斯达克100指数ETF-ProShares"),
    ("QQQ",       "纳指100ETF-Invesco QQQ Trust"),
    ("RTH",       "零售指数ETF-VanEck"),
    ("SMH",       "半导体指数ETF-VanEck"),
    ("SSO",       "2倍做多标普500ETF-ProShares"),
    ("TAN",       "太阳能ETF-Invesco"),
    ("TNA",       "三倍做多小盘股ETF-Direxion"),
    ("TWM",       "罗素2000指数ETF-ProShares两倍做空"),
    ("UDOW",      "三倍做多道指30ETF-ProShares"),
    ("UNG",       "美国天然气ETF"),
    ("UPRO",      "三倍做多标普500ETF-ProShares"),
    ("URE",       "2倍做多房地产ETF-ProShares"),
    ("UVXY",      "1.5倍做多短期期货恐慌指数ETF-Proshares"),
    ("UWM",       "罗素2000指数ETF-ProShares两倍做多"),
    ("UYG",       "两倍做多金融股ETF-ProShares"),
    ("UYM",       "2倍做多基础材料ETF-ProShares"),
    ("VIXY",      "短期期货恐慌指数ETF-Proshares"),
    ("VNQ",       "不动产信托指数ETF-Vanguard"),
    ("VOO",       "标普500ETF-Vanguard"),
    ("VXX",       "标普500短期期货恐慌指数ETN-iPath"),
    ("VXZ",       "恐慌中期做多ETN-iPath S&P"),
    ("XHB",       "标普房屋建筑商ETF-SPDR"),
    ("XLB",       "SPDR原物料类ETF"),
    ("XLE",       "能源指数ETF-SPDR"),
    ("XLF",       "金融行业ETF-SPDR"),
    ("XLI",       "工业指数ETF-SPDR"),
    ("XLK",       "科技行业精选指数ETF-SPDR"),
    ("XLP",       "日常消费品精选行业指数ETF-SPDR"),
    ("XLU",       "公用事业精选行业指数ETF-SPDR"),
    ("XLV",       "医疗保健精选行业指数ETF-SPDR"),
    ("XLY",       "非必需消费类ETF-SPDR"),
    ("XME",       "SPDR标普金属与矿产业ETF"),
    ("XRT",       "标普零售指数ETF-SPDR"),
]

# name lookup
TICKER_NAMES = {t: n for t, n in WATCHLIST}


# ═══════════════════════════════════════════════════════════════════
#  INDICATOR CORE
# ═══════════════════════════════════════════════════════════════════

def calc_garypower(df):
    o, h, l, c, v = df["open"], df["high"], df["low"], df["close"], df["volume"]

    # 1. 基础价格与 PJJ 计算
    # PJJ:=DMA((H + L + C * 2) / 4, 0.9);
    pjj_input = (h + l + c * 2) / 4
    pjj = pjj_input.ewm(alpha=0.9, adjust=False).mean()

    # 2. EMA 计算
    def pine_ema(series, period):
        alpha = 2 / (period + 1)
        return series.ewm(alpha=alpha, adjust=False).mean()

    jj1 = pine_ema(pjj, 3)
    jj = jj1.shift(1)

    # 3. 流量控制算法 (XVL)
    # QJJ:=VOL / ((H - L) * 2 - ABS(C - O));
    denom = (h - l) * 2 - (c - o).abs()
    denom = denom.replace(0, np.nan)  # 规避分母为0导致的极值不稳定
    qjj = v / denom

    bull = c > o
    bear = c < o

    xvl1 = np.where(bull, qjj * (h - l), np.where(bear, qjj * (h - o + c - l), v / 2))
    xvl2 = np.where(bull, -(qjj * (h - c + o - l)), np.where(bear, -(qjj * (h - l)), -(v / 2)))
    xvl = xvl1 + xvl2

    hsl = pd.Series(xvl, index=df.index) / 20 / 1.15
    gp = hsl * 0.6  # 力度:HSL*0.6 完美对齐

    gjll = hsl * 0.55 + hsl.shift(1) * 0.33 + hsl.shift(2) * 0.22
    gs = pine_ema(gjll.fillna(0), 3)
    pw = gp / gs.abs()

    # 4. 力度新高:TOPRANGE(力度) -> 动态回溯算法
    src = gp.values
    n = len(src)
    days = np.zeros(n)
    
    for idx in range(1, n):
        val = src[idx]
        count = 0
        for j in range(idx - 1, -1, -1):
            if src[j] < val:
                count += 1
            else:
                break
        days[idx] = count

    days_series = pd.Series(days, index=df.index)

    # 5. 状态机逻辑及错位对齐
    bar_index = np.arange(n)
    since_last_gt100 = np.full(n, np.nan)
    last_gt100_bar = np.nan

    for idx in range(n):
        if not np.isnan(days[idx]) and days[idx] > 100:
            last_gt100_bar = bar_index[idx]
        if not np.isnan(last_gt100_bar):
            since_last_gt100[idx] = bar_index[idx] - last_gt100_bar

    since_last_gt100_series = pd.Series(since_last_gt100, index=df.index)

    # 6. 条件判断：days > 100 并且【上一根】距上次新高天数 > 100
    condition_a = (days_series > 100) & (since_last_gt100_series.shift(1) > 100)

    # 7. 组装输出
    out = df.copy()
    out["gp"] = gp
    out["gs"] = gs
    out["pw"] = pw
    out["days"] = days_series
    out["since_last_gt100"] = since_last_gt100_series
    out["conditionA"] = condition_a
    return out


# ═══════════════════════════════════════════════════════════════════
#  DATA FETCH (强力穿透与高精度版：确保拿到最新价，保留3位小数)
# ═══════════════════════════════════════════════════════════════════

def fetch_data(ticker, period="2y"):
    import yfinance as yf
    import pandas as pd
    import numpy as np
    
    t = yf.Ticker(ticker)
    
    # 1. 核心大招：利用 period="1mo" 的最高实时权限榨干 Yahoo 的最新“今天”数据
    # Yahoo 的服务器对 1mo/3mo 内的数据刷新率最高，能强制穿透未完全结算的最新交易日
    df_recent = t.history(period="1mo", interval="1d", auto_adjust=True, keepna=True)
    
    # 2. 如果最新数据里没有今天，或者你想双重保险，拉取 2y 的基础历史数据
    df_history = t.history(period=period, interval="1d", auto_adjust=True, keepna=True)
    
    # 3. 合并新旧账本，确保最新的一天（周五）绝对被囊括进来
    # combined 会自动根据日期 Index 去重并保留最新的那根 K 线
    raw = pd.concat([df_history, df_recent]).sort_index()
    raw = raw[~raw.index.duplicated(keep='last')]
    
    if raw.empty:
        raise ValueError(f"No data returned for {ticker}")
        
    # 兼容多级索引
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
        
    raw.columns = [c.lower() for c in raw.columns]
    
    # 4. 过滤成交量为 0 的日子（但如果是今天且正在交易，Volume 可能暂时为 NaN，要保留）
    # 只有当 Volume 明确存在且等于 0 的非交易日才过滤
    raw = raw[~(raw["volume"] == 0)]
    
    # 5. 关键修复：不要做任何 round() 强制截断！
    # 很多低价股/美股 ETF 报价在 3 位甚至 4 位小数，这里必须保持原始 float64 精度用于后面指标计算
    # 向前填充未结算数据（如果是盘中，防止 Close 暂时为 NaN）
    raw = raw.ffill()
    
    return raw[["open", "high", "low", "close", "volume"]].dropna()


# ═══════════════════════════════════════════════════════════════════
#  SCANNER
# ═══════════════════════════════════════════════════════════════════

def scan_ticker(ticker, period="2y"):
    try:
        df = fetch_data(ticker, period=period)
        out = calc_garypower(df)
        
        # 获取最后一根 K 线的数据
        last = out.iloc[-1]
        c = last["close"]
        gp_val = last["gp"]
        d = last["days"]
        s = last["since_last_gt100"]
        cond_a = last["conditionA"]
       
        # 打印触发状态 (已增加 Close 和 力度 并在控制台格式化对齐)
        # 找到这部分代码，修改控制台打印和 round 位数：
        status_str = "🔥【触发信号】" if cond_a else ""
        # 修复控制台打印：Close 改为 :>.3f 保留3位小数
        print(f": Close={c:>.3f}, 力度(gp)={gp_val:>.2f}, "
              f"Days={int(d) if not np.isnan(d) else 'NaN'}, "
              f"Since={out['since_last_gt100'].shift(1).iloc[-1]}  {status_str}")

        return {
            "ticker"          : ticker,
            "name"            : TICKER_NAMES.get(ticker, ""),
            "date"            : out.index[-1].strftime("%Y-%m-%d"),
            # 💡 核心修改：close 的四舍五入至少保留 4 位，或者干脆不 round 维持高精度
            "close"           : round(float(last["close"]), 4), 
            "gp"              : round(float(last["gp"]), 2),
            "gs"              : round(float(last["gs"]), 2),
            "pw"              : round(float(last["pw"]), 4),
            "days"            : int(d) if not np.isnan(d) else None,
            "since_last_gt100": int(s) if not np.isnan(s) else None,
            "conditionA"      : bool(cond_a),
            "error"           : None,
        }
    except Exception as e:
        return {
            "ticker": ticker, "name": TICKER_NAMES.get(ticker, ""),
            "date": None, "close": None, "gp": None, "gs": None,
            "pw": None, "days": None, "since_last_gt100": None,
            "conditionA": False, "error": str(e),
        }

def scan_all(period="2y"):
    tickers = [t for t, _ in WATCHLIST]
    total   = len(tickers)
    results = []
    for i, t in enumerate(tickers, 1):
        print(f"[{i:>{len(str(total))}}/{total}] {t:<11}", end=" ", flush=True)
        r = scan_ticker(t, period=period)
        results.append(r)

    df = pd.DataFrame(results)
    df = df.sort_values(["conditionA", "days"], ascending=[False, False])
    return df


# ═══════════════════════════════════════════════════════════════════
#  EMAIL  (Resend)
# ═══════════════════════════════════════════════════════════════════

RESEND_FROM = "gary@ceic.ca"
RESEND_TO   = "garyfocus@hotmail.com"


def build_html(signals, scan_date, total_scanned, errors):
    """Build a clean HTML email body."""

    def signal_rows(rows):
        out = ""
        for r in rows:
            out += f"""
            <tr>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;font-weight:600;color:#f0f0f0;">{r['ticker']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#aaa;">{r['name']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#f0f0f0;text-align:right;">{r['close']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#4ade80;text-align:right;">{r['days']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#60a5fa;text-align:right;">{r['since_last_gt100']}</td>
              <td style="padding:8px 12px;border-bottom:1px solid #2a2a2a;color:#fbbf24;text-align:right;">{round(r['pw'],3) if r['pw'] else '–'}</td>
            </tr>"""
        return out

    error_section = ""
    if errors:
        error_section = f"""
        <p style="margin-top:24px;color:#888;font-size:12px;">
          ⚠ {len(errors)} ticker(s) failed to load:
          {', '.join(e['ticker'] for e in errors)}
        </p>"""

    signal_count = len(signals)
    subject_note = f"{signal_count} signal(s)" if signal_count else "No signals"

    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#0d0d0d;font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;">
  <div style="max-width:680px;margin:32px auto;background:#141414;border-radius:12px;overflow:hidden;border:1px solid #222;">

    <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:28px 32px;">
      <div style="font-size:22px;font-weight:700;color:#e2e8f0;letter-spacing:1px;">
        📡 GaryPOWER Signal Report
      </div>
      <div style="margin-top:6px;color:#64748b;font-size:13px;">
        {scan_date} &nbsp;·&nbsp; {total_scanned} tickers scanned &nbsp;·&nbsp; {subject_note}
      </div>
    </div>

    <div style="padding:28px 32px;">
      {'<p style="color:#4ade80;font-size:15px;font-weight:600;margin-bottom:16px;">🔔 conditionA Triggered</p>' if signals else '<p style="color:#888;font-size:15px;">No conditionA signals today.</p>'}

      {'<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#1e1e1e;"><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">Ticker</th><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">名称</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Close</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Days</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Since</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">PW</th></tr></thead><tbody>' + signal_rows(signals) + '</tbody></table>' if signals else ''}

      <div style="margin-top:24px;padding:16px;background:#1a1a1a;border-radius:8px;font-size:12px;color:#64748b;line-height:1.8;">
        <strong style="color:#94a3b8;">指标说明</strong><br>
        <span style="color:#4ade80;">Days</span> — 力度新高持续天数（&gt;100 触发）<br>
        <span style="color:#60a5fa;">Since</span> — 距上次 Days&gt;100 事件的天数（前一根 &gt;100 触发）<br>
        <span style="color:#fbbf24;">PW</span> — 力度 / |流量|
      </div>

      {error_section}
    </div>

    <div style="padding:16px 32px;border-top:1px solid #1e1e1e;text-align:center;font-size:11px;color:#374151;">
      GaryPOWER · Automated by GitHub Actions
    </div>
  </div>
</body>
</html>
""", f"GaryPOWER {scan_date} | {subject_note}"


def send_email(api_key, html_body, subject):
    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type" : "application/json",
                "User-Agent"   : "Mozilla/5.0 (compatible; GaryPOWER/1.0)",
            },
            json={
                "from"   : RESEND_FROM,
                "to"     : [RESEND_TO],
                "subject": subject,
                "html"   : html_body,
            },
            timeout=20,
        )
        if resp.status_code in (200, 201):
            print(f"✅ Email sent  →  {RESEND_TO}  (status {resp.status_code})")
            return True
        else:
            print(f"❌ Resend error {resp.status_code}: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Email send failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════

def main():
    api_key = os.environ.get("RESEND_KEY", "")
    period  = os.environ.get("SCAN_PERIOD", "2y")

    scan_date = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'═'*60}")
    print(f"   GaryPOWER Scanner  |  {scan_date}")
    print(f"   Period: {period}  |  Tickers: {len(WATCHLIST)}")
    print(f"{'═'*60}\n")

    results = scan_all(period=period)

    signals = results[results["conditionA"] == True].to_dict("records")
    errors  = results[results["error"].notna()].to_dict("records")

    # ── terminal summary ─────────────────────────────────────────
    print(f"\n{'─'*60}")
    if signals:
        print(f"   🔔 {len(signals)} conditionA signal(s):")
        for r in signals:
            print(f"     {r['ticker']:<14} {r['name']:<20}  "
                  f"close={r['close']:<8} gp(力度)={r['gp']:<8} days={r['days']:<5} since={r['since_last_gt100']}")
    else:
        print("   No conditionA signals today.")
    if errors:
        print(f"\n  ⚠ {len(errors)} error(s): {', '.join(e['ticker'] for e in errors)}")
    print(f"{'─'*60}\n")

    # ── send email ───────────────────────────────────────────────
    if not api_key:
        print("⚠  RESEND_KEY not set — skipping email.")
        sys.exit(0)

    html, subject = build_html(signals, scan_date, len(WATCHLIST), errors)
    send_email(api_key, html, subject)


if __name__ == "__main__":
    main()
