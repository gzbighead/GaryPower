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
("A", "安捷伦科技"),
("AA", "美国铝业公司"),
("AAPL", "苹果"),
("ABBV", "艾伯维公司"),
("ABEV", "Ambev SA"),
("ABNB", "爱彼迎"),
("ABT", "雅培"),
("ACGL", "艾奇资本"),
("ACN", "埃森哲"),
("ADBE", "Adobe"),
("ADI", "亚德诺"),
("ADM", "Archer Daniels Midland"),
("ADP", "自动数据处理"),
("ADSK", "欧特克"),
("AEE", "阿曼瑞恩"),
("AEM", "伊格尔矿业"),
("AEP", "美国电力"),
("AER", "AerCap飞机租赁"),
("AFL", "美国家庭寿险"),
("AFRM", "Affirm Holdings"),
("AIG", "美国国际集团"),
("AJG", "亚瑟加拉格尔"),
("AKAM", "阿克迈"),
("ALAB", "Astera Labs"),
("ALB", "美国雅保"),
("ALC", "Alcon"),
("ALL", "好事达"),
("ALNY", "阿里拉姆制药"),
("AMAT", "应用材料"),
("AMCR", "Amcor"),
("AMD", "美国超微公司"),
("AME", "阿美特克"),
("AMGN", "安进"),
("AMKR", "艾马克技术"),
("AMP", "阿莫斯莱斯金融"),
("AMRZ", "Amrize"),
("AMT", "美国电塔"),
("AMX", "美洲移动"),
("AMZN", "亚马逊"),
("ANET", "Arista Networks"),
("AON", "怡安保险"),
("APD", "Air Products & Chemicals"),
("APG", "APi Group"),
("APH", "安费诺"),
("APO", "阿波罗全球管理"),
("APP", "Applovin"),
("ARES", "Ares Management"),
("ARGX", "argenx SE"),
("ARM", "Arm Holdings"),
("ARXS", "Arxis"),
("AS", "亚玛芬体育"),
("ASML", "阿斯麦"),
("ASTS", "AST SpaceMobile"),
("ASX", "日月光半导体"),
("ATI", "ATI Inc"),
("ATO", "Atmos Energy"),
("AU", "AngloGold Ashanti"),
("AVB", "阿湾物产"),
("AVGO", "博通"),
("AWK", "美国水务"),
("AXIA", "AXIA Energia"),
("AXIA.PR", "AXIA ENERGIA SPON ADR EA RE 1 PRF B1 SHS"),
("AXON", "Axon Enterprise"),
("AXP", "美国运通"),
("AZN", "阿斯利康"),
("AZO", "汽车地带"),
("B", "Barrick Mining"),
("BA", "波音"),
("BABA", "阿里巴巴"),
("BAC", "美国银行"),
("BALL", "鲍尔包装"),
("BAM", "布鲁克菲尔德资产管理"),
("BAP", "Credicorp"),
("BBD", "布拉德斯科银行-Preferred"),
("BBDO", "布拉德斯科银行-Common"),
("BBVA", "西班牙毕尔巴鄂银行"),
("BBY", "百思买"),
("BCE", "加拿大贝尔"),
("BCH", "智利银行"),
("BCS", "巴克莱银行"),
("BDX", "碧迪医疗"),
("BE", "Bloom Energy"),
("BEKE", "贝壳"),
("BEN", "Franklin Resources"),
("BG", "邦吉"),
("BHP", "必和必拓"),
("BIDU", "百度"),
("BIIB", "渤健公司"),
("BIP", "Brookfield基础设施"),
("BKNG", "Booking Holdings"),
("BKR", "Baker Hughes"),
("BLK", "贝莱德"),
("BMO", "蒙特利尔银行"),
("BMY", "施贵宝"),
("BN", "Brookfield"),
("BNS", "丰业银行"),
("BNT", "Brookfield Wealth Solutions"),
("BNTX", "BioNTech"),
("BNY", "纽约梅隆银行"),
("BP", "英国石油"),
("BR", "Broadridge金融解决方案"),
("BRK.A", "伯克希尔-A"),
("BRK.B", "伯克希尔-B"),
("BRO", "Brown & Brown"),
("BSAC", "智利桑坦德银行(智利)"),
("BSBR", "桑坦德银行(巴西)"),
("BSX", "波士顿科学"),
("BTI", "英美烟草"),
("BUD", "百威英博"),
("BURL", "伯灵顿百货"),
("BWA", "博格华纳"),
("BWXT", "BWX Technologies"),
("BX", "黑石"),
("C", "花旗集团"),
("CAH", "卡地纳健康"),
("CARR", "开利全球"),
("CASY", "Caseys General Stores"),
("CAT", "卡特彼勒"),
("CB", "安达保险"),
("CBRE", "世邦魏理仕"),
("CBRS", "Cerebras Systems"),
("CCEP", "可口可乐欧洲太平洋"),
("CCI", "冠城国际"),
("CCJ", "Cameco"),
("CCL", "嘉年华邮轮"),
("CCZ", "COMCAST HOLDINGS CORPORATION 2% CNV PREF SEC15/10/2029 USD71"),
("CDE", "科尔黛伦矿业"),
("CDNS", "铿腾电子"),
("CDW", "CDW Corp"),
("CEG", "Constellation Energy"),
("CF", "CF工业控股"),
("CFG", "Citizens Financial"),
("CG", "凯雷"),
("CHD", "丘奇&德怀特"),
("CHRW", "罗宾逊物流"),
("CHT", "中华电信"),
("CHTR", "特许通讯"),
("CI", "信诺"),
("CIB", "哥伦比亚银行"),
("CIEN", "Ciena"),
("CINF", "辛辛纳提金融"),
("CL", "高露洁"),
("CLH", "Clean Harbors"),
("CLS", "天弘科技"),
("CM", "加拿大帝国商业银行"),
("CMCSA", "康卡斯特"),
("CME", "芝加哥商品交易所"),
("CMG", "奇波雷墨西哥烧烤"),
("CMI", "康明斯"),
("CMS", "CMS能源"),
("CNC", "康西哥"),
("CNI", "加拿大国家铁路"),
("CNP", "中点能源"),
("CNQ", "加拿大自然资源"),
("COF", "第一资本信贷"),
("COHR", "Coherent"),
("COIN", "Coinbase"),
("COP", "康菲石油"),
("COR", "Cencora"),
("COST", "好市多"),
("CP", "加拿大太平洋铁路"),
("CPAY", "Corpay"),
("CPNG", "Coupang"),
("CPRT", "科帕特"),
("CQP", "Cheniere Energy Partners LP"),
("CRCL", "Circle"),
("CRDO", "Credo Technology"),
("CRH", "CRH水泥"),
("CRM", "赛富时"),
("CRS", "卡朋特科技"),
("CRWD", "CrowdStrike"),
("CRWV", "CoreWeave"),
("CSCO", "思科"),
("CSX", "CSX运输"),
("CTAS", "信达思"),
("CTSH", "高知特"),
("CTVA", "Corteva"),
("CVE", "Cenovus能源"),
("CVNA", "Carvana"),
("CVS", "西维斯健康"),
("CVX", "雪佛龙"),
("CW", "寇蒂斯莱特"),
("CX", "西麦斯"),
("D", "道明尼资源"),
("DAL", "达美航空"),
("DASH", "DoorDash"),
("DB", "德意志银行"),
("DD", "杜邦"),
("DDOG", "Datadog"),
("DE", "迪尔股份"),
("DECK", "Deckers Outdoor"),
("DELL", "戴尔科技"),
("DEO", "帝亚吉欧"),
("DG", "美国达乐公司"),
("DGX", "奎斯特诊疗"),
("DHI", "霍顿房屋"),
("DHR", "丹纳赫"),
("DIS", "迪士尼"),
("DKNG", "DraftKings"),
("DKS", "迪克体育用品"),
("DLR", "数字房地产信托公司"),
("DLTR", "美元树公司"),
("DOCN", "DigitalOcean"),
("DOV", "都福集团"),
("DOW", "陶氏化学"),
("DRI", "达登饭店"),
("DTE", "DTE能源"),
("DUK", "杜克能源"),
("DVN", "戴文能源"),
("DXCM", "德康医疗"),
("E", "埃尼石油"),
("EA", "艺电"),
("EBAY", "eBay"),
("EC", "哥伦比亚国家石油"),
("ECL", "艺康集团"),
("ED", "爱迪生联合电气"),
("EFX", "艾可菲"),
("EIX", "爱迪生国际"),
("EL", "雅诗兰黛"),
("ELV", "Elevance Health"),
("EMA", "Emera"),
("EME", "EMCOR Group"),
("EMR", "艾默生电气"),
("ENB", "恩桥"),
("ENBA", "Enbridge Inc."),
("ENTG", "英特格"),
("EOG", "EOG能源"),
("EPD", "Enterprise Products"),
("EQIX", "易昆尼克斯"),
("EQNR", "Equinor"),
("EQR", "资产住宅公司"),
("EQT", "EQT能源"),
("ERIC", "爱立信"),
("ES", "Eversource Energy"),
("ESLT", "埃尔比特系统"),
("ESS", "埃塞克斯信托"),
("ET", "Energy Transfer"),
("ETN", "伊顿"),
("ETR", "安特吉"),
("EVRG", "西星能源"),
("EW", "爱德华生命科学"),
("EWBC", "华美银行"),
("EXC", "爱克斯龙电力"),
("EXE", "Expand Energy"),
("EXPD", "康捷国际物流"),
("EXPE", "Expedia"),
("EXR", "Extra Space Storage"),
("F", "福特汽车"),
("FANG", "Diamondback Energy"),
("FAST", "快扣"),
("FCNCA", "第一公民银行股份"),
("FCX", "麦克莫兰铜金"),
("FDX", "联邦快递"),
("FDXF", "FEDEX FREIGHT HOLDING CO INC"),
("FE", "第一能源"),
("FER", "Ferrovial SE"),
("FERG", "Ferguson"),
("FFIV", "F5 Inc"),
("FICO", "Fair Isaac"),
("FIS", "繁德信息技术"),
("FISV", "费哲金融服务"),
("FITB", "五三银行"),
("FIX", "美国舒适系统"),
("FLEX", "伟创力"),
("FLUT", "Flutter Entertainment"),
("FMX", "FEMSA"),
("FN", "Fabrinet"),
("FNV", "Franco-Nevada"),
("FOX", "福克斯公司-B"),
("FOXA", "福克斯公司-A"),
("FPS", "Forgent Power Solutions"),
("FSLR", "第一太阳能"),
("FTAI", "FTAI Aviation"),
("FTI", "德希尼布FMC"),
("FTNT", "飞塔信息"),
("FTS", "Fortis"),
("FTV", "Fortive"),
("FWONA", "Liberty Formula One-A"),
("FWONK", "Liberty Formula One-C"),
("GD", "通用动力"),
("GE", "GE航天航空"),
("GEHC", "GE HealthCare Technologies"),
("GEV", "GE Vernova"),
("GFI", "金田"),
("GFS", "GlobalFoundries"),
("GH", "Guardant Health"),
("GILD", "吉利德科学"),
("GIS", "通用磨坊"),
("GLW", "康宁"),
("GM", "通用汽车"),
("GMAB", "Genmab"),
("GNRC", "Generac"),
("GOOG", "谷歌-C"),
("GOOGL", "谷歌-A"),
("GPN", "环汇有限公司"),
("GRMN", "佳明"),
("GS", "高盛"),
("GSK", "葛兰素史克"),
("GWW", "美国固安捷"),
("H", "凯悦酒店"),
("HAL", "哈里伯顿"),
("HBAN", "亨廷顿银行"),
("HCA", "HCA医疗"),
("HD", "家得宝"),
("HDB", "HDFC银行"),
("HEI", "海科航空"),
("HEI.A", "海科航空-A"),
("HIG", "哈特福德金融"),
("HLN", "Haleon"),
("HLT", "希尔顿酒店"),
("HMC", "本田汽车"),
("HON", "霍尼韦尔"),
("HOOD", "Robinhood"),
("HPE", "慧与科技"),
("HPQ", "惠普"),
("HSBC", "汇丰控股"),
("HST", "美国豪斯特酒店"),
("HSY", "好时"),
("HUBB", "哈勃集团"),
("HUM", "哈门那"),
("HWM", "Howmet Aerospace"),
("IBKR", "盈透证券"),
("IBM", "IBM Corp"),
("IBN", "印度工业信贷投资银行"),
("ICE", "洲际交易所"),
("IDXX", "爱德士"),
("IEX", "IDEX Corp"),
("IFF", "国际香料香精"),
("IHG", "洲际酒店"),
("ILMN", "Illumina"),
("INCY", "因塞特"),
("INFY", "印孚瑟斯"),
("ING", "荷兰国际集团"),
("INIO", "INNIO N.V"),
("INSM", "Insmed"),
("INTC", "英特尔"),
("INTU", "财捷"),
("INVH", "Invitation Homes"),
("IONQ", "IonQ Inc"),
("IOT", "Samsara"),
("IP", "国际纸业"),
("IQV", "艾昆纬"),
("IR", "英格索兰"),
("IREN", "IREN Ltd"),
("IRM", "铁山"),
("ISRG", "直觉外科公司"),
("ITT", "ITT Inc"),
("ITUB", "Itaú巴西联合银行"),
("ITW", "伊利诺伊机械"),
("IX", "欧力士"),
("JBHT", "JB亨特运输服务"),
("JBL", "捷普科技"),
("JBS", "JBS N.V"),
("JCI", "江森自控"),
("JD", "京东"),
("JNJ", "强生"),
("JPM", "摩根大通"),
("KB", "韩国国民银行"),
("KDP", "Keurig Dr Pepper"),
("KEP", "韩国电力"),
("KEY", "KeyCorp"),
("KEYS", "Keysight Technologies"),
("KGC", "金罗斯黄金"),
("KHC", "卡夫亨氏"),
("KIM", "金科"),
("KKR", "KKR & Co"),
("KLAC", "科磊"),
("KMB", "金佰利"),
("KMI", "金德尔摩根"),
("KO", "可口可乐"),
("KOF", "可口可乐凡萨瓶装"),
("KR", "克罗格"),
("KSPI", "Kaspi.kz"),
("KVUE", "Kenvue"),
("L", "洛斯公司"),
("LAMR", "拉马尔户外广告"),
("LDOS", "Leidos"),
("LEN", "莱纳建筑"),
("LEN.B", "莱纳建筑-B"),
("LH", "徕博科"),
("LHX", "L3Harris Technologies"),
("LII", "雷诺士"),
("LIN", "林德气体"),
("LITE", "Lumentum"),
("LLY", "礼来"),
("LMT", "洛克希德马丁"),
("LNG", "Cheniere Energy"),
("LNT", "美国联合能源"),
("LOGI", "罗技"),
("LOW", "劳氏"),
("LPLA", "LPL Financial"),
("LRCX", "泛林集团"),
("LSCC", "莱迪思半导体"),
("LTM", "南美航空集团"),
("LUV", "西南航空"),
("LVS", "金沙集团"),
("LYB", "利安德巴塞尔"),
("LYG", "劳埃德"),
("LYV", "Live Nation Entertainment"),
("MA", "万事达"),
("MAA", "MAA房产信托"),
("MAIR", "Madison Air Solutions Corp"),
("MAR", "万豪酒店"),
("MCD", "麦当劳"),
("MCHP", "微芯科技"),
("MCK", "麦克森"),
("MCO", "穆迪"),
("MDB", "MongoDB"),
("MDLN", "Medline"),
("MDLZ", "亿滋"),
("MDT", "美敦力"),
("MELI", "MercadoLibre"),
("MET", "大都会人寿"),
("META", "Meta Platforms"),
("MFC", "宏利金融"),
("MFG", "瑞穗金融"),
("MGA", "曼格纳国际"),
("MKL", "Markel Group"),
("MKSI", "MKS仪器"),
("MLI", "木勒工业"),
("MLM", "马丁-玛丽埃塔材料"),
("MMM", "3M"),
("MNST", "怪物饮料"),
("MO", "奥驰亚"),
("MPC", "马拉松原油"),
("MPLX", "MPLX LP"),
("MPWR", "Monolithic Power Systems"),
("MRK", "默沙东"),
("MRNA", "Moderna"),
("MRSH", "达信"),
("MRVL", "迈威尔科技"),
("MS", "摩根士丹利"),
("MSCI", "MSCI Inc"),
("MSFT", "微软"),
("MSI", "摩托罗拉解决方案"),
("MSTR", "Strategy"),
("MT", "安赛乐米塔尔"),
("MTB", "美国制商银行"),
("MTD", "梅特勒-托利多"),
("MTSI", "MACOM Technology Solutions"),
("MTZ", "MasTec"),
("MU", "美光科技"),
("MUFG", "三菱日联金融"),
("NBIS", "NEBIUS"),
("NBIX", "神经分泌生物科学"),
("NDAQ", "纳斯达克"),
("NDSN", "Nordson"),
("NEE", "新纪元能源"),
("NEM", "纽曼矿业"),
("NET", "Cloudflare"),
("NFLX", "奈飞"),
("NGG", "英国国家电网公司"),
("NI", "印北瓦电"),
("NIMC", "NISOURCE INC CORP UNIT SERIES A"),
("NKE", "耐克"),
("NLY", "Annaly Capital Management"),
("NMR", "野村控股"),
("NOC", "诺斯罗普格鲁曼"),
("NOK", "诺基亚"),
("NOW", "ServiceNow"),
("NRG", "NRG Energy"),
("NSC", "诺福克南方"),
("NTAP", "美国网存"),
("NTES", "网易"),
("NTR", "Nutrien"),
("NTRA", "Natera"),
("NTRS", "北方信托"),
("NU", "Nu Holdings"),
("NUE", "纽柯钢铁"),
("NVDA", "英伟达"),
("NVMI", "Nova"),
("NVO", "诺和诺德"),
("NVR", "NVR Inc"),
("NVS", "诺华制药"),
("NVT", "nVent Electric"),
("NWG", "NatWest"),
("NWS", "新闻集团-B"),
("NXPI", "恩智浦"),
("NXT", "Nextpower"),
("O", "Realty Income"),
("ODFL", "Old Dominion Freight Line"),
("OKE", "欧尼克(万欧卡)"),
("OKTA", "Okta"),
("OMC", "宏盟集团"),
("ON", "安森美半导体"),
("ONC", "百济神州"),
("ONTO", "Onto Innovation"),
("ORCL", "甲骨文"),
("ORLY", "奥莱利"),
("OTIS", "奥的斯"),
("OVV", "Ovintiv"),
("OWL", "Blue Owl Capital"),
("OXY", "西方石油"),
("P", "Everpure"),
("PAA", "Plains All American Pipeline"),
("PAAS", "泛美白银"),
("PANW", "Palo Alto Networks"),
("PAYX", "沛齐"),
("PBA", "Pembina Pipeline"),
("PBR", "巴西石油公司"),
("PBR.A", "巴西石油公司-Prefer"),
("PCAR", "帕卡"),
("PCG", "太平洋煤电"),
("PDD", "拼多多"),
("PEG", "公务集团"),
("PEP", "百事可乐"),
("PFE", "辉瑞"),
("PFG", "信安金融"),
("PFGC", "Performance Food"),
("PG", "宝洁"),
("PGR", "前进保险"),
("PH", "派克汉尼汾"),
("PHG", "飞利浦"),
("PHM", "普得集团"),
("PKG", "美国包装公司"),
("PKX", "浦项钢铁"),
("PLD", "安博"),
("PLTR", "Palantir"),
("PM", "菲利普莫里斯"),
("PNC", "PNC金融服务集团"),
("PPG", "PPG工业"),
("PPL", "宾州电力"),
("PR", "Permian Resources"),
("PRU", "保德信金融"),
("PSA", "公共存储公司"),
("PSX", "Phillips 66"),
("PUK", "英国保诚"),
("PWR", "广达服务"),
("PYPL", "PayPal"),
("Q", "Qnity Electronics"),
("QCOM", "高通"),
("QSR", "餐饮品牌国际"),
("RACE", "法拉利"),
("RBA", "里奇兄弟拍卖"),
("RBC", "RBC轴承"),
("RBLX", "Roblox"),
("RCI", "罗杰斯通信"),
("RCL", "皇家加勒比邮轮"),
("RDDT", "Reddit"),
("REGN", "再生元制药公司"),
("RELX", "RELX PLC"),
("RF", "地区金融"),
("RGLD", "皇家黄金"),
("RIO", "力拓"),
("RIVN", "Rivian Automotive"),
("RJF", "瑞杰金融"),
("RKLB", "Rocket Lab"),
("RKT", "Rocket"),
("RL", "拉夫劳伦"),
("RMBS", "Rambus"),
("RMD", "瑞思迈"),
("ROIV", "Roivant Sciences"),
("ROK", "罗克韦尔自动化"),
("ROKU", "Roku Inc"),
("ROL", "Rollins"),
("ROP", "儒博实业"),
("ROST", "罗斯百货"),
("RPRX", "Royalty Pharma"),
("RS", "Reliance"),
("RSG", "共和废品处理"),
("RTO", "Rentokil Initial PLC"),
("RTX", "雷神技术"),
("RVMD", "Revolution Medicines"),
("RY", "加拿大皇家银行"),
("RYAAY", "Ryanair"),
("SABRP", "SABRE CORP 6.50% MANDATORY CON PFD STK SER A"),
("SAN", "桑坦德银行"),
("SAP", "SAP SE"),
("SATA", "STRIVE INC PERP PFD SER A VAR RATE"),
("SATS", "回声星通信"),
("SBAC", "SBA通信公司"),
("SBS", "Sabesp"),
("SBUX", "星巴克"),
("SCCO", "南方铜业"),
("SCHW", "嘉信理财"),
("SE", "Sea"),
("SGI", "泰浦陛迪国际公司"),
("SHEL", "壳牌"),
("SHG", "新韩金融"),
("SHOP", "Shopify"),
("SHW", "宣伟公司"),
("SITM", "SiTime"),
("SLB", "斯伦贝谢"),
("SLF", "永明金融"),
("SMCI", "超微电脑"),
("SMFG", "三井住友金融"),
("SMTC", "先科电子"),
("SN", "SharkNinja"),
("SNA", "实耐宝"),
("SNDK", "闪迪"),
("SNOW", "Snowflake"),
("SNPS", "新思科技"),
("SNX", "新聚思"),
("SNY", "赛诺菲安万特"),
("SO", "美国南方公司"),
("SOFI", "SoFi Technologies"),
("SOJC", "SOUTHERN CO. 5.25% JR SUB NTS SR 2017B 01/12/77 USD25"),
("SONY", "索尼"),
("SPCX", "SpaceX"),
("SPG", "西蒙地产"),
("SPGI", "标普全球"),
("SPOT", "Spotify Technology"),
("SQM", "智利矿业化工"),
("SRE", "桑普拉能源"),
("SSNC", "SS&C Technologies"),
("STE", "思泰瑞医疗"),
("STLA", "Stellantis NV"),
("STLD", "Steel Dynamics"),
("STM", "意法半导体"),
("STRL", "Sterling Infrastructure"),
("STT", "道富银行"),
("STX", "希捷科技"),
("STZ", "星座品牌"),
("SU", "森科能源"),
("SUI", "Sun Communities"),
("SUNB", "Sunbelt Rentals Holdings"),
("SW", "Smurfit WestRock"),
("SYF", "Synchrony Financial"),
("SYK", "史赛克"),
("SYM", "Symbotic"),
("SYY", "西思科公司"),
("T", "AT&T"),
("TAK", "武田制药"),
("TCOM", "携程网"),
("TD", "多伦多道明银行"),
("TDG", "TransDigm"),
("TDY", "Teledyne Technologies"),
("TEAM", "Atlassian"),
("TECK", "泰克资源有限公司"),
("TEL", "泰科电子"),
("TER", "泰瑞达"),
("TEVA", "梯瓦制药"),
("TFC", "Truist Financial"),
("TGT", "塔吉特"),
("THC", "泰尼特"),
("TIGO", "Millicom International Cellular"),
("TJX", "TJX公司"),
("TKO", "TKO Group Holdings"),
("TLK", "印尼电信"),
("TLN", "Talen Energy"),
("TM", "丰田汽车"),
("TMO", "赛默飞世尔"),
("TMUS", "T-Mobile US"),
("TPG", "TPG Inc"),
("TPL", "Texas Pacific Land"),
("TPR", "Tapestry"),
("TRGP", "Targa Resources"),
("TRI", "汤森路透"),
("TROW", "普信集团"),
("TRP", "TC Energy"),
("TRV", "旅行者财产险集团"),
("TS", "泰纳瑞斯钢铁"),
("TSCO", "拖拉机供应公司"),
("TSEM", "Tower半导体"),
("TSLA", "特斯拉"),
("TSM", "台积电"),
("TSN", "泰森食品"),
("TT", "Trane技术"),
("TTE", "道达尔"),
("TTMI", "TTM科技"),
("TTWO", "Take-Two互动软件"),
("TU", "泰勒斯"),
("TW", "Tradeweb Markets"),
("TWLO", "Twilio"),
("TXN", "德州仪器"),
("TXT", "德事隆"),
("UAL", "联合大陆航空"),
("UBER", "优步"),
("UBS", "瑞银"),
("UI", "厄比奎蒂"),
("UL", "联合利华(英国)"),
("ULS", "UL Solutions"),
("ULTA", "Ulta美容"),
("UMC", "联电"),
("UNH", "联合健康"),
("UNP", "联合太平洋"),
("UPS", "联合包裹"),
("URI", "联合租赁"),
("USB", "美国合众银行"),
("USFD", "美国食品控股"),
("UTHR", "美国联合医疗"),
("V", "Visa"),
("VALE", "淡水河谷"),
("VEEV", "Veeva Systems"),
("VG", "Venture Global"),
("VICI", "VICI Properties"),
("VIK", "Viking Holdings"),
("VIV", "巴西电信"),
("VLO", "瓦莱罗能源"),
("VLTO", "Veralto Corp"),
("VMC", "火神材料"),
("VNOM", "Viper Energy"),
("VOD", "沃达丰"),
("VRSK", "Verisk分析"),
("VRSN", "威瑞信"),
("VRT", "Vertiv Holdings"),
("VRTX", "福泰制药"),
("VST", "Vistra Energy"),
("VTR", "芬塔公司"),
("VTRS", "Viatris"),
("VZ", "Verizon"),
("WAB", "美国西屋制动"),
("WAT", "沃特世"),
("WBD", "Warner Bros Discovery"),
("WCC", "西科国际"),
("WCN", "Waste Connections"),
("WDAY", "Workday"),
("WDC", "西部数据"),
("WDS", "Woodside Energy"),
("WEC", "威州能源"),
("WELL", "Welltower"),
("WES", "Western Midstream"),
("WF", "韩国友利金融"),
("WFC", "富国银行"),
("WIT", "Wipro"),
("WM", "美国废物管理"),
("WMB", "威廉姆斯"),
("WMT", "沃尔玛"),
("WPC", "W.P. Carey"),
("WPM", "Wheaton Precious Metals"),
("WRB", "WR柏克利"),
("WSM", "Williams-Sonoma"),
("WSO", "华斯科"),
("WST", "West Pharmaceutical Services"),
("WTW", "韦莱韬悦"),
("WWD", "伍德沃德"),
("WY", "惠好"),
("XEL", "埃克西尔能源"),
("XOM", "埃克森美孚"),
("XPO", "XPO"),
("XYL", "赛莱默"),
("XYZ", "Block"),
("YPF", "阿根廷YPF"),
("YUM", "Yum! Brands"),
("YUMC", "百胜中国"),
("ZBH", "齐默巴奥米特控股"),
("ZM", "Zoom通讯"),
("ZS", "Zscaler"),
("ZTO", "中通快递"),
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
]
RESEND_FROM = "美股-选股 <messenger@ceic.ca>"


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
        📡 美股-选股
      </div>
      <div style="margin-top:6px;color:#64748b;font-size:13px;">
        {scan_date} &nbsp;·&nbsp; 
      </div>
    </div>

    <div style="padding:28px 32px;">
      {'<p style="color:#4ade80;font-size:15px;font-weight:600;margin-bottom:16px;">🔔 满足选股条件</p>' if signals else '<p style="color:#888;font-size:15px;">No conditionA signals today.</p>'}

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
