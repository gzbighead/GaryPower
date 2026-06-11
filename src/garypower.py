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
from zoneinfo import ZoneInfo  # 必须引入这个

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
    ("A", "安捷伦科技"),
    ("AA", "美国铝业公司"),
    ("AAL", "美国航空"),
    ("AAOI", "Applied Optoelectronics"),
    ("AAON", "艾伦建材"),
    ("ABBV", "艾伯维公司"),
    ("ABCL", "AbCellera Biologics"),
    ("ABNB", "爱彼迎"),
    ("ABT", "雅培"),
    ("ABVX", "Abivax S.A."),
    ("ACGL", "艾奇资本"),
    ("ACHC", "阿卡迪亚医疗保健"),
    ("ACHR", "Archer Aviation"),
    ("ACLS", "Axcelis Technologies"),
    ("ACMR", "ACM Research"),
    ("ACN", "埃森哲"),
    ("ADBE", "Adobe"),
    ("ADEA", "Adeia"),
    ("ADI", "亚德诺"),
    ("ADM", "Archer Daniels Midland"),
    ("ADP", "自动数据处理"),
    ("ADSK", "欧特克"),
    ("AEE", "阿曼瑞恩"),
    ("AEHR", "Aehr Test Systems"),
    ("AEIS", "先进能源工业"),
    ("AEM", "伊格尔矿业"),
    ("AEVA", "Aeva Technologies"),
    ("AFL", "美国家庭寿险"),
    ("AFRM", "Affirm Holdings"),
    ("AG", "First Majestic Silver"),
    ("AGI", "Alamos Gold"),
    ("AGNC", "美国资本代理公司"),
    ("AGX", "Argan"),
    ("AIG", "美国国际集团"),
    ("AJG", "亚瑟加拉格尔"),
    ("AKAM", "阿克迈"),
    ("ALAB", "Astera Labs"),
    ("ALB", "美国雅保"),
    ("ALGM", "Allegro Microsystems"),
    ("ALGN", "艾利科技"),
    ("ALGT", "忠诚旅游"),
    ("ALHC", "Alignment Healthcare"),
    ("ALKS", "阿尔凯默斯"),
    ("ALL", "好事达"),
    ("ALM", "Almonty Industries"),
    ("ALNY", "阿里拉姆制药"),
    ("AMAT", "应用材料"),
    ("AMBA", "安霸"),
    ("AMD", "美国超微公司"),
    ("AME", "阿美特克"),
    ("AMG", "Affiliated Managers"),
    ("AMGN", "安进"),
    ("AMKR", "艾马克技术"),
    ("AMP", "阿莫斯莱斯金融"),
    ("AMRZ", "Amrize"),
    ("AMSC", "美国超导"),
    ("AMT", "美国电塔"),
    ("ANET", "Arista Networks"),
    ("AON", "怡安保险"),
    ("APA", "阿帕奇石油"),
    ("APD", "Air Products & Chemicals"),
    ("APGE", "Apogee Therapeutics"),
    ("APH", "安费诺"),
    ("APLD", "Applied Digital"),
    ("APO", "阿波罗全球管理"),
    ("APP", "Applovin"),
    ("APPF", "Appfolio"),
    ("APPS", "Digital Turbine"),
    ("APTV", "Aptiv PLC"),
    ("ARCB", "ArcBest"),
    ("ARCC", "阿瑞斯"),
    ("ARES", "Ares Management"),
    ("ARGX", "argenx SE"),
    ("ARM", "Arm Holdings"),
    ("ARRY", "Array Technologies"),
    ("ARWR", "Arrowhead Pharmaceuticals"),
    ("ASML", "阿斯麦"),
    ("ASND", "Ascendis Pharma A/S"),
    ("ASO", "Academy"),
    ("ASPI", "ASP Isotopes"),
    ("ASST", "Strive"),
    ("ASTS", "AST SpaceMobile"),
    ("ASX", "日月光半导体"),
    ("ATI", "ATI Inc"),
    ("ATO", "Atmos Energy"),
    ("AU", "AngloGold Ashanti"),
    ("AUR", "Aurora Innovation"),
    ("AVAV", "AeroVironment"),
    ("AVGO", "博通"),
    ("AVT", "安富利"),
    ("AWK", "美国水务"),
    ("AXON", "Axon Enterprise"),
    ("AXP", "美国运通"),
    ("AXSM", "Axsome Therapeutics"),
    ("AXTI", "AXT Inc"),
    ("AZN", "阿斯利康"),
    ("AZO", "汽车地带"),
    ("B", "Barrick Mining"),
    ("BA", "波音"),
    ("BABA", "阿里巴巴"),
    ("BAC", "美国银行"),
    ("BAND", "Bandwidth"),
    ("BAP", "Credicorp"),
    ("BB", "黑莓"),
    ("BBIO", "BridgeBio Pharma"),
    ("BBY", "百思买"),
    ("BCDA", "BioCardia"),
    ("BDX", "碧迪医疗"),
    ("BE", "Bloom Energy"),
    ("BEAM", "Beam Therapeutics"),
    ("BELFB", "Bel Fuse-B"),
    ("BGMS", "Bio Green Med Solution"),
    ("BHP", "必和必拓"),
    ("BIDU", "百度"),
    ("BIIB", "渤健公司"),
    ("BILI", "哔哩哔哩"),
    ("BJ", "BJ批发俱乐部"),
    ("BKNG", "Booking Holdings"),
    ("BKR", "Baker Hughes"),
    ("BLD", "Topbuild"),
    ("BLDP", "巴拉德动力系统"),
    ("BLK", "贝莱德"),
    ("BLLN", "BillionToOne"),
    ("BMNR", "Bitmine Immersion Technologies"),
    ("BMRN", "拜玛林制药"),
    ("BMY", "施贵宝"),
    ("BNAI", "Brand Engagement Network"),
    ("BNTX", "BioNTech"),
    ("BNY", "纽约梅隆银行"),
    ("BP", "英国石油"),
    ("BPOP", "大众银行"),
    ("BR", "Broadridge金融解决方案"),
    ("BRK.A", "伯克希尔-A"),
    ("BRK.B", "伯克希尔-B"),
    ("BRKR", "布鲁克"),
    ("BRUN", "Boost Run"),
    ("BRZE", "Braze"),
    ("BSX", "波士顿科学"),
    ("BSY", "Bentley Systems"),
    ("BTDR", "Bitdeer Technologies Group"),
    ("BTI", "英美烟草"),
    ("BTSG", "BrightSpring Health Services"),
    ("BULL", "微牛"),
    ("BURL", "伯灵顿百货"),
    ("BWA", "博格华纳"),
    ("BX", "黑石"),
    ("BZ", "BOSS直聘"),
    ("C", "花旗集团"),
    ("CAG", "康尼格拉"),
    ("CAH", "卡地纳健康"),
    ("CAKE", "芝乐坊餐馆"),
    ("CALM", "Cal-Maine Foods"),
    ("CAMT", "康特科技"),
    ("CAR", "安飞士"),
    ("CARR", "开利全球"),
    ("CART", "Maplebear"),
    ("CASY", "Caseys General Stores"),
    ("CAT", "卡特彼勒"),
    ("CB", "安达保险"),
    ("CBRE", "世邦魏理仕"),
    ("CBRS", "Cerebras Systems"),
    ("CBSH", "科默斯银行"),
    ("CCEP", "可口可乐欧洲太平洋"),
    ("CCI", "冠城国际"),
    ("CCJ", "Cameco"),
    ("CCL", "嘉年华邮轮"),
    ("CDE", "科尔黛伦矿业"),
    ("CDNS", "铿腾电子"),
    ("CDW", "CDW Corp"),
    ("CECO", "CECO环保"),
    ("CEG", "Constellation Energy"),
    ("CELC", "Celcuity"),
    ("CELH", "Celsius Holdings"),
    ("CENX", "世纪铝业"),
    ("CEVA", "CEVA Inc"),
    ("CF", "CF工业控股"),
    ("CFG", "Citizens Financial"),
    ("CG", "凯雷"),
    ("CGNX", "康耐视"),
    ("CGON", "CG Oncology"),
    ("CHD", "丘奇&德怀特"),
    ("CHKP", "Check Point软件"),
    ("CHRD", "Chord Energy"),
    ("CHRW", "罗宾逊物流"),
    ("CHTR", "特许通讯"),
    ("CHYM", "Chime Financial"),
    ("CI", "信诺"),
    ("CIEN", "Ciena"),
    ("CIFR", "Cipher Digital"),
    ("CINF", "辛辛纳提金融"),
    ("CL", "高露洁"),
    ("CLF", "克利夫兰克里夫"),
    ("CLS", "天弘科技"),
    ("CLSK", "CleanSpark"),
    ("CLX", "高乐氏"),
    ("CMCSA", "康卡斯特"),
    ("CME", "芝加哥商品交易所"),
    ("CMG", "奇波雷墨西哥烧烤"),
    ("CMI", "康明斯"),
    ("CMND", "Clearmind Medicine"),
    ("CMPS", "COMPASS Pathways"),
    ("CMS", "CMS能源"),
    ("CNC", "康西哥"),
    ("CNQ", "加拿大自然资源"),
    ("CNTA", "Centessa Pharmaceuticals"),
    ("COCO", "Vita Coco"),
    ("COF", "第一资本信贷"),
    ("COGT", "Cogent Biosciences"),
    ("COHR", "Coherent"),
    ("COHU", "科休半导体"),
    ("COIN", "Coinbase"),
    ("COKE", "可口可乐装瓶"),
    ("COLB", "哥伦比亚银行系统"),
    ("COO", "库珀医疗"),
    ("COP", "康菲石油"),
    ("COR", "Cencora"),
    ("CORT", "Corcept医疗"),
    ("CORZ", "Core Scientific"),
    ("COST", "好市多"),
    ("CP", "加拿大太平洋铁路"),
    ("CPB", "金宝公司"),
    ("CPNG", "Coupang"),
    ("CPRT", "科帕特"),
    ("CRCL", "Circle"),
    ("CRDO", "Credo Technology"),
    ("CRH", "CRH水泥"),
    ("CRM", "赛富时"),
    ("CRML", "Critical Metals"),
    ("CROX", "卡骆驰"),
    ("CRS", "卡朋特科技"),
    ("CRSP", "CRISPR Therapeutics"),
    ("CRUS", "凌云半导体"),
    ("CRWV", "CoreWeave"),
    ("CSCO", "思科"),
    ("CSGP", "科斯塔"),
    ("CSIQ", "阿特斯太阳能"),
    ("CSX", "CSX运输"),
    ("CTAS", "信达思"),
    ("CTSH", "高知特"),
    ("CTVA", "Corteva"),
    ("CVCO", "卡寇工业"),
    ("CVE", "Cenovus能源"),
    ("CVLT", "康沃系统"),
    ("CVNA", "Carvana"),
    ("CVS", "西维斯健康"),
    ("CVX", "雪佛龙"),
    ("CWST", "Casella Waste Systems"),
    ("CYTK", "Cytokinetics"),
    ("CZR", "凯撒娱乐"),
    ("D", "道明尼资源"),
    ("DAL", "达美航空"),
    ("DASH", "DoorDash"),
    ("DAVE", "Dave Inc"),
    ("DBX", "Dropbox"),
    ("DDOG", "Datadog"),
    ("DE", "迪尔股份"),
    ("DELL", "戴尔科技"),
    ("DFTX", "Definium Therapeutics"),
    ("DG", "美国达乐公司"),
    ("DGXX", "Digi Power X"),
    ("DHI", "霍顿房屋"),
    ("DHR", "丹纳赫"),
    ("DINO", "HF Sinclair"),
    ("DIOD", "Diodes"),
    ("DIS", "迪士尼"),
    ("DKNG", "DraftKings"),
    ("DKS", "迪克体育用品"),
    ("DLR", "数字房地产信托公司"),
    ("DLTR", "美元树公司"),
    ("DNTH", "Dianthus Therapeutics"),
    ("DOCN", "DigitalOcean"),
    ("DOCU", "DocuSign"),
    ("DOW", "陶氏化学"),
    ("DOX", "Amdocs"),
    ("DPZ", "达美乐比萨"),
    ("DRI", "达登饭店"),
    ("DT", "Dynatrace"),
    ("DTE", "DTE能源"),
    ("DUK", "杜克能源"),
    ("DUOL", "多邻国"),
    ("DVN", "戴文能源"),
    ("DXCM", "德康医疗"),
    ("DXYZ", "Destiny Tech100"),
    ("DY", "戴康工业"),
    ("EA", "艺电"),
    ("EBAY", "eBay"),
    ("ECL", "艺康集团"),
    ("ED", "爱迪生联合电气"),
    ("EEFT", "嘉银通"),
    ("EFX", "艾可菲"),
    ("EG", "Everest Group"),
    ("EL", "雅诗兰黛"),
    ("ELF", "e.l.f. Beauty"),
    ("ELV", "Elevance Health"),
    ("EME", "EMCOR Group"),
    ("EMR", "艾默生电气"),
    ("ENPH", "Enphase Energy"),
    ("ENSG", "恩赛因"),
    ("ENTG", "英特格"),
    ("ENVX", "Enovix"),
    ("EOG", "EOG能源"),
    ("EOSE", "Eos Energy"),
    ("EQIX", "易昆尼克斯"),
    ("EQT", "EQT能源"),
    ("ERAS", "Erasca"),
    ("ERIC", "爱立信"),
    ("ES", "Eversource Energy"),
    ("ESLT", "埃尔比特系统"),
    ("ET", "Energy Transfer"),
    ("ETN", "伊顿"),
    ("ETR", "安特吉"),
    ("EVRG", "西星能源"),
    ("EW", "爱德华生命科学"),
    ("EWBC", "华美银行"),
    ("EWTX", "Edgewise Therapeutics"),
    ("EXC", "爱克斯龙电力"),
    ("EXE", "Expand Energy"),
    ("EXEL", "伊克力西斯"),
    ("EXLS", "伊克赛尔服务"),
    ("EXPD", "康捷国际物流"),
    ("EXPE", "Expedia"),
    ("EXR", "Extra Space Storage"),
    ("F", "福特汽车"),
    ("FANG", "Diamondback Energy"),
    ("FAST", "快扣"),
    ("FCEL", "燃料电池能源"),
    ("FCFS", "第一富金融服务"),
    ("FCNCA", "第一公民银行股份"),
    ("FCX", "麦克莫兰铜金"),
    ("FDX", "联邦快递"),
    ("FDXF", "FEDEX FREIGHT HOLDING CO INC"),
    ("FER", "Ferrovial SE"),
    ("FERG", "Ferguson"),
    ("FFIV", "F5 Inc"),
    ("FICO", "Fair Isaac"),
    ("FIG", "Figma Inc"),
    ("FIGR", "Figure Technology Solutions"),
    ("FIS", "繁德信息技术"),
    ("FISV", "费哲金融服务"),
    ("FITB", "五三银行"),
    ("FIVE", "Five Below"),
    ("FIVN", "Five9"),
    ("FIX", "美国舒适系统"),
    ("FLEX", "伟创力"),
    ("FLNC", "Fluence Energy"),
    ("FLUT", "Flutter Entertainment"),
    ("FLY", "Firefly Aerospace"),
    ("FN", "Fabrinet"),
    ("FNV", "Franco-Nevada"),
    ("FORM", "FormFactor"),
    ("FOX", "福克斯公司-B"),
    ("FOXA", "福克斯公司-A"),
    ("FPS", "Forgent Power Solutions"),
    ("FRMI", "Fermi"),
    ("FROG", "JFrog"),
    ("FRPT", "Freshpet"),
    ("FRSH", "Freshworks"),
    ("FRVO", "FERVO ENERGY COMPANY"),
    ("FSLR", "第一太阳能"),
    ("FSLY", "Fastly"),
    ("FTAI", "FTAI Aviation"),
    ("FTNT", "飞塔信息"),
    ("FUTU", "富途控股"),
    ("FWONK", "Liberty Formula One-C"),
    ("GD", "通用动力"),
    ("GDS", "万国数据"),
    ("GE", "GE航天航空"),
    ("GEHC", "GE HealthCare Technologies"),
    ("GEN", "Gen Digital"),
    ("GEV", "GE Vernova"),
    ("GFI", "金田"),
    ("GFS", "GlobalFoundries"),
    ("GH", "Guardant Health"),
    ("GIII", "G-III服装集团"),
    ("GILD", "吉利德科学"),
    ("GIS", "通用磨坊"),
    ("GLNG", "Golar LNG"),
    ("GLPI", "Gaming & Leisure Properties"),
    ("GLW", "康宁"),
    ("GLXY", "Galaxy Digital"),
    ("GM", "通用汽车"),
    ("GMAB", "Genmab"),
    ("GNRC", "Generac"),
    ("GNTX", "真泰克"),
    ("GOOG", "谷歌-C"),
    ("GOOGL", "谷歌-A"),
    ("GPN", "环汇有限公司"),
    ("GRAB", "Grab Holdings"),
    ("GS", "高盛"),
    ("GSAT", "全球星"),
    ("GSK", "葛兰素史克"),
    ("GTLB", "Gitlab"),
    ("GTX", "Garrett Motion"),
    ("GWRE", "Guidewire Software"),
    ("GWW", "美国固安捷"),
    ("HAL", "哈里伯顿"),
    ("HALO", "奥洛兹美医疗"),
    ("HAS", "孩之宝"),
    ("HBAN", "亨廷顿银行"),
    ("HBM", "Hudbay Minerals"),
    ("HCA", "HCA医疗"),
    ("HD", "家得宝"),
    ("HDB", "HDFC银行"),
    ("HIG", "哈特福德金融"),
    ("HIMS", "Hims & Hers Health"),
    ("HIMX", "奇景光电"),
    ("HIVE", "HIVE Digital Technologies"),
    ("HL", "赫克拉矿业"),
    ("HLIT", "谐波"),
    ("HLNE", "Hamilton Lane"),
    ("HLT", "希尔顿酒店"),
    ("HON", "霍尼韦尔"),
    ("HOOD", "Robinhood"),
    ("HPE", "慧与科技"),
    ("HPQ", "惠普"),
    ("HQY", "HealthEquity"),
    ("HSBC", "汇丰控股"),
    ("HSIC", "汉瑞祥"),
    ("HST", "美国豪斯特酒店"),
    ("HSY", "好时"),
    ("HTHT", "华住"),
    ("HUBB", "哈勃集团"),
    ("HUBS", "HubSpot"),
    ("HUM", "哈门那"),
    ("HUT", "Hut 8"),
    ("HWC", "汉考克惠特尼"),
    ("HWM", "Howmet Aerospace"),
    ("HYMC", "Hycroft Mining"),
    ("IBKR", "盈透证券"),
    ("IBM", "IBM Corp"),
    ("IBN", "印度工业信贷投资银行"),
    ("IBRX", "ImmunityBio"),
    ("ICE", "洲际交易所"),
    ("ICHR", "Ichor Holdings"),
    ("ICLR", "Icon PLC"),
    ("IDCC", "InterDigital"),
    ("IDXX", "爱德士"),
    ("IESC", "IES Holdings"),
    ("ILMN", "Illumina"),
    ("INCY", "因塞特"),
    ("INDV", "Indivior"),
    ("INFQ", "Infleqtion"),
    ("INIO", "INNIO N.V"),
    ("INOD", "Innodata"),
    ("INSM", "Insmed"),
    ("INTC", "英特尔"),
    ("INTU", "财捷"),
    ("IONQ", "IonQ Inc"),
    ("IONS", "Ionis Pharmaceuticals"),
    ("IOT", "Samsara"),
    ("IOVA", "Iovance Biotherapeutics"),
    ("IQV", "艾昆纬"),
    ("IR", "英格索兰"),
    ("IRDM", "铱星通讯"),
    ("IREN", "IREN Ltd"),
    ("IRM", "铁山"),
    ("IRTC", "iRhythm Technologies"),
    ("ISRG", "直觉外科公司"),
    ("IT", "加特纳"),
    ("ITRI", "伊管"),
    ("ITUB", "Itaú巴西联合银行"),
    ("ITW", "伊利诺伊机械"),
    ("IVZ", "景顺"),
    ("JAZZ", "爵士制药"),
    ("JBHT", "JB亨特运输服务"),
    ("JBL", "捷普科技"),
    ("JBLU", "捷蓝航空"),
    ("JCI", "江森自控"),
    ("JD", "京东"),
    ("JKHY", "杰克亨利"),
    ("JNJ", "强生"),
    ("JOBY", "Joby Aviation"),
    ("JPM", "摩根大通"),
    ("KDP", "Keurig Dr Pepper"),
    ("KEEL", "Keel Infrastructure"),
    ("KEY", "KeyCorp"),
    ("KEYS", "Keysight Technologies"),
    ("KGC", "金罗斯黄金"),
    ("KHC", "卡夫亨氏"),
    ("KKR", "KKR & Co"),
    ("KLAC", "科磊"),
    ("KLIC", "库力索法半导体"),
    ("KMB", "金佰利"),
    ("KMI", "金德尔摩根"),
    ("KNX", "Knight-Swift Transportation"),
    ("KO", "可口可乐"),
    ("KOPN", "高平电子"),
    ("KR", "克罗格"),
    ("KRYS", "Krystal Biotech"),
    ("KSPI", "Kaspi.kz"),
    ("KTOS", "克瑞拓斯安全防卫"),
    ("KVUE", "Kenvue"),
    ("LAES", "SEALSQ Corp"),
    ("LAMR", "拉马尔户外广告"),
    ("LASE", "Laser Photonics"),
    ("LASR", "nLIGHT"),
    ("LCID", "Lucid Group"),
    ("LECO", "林肯电气"),
    ("LEGN", "传奇生物"),
    ("LEN", "莱纳建筑"),
    ("LEU", "Centrus Energy"),
    ("LFTO", "Liftoff Mobile"),
    ("LFUS", "美国力特保险丝"),
    ("LGN", "Legence"),
    ("LHX", "L3Harris Technologies"),
    ("LI", "理想汽车"),
    ("LIN", "林德气体"),
    ("LITE", "Lumentum"),
    ("LKQ", "LKQ Corp"),
    ("LLY", "礼来"),
    ("LMT", "洛克希德马丁"),
    ("LNG", "Cheniere Energy"),
    ("LNT", "美国联合能源"),
    ("LNTH", "Lantheus"),
    ("LOGI", "罗技"),
    ("LOW", "劳氏"),
    ("LPLA", "LPL Financial"),
    ("LPTH", "LightPath Technologies"),
    ("LQDA", "Liquidia"),
    ("LRCX", "泛林集团"),
    ("LSCC", "莱迪思半导体"),
    ("LSTR", "莱帝运输"),
    ("LULU", "Lululemon Athletica"),
    ("LUNR", "Intuitive Machines"),
    ("LUV", "西南航空"),
    ("LWLG", "Lightwave Logic"),
    ("LYB", "利安德巴塞尔"),
    ("LYFT", "Lyft Inc"),
    ("LYV", "Live Nation Entertainment"),
    ("MA", "万事达"),
    ("MANH", "Manhattan Associates"),
    ("MAR", "万豪酒店"),
    ("MARA", "MARA Holdings"),
    ("MAS", "马斯科"),
    ("MASI", "麦斯莫医疗"),
    ("MASK", "3 E Network Technology"),
    ("MAT", "美泰"),
    ("MBLY", "Mobileye Global"),
    ("MCD", "麦当劳"),
    ("MCHP", "微芯科技"),
    ("MCK", "麦克森"),
    ("MCO", "穆迪"),
    ("MDB", "MongoDB"),
    ("MDGL", "Madrigal Pharmaceuticals"),
    ("MDLN", "Medline"),
    ("MDLZ", "亿滋"),
    ("MDT", "美敦力"),
    ("MEDP", "Medpace"),
    ("MELI", "MercadoLibre"),
    ("MET", "大都会人寿"),
    ("META", "Meta Platforms"),
    ("MIDD", "The Middleby"),
    ("MIRM", "Mirum Pharmaceuticals"),
    ("MKSI", "MKS仪器"),
    ("MKTX", "MarketAxess"),
    ("MLM", "马丁-玛丽埃塔材料"),
    ("MLYS", "Mineralys Therapeutics"),
    ("MMM", "3M"),
    ("MNDY", "monday.com"),
    ("MNST", "怪物饮料"),
    ("MNTS", "Momentus"),
    ("MO", "奥驰亚"),
    ("MOD", "摩丁制造"),
    ("MORN", "晨星"),
    ("MOS", "美国美盛"),
    ("MP", "MP Materials"),
    ("MPC", "马拉松原油"),
    ("MPWR", "Monolithic Power Systems"),
    ("MRAM", "Everspin Technologies"),
    ("MRCY", "Mercury Systems"),
    ("MRK", "默沙东"),
    ("MRLN", "Merlin Inc"),
    ("MRNA", "Moderna"),
    ("MRSH", "达信"),
    ("MS", "摩根士丹利"),
    ("MSCI", "MSCI Inc"),
    ("MSI", "摩托罗拉解决方案"),
    ("MSTR", "Strategy"),
    ("MTB", "美国制商银行"),
    ("MTCH", "Match group"),
    ("MTD", "梅特勒-托利多"),
    ("MTSI", "MACOM Technology Solutions"),
    ("MTZ", "MasTec"),
    ("MU", "美光科技"),
    ("MXL", "MaxLinear"),
    ("MYRG", "MYR Group"),
    ("NAVN", "Navan"),
    ("NBIS", "NEBIUS"),
    ("NBIX", "神经分泌生物科学"),
    ("NCLH", "挪威邮轮"),
    ("NDAQ", "纳斯达克"),
    ("NDSN", "Nordson"),
    ("NEE", "新纪元能源"),
    ("NEM", "纽曼矿业"),
    ("NET", "Cloudflare"),
    ("NFLX", "奈飞"),
    ("NICE", "NICE Ltd"),
    ("NIO", "蔚来"),
    ("NKE", "耐克"),
    ("NKTR", "内克塔治疗"),
    ("NN", "NextNav"),
    ("NNE", "NANO Nuclear Energy"),
    ("NOC", "诺斯罗普格鲁曼"),
    ("NOK", "诺基亚"),
    ("NOTV", "Inotiv"),
    ("NOVT", "Novanta"),
    ("NOVTU", "NOVANTA INC TANGIBLE EQUITY UNIT(01/11/2028)"),
    ("NOW", "ServiceNow"),
    ("NRG", "NRG Energy"),
    ("NSC", "诺福克南方"),
    ("NSIT", "Insight Enterprises"),
    ("NTAP", "美国网存"),
    ("NTES", "网易"),
    ("NTLA", "Intellia Therapeutics"),
    ("NTNX", "Nutanix"),
    ("NTRA", "Natera"),
    ("NTRS", "北方信托"),
    ("NTSK", "Netskope"),
    ("NU", "Nu Holdings"),
    ("NUAI", "New Era Energy & Digital"),
    ("NUE", "纽柯钢铁"),
    ("NUVL", "Nuvalent"),
    ("NVMI", "Nova"),
    ("NVO", "诺和诺德"),
    ("NVS", "诺华制药"),
    ("NVT", "nVent Electric"),
    ("NVTS", "纳微半导体"),
    ("NWL", "纽威"),
    ("NWSA", "新闻集团-A"),
    ("NXPI", "恩智浦"),
    ("NXT", "Nextpower"),
    ("O", "Realty Income"),
    ("ODFL", "Old Dominion Freight Line"),
    ("OKE", "欧尼克(万欧卡)"),
    ("OKLO", "Oklo Inc"),
    ("OKTA", "Okta"),
    ("OLED", "Universal Display"),
    ("OLLI", "Ollie's Bargain Outlet"),
    ("OMC", "宏盟集团"),
    ("ON", "安森美半导体"),
    ("ONB", "Old National Bancorp"),
    ("ONC", "百济神州"),
    ("ONDS", "Ondas"),
    ("ONTO", "Onto Innovation"),
    ("OPCH", "Option Care Health"),
    ("OPEN", "Opendoor Technologies"),
    ("ORCL", "甲骨文"),
    ("ORKA", "Oruka Therapeutics"),
    ("ORLY", "奥莱利"),
    ("OSCR", "Oscar Health"),
    ("OTIS", "奥的斯"),
    ("OUST", "Ouster"),
    ("OWL", "Blue Owl Capital"),
    ("OXY", "西方石油"),
    ("OZK", "欧扎克银行"),
    ("P", "Everpure"),
    ("PAA", "Plains All American Pipeline"),
    ("PAAS", "泛美白银"),
    ("PANW", "Palo Alto Networks"),
    ("PATH", "UiPath"),
    ("PAYX", "沛齐"),
    ("PBR", "巴西石油公司"),
    ("PCAR", "帕卡"),
    ("PCG", "太平洋煤电"),
    ("PCT", "PureCycle Technologies"),
    ("PCTY", "Paylocity"),
    ("PCVX", "Vaxcyte"),
    ("PDD", "拼多多"),
    ("PEGA", "Pegasystems"),
    ("PENG", "Penguin Solutions"),
    ("PENN", "佩恩国民博彩"),
    ("PEP", "百事可乐"),
    ("PFE", "辉瑞"),
    ("PFG", "信安金融"),
    ("PG", "宝洁"),
    ("PGR", "前进保险"),
    ("PGY", "Pagaya Technologies"),
    ("PH", "派克汉尼汾"),
    ("PI", "Impinj"),
    ("PINS", "Pinterest"),
    ("PL", "Planet Labs PBC"),
    ("PLAB", "福尼克斯"),
    ("PLD", "安博"),
    ("PLUG", "普拉格能源"),
    ("PLXS", "普雷克萨斯"),
    ("PM", "菲利普莫里斯"),
    ("PNC", "PNC金融服务集团"),
    ("PODD", "银休特"),
    ("POET", "POET Technologies"),
    ("PONY", "小马智行"),
    ("POOL", "Pool Corp"),
    ("POWI", "帕沃英蒂格盛"),
    ("POWL", "Powell Industries"),
    ("PPC", "Pilgrim's Pride"),
    ("PPG", "PPG工业"),
    ("PPL", "宾州电力"),
    ("PPTA", "Perpetua Resources"),
    ("PRAX", "Praxis Precision Medicines"),
    ("PRIM", "Primoris Services"),
    ("PRU", "保德信金融"),
    ("PSA", "公共存储公司"),
    ("PSKY", "Paramount Skydance"),
    ("PSMT", "普尔斯玛特"),
    ("PSX", "Phillips 66"),
    ("PTC", "PTC Inc"),
    ("PTCT", "PTC Therapeutics"),
    ("PTEN", "Patterson-UTI Energy"),
    ("PTGX", "Protagonist Therapeutics"),
    ("PTON", "Peloton Interactive"),
    ("PURR", "HYPERLIQUID STRATEGIES INC"),
    ("PWR", "广达服务"),
    ("PYPL", "PayPal"),
    ("Q", "Qnity Electronics"),
    ("QBTS", "D-Wave Quantum"),
    ("QCOM", "高通"),
    ("QLYS", "科力斯"),
    ("QNT", "QUANTINUUM INC"),
    ("QRVO", "Qorvo"),
    ("QS", "QuantumScape"),
    ("QSR", "餐饮品牌国际"),
    ("QUBT", "Quantum Computing"),
    ("QXO", "QXO Inc"),
    ("RBLX", "Roblox"),
    ("RBRK", "Rubrik"),
    ("RCAT", "Red Cat Holdings"),
    ("RCL", "皇家加勒比邮轮"),
    ("RDDT", "Reddit"),
    ("RDNT", "RadNet"),
    ("RDW", "Redwire"),
    ("REG", "Regency Centers Corp."),
    ("REGN", "再生元制药公司"),
    ("RELY", "Remitly Global"),
    ("RF", "地区金融"),
    ("RGEN", "Repligen"),
    ("RGLD", "皇家黄金"),
    ("RGTI", "Rigetti Computing"),
    ("RIO", "力拓"),
    ("RIOT", "Riot Platforms"),
    ("RIVN", "Rivian Automotive"),
    ("RKT", "Rocket"),
    ("RL", "拉夫劳伦"),
    ("RLAY", "Relay Therapeutics"),
    ("RMBS", "Rambus"),
    ("RMD", "瑞思迈"),
    ("RMSG", "Real Messenger"),
    ("ROIV", "Roivant Sciences"),
    ("ROK", "罗克韦尔自动化"),
    ("ROKU", "Roku Inc"),
    ("ROL", "Rollins"),
    ("ROP", "儒博实业"),
    ("ROST", "罗斯百货"),
    ("RPRX", "Royalty Pharma"),
    ("RSG", "共和废品处理"),
    ("RTX", "雷神技术"),
    ("RUN", "Sunrun"),
    ("RVMD", "Revolution Medicines"),
    ("RXRX", "Recursion Pharmaceuticals"),
    ("RXT", "Rackspace Technology"),
    ("RY", "加拿大皇家银行"),
    ("RYAAY", "Ryanair"),
    ("RZLV", "Rezolve AI"),
    ("SAIA", "Saia"),
    ("SAIC", "Science Applications International"),
    ("SAIL", "SailPoint"),
    ("SANM", "新美亚电子"),
    ("SAP", "SAP SE"),
    ("SATA", "STRIVE INC PERP PFD SER A VAR RATE"),
    ("SATL", "Satellogic"),
    ("SATS", "回声星通信"),
    ("SBAC", "SBA通信公司"),
    ("SBET", "SharpLink"),
    ("SBRA", "Sabra Health Care REIT"),
    ("SBUX", "星巴克"),
    ("SCAG", "Scage Future"),
    ("SCCO", "南方铜业"),
    ("SCHW", "嘉信理财"),
    ("SCI", "Service Corporation International"),
    ("SE", "Sea"),
    ("SEDG", "SolarEdge Technologies"),
    ("SEI", "Solaris Energy Infrastructure"),
    ("SEIC", "SEI Investments"),
    ("SERV", "Serve Robotics"),
    ("SEZL", "Sezzle"),
    ("SFM", "Sprouts Farmers Market"),
    ("SHAZ", "SharonAI Holdings"),
    ("SHEL", "壳牌"),
    ("SHLS", "Shoals Technologies"),
    ("SHOP", "Shopify"),
    ("SHW", "宣伟公司"),
    ("SIDU", "Sidus Space"),
    ("SIMO", "慧荣科技"),
    ("SIRI", "Sirius XM"),
    ("SITM", "SiTime"),
    ("SJM", "斯马克"),
    ("SLAB", "芯科实验室"),
    ("SLB", "斯伦贝谢"),
    ("SLM", "学贷美"),
    ("SLS", "Sellas Life Sciences"),
    ("SMCI", "超微电脑"),
    ("SMMT", "Summit Therapeutics"),
    ("SMR", "NuScale Power"),
    ("SMTC", "先科电子"),
    ("SMTK", "SmartKem"),
    ("SN", "SharkNinja"),
    ("SNAP", "Snap Inc"),
    ("SNBR", "Sleep Number"),
    ("SNDK", "闪迪"),
    ("SNEX", "StoneX"),
    ("SNOW", "Snowflake"),
    ("SNPS", "新思科技"),
    ("SNY", "赛诺菲安万特"),
    ("SO", "美国南方公司"),
    ("SOFI", "SoFi Technologies"),
    ("SOLS", "Solstice Advanced Materials"),
    ("SOUN", "SoundHound AI"),
    ("SPG", "西蒙地产"),
    ("SPGI", "标普全球"),
    ("SPHL", "Springview Holdings"),
    ("SPOT", "Spotify Technology"),
    ("SRE", "桑普拉能源"),
    ("SRRK", "Scholar Rock"),
    ("SSNC", "SS&C Technologies"),
    ("SSRM", "SSR Mining"),
    ("STAK", "斯塔克工业"),
    ("STE", "思泰瑞医疗"),
    ("STI", "Solidion Technology"),
    ("STLD", "Steel Dynamics"),
    ("STM", "意法半导体"),
    ("STRC", "STRATEGY INC VAR RT SER A PERP STRETCH PREFERRED STK"),
    ("STRL", "Sterling Infrastructure"),
    ("STT", "道富银行"),
    ("STX", "希捷科技"),
    ("STZ", "星座品牌"),
    ("SU", "森科能源"),
    ("SUNB", "Sunbelt Rentals Holdings"),
    ("SWKS", "思佳讯"),
    ("SYF", "Synchrony Financial"),
    ("SYK", "史赛克"),
    ("SYM", "Symbotic"),
    ("SYNA", "Synaptics"),
    ("SYRE", "Spyre Therapeutics"),
    ("SYY", "西思科公司"),
    ("T", "AT&T"),
    ("TCBI", "Texas Capital Bancshares"),
    ("TCOM", "携程网"),
    ("TD", "多伦多道明银行"),
    ("TDG", "TransDigm"),
    ("TE", "T1 Energy"),
    ("TEAM", "Atlassian"),
    ("TECH", "Bio-Techne"),
    ("TECK", "泰克资源有限公司"),
    ("TEL", "泰科电子"),
    ("TEM", "Tempus AI"),
    ("TENB", "Tenable Holdings"),
    ("TER", "泰瑞达"),
    ("TEVA", "梯瓦制药"),
    ("TFC", "Truist Financial"),
    ("TGT", "塔吉特"),
    ("TGTX", "TG Therapeutics"),
    ("TIGO", "Millicom International Cellular"),
    ("TJX", "TJX公司"),
    ("TKO", "TKO Group Holdings"),
    ("TLN", "Talen Energy"),
    ("TMDX", "TransMedics"),
    ("TMHC", "Taylor Morrison Home"),
    ("TMO", "赛默飞世尔"),
    ("TMUS", "T-Mobile US"),
    ("TNGX", "Tango Therapeutics"),
    ("TOST", "Toast"),
    ("TPG", "TPG Inc"),
    ("TPR", "Tapestry"),
    ("TRGP", "Targa Resources"),
    ("TRI", "汤森路透"),
    ("TRMB", "天宝导航公司"),
    ("TROW", "普信集团"),
    ("TRV", "旅行者财产险集团"),
    ("TSCO", "拖拉机供应公司"),
    ("TSEM", "Tower半导体"),
    ("TSM", "台积电"),
    ("TSN", "泰森食品"),
    ("TT", "Trane技术"),
    ("TTAN", "ServiceTitan"),
    ("TTD", "The Trade Desk"),
    ("TTEK", "德照科技"),
    ("TTMI", "TTM科技"),
    ("TTWO", "Take-Two互动软件"),
    ("TVTX", "Travere Therapeutic"),
    ("TW", "Tradeweb Markets"),
    ("TWLO", "Twilio"),
    ("TWST", "Twist Bioscience"),
    ("TXG", "10x Genomics"),
    ("TXN", "德州仪器"),
    ("TXRH", "德州公路酒吧"),
    ("TYL", "泰勒科技"),
    ("U", "Unity Software"),
    ("UAL", "联合大陆航空"),
    ("UBER", "优步"),
    ("UCTT", "超科林半导体"),
    ("UFPT", "UFP技术"),
    ("UHS", "Universal Health Services"),
    ("UL", "联合利华(英国)"),
    ("ULTA", "Ulta美容"),
    ("UMBF", "UMB金融"),
    ("UMC", "联电"),
    ("UNH", "联合健康"),
    ("UNP", "联合太平洋"),
    ("UPS", "联合包裹"),
    ("UPST", "Upstart"),
    ("URBN", "都市服饰"),
    ("URI", "联合租赁"),
    ("USAR", "USA Rare Earth"),
    ("USB", "美国合众银行"),
    ("USFD", "美国食品控股"),
    ("UTHR", "美国联合医疗"),
    ("V", "Visa"),
    ("VALE", "淡水河谷"),
    ("VCYT", "Veracyte"),
    ("VECO", "维易科精密仪器"),
    ("VEEV", "Veeva Systems"),
    ("VELO", "Velo3D"),
    ("VIAV", "Viavi Solutions"),
    ("VICI", "VICI Properties"),
    ("VICR", "Vicor电子"),
    ("VISN", "Vistance Networks"),
    ("VKTX", "Viking Therapeutics"),
    ("VLO", "瓦莱罗能源"),
    ("VLY", "硅谷国家银行"),
    ("VMC", "火神材料"),
    ("VNET", "世纪互联"),
    ("VNOM", "Viper Energy"),
    ("VRNS", "Varonis系统"),
    ("VRSK", "Verisk分析"),
    ("VRSN", "威瑞信"),
    ("VRT", "Vertiv Holdings"),
    ("VRTX", "福泰制药"),
    ("VSAT", "卫讯公司"),
    ("VSEC", "VSE技术服务"),
    ("VSH", "威世科技"),
    ("VST", "Vistra Energy"),
    ("VSXY", "维多利亚的秘密"),
    ("VTR", "芬塔公司"),
    ("VTRS", "Viatris"),
    ("VVOS", "Vivos Therapeutics"),
    ("VZ", "Verizon"),
    ("W", "Wayfair"),
    ("WAT", "沃特世"),
    ("WBD", "Warner Bros Discovery"),
    ("WCN", "Waste Connections"),
    ("WDAY", "Workday"),
    ("WDC", "西部数据"),
    ("WEC", "威州能源"),
    ("WELL", "Welltower"),
    ("WEN", "温蒂汉堡"),
    ("WFC", "富国银行"),
    ("WFRD", "Weatherford国际"),
    ("WGS", "GeneDx Holdings"),
    ("WING", "Wingstop"),
    ("WIX", "Wix.com"),
    ("WM", "美国废物管理"),
    ("WMB", "威廉姆斯"),
    ("WMG", "华纳音乐"),
    ("WMS", "Advanced Drainage"),
    ("WMT", "沃尔玛"),
    ("WOLF", "Wolfspeed"),
    ("WPM", "Wheaton Precious Metals"),
    ("WSC", "WillScot Holdings"),
    ("WST", "West Pharmaceutical Services"),
    ("WTFC", "信达金融"),
    ("WTW", "韦莱韬悦"),
    ("WULF", "TeraWulf"),
    ("WWD", "伍德沃德"),
    ("WYNN", "永利度假村"),
    ("XE", "X-Energy"),
    ("XEL", "埃克西尔能源"),
    ("XENE", "Xenon制药"),
    ("XMTR", "Xometry"),
    ("XNDU", "哈纳杜量子技术"),
    ("XOM", "埃克森美孚"),
    ("XP", "XP Inc"),
    ("XPO", "XPO"),
    ("XYL", "赛莱默"),
    ("XYZ", "Block"),
    ("YUM", "Yum! Brands"),
    ("Z", "Zillow-C"),
    ("ZBRA", "斑马技术"),
    ("ZETA", "Zeta Global"),
    ("ZION", "齐昂银行"),
    ("ZM", "Zoom通讯"),
    ("ZS", "Zscaler"),
    ("ZTS", "Zoetis"),
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
    "gary@ceic.ca",
]
RESEND_FROM = "美股选股 <messenger@ceic.ca>"


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
