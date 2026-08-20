"""
GaryPOWER Signal Scanner
Ported from Pine Script v6 by Gary
Detects conditionA: days > 400 AND since_last_gt100[1] > 100
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
from zoneinfo import ZoneInfo  # 必须引入这个

# ═══════════════════════════════════════════════════════════════════
#  WATCHLIST
# ═══════════════════════════════════════════════════════════════════

WATCHLIST = [
    # ─── 美股核心 ─────────────────────────────────────────────────
    ("MU", "美光科技"),
    ("SNDK", "闪迪"),
    ("SPCX", "SpaceX"),
    ("NVDA", "英伟达"),
    ("MRNA", "Moderna"),
    ("TSLA", "特斯拉"),
    ("WMT", "沃尔玛"),
    ("AAPL", "苹果"),
    ("INTC", "英特尔"),
    ("AMD", "美国超微公司"),
    ("NBIS", "NEBIUS"),
    ("MRVL", "迈威尔科技"),
    ("META", "Meta Platforms"),
    ("AVGO", "博通"),
    ("AMZN", "亚马逊"),
    ("MSFT", "微软"),
    ("MSTR", "Strategy"),
    ("GOOGL", "谷歌-A"),
    ("PLTR", "Palantir"),
    ("SKHY", "SK海力士"),
    ("GOOG", "谷歌-C"),
    ("LITE", "Lumentum"),
    ("COIN", "Coinbase"),
    ("STX", "希捷科技"),
    ("HOOD", "Robinhood"),
    ("WDC", "西部数据"),
    ("SMCI", "超微电脑"),
    ("AMAT", "应用材料"),
    ("NFLX", "奈飞"),
    ("COST", "好市多"),
    ("CRWV", "CoreWeave"),
    ("CRWD", "CrowdStrike"),
    ("TEM", "Tempus AI"),
    ("IREN", "IREN Ltd"),
    ("CBRS", "Cerebras Systems"),
    ("PANW", "Palo Alto Networks"),
    ("ASML", "阿斯麦"),
    ("LRCX", "泛林集团"),
    ("ISRG", "直觉外科公司"),
    ("DASH", "DoorDash"),
    ("AAOI", "Applied Optoelectronics"),
    ("APP", "Applovin"),
    ("RKLB", "Rocket Lab"),
    ("CSCO", "思科"),
    ("CRNX", "Crinetics"),
    ("KLAC", "科磊"),
    ("TEAM", "Atlassian"),
    ("TXN", "德州仪器"),
    ("ADI", "亚德诺"),
    ("AAL", "美国航空"),
    ("MARA", "MARA Holdings"),
    ("SOFI", "SoFi Technologies"),
    ("QCOM", "高通"),
    ("ABNB", "爱彼迎"),
    ("INTU", "财捷"),
    ("ROST", "罗斯百货"),
    ("AMGN", "安进"),
    ("PYPL", "PayPal"),
    ("CRDO", "Credo Technology"),
    ("MELI", "MercadoLibre"),
    ("SHOP", "Shopify"),
    ("LIN", "林德气体"),
    ("ILMN", "Illumina"),
    ("ARM", "Arm Holdings"),
    ("ONDS", "Ondas"),
    ("ADBE", "Adobe"),
    ("PEP", "百事可乐"),
    ("SBUX", "星巴克"),
    ("AXTI", "AXT Inc"),
    ("DDOG", "Datadog"),
    ("GILD", "吉利德科学"),
    ("TMUS", "T-Mobile US"),
    ("ALAB", "Astera Labs"),
    ("EBAY", "eBay"),
    ("CIFR", "Cipher Digital"),
    ("BKNG", "Booking Holdings"),
    ("FUTU", "富途控股"),
    ("ASTS", "AST SpaceMobile"),
    ("TER", "泰瑞达"),
    ("PURR", "HYPERLIQUID STRATEGIES INC"),
    ("BULL", "微牛"),
    ("HBAN", "亨廷顿银行"),
    ("MAR", "万豪酒店"),
    ("HONA", "Honeywell Aerospace"),
    ("STLD", "Steel Dynamics"),
    ("NTRA", "Natera"),
    ("DXCM", "德康医疗"),
    ("WULF", "TeraWulf"),
    ("TTWO", "Take-Two互动软件"),
    ("RIOT", "Riot Platforms"),
    ("WDAY", "Workday"),
    ("PDD", "拼多多"),
    ("UAL", "联合大陆航空"),
    ("CEG", "Constellation Energy"),
    ("MDB", "MongoDB"),
    ("HON", "霍尼韦尔"),
    ("ORLY", "奥莱利"),
    ("BNTX", "BioNTech"),
    ("CHTR", "特许通讯"),
    ("FTNT", "飞塔信息"),
    ("BIDU", "百度"),
    ("WBD", "Warner Bros Discovery"),
    ("APLD", "Applied Digital"),
    ("AXON", "Axon Enterprise"),
    ("IOVA", "Iovance Biotherapeutics"),
    ("NDSN", "Nordson"),
    ("NTAP", "美国网存"),
    ("HUT", "Hut 8"),
    ("ALNY", "阿里拉姆制药"),
    ("FANG", "Diamondback Energy"),
    ("SNPS", "新思科技"),
    ("CMCSA", "康卡斯特"),
    ("CDNS", "铿腾电子"),
    ("BKR", "Baker Hughes"),
    ("SGLY", "Singularity Future Technology"),
    ("ON", "安森美半导体"),
    ("LULU", "Lululemon Athletica"),
    ("RGTI", "Rigetti Computing"),
    ("CDW", "CDW Corp"),
    ("TWST", "Twist Bioscience"),
    ("CLSK", "CleanSpark"),
    ("EQIX", "易昆尼克斯"),
    ("MPWR", "Monolithic Power Systems"),
    ("ZS", "Zscaler"),
    ("REGN", "再生元制药公司"),
    ("GH", "Guardant Health"),
    ("VRTX", "福泰制药"),
    ("AMLX", "Amylyx Pharmaceuticals"),
    ("OKTA", "Okta"),
    ("CTAS", "信达思"),
    ("CME", "芝加哥商品交易所"),
    ("ADP", "自动数据处理"),
    ("MCHP", "微芯科技"),
    ("NXPI", "恩智浦"),
    ("FBRX", "Forte Biosciences"),
    ("CPRT", "科帕特"),
    ("HUIZ", "慧择"),
    ("RGEN", "Repligen"),
    ("BTCT", "BTC Digital"),
    ("PSNL", "Personalis"),
    ("FLEX", "伟创力"),
    ("FSLR", "第一太阳能"),
    ("DPZ", "达美乐比萨"),
    ("XEL", "埃克西尔能源"),
    ("RIVN", "Rivian Automotive"),
    ("ADSK", "欧特克"),
    ("CSX", "CSX运输"),
    ("ARGX", "argenx SE"),
    ("AVAV", "AeroVironment"),
    ("MNST", "怪物饮料"),
    ("TLN", "Talen Energy"),
    ("APA", "阿帕奇石油"),
    ("FTAI", "FTAI Aviation"),
    ("BTDR", "Bitdeer Technologies Group"),
    ("CELH", "Celsius Holdings"),
    ("FISV", "费哲金融服务"),
    ("MKTX", "MarketAxess"),
    ("UPST", "Upstart"),
    ("CPB", "金宝公司"),
    ("STRL", "Sterling Infrastructure"),
    ("USAR", "USA Rare Earth"),
    ("WWD", "伍德沃德"),
    ("IDXX", "爱德士"),
    ("KTOS", "克瑞拓斯安全防卫"),
    ("CTSH", "高知特"),
    ("MDLZ", "亿滋"),
    ("PCAR", "帕卡"),
    ("KDP", "Keurig Dr Pepper"),
    ("FCEL", "燃料电池能源"),
    ("RVMD", "Revolution Medicines"),
    ("EXE", "Expand Energy"),
    ("KHC", "卡夫亨氏"),
    ("KMB", "金佰利"),
    ("VICR", "Vicor电子"),
    ("QBTS", "D-Wave Quantum"),
    ("PAYX", "沛齐"),
    ("CORZ", "Core Scientific"),
    ("SMTC", "先科电子"),
    ("IBKR", "盈透证券"),
    ("TECH", "Bio-Techne"),
    ("AEHR", "Aehr Test Systems"),
    ("EXPE", "Expedia"),
    ("CSGP", "科斯塔"),
    ("FIVE", "Five Below"),
    ("ECHO", "回声星通信"),
    ("GMAB", "Genmab"),
    ("FWONK", "Liberty Formula One-C"),
    ("CASY", "Caseys General Stores"),
    ("CART", "Maplebear"),
    ("AMKR", "艾马克技术"),
    ("TSEM", "Tower半导体"),
    ("GLPI", "Gaming & Leisure Properties"),
    ("TTMI", "TTM科技"),
    ("DLTR", "美元树公司"),
    ("DKNG", "DraftKings"),
    ("MDLN", "Medline"),
    ("MKSI", "MKS仪器"),
    ("TSCO", "拖拉机供应公司"),
    ("AKAM", "阿克迈"),
    ("FAST", "快扣"),
    ("JZ", "见知教育"),
    ("TXG", "10x Genomics"),
    ("NTNX", "Nutanix"),
    ("INSM", "Insmed"),
    ("CRSP", "CRISPR Therapeutics"),
    ("SWKS", "思佳讯"),
    ("MANH", "Manhattan Associates"),
    ("NTES", "网易"),
    ("SITM", "SiTime"),
    ("FOXA", "福克斯公司-A"),
    ("MTSI", "MACOM Technology Solutions"),
    ("BLZE", "Backblaze"),
    ("PRAX", "Praxis Precision Medicines"),
    ("ASST", "Strive"),
    ("ALM", "Almonty Industries"),
    ("MWH", "SOLV Energy"),
    ("STRC", "STRATEGY INC VAR RT SER A PERP STRETCH PREFERRED STK"),
    ("WETO", "Wetour Robotics"),
    ("AUR", "Aurora Innovation"),
    ("SOUN", "SoundHound AI"),
    ("NTRS", "北方信托"),
    ("HIVE", "HIVE Digital Technologies"),
    ("TTD", "The Trade Desk"),
    ("APGE", "Apogee Therapeutics"),
    ("CAKE", "芝乐坊餐馆"),
    ("AEP", "美国电力"),
    ("ZM", "Zoom通讯"),
    ("ULTA", "Ulta美容"),
    ("ROP", "儒博实业"),
    ("CHYM", "Chime Financial"),
    ("AFRM", "Affirm Holdings"),
    ("ZBRA", "斑马技术"),
    ("RPRX", "Royalty Pharma"),
    ("ROKU", "Roku Inc"),
    ("JD", "京东"),
    ("TRMB", "天宝导航公司"),
    ("ENTG", "英特格"),
    ("WYNN", "永利度假村"),
    ("FIGR", "Figure Technology Solutions"),
    ("ODFL", "Old Dominion Freight Line"),
    ("SANM", "新美亚电子"),
    ("BBIO", "BridgeBio Pharma"),
    ("NDAQ", "纳斯达克"),
    ("MEDP", "Medpace"),
    ("TRI", "汤森路透"),
    ("AGNC", "美国资本代理公司"),
    ("EOSE", "Eos Energy"),
    ("GYGY", "Game Your Game"),
    ("GLXY", "Galaxy Digital"),
    ("TW", "Tradeweb Markets"),
    ("JBLU", "捷蓝航空"),
    ("EXC", "爱克斯龙电力"),
    ("LUNR", "Intuitive Machines"),
    ("JBHT", "JB亨特运输服务"),
    ("VRSK", "Verisk分析"),
    ("NXT", "Nextpower"),
    ("GFS", "GlobalFoundries"),
    ("LNTH", "Lantheus"),
    ("LYFT", "Lyft Inc"),
    ("EVRG", "西星能源"),
    ("UTHR", "美国联合医疗"),
    ("JKHY", "杰克亨利"),
    ("VIAV", "Viavi Solutions"),
    ("CAI", "Caris Life Sciences"),
    ("ASND", "Ascendis Pharma A/S"),
    ("SIMO", "慧荣科技"),
    ("LPLA", "LPL Financial"),
    ("SHAZ", "SharonAI Holdings"),
    ("SOLS", "Solstice Advanced Materials"),
    ("SNY", "赛诺菲安万特"),
    ("PODD", "银休特"),
    ("MXL", "MaxLinear"),
    ("WIX", "Wix.com"),
    ("GEHC", "GE HealthCare Technologies"),
    ("TPG", "TPG Inc"),
    ("BIVI", "BioVie"),
    ("KEEL", "Keel Infrastructure"),
    ("INIO", "INNIO N.V"),
    ("SBET", "SharpLink"),
    ("TGTX", "TG Therapeutics"),
    ("SSRM", "SSR Mining"),
    ("SLS", "Sellas Life Sciences"),
    ("TTEK", "德照科技"),
    ("QS", "QuantumScape"),
    ("BRZE", "Braze"),
    ("HST", "美国豪斯特酒店"),
    ("HALO", "奥洛兹美医疗"),
    ("RYAAY", "Ryanair"),
    ("CHRW", "罗宾逊物流"),
    ("GEN", "Gen Digital"),
    ("NVTS", "纳微半导体"),
    ("INCY", "因塞特"),
    ("SFM", "Sprouts Farmers Market"),
    ("MRVI", "Maravai LifeSciences"),
    ("RGLD", "皇家黄金"),
    ("WTW", "韦莱韬悦"),
    ("BIIB", "渤健公司"),
    ("ACGL", "艾奇资本"),
    ("IPST", "IP Strategy"),
    ("FROG", "JFrog"),
    ("OPEN", "Opendoor Technologies"),
    ("MDGL", "Madrigal Pharmaceuticals"),
    ("VRSN", "威瑞信"),
    ("GRAL", "Grail"),
    ("CYTK", "Cytokinetics"),
    ("ABVX", "Abivax S.A."),
    ("ALGN", "艾利科技"),
    ("FLNC", "Fluence Energy"),
    ("CCEP", "可口可乐欧洲太平洋"),
    ("DAVE", "Dave Inc"),
    ("LSCC", "莱迪思半导体"),
    ("FSLY", "Fastly"),
    ("CROX", "卡骆驰"),
    ("PLUG", "普拉格能源"),
    ("OUST", "Ouster"),
    ("IONS", "Ionis Pharmaceuticals"),
    ("BTBT", "Bit Digital"),
    ("URBN", "都市服饰"),
    ("LOGI", "罗技"),
    ("LQDA", "Liquidia"),
    ("WING", "Wingstop"),
    ("CHRD", "Chord Energy"),
    ("PTC", "PTC Inc"),
    ("RARE", "Ultragenyx Pharmaceutical"),
    ("AEIS", "先进能源工业"),
    ("MRCY", "Mercury Systems"),
    ("AUGO", "Aura Minerals"),
    ("XE", "X-Energy"),
    ("AXSM", "Axsome Therapeutics"),
    ("FER", "Ferrovial SE"),
    ("RITR", "域塔物流科技"),
    ("NBIX", "神经分泌生物科学"),
    ("VSAT", "卫讯公司"),
    ("STKH", "Steakholder Foods"),
    ("CENX", "世纪铝业"),
    ("LNT", "美国联合能源"),
    ("TTAN", "ServiceTitan"),
    ("DUOL", "多邻国"),
    ("LCID", "Lucid Group"),
    ("PENG", "Penguin Solutions"),
    ("GTLB", "Gitlab"),
    ("ENPH", "Enphase Energy"),
    ("GRAB", "Grab Holdings"),
    ("ATAT", "亚朵"),
    ("NVMI", "Nova"),
    ("ROIV", "Roivant Sciences"),
    ("LKQ", "LKQ Corp"),
    ("TIGO", "Millicom International Cellular"),
    ("EQPT", "EquipmentShare.com"),
    ("TCOM", "携程网"),
    ("BTSG", "BrightSpring Health Services"),
    ("PSKY", "Paramount Skydance"),
    ("TXRH", "德州公路酒吧"),
    ("FFIV", "F5 Inc"),
    ("TROW", "普信集团"),
    ("ZION", "齐昂银行"),
    ("BRLS", "Borealis Foods"),
    ("WYFI", "WhiteFiber"),
    ("MTCH", "Match group"),
    ("OLLI", "Ollie's Bargain Outlet"),
    ("CDTG", "城道通环保科技"),
    ("COLB", "哥伦比亚银行系统"),
    ("FCNCA", "第一公民银行股份"),
    ("FRMI", "Fermi"),
    ("BRKR", "布鲁克"),
    ("RXRX", "Recursion Pharmaceuticals"),
    ("DOCU", "DocuSign"),
    ("SGRY", "Surgery Partners"),
    ("FLY", "Firefly Aerospace"),
    ("JAZZ", "爵士制药"),
    ("HYMC", "Hycroft Mining"),
    ("RMBS", "Rambus"),
    ("FRPT", "Freshpet"),
    ("HTFL", "Heartflow"),
    ("PGY", "Pagaya Technologies"),
    ("QNT", "Quantinuum"),
    ("CACC", "Credit Acceptance"),
    ("ALGM", "Allegro Microsystems"),
    ("EXEL", "伊克力西斯"),
    ("CHKP", "Check Point软件"),
    ("KSPI", "Kaspi.kz"),
    ("CORT", "Corcept医疗"),
    ("CVLT", "康沃系统"),
    ("SATA", "STRIVE INC PERP PFD SER A VAR RATE"),
    ("UCTT", "超科林半导体"),
    ("ABCL", "AbCellera Biologics"),
    ("SEZL", "Sezzle"),
    ("ICLR", "Icon PLC"),
    ("ARQT", "Arcutis Biotherapeutics"),
    ("IESC", "IES Holdings"),
    ("HTHT", "华住"),
    ("LOOP", "Loop Industries"),
    ("VNOM", "Viper Energy"),
    ("GGAL", "加利西亚金融"),
    ("XOS", "Xos Inc"),
    ("DFTX", "Definium Therapeutics"),
    ("SMMT", "Summit Therapeutics"),
    ("BZ", "BOSS直聘"),
    ("QUBT", "Quantum Computing"),
    ("LECO", "林肯电气"),
    ("CG", "凯雷"),
    ("BEAM", "Beam Therapeutics"),
    ("CCC", "CCC Intelligent Solutions Holdings"),
    ("VISN", "Vistance Networks"),
    ("CRUS", "凌云半导体"),
    ("SCSC", "ScanSource"),
    ("VTRS", "Viatris"),
    ("HAS", "孩之宝"),
    ("XP", "XP Inc"),
    ("PFG", "信安金融"),
    ("ORKA", "Oruka Therapeutics"),
    ("GOOGN", "ALPHABET INC DEP SHS REPSTG 1/20TH INT B"),
    ("HQY", "HealthEquity"),
    ("FRVO", "Fervo Energy"),
    ("IRTC", "iRhythm Technologies"),
    ("VLY", "硅谷国家银行"),
    ("MFP", "Midera Food Processing"),
    ("SEDG", "SolarEdge Technologies"),
    ("CALM", "Cal-Maine Foods"),
    ("RCAT", "Red Cat Holdings"),
    ("DNTH", "Dianthus Therapeutics"),
    ("PCLA", "PicoCELA"),
    ("ONB", "Old National Bancorp"),
    ("ARCC", "阿瑞斯"),
    ("PTEN", "Patterson-UTI Energy"),
    ("ETOR", "eToro Group"),
    ("CGNX", "康耐视"),
    ("SBAC", "SBA通信公司"),
    ("COO", "库珀医疗"),
    ("COGT", "Cogent Biosciences"),
    ("ARWR", "Arrowhead Pharmaceuticals"),
    ("BILI", "哔哩哔哩"),
    ("PTGX", "Protagonist Therapeutics"),
    ("LAMR", "拉马尔户外广告"),
    ("POWL", "Powell Industries"),
    ("NTLA", "Intellia Therapeutics"),
    ("EXLS", "伊克赛尔服务"),
    ("SSNC", "SS&C Technologies"),
    ("REPL", "Replimune"),
    ("GLNG", "Golar LNG"),
    ("FORM", "FormFactor"),
    ("MYRG", "MYR Group"),
    ("IBRX", "ImmunityBio"),
    ("SAIA", "Saia"),
    ("SEIC", "SEI Investments"),
    ("KLIC", "库力索法半导体"),
    ("MMSI", "Merit Medical Systems"),
    ("ONC", "百济神州"),
    ("RELY", "Remitly Global"),
    ("CHDN", "Churchill Downs"),
    ("Z", "Zillow-C"),
    ("BMRN", "拜玛林制药"),
    ("APPF", "Appfolio"),
    ("NOVT", "Novanta"),
    ("SYRE", "Spyre Therapeutics"),
    ("COKE", "可口可乐装瓶"),
    ("LFUS", "美国力特保险丝"),
    ("POOL", "Pool Corp"),
    ("ATAI", "AtaiBeckley"),
    ("ACMR", "ACM Research"),
    ("NXTT", "Next Technology"),
    ("PONY", "小马智行"),
    ("CAPR", "Capricor Therapeutics"),
    ("VSEC", "VSE技术服务"),
    ("AAON", "艾伦建材"),
    ("TVTX", "Travere Therapeutic"),
    ("QLYS", "科力斯"),
    ("POET", "POET Technologies"),
    ("BLLN", "BillionToOne"),
    ("QRVO", "Qorvo"),
    ("PAA", "Plains All American Pipeline"),
    ("RUN", "Sunrun"),
    ("ASO", "Academy"),
    ("RYTM", "Rhythm Pharmaceuticals"),
    ("BSY", "Bentley Systems"),
    ("SYM", "Symbotic"),
    ("ERIC", "爱立信"),
    ("COLM", "哥伦比亚户外"),
    ("OCTV", "Octave Intelligence"),
    ("NWSA", "新闻集团-A"),
    ("SHC", "Sotera Health Company"),
    ("KYMR", "Kymera Therapeutics"),
    ("QURE", "uniQure NV"),
    ("DJCO", "每日期刊"),
    ("MEOH", "梅思恩"),
    ("SRRK", "Scholar Rock"),
    ("MORN", "晨星"),
    ("LEGN", "传奇生物"),
    ("GSAT", "全球星"),
    ("NVAX", "诺瓦瓦克斯医药"),
    ("REG", "Regency Centers Corp."),
    ("VKTX", "Viking Therapeutics"),
    ("AVT", "安富利"),
    ("ELVN", "Enliven Therapeutics"),
    ("OMH", "Ohmyhome"),
    ("RLAY", "Relay Therapeutics"),
    ("AMBA", "安霸"),
    ("SIRI", "Sirius XM"),
    ("MNDY", "monday.com"),
    ("SLAB", "芯科实验室"),
    ("FRHC", "Freedom Holding"),
    ("ENSG", "恩赛因"),
    ("LIF", "Life360"),
    ("VCTR", "Victory Capital"),
    ("AUPH", "Aurinia Pharmaceuticals"),
    ("CZR", "凯撒娱乐"),
    ("GDS", "万国数据"),
    ("ESLT", "埃尔比特系统"),
    ("LIFE", "Ethos Technologies"),
    ("INOD", "Innodata"),
    ("URGN", "乌龙制药"),
    ("UMBF", "UMB金融"),
    ("ATRO", "Astronics"),
    ("HSAI", "禾赛"),
    ("BPOP", "大众银行"),
    ("SAIC", "Science Applications International"),
    ("GOOGM", "ALPHABET INC DEP SHS REPSTG 1/20TH INT A"),
    ("SHLS", "Shoals Technologies"),
    ("IDCC", "InterDigital"),
    ("COCO", "Vita Coco"),
    ("HSIC", "汉瑞祥"),
    ("GPCR", "硕迪生物"),
    ("BYND", "Beyond Meat"),
    ("ALHC", "Alignment Healthcare"),
    ("FIVN", "Five9"),
    ("PTCT", "PTC Therapeutics"),
    ("MCHPP", "MICROCHIP TECHNOLOGY DEP SHS REPSTG 1/20TH PFD CONV SER A"),
    ("ALGT", "忠诚旅游"),
    ("EYPT", "EyePoint"),
    ("DBX", "Dropbox"),
    ("KRYS", "Krystal Biotech"),
    ("MGNI", "Magnite"),
    ("VERA", "Vera Therapeutics"),
    ("CINF", "辛辛纳提金融"),
    ("EWBC", "华美银行"),
    ("AXGN", "AxoGen"),
    ("MIDD", "The Middleby"),
    ("PGEN", "Precigen"),
    ("IPGP", "IPG光电"),
    ("SBLK", "Star Bulk Carriers"),
    ("OSIS", "OSI Systems"),
    ("UFPT", "UFP技术"),
    ("ATRC", "AtriCure"),
    ("NESR", "National Energy Services Reunited"),
    ("ARCB", "ArcBest"),
    ("ALKS", "阿尔凯默斯"),
    ("BHF", "Brighthouse Financial"),
    ("CVCO", "卡寇工业"),
    ("NXST", "Nexstar Media Group"),
    ("NCI", "思宏国际"),
    ("CRML", "Critical Metals"),
    ("ICUI", "ICU医疗"),
    ("CAMT", "康特科技"),
    ("CGON", "CG Oncology"),
    ("FCFS", "第一富金融服务"),
    ("YJ", "云集"),
    ("IRDM", "铱星通讯"),
    ("CELC", "Celcuity"),
    ("MBLY", "Mobileye Global"),
    ("PPC", "Pilgrim's Pride"),
    ("DOX", "Amdocs"),
    ("ALOY", "REalloys"),
    ("LOPE", "大峡谷教育"),
    ("NEO", "NeoGenomics"),
    ("WEN", "温蒂汉堡"),
    ("ADPT", "Adaptive Biotechnologies"),
    ("TMDX", "TransMedics"),
    ("BEEM", "Beam Global"),
    ("ERIE", "伊瑞保险"),
    ("FHB", "First Hawaiian"),
    ("STNE", "StoneCo"),
    ("ERAS", "Erasca"),
    ("PCTY", "Paylocity"),
    ("ZLAB", "再鼎医药"),
    ("IDYA", "IDEAYA生物科学"),
    ("LGN", "Legence"),
    ("PSMT", "普尔斯玛特"),
    ("BELFA", "Bel Fuse-A"),
    ("SYNA", "Synaptics"),
    ("BBNX", "Beta Bionics"),
    ("CCXI", "Churchill Capital Corp XI"),
    ("HLNE", "Hamilton Lane"),
    ("ARRY", "Array Technologies"),
    ("LASR", "nLIGHT"),
    ("CLDX", "塞德斯医疗"),
    ("GTX", "Garrett Motion"),
    ("TNGX", "Tango Therapeutics"),
    ("VSNT", "Versant Media"),
    ("VCYT", "Veracyte"),
    ("PEGA", "Pegasystems"),
    ("CBSH", "科默斯银行"),
    ("DJT", "特朗普媒体科技集团"),
    ("WTFC", "信达金融"),
    ("XNCR", "Xencor"),
    ("DIOD", "Diodes"),
    ("PCVX", "Vaxcyte"),
    ("EEFT", "嘉银通"),
    ("SRPT", "Sarepta Therapeutics"),
    ("GRPN", "GroupOn"),
    ("HTZ", "赫兹租车"),
    ("HWC", "汉考克惠特尼"),
    ("NAVN", "Navan"),
    ("CECO", "CECO环保"),
    ("NN", "NextNav"),
    ("ECPG", "安可资本"),
    ("HUBG", "Hub Group"),
    ("AYA", "Aya Gold & Silver"),
    ("GT", "固特异轮胎橡胶"),
    ("SAIL", "SailPoint"),
    ("FRSH", "Freshworks"),
    ("ICHR", "Ichor Holdings"),
    ("PLAB", "福尼克斯"),
    ("CSIQ", "阿特斯太阳能"),
    ("LGND", "Ligand Pharmaceuticals"),
    ("IMVT", "Immunovant"),
    ("INDV", "Indivior"),
    ("NCNO", "nCino"),
    ("ZG", "Zillow-A"),
    ("WSC", "WillScot Holdings"),
    ("CHEF", "The Chefs' Warehouse"),
    ("DLO", "DLocal"),
    ("QDEL", "窥得儿医药"),
    ("PCT", "PureCycle Technologies"),
    ("WFRD", "Weatherford国际"),
    ("CDNA", "CareDx"),
    ("IOND", "IONIC DIGITAL INC"),
    ("BATRK", "Atlanta Braves-C"),
    ("ZBIO", "Zenas BioPharma"),
    ("OTEX", "Open Text"),
    ("SHOO", "史蒂夫·马登"),
    ("QMCO", "昆腾"),
    ("FTDR", "Frontdoor"),
    ("ETON", "Eton Pharmaceutical"),
    ("DYN", "戴纳基"),
    ("VOD", "沃达丰"),
    ("AVAH", "Aveanna Healthcare"),
    ("CMPS", "COMPASS Pathways"),
    ("BSP", "Bending Spoons S.p.A"),
    ("DSGX", "笛卡尔物流系统集团"),
    ("ROAD", "Construction Partners"),
    ("CAST", "FreeCast"),
    ("MRX", "Marex Group"),
    ("SBCF", "Seacoast Bank"),
    ("SLM", "学贷美"),
    ("FOX", "福克斯公司-B"),
    ("FSV", "Firstservice"),
    ("TENB", "Tenable Holdings"),
    ("BLTE", "Belite Bio"),
    ("WB", "微博"),
    ("WMG", "华纳音乐"),
    ("XRAY", "登士柏"),
    ("VNET", "世纪互联"),
    ("GNTX", "真泰克"),
    ("POWI", "帕沃英蒂格盛"),
    ("HURN", "休伦咨询"),
    ("SKWD", "Skyward Specialty Insurance"),
    ("PENN", "佩恩国民博彩"),
    ("AGYS", "阿吉赛斯"),
    ("MAT", "美泰"),
    ("KC", "金山云"),
    ("GSHD", "Goosehead Insurance"),
    ("XENE", "Xenon制药"),
    ("OLED", "Universal Display"),
    ("COHU", "科休半导体"),
    ("PLPC", "Preformed Line Products"),
    ("CLBT", "Cellebrite"),
    ("EWTX", "Edgewise Therapeutics"),
    ("WGS", "GeneDx Holdings"),
    ("TCBI", "Texas Capital Bancshares"),
    ("PATK", "Patrick Industries"),
    ("PLXS", "普雷克萨斯"),
    ("GEMI", "Gemini Space Station"),
    ("PPTA", "Perpetua Resources"),
    ("NTSK", "Netskope"),
    ("LSTR", "莱帝运输"),
    ("LYTS", "LSI设备"),
    ("NKTR", "内克塔治疗"),
    ("ESTA", "Establishment Labs"),
    ("DGII", "美国迪进国际"),
    ("PTRN", "Pattern Group"),
    ("BELFB", "Bel Fuse-B"),
    ("TNDM", "Tandem Diabetes Care"),
    ("OPCH", "Option Care Health"),
    ("MGN", "Megan"),
    ("NNE", "NANO Nuclear Energy"),
    ("MNPR", "Monopar Therapeutics"),
    ("BRUN", "Boost Run"),
    ("OCUL", "Ocular Therapeutix"),
    ("TRIP", "猫途鹰"),
    ("OMER", "奥麦罗制药"),
    ("ABSI", "Absci Corp"),
    ("LAES", "SEALSQ Corp"),
    ("NWL", "纽威"),
    ("KALU", "凯撒铝业"),
    ("EBC", "Eastern Bankshares"),
    ("INDI", "indie Semiconductor"),
    ("FIBK", "First Interstate BancSystem"),
    ("NICE", "NICE Ltd"),
    ("LPTH", "LightPath Technologies"),
    ("ENVX", "Enovix"),
    ("TARS", "Tarsus Pharmaceuticals"),
    ("OZK", "欧扎克银行"),
    ("VRNS", "Varonis系统"),
    ("ARCT", "Arcturus Therapeutics"),
    ("CLMT", "卡路美"),
    ("ACAD", "阿卡迪亚"),
    ("CBRL", "CB乡村店"),
    ("LINC", "林肯教育服务"),
    ("BLBD", "Blue Bird"),
    ("SNEX", "StoneX"),
    ("QFIN", "奇富科技"),
    ("ORBS", "Eightco Holdings"),
    ("LI", "理想汽车"),
    ("SFD", "Smithfield Foods"),
    ("PZZA", "棒约翰"),
    ("SUPN", "Supernus Pharmaceuticals"),
    ("UBSI", "联合银行"),
    ("TIGR", "向上融科"),
    ("PRCT", "PROCEPT BioRobotics"),
    ("HIFS", "欣厄姆银行"),
    ("PECO", "Phillips Edison"),
    ("RDNT", "RadNet"),
    ("LAUR", "Laureate Education"),
    ("PI", "Impinj"),
    ("ACIW", "ACI环球"),
    ("AEVA", "Aeva Technologies"),
    ("NSIT", "Insight Enterprises"),
    ("INBX", "Inhibrx Biosciences"),
    ("MMED", "MiniMed Group"),
    ("PVLA", "Palvella Therapeutics"),
    ("FULT", "富尔顿金融"),
    ("CEVA", "CEVA Inc"),
    ("PAGP", "Plains GP Holdings"),
    ("MIRM", "Mirum Pharmaceuticals"),
    ("LIVN", "LivaNova"),
    ("WRLD", "环球验收"),
    ("HAPN", "Happen Inc"),
    ("WAY", "Waystar Holding"),
    ("MZTI", "Marzetti"),
    ("ABTC", "American Bitcoin"),
    ("MBX", "MBX Biosciences"),
    ("PHVS", "Pharvaris"),
    ("DXPE", "DXP Enterprises"),
    ("NRIX", "Nurix Therapeutics"),
    ("WYHG", "荣业食品"),
    ("HELP", "Cybin"),
    ("EWAV", "East West Ave Acquisition Corp"),
    ("GLBE", "Global-E Online"),
    ("PPLI", "People"),
    ("IMNM", "Immunome"),
    ("KURA", "Kura Oncology"),
    ("REAL", "TheRealReal"),
    ("BLFS", "BioLife Solutions"),
    ("DVLT", "Datavault AI"),
    ("ITRI", "伊管"),
    ("SIGI", "Selective Insurance"),
    ("NUAI", "New Era Energy & Digital"),
    ("BTTC", "Black Titan"),
    ("KNSA", "Kiniksa Pharmaceuticals International"),
    ("PGNY", "Progyny"),
    ("INTA", "Intapp"),
    ("ALNT", "Allient"),
    ("MLAB", "Mesa Laboratories"),
    ("JBSS", "John B. Sanfilippo & Son"),
    ("LFST", "LifeStance Health"),
    ("SKYW", "西空航空"),
    ("BAND", "Bandwidth"),
    ("WERN", "沃纳企业"),
    ("STEP", "StepStone Group"),
    ("SPSC", "SPS Commerce"),
    ("ACHC", "阿卡迪亚医疗保健"),
    ("PNRG", "PrimeEnergy Resources"),
    ("BGC", "BGC Group"),
    ("LGCL", "罗科仕"),
    ("VC", "伟世通"),
    ("UFPI", "UFP Industries"),
    ("STOK", "Stoke Therapeutics"),
    ("PTON", "Peloton Interactive"),
    ("JOYY", "欢聚"),
    ("SSYS", "Stratasys"),
    ("SATL", "Satellogic"),
    ("AZTA", "Azenta"),
    ("CADL", "Candel Therapeutics"),
    ("CAN", "嘉楠科技"),
    ("MMYT", "MakeMyTrip"),
    ("RUSHA", "Rush Enterprises-A"),
    ("FGL", "FOUNDER GROUP LIMITED"),
    ("XMTR", "Xometry"),
    ("HRMY", "Harmony Biosciences"),
    ("CLBK", "Columbia Financial"),
    ("CAR", "安飞士"),
    ("DRS", "Leonardo DRS, Inc."),
    ("TRVI", "Trevi Therapeutics"),
    ("BLKB", "布莱克波特科技"),
    ("MRAM", "Everspin Technologies"),
    ("APPS", "Digital Turbine"),
    ("BOKF", "BOK银行"),
    ("USLM", "美国灰矿建材"),
    ("SBRA", "Sabra Health Care REIT"),
    ("TLRY", "Tilray Brands"),
    ("INDB", "美国独立银行"),
    ("IMMX", "Immix Biopharma"),
    ("RXT", "Rackspace Technology"),
    ("DNLI", "Denali Therapeutics"),
    ("RRR", "Red Rock Resorts"),
    ("THEO", "BOA Acquisition Corp II"),
    ("LILAK", "Liberty Latin America-C"),
    ("NUTX", "Nutex Health"),
    ("JBIO", "Jade Biosciences"),
    ("ARXS", "Arxis"),
    ("ALMS", "Alumis"),
    ("COAG", "Hemab Therapeutics Holdings"),
    ("INDP", "Indaptus Therapeutics"),
    ("SFNC", "Simmons First National"),
    ("ATEX", "Anterix"),
    ("FFIN", "First Financial Bankshares"),
    ("EYE", "National Vision"),
    ("REYN", "Reynolds Consumer Products"),
    ("TRAX", "First Tracks Biotherapeutics"),
    ("IRON", "Disc Medicine"),
    ("ACLS", "Axcelis Technologies"),
    ("NEXT", "NextDecade"),
    ("FDMT", "4D Molecular Therapeutics"),
    ("IPAR", "依特香水"),
    ("CRSR", "Corsair Gaming"),
    ("BWMN", "Bowman Consulting"),
    ("PLMR", "Palomar Holdings"),
    ("ADMA", "ADMA Biologics"),
    ("ANAB", "AnaptysBio"),
    ("SERV", "Serve Robotics"),
    ("IEP", "伊坎企业"),
    ("LBTYA", "自由全球-A"),
    ("CABA", "Cabaletta Bio"),
    ("SCTX", "Scribe Therapeutics"),
    ("VELO", "Velo3D"),
    ("VECO", "维易科精密仪器"),
    ("QCRH", "QCR Holdings"),
    ("CERT", "Certara"),
    ("GCT", "大健云仓"),
    ("RUM", "RUM Group"),
    ("FFBC", "第一金融银行"),
    ("CBC", "Central Bancompany"),
    ("DORM", "Dorman Products"),
    ("AGIO", "Agios Pharmaceuticals"),
    ("FLYW", "Flywire"),
    ("BFC", "Bank First"),
    ("CNXC", "Concentrix"),
    ("CELZ", "Creative Medical Technology"),
    ("BCPC", "拜切"),
    ("MLTX", "MoonLake Immunotherapeutics"),
    ("EXTR", "极速网络"),
    ("CVBF", "CVB金融"),
    ("TNON", "Tenon Medical"),
    ("EVAX", "Evaxion A/S"),
    ("BCRX", "BioCryst制药"),
    ("CATY", "国泰万通金控"),
    ("LWLG", "Lightwave Logic"),
    ("STAA", "STAAR Surgical"),
    ("NMRK", "Newmark Group"),
    ("WSBC", "韦斯银行"),
    ("TBBK", "The Bancorp"),
    ("APEI", "美国公共教育"),
    ("OMDA", "Omada Health"),
    ("LLYVK", "Liberty Live-C"),
    ("AVPT", "AvePoint"),
    ("DRH", "DIAMONDROCK HOSPITALITY CO"),
    ("OMCL", "Omnicell"),
    ("SNDX", "Syndax Pharmaceuticals"),
    ("AMPL", "Amplitude"),
    ("RZLV", "Rezolve AI"),
    ("SWMR", "Swarmer"),
    ("LMRI", "Lumexa Imaging"),
    ("PDFS", "PDF Solutions"),
    ("LIND", "Lindblad Expeditions"),
    ("ZD", "Ziff Davis"),
    ("TOWN", "TowneBank"),
    ("NAMS", "NewAmsterdam Pharma"),
    ("ANIP", "ANI Pharmaceuticals"),
    ("INTR", "Inter & Co"),
    ("CGEM", "Cullinan Therapeutics"),
    ("DFDV", "DeFi Development"),
    ("BJRI", "BJ's餐饮"),
    ("ESQ", "Esquire Financial"),
    ("GENB", "Generate Biomedicines"),
    ("LMAT", "勒梅特微管医疗"),
    ("MCRI", "Monarch Casino & Resort"),
    ("CWST", "Casella Waste Systems"),
    ("CASH", "Pathward Financial"),
    ("VRDN", "Viridian Therapeutics"),
    ("MLYS", "Mineralys Therapeutics"),
    ("HROW", "Harrow"),
    ("AOSL", "阿尔法和欧米伽半导体"),
    ("PRLD", "Prelude Therapeutics"),
    ("SDGR", "Schrodinger"),
    ("SRAD", "Sportradar Group AG"),
    ("APPN", "Appian"),
    ("BUSE", "First Busey"),
    ("ALKT", "Alkami Technology"),
    ("GO", "Grocery Outlet"),
    ("EXPO", "毅博科技咨询"),
    ("WDFC", "WD-40"),
    ("KOPN", "高平电子"),
    ("APMD", "Apnimed"),
    ("CDNL", "Cardinal Infrastructure Group"),
    ("ARDX", "Ardelyx"),
    ("LIME", "Neutron Holdings"),
    ("VCEL", "Vericel"),
    ("ATLC", "Atlanticus"),
    ("FTRE", "Fortrea Holdings"),
    ("METC", "Ramaco Resources-A"),
    ("ADUS", "爱德斯"),
    ("BAOS", "宝盛"),
    ("TSAT", "Telesat"),
    ("CCOI", "Cogent通信"),
    ("NWS", "新闻集团-B"),
    ("VSTM", "Verastem"),
    ("HWKN", "霍金斯材料"),
    ("BANF", "BancFirst银行"),
    ("AKBA", "Akebia Therapeutics"),
    ("ALT", "Altimmune"),
    ("EZPW", "艾茨克普"),
    ("ASPI", "ASP Isotopes"),
    ("IMCR", "Immunocore"),
    ("OCFC", "OceanFirst Financial"),
    ("TMC", "TMC the metals"),
    ("DGXX", "Digi Power X"),
    ("BL", "BlackLine"),
    ("REAX", "The Real Brokerage"),
    ("NB", "NioCorp Developments"),
    ("CYPH", "Cypherpunk Technologies"),
    ("PRPO", "Precipio"),
    ("UPWK", "Upwork"),
    ("MNKD", "曼恩凯德生物医疗"),
    ("LINE", "Lineage"),
    ("TJGC", "TJGC Group"),
    ("DRVN", "Driven Brands"),
    ("FA", "First Advantage"),
    ("BWIN", "Baldwin Insurance Group"),
    ("SYBT", "Stock Yards Bancorp"),
    ("JJSF", "JJSF食品"),
    ("PLUS", "正羽科技"),
    ("PRME", "Prime Medicine"),
    ("KOD", "Kodiak Sciences"),
    ("CLYM", "Climb Bio"),
    ("ULCC", "Frontier Group"),
    ("BANR", "邦纳"),
    ("RPD", "Rapid7"),
    ("HCSG", "Healthcare Services Group"),
    ("TH", "Target Hospitality"),
    ("NHP", "National Healthcare Properties"),
    ("NVCR", "Novocure"),
    ("CLOV", "Clover Health"),
    ("JANX", "Janux Therapeutics"),
    ("OSW", "OneSpaWorld"),
    ("DUOT", "Duos Technologies"),
    ("WSFS", "WSFS金融"),
    ("BETR", "Better Home & Finance"),
    ("RDVT", "Red Violet"),
    ("MITK", "Mitek Systems"),
    ("XHLD", "TEN Holdings"),
    ("CRAI", "CRA国际"),
    ("VREX", "Varex Imaging"),
    ("AGEN", "艾吉纳斯"),
    ("FRNM", "Freenome"),
    ("LFTO", "Liftoff Mobile"),
    ("TRMD", "Torm"),
    ("AMSC", "美国超导"),
    ("CARG", "CarGurus"),
    ("PRVA", "Privia Health"),
    ("BTCS", "BTCS Inc"),
    ("BOT", "RoboStrategy"),
    ("COLL", "Collegium Pharmaceutical"),
    ("HNST", "The Honest"),
    ("CIGI", "高力国际集团"),
    ("ZTG", "道元集团"),
    ("SPRY", "ARS Pharmaceuticals"),
    ("SLNH", "Soluna Holdings"),
    ("JACK", "Jack in the Box"),
    ("GLUE", "Monte Rosa Therapeutics"),
    ("USDE", "StablecoinX"),
    ("AMRX", "Amneal Pharmaceuticals"),
    ("FEIM", "高频电子"),
    ("ITIC", "投资者不动产"),
    ("ADEA", "Adeia"),
    ("PUBM", "Pubmatic"),
    ("NWE", "NorthWestern"),
    ("ACHV", "Achieve Life"),
    ("HTO", "H2O America"),
    ("NTCT", "网侦系统"),
    ("ROOT", "Root Inc"),
    ("UPBD", "Upbound Group"),
    ("NVEC", "NVE Corp"),
    ("CGC", "Canopy Growth"),
    ("NMIH", "NMI Holdings"),
    ("SPT", "Sprout Social"),
    ("PHAT", "Phathom Pharmaceuticals"),
    ("CAE", "CAE Inc"),
    ("CSWC", "西南资本"),
    ("IBOC", "International Bancshares"),
    ("CJMB", "Callan JMB"),
    ("FTH", "Faeth Therapeutics"),
    ("ENLT", "Enlight Renewable Energy"),
    ("EDIT", "Editas Medicine"),
    ("VOR", "Vor Biopharma"),
    ("OABI", "OmniAb"),
    ("CHCO", "City Holding"),
    ("OPRA", "欧朋公司"),
    ("GRRR", "Gorilla Technology"),
    ("HLIT", "谐波"),
    ("GTM", "ZoomInfo"),
    ("SEPN", "Septerna"),
    ("FHTX", "Foghorn Therapeutics"),
    ("PWCM", "PowerCompute"),
    ("CMPR", "Cimpress"),
    ("WVE", "Wave Life Sciences"),
    ("SENEA", "Seneca Foods-A"),
    ("NWPX", "NWPX 基础设施"),
    ("ANDE", "安德森斯"),
    ("WINA", "威玛克工贸"),
    ("PSEC", "普罗斯佩克特资本"),
    ("GILT", "吉来特卫星网络"),
    ("ALRM", "Alarm.com"),
    ("XERS", "Xeris制药"),
    ("MGTX", "MeiraGTx Holdings"),
    ("AVTX", "Avalo Therapeutics"),
    ("LMB", "Limbach"),
    ("BLMN", "Bloomin Brands"),
    ("SMCIP", "SUPER MICRO COMPUTER INC 7 % DEP SHS REPSTG 1/20TH PFD CONV SER A"),
    ("ZVRA", "Zevra Therapeutics"),
    ("IQ", "爱奇艺"),
    ("ARHS", "Arhaus"),
    ("BRNX", "BrenX"),
    ("DOO", "BRP Inc"),
    ("AIP", "Arteris"),
    ("SMPL", "The Simply Good Foods"),
    ("ASTL", "Algoma Steel"),
    ("SVRA", "Savara"),
    ("SONO", "搜诺思公司"),
    ("DNUT", "Krispy Kreme"),
    ("TSSI", "TSS Inc"),
    ("GPRE", "绿色平原能源"),
    ("LZ", "LegalZoom"),
    ("ORIC", "Oric Pharmaceuticals"),
    ("GLIBK", "GCI Liberty-C"),
    ("WRD", "文远知行"),
    ("ALLO", "Allogene Therapeutics"),
    ("SLE", "Super League Enterprise"),
    ("SAFT", "Safety Insurance"),
    ("WLDN", "Willdan集团"),
    ("NNBR", "NN Inc"),
    ("OSS", "One Stop Systems"),
    ("AQST", "Aquestive Therapeutics"),
    ("ATEC", "阿尔法泰克"),
    ("TRNS", "Transcat"),
    ("DRUG", "Bright Minds Biosciences"),
    ("MLCO", "新濠博亚娱乐"),
    ("SLDE", "Slide Insurance Holdings"),
    ("TILE", "Interface"),
    ("PLSE", "Pulse Biosciences"),
    ("AHCO", "AdaptHealth"),
    ("NBN", "东北银行"),
    ("OLMA", "Olema Pharmaceuticals"),
    ("AVR", "安特瑞斯科技"),
    ("VERI", "Veritone"),
    ("WAFD", "WaFd"),
    ("HIMX", "奇景光电"),
    ("RNW", "ReNew Energy Global"),
    ("SVC", "Service Properties Trust"),
    ("NEOG", "纽尔真检测"),
    ("PRDO", "Perdoceo Education"),
    ("PLAY", "Dave & Buster's Entertainment"),
    ("SANA", "Sana Biotechnology"),
    ("AVBP", "ArriVent BioPharma"),
    ("OTTR", "奥特泰尔"),
    ("SGMT", "Sagimet Biosciences"),
    ("ATTO", "Attovia Therapeutics"),
    ("FRME", "第一招商股份"),
    ("PWP", "温伯格合伙公司"),
    ("VERX", "Vertex"),
    ("STRD", "STRATEGY INC 10% NON CUM PREF SER A PERP STRIDE WI"),
    ("MATW", "马修国际"),
    ("IMKTA", "安格莱斯市场"),
    ("CTRN", "Citi Trends"),
    ("AIRJ", "AirJoule Technologies"),
    ("WSE", "WISE GROUP PLC"),
    ("SCZM", "Santacruz Silver Mining"),
    ("UNIT", "Uniti Group"),
    ("LXRX", "莱斯康制药"),
    ("TREE", "LendingTree"),
    ("SION", "Sionna Therapeutics"),
    ("FELE", "富兰克林电子"),
    ("QNST", "QuinStreet"),
    ("HTLD", "哈特兰快递"),
    ("ALMU", "Aeluma Inc"),
    ("PFSA", "Profusa"),
    ("KLRA", "Kailera Therapeutics"),
    ("LGIH", "LGI Homes"),
    ("STRA", "Strategic Education"),
    ("NXH", "Neighborhood Intelligence"),
    ("ZSTK", "ZeroStack"),
    ("CMRC", "Commerce.com"),
    ("MNRO", "Monro"),
    ("IVVD", "Invivyd"),
    ("AUTL", "Autolus Therapeutics"),
    ("GDRX", "GoodRx"),
    ("CIRC", "Circle8"),
    ("TCBK", "TriCo Bancshares"),
    ("VITL", "Vital Farms"),
    ("CCB", "Coastal Financial"),
    ("SHOE", "Shoe Station Group"),
    ("XNDU", "哈纳杜量子技术"),
    ("QTEX", "Qtrex Quantum"),
    ("CCCC", "C4 Therapeutics"),
    ("FDUS", "Fidus Investment"),
    ("RGNX", "Regenxbio"),
    ("CRVS", "Corvus Pharmaceuticals"),
    ("TSHA", "Taysha Gene Therapies"),
    ("FLXS", "Flexsteel Industries"),
    ("CSTL", "Castle Biosciences"),
    ("SMTI", "Sanara MedTech"),
    ("PSIX", "Power Solutions International"),
    ("EVLV", "Evolv Technologies"),
    ("GERN", "杰龙"),
    ("MGRC", "McGrath RentCorp"),
    ("FIZZ", "National Beverage"),
    ("CERS", "Cerus"),
    ("WLFC", "威利斯金融租赁"),
    ("KRT", "Karat Packaging"),
    ("ODD", "ODDITY Tech"),
    ("LBRX", "LB Pharmaceuticals"),
    ("MLKN", "MillerKnoll"),
    ("BVS", "Bioventus"),
    ("VRRM", "Verra Mobility"),
    ("SGML", "Sigma Lithium"),
    ("PAX", "Patria Investments"),
    ("STRF", "STRATEGY INC 10.00% SER A PERPETUAL STRIFE PFD STK"),
    ("THRM", "Gentherm"),
    ("INVA", "Innoviva"),
    ("EVGO", "EVgo Inc"),
    ("TCGX", "TCGX ACQUISITION CORPORATION"),
    ("CRVL", "CorVel"),
    ("PRGS", "Progress Software"),
    ("NHIC", "NewHold Investment Corp. III"),
    ("EVER", "EverQuote"),
    ("TFSL", "TFS Financial"),
    ("LLYVA", "Liberty Live-A"),
    ("IPX", "IperionX"),
    ("GBDC", "Golub Capital BDC"),
    ("BCAX", "Bicara Therapeutics"),
    ("ACDC", "ProFrac Holding"),
    ("EMBC", "Embecta"),
    ("RIGL", "Rigel Pharmaceuticals"),
    ("NTWO", "Newbury Street II Acquisition Corp"),
    ("CRMD", "CorMedix"),
    ("LBTYK", "自由全球-C"),
    ("TRUP", "Trupanion"),
    ("TCMD", "Tactile Systems Technology"),
    ("PAYO", "Payoneer Global"),
    ("CRTO", "Criteo"),
    ("FWDI", "福沃德工业"),
    ("STRK", "STRATEGY INC 8.00% SERIES A PERPETUAL STRIKE PFD"),
    ("TENX", "Tenax Therapeutics"),
    ("ICFI", "ICF国际"),
    ("BLDP", "巴拉德动力系统"),
    ("RAPP", "Rapport Therapeutics"),
    ("FBNC", "第一银行(北卡)"),
    ("RBCAA", "Republic Bancorp"),
    ("FSUN", "FirstSun Capital Bancorp"),
    ("SLDB", "Solid Biosciences"),
    ("CYRX", "Cryoport"),
    ("PBLS", "Parabilis Medicines"),
    ("NWBI", "Northwest Bancshares"),
    ("ADTN", "亚川"),
    ("ALMR", "Alamar Biosciences"),
    ("HLMN", "Hillman Solutions"),
    ("JCAP", "Jefferson Capital Inc"),
    ("PRCH", "Porch Group"),
    ("GIII", "G-III服装集团"),
    ("KYTX", "Kyverna Therapeutics"),
    ("LKFT", "Lakefront Biotherapeutics"),
    ("TBLA", "Taboola Com"),
    ("MQ", "Marqeta"),
    ("IMXI", "国际货币快递"),
    ("MFIC", "MidCap Financial Investment Corporation"),
    ("ELVA", "Electrovaya"),
    ("ACRS", "Aclaris Therapeutics"),
    ("TOYO", "TOYO Co"),
    ("SIDU", "Sidus Space"),
    ("UROY", "Uranium Royalty"),
    ("FOXF", "Fox Factory"),
    ("SFIX", "Stitch Fix"),
    ("TDUP", "ThredUp"),
    ("NAVI", "Navient"),
    ("MASS", "908 Devices"),
    ("NCT", "Intercont"),
    ("USAU", "美国黄金公司"),
    ("HOPE", "Hope Bancorp"),
    ("MVST", "Microvast"),
    ("IART", "英特格拉生命科学"),
    ("OSBC", "Old Second Bancorp"),
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

    # 计算距离上次满足条件距今的天数
    for idx in range(n):
        if not np.isnan(days[idx]) and days[idx] > 400:
            last_gt100_bar = bar_index[idx]
        if not np.isnan(last_gt100_bar):
            since_last_gt100[idx] = bar_index[idx] - last_gt100_bar

    since_last_gt100_series = pd.Series(since_last_gt100, index=df.index)

    # 6. 条件判断：days > 400 并且【上一根】距上次>100天数 > 100，创400日新高，同时距离上次创100日新高的天数是100天
    condition_a = (days_series > 400) & (since_last_gt100_series.shift(1) > 100)

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

        if cond_a:
           save_signal_to_kv(ticker, c, d, s)

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
#  写入CLOUDFLARE KV
# ═══════════════════════════════════════════════════════════════════
# 1. 独立且安全的 KV 写入函数（完全独立，不影响原程序）
def save_signal_to_kv(ticker, close, days, since):
    try:
        # 获取环境变量
        account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
        namespace_id = os.environ.get("CLOUDFLARE_KV_NAMESPACE_ID")
        api_token = os.environ.get("CLOUDFLARE_API_TOKEN")
        
        if not all([account_id, namespace_id, api_token]):
            print(f"DEBUG - Missing Configs:")
            print(f"  Account ID: {bool(account_id)}")
            print(f"  Namespace ID: {bool(namespace_id)}")
            print(f"  API Token: {bool(api_token)}")
            return

        vancouver_tz = ZoneInfo("America/Vancouver")
        date_str = datetime.now(vancouver_tz).strftime("%Y-%m-%d")
        key = f"signals:{date_str}:{ticker}"
        
        record = {
            "date": date_str,
            "code": ticker,
            "price": float(close),
            "days": int(days),
            "since": int(since),
            "receivedAt": datetime.now().isoformat() + "Z",
            "source": "scanner"
        }
        
        url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/storage/kv/namespaces/{namespace_id}/values/{key}"
        requests.put(url, headers={"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}, json=record)
    except Exception as e:
        print(f"KV 写入跳过或失败: {e}")

# ═══════════════════════════════════════════════════════════════════
#  EMAIL  (Resend)
# ═══════════════════════════════════════════════════════════════════


RESEND_TO   = [
    "garyfocus@hotmail.com",
    "zhyld13@gmail.com",
]
RESEND_FROM = "AI-选股 <messenger@ceic.ca>"


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
        📡 AI-选股
      </div>
      <div style="margin-top:6px;color:#64748b;font-size:13px;">
        {scan_date} &nbsp;·&nbsp; 
      </div>
    </div>

    <div style="padding:28px 32px;">
      {'<p style="color:#4ade80;font-size:15px;font-weight:600;margin-bottom:16px;">🔔 AI 选股结果</p>' if signals else '<p style="color:#888;font-size:15px;">今天没有符合条件的个股.</p>'}

      {'<table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#1e1e1e;"><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">Ticker</th><th style="padding:8px 12px;text-align:left;color:#64748b;font-weight:500;">名称</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Close</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">分数</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">Since</th><th style="padding:8px 12px;text-align:right;color:#64748b;font-weight:500;">量能</th></tr></thead><tbody>' + signal_rows(signals) + '</tbody></table>' if signals else ''}

      {error_section}
    </div>

    <div style="padding:16px 32px;border-top:1px solid #1e1e1e;text-align:center;font-size:11px;color:#374151;">
      Gary AI 选股 · Automated by GitHub Actions
    </div>
  </div>
</body>
</html>
""", f"Gary AI 选股结果 {scan_date} | {subject_note}"


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
                "to"     : RESEND_TO,
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
    print(f"   Gary AI Scanner  |  {scan_date}")
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
        print("   今天没有符合条件的个股.")
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
