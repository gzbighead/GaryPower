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
    # ─── A股 ──────────────────────────────────────────────────────
    ("000001.SS", "上证指数"),
    ("399001.SZ", "深证成指"),
    ("399673.SZ", "五粮液"),
    ("600941.SS", "中国移动"),
    # ─── A股 ETF ──────────────────────────────────────────────────
    ("159007.SZ", "养殖ETF华泰柏瑞"),
    ("159008.SZ", "证券ETF景顺"),
    ("159013.SZ", "工业互联网ETF大成"),
    ("159020.SZ", "养殖ETF易方达"),
    ("159022.SZ", "科创创业人工智能ETF富国"),
    ("159107.SZ", "创业板软件ETF富国"),
    ("159141.SZ", "科创创业人工智能ETF永赢"),
    ("159146.SZ", "电力ETF华宝"),
    ("159147.SZ", "电池ETF南方"),
    ("159149.SZ", "创业板新能源ETF工银"),
    ("159151.SZ", "食品ETF华夏"),
    ("159155.SZ", "电池ETF大成"),
    ("159157.SZ", "有色金属ETF天弘"),
    ("159160.SZ", "电池ETF东财"),
    ("159165.SZ", "养殖ETF永赢"),
    ("159168.SZ", "有色ETF富国"),
    ("159172.SZ", "养殖ETF汇添富"),
    ("159175.SZ", "电池ETF易方达"),
    ("159178.SZ", "消费电子ETF汇添富"),
    ("159190.SZ", "创业板新能源ETF天弘"),
    ("159192.SZ", "家电ETF汇添富"),
    ("159193.SZ", "新能源电池ETF银华"),
    ("159201.SZ", "自由现金流ETF华夏"),
    ("159206.SZ", "卫星ETF永赢"),
    ("159207.SZ", "高股息ETF广发"),
    ("159208.SZ", "航空航天ETF万家"),
    ("159209.SZ", "红利质量ETF招商"),
    ("159213.SZ", "机器人ETF汇添富"),
    ("159218.SZ", "卫星ETF招商"),
    ("159221.SZ", "现金流ETF嘉实"),
    ("159222.SZ", "自由现金流ETF易方达"),
    ("159227.SZ", "航空航天ETF华夏"),
    ("159230.SZ", "通用航空ETF华夏"),
    ("159232.SZ", "自由现金流ETF南方"),
    ("159233.SZ", "自由现金流ETF平安"),
    ("159235.SZ", "中证现金流ETF大成"),
    ("159241.SZ", "航空航天ETF天弘"),
    ("159242.SZ", "创业板人工智能ETF大成"),
    ("159243.SZ", "创业板人工智能ETF招商"),
    ("159246.SZ", "创业板人工智能ETF富国"),
    ("159247.SZ", "创业板ETF汇添富"),
    ("159248.SZ", "人工智能ETF万家"),
    ("159249.SZ", "A500增强ETF工银"),
    ("159256.SZ", "创业板软件ETF华夏"),
    ("159258.SZ", "机器人ETF南方"),
    ("159259.SZ", "成长ETF易方达"),
    ("159263.SZ", "价值ETF易方达"),
    ("159267.SZ", "航天ETF华安"),
    ("159272.SZ", "机器人ETF富国"),
    ("159273.SZ", "云计算ETF汇添富"),
    ("159278.SZ", "机器人ETF鹏华"),
    ("159279.SZ", "创业板人工智能ETF华安"),
    ("159299.SZ", "金融科技ETF易方达"),
    ("159305.SZ", "储能电池ETF广发"),
    ("159310.SZ", "芯片ETF天弘"),
    ("159320.SZ", "电网设备ETF广发"),
    ("159321.SZ", "黄金股ETF华安"),
    ("159325.SZ", "半导体ETF南方"),
    ("159326.SZ", "电网设备ETF华夏"),
    ("159327.SZ", "半导体设备ETF万家"),
    ("159363.SZ", "创业板人工智能ETF华宝"),
    ("159368.SZ", "创业板新能源ETF华夏"),
    ("159378.SZ", "通用航空ETF永赢"),
    ("159381.SZ", "创业板人工智能ETF华夏"),
    ("159382.SZ", "创业板人工智能ETF南方"),
    ("159387.SZ", "创业板新能源ETF国泰"),
    ("159388.SZ", "创业板人工智能ETF国泰"),
    ("159399.SZ", "现金流ETF国泰"),
    ("159511.SZ", "通信ETF南方"),
    ("159516.SZ", "半导体设备ETF国泰"),
    ("159526.SZ", "机器人ETF嘉实"),
    ("159529.SZ", "标普消费ETF景顺"),
    ("159530.SZ", "机器人ETF易方达"),
    ("159537.SZ", "信创ETF国泰"),
    ("159540.SZ", "信创ETF易方达"),
    ("159546.SZ", "集成电路ETF国泰"),
    ("159547.SZ", "红利低波ETF华夏"),
    ("159549.SZ", "红利低波ETF天弘"),
    ("159551.SZ", "机器人ETF国泰"),
    ("159558.SZ", "半导体设备ETF易方达"),
    ("159559.SZ", "机器人ETF景顺"),
    ("159560.SZ", "芯片ETF景顺"),
    ("159562.SZ", "黄金股ETF华夏"),
    ("159565.SZ", "汽车零部件ETF易方达"),
    ("159566.SZ", "储能电池ETF易方达"),
    ("159581.SZ", "红利ETF万家"),
    ("159582.SZ", "半导体ETF博时"),
    ("159583.SZ", "通信ETF富国"),
    ("159586.SZ", "计算机ETF南方"),
    ("159590.SZ", "软件ETF汇添富"),
    ("159597.SZ", "创业板成长ETF易方达"),
    ("159599.SZ", "芯片ETF东财"),
    ("159611.SZ", "电力ETF广发"),
    ("159622.SZ", "创新药ETF东财"),
    ("159625.SZ", "绿色电力ETF嘉实"),
    ("159635.SZ", "基建ETF华夏"),
    ("159637.SZ", "新能源车ETF东财"),
    ("159638.SZ", "高端装备ETF嘉实"),
    ("159647.SZ", "中药ETF鹏华"),
    ("159652.SZ", "有色ETF汇添富"),
    ("159663.SZ", "机床ETF华夏"),
    ("159665.SZ", "半导体龙头ETF工银"),
    ("159667.SZ", "工业母机ETF国泰"),
    ("159671.SZ", "稀有金属ETF工银"),
    ("159690.SZ", "有色矿业ETF招商"),
    ("159692.SZ", "证券ETF东财"),
    ("159698.SZ", "粮食ETF鹏华"),
    ("159707.SZ", "地产ETF华宝"),
    ("159713.SZ", "稀土ETF富国"),
    ("159715.SZ", "稀土ETF易方达"),
    ("159731.SZ", "石化ETF华夏"),
    ("159732.SZ", "消费电子ETF华夏"),
    ("159736.SZ", "食品饮料ETF天弘"),
    ("159738.SZ", "云计算ETF华泰柏瑞"),
    ("159739.SZ", "云计算ETF鹏华"),
    ("159745.SZ", "建材ETF国泰"),
    ("159748.SZ", "创新药ETF富国"),
    ("159752.SZ", "新能源ETF申万菱信"),
    ("159755.SZ", "电池ETF广发"),
    ("159757.SZ", "电池ETF景顺"),
    ("159758.SZ", "红利质量ETF华夏"),
    ("159761.SZ", "新材料ETF国泰"),
    ("159767.SZ", "电池龙头ETF兴银"),
    ("159768.SZ", "房地产ETF银华"),
    ("159770.SZ", "机器人ETF天弘"),
    ("159775.SZ", "电池ETF建信"),
    ("159779.SZ", "消费电子ETF招商"),
    ("159786.SZ", "VRETF银华"),
    ("159790.SZ", "碳中和ETF华夏"),
    ("159796.SZ", "电池ETF汇添富"),
    ("159801.SZ", "芯片ETF广发"),
    ("159805.SZ", "传媒ETF鹏华"),
    ("159806.SZ", "新能源车ETF国泰"),
    ("159813.SZ", "半导体ETF鹏华"),
    ("159819.SZ", "人工智能ETF易方达"),
    ("159825.SZ", "农业ETF富国"),
    ("159828.SZ", "医疗ETF国泰"),
    ("159837.SZ", "生物科技ETF易方达"),
    ("159839.SZ", "生物医药ETF汇添富"),
    ("159840.SZ", "锂电池ETF工银"),
    ("159841.SZ", "证券ETF天弘"),
    ("159842.SZ", "券商ETF银华"),
    ("159851.SZ", "金融科技ETF华宝"),
    ("159852.SZ", "软件ETF嘉实"),
    ("159855.SZ", "影视ETF银华"),
    ("159857.SZ", "光伏ETF天弘"),
    ("159859.SZ", "生物医药ETF天弘"),
    ("159864.SZ", "光伏ETF国泰"),
    ("159865.SZ", "养殖ETF国泰"),
    ("159867.SZ", "养殖ETF鹏华"),
    ("159869.SZ", "游戏ETF华夏"),
    ("159871.SZ", "有色ETF银华"),
    ("159875.SZ", "新能源ETF嘉实"),
    ("159876.SZ", "有色ETF华宝"),
    ("159880.SZ", "有色ETF鹏华"),
    ("159881.SZ", "有色金属ETF国泰"),
    ("159883.SZ", "医疗器械ETF永赢"),
    ("159887.SZ", "银行ETF富国"),
    ("159888.SZ", "智能汽车ETF华夏"),
    ("159890.SZ", "云计算ETF招商"),
    ("159899.SZ", "软件ETF招商"),
    ("159903.SZ", "深成 ETF南方"),
    ("159905.SZ", "红利ETF工银"),
    ("159916.SZ", "基本面ETF建信"),
    ("159928.SZ", "消费ETF汇添富"),
    ("159929.SZ", "医药ETF汇添富"),
    ("159938.SZ", "医药ETF广发"),
    ("159939.SZ", "信息技术ETF广发"),
    ("159944.SZ", "材料ETF广发"),
    ("159949.SZ", "创业板50ETF华安"),
    ("159980.SZ", "有色ETF大成"),
    ("159992.SZ", "创新药ETF银华"),
    ("159993.SZ", "证券ETF鹏华"),
    ("159994.SZ", "通信ETF银华"),
    ("159995.SZ", "芯片ETF华夏"),
    ("159996.SZ", "家电ETF国泰"),
    ("159997.SZ", "电子ETF天弘"),
    ("159998.SZ", "计算机ETF天弘"),
    ("510050.SS", "上证50ETF华夏"),
    ("510150.SS", "消费ETF招商"),
    ("510170.SS", "大宗商品ETF国联安"),
    ("510230.SS", "金融ETF国泰"),
    ("510300.SS", "沪深300ETF华泰柏瑞"),
    ("510410.SS", "资源ETF博时"),
    ("510500.SS", "中证500ETF南方"),
    ("510630.SS", "消费ETF华夏"),
    ("510720.SS", "红利国企ETF国泰"),
    ("510880.SS", "红利ETF华泰柏瑞"),
    ("512070.SS", "证券保险ETF易方达"),
    ("512100.SS", "中证1000ETF富国"),
    ("512170.SS", "医疗ETF华宝"),
    ("512200.SS", "房地产ETF南方"),
    ("512290.SS", "生物医药ETF国泰"),
    ("512380.SS", "沪深300增强ETF景顺"),
    ("512400.SS", "有色金属ETF南方"),
    ("512460.SS", "电池ETF华夏"),
    ("512480.SS", "半导体ETF国联安"),
    ("512560.SS", "军工ETF易方达"),
    ("512570.SS", "证券ETF易方达"),
    ("512630.SS", "卫星ETF广发"),
    ("512660.SS", "军工ETF国泰"),
    ("512670.SS", "国防ETF鹏华"),
    ("512680.SS", "军工ETF广发"),
    ("512690.SS", "酒ETF鹏华"),
    ("512700.SS", "银行ETF南方"),
    ("512710.SS", "军工龙头ETF富国"),
    ("512720.SS", "计算机ETF国泰"),
    ("512800.SS", "银行ETF华宝"),
    ("512810.SS", "军工ETF华宝"),
    ("512820.SS", "银行ETF汇添富"),
    ("512880.SS", "证券ETF国泰"),
    ("512890.SS", "红利低波ETF华泰柏瑞"),
    ("512900.SS", "证券ETF南方"),
    ("512930.SS", "AI人工智能ETF平安"),
    ("512940.SS", "有色ETF华安"),
    ("512950.SS", "央企改革ETF华夏"),
    ("513360.SS", "教育ETF博时"),
    ("515010.SS", "证券ETF华夏"),
    ("515020.SS", "银行ETF华夏"),
    ("515030.SS", "新能源车ETF华夏"),
    ("515050.SS", "通信ETF华夏"),
    ("515060.SS", "房地产ETF华夏"),
    ("515070.SS", "人工智能ETF华夏"),
    ("515080.SS", "中证红利ETF招商"),
    ("515120.SS", "创新药ETF广发"),
    ("515170.SS", "食品饮料ETF华夏"),
    ("515210.SS", "钢铁ETF国泰"),
    ("515220.SS", "煤炭ETF国泰"),
    ("515230.SS", "软件ETF国泰"),
    ("515250.SS", "智能汽车ETF富国"),
    ("515260.SS", "电子ETF华宝"),
    ("515290.SS", "银行ETF天弘"),
    ("515370.SS", "光伏ETF华夏"),
    ("515400.SS", "大数据ETF富国"),
    ("515630.SS", "证券保险ETF鹏华"),
    ("515650.SS", "消费50ETF富国"),
    ("515700.SS", "新能源车ETF平安"),
    ("515710.SS", "食品饮料ETF华宝"),
    ("515790.SS", "光伏ETF华泰柏瑞"),
    ("515800.SS", "中证800ETF汇添富"),
    ("515850.SS", "证券ETF富国"),
    ("515880.SS", "通信ETF国泰"),
    ("515970.SS", "工程机械ETF华夏"),
    ("515980.SS", "人工智能ETF华富"),
    ("516010.SS", "游戏ETF国泰"),
    ("516020.SS", "化工ETF华宝"),
    ("516050.SS", "科技龙头ETF工银"),
    ("516080.SS", "创新药ETF易方达"),
    ("516090.SS", "新能源ETF易方达"),
    ("516100.SS", "金融科技ETF华夏"),
    ("516110.SS", "汽车ETF国泰"),
    ("516120.SS", "化工ETF富国"),
    ("516150.SS", "稀土ETF嘉实"),
    ("516160.SS", "新能源ETF南方"),
    ("516220.SS", "化工ETF国泰"),
    ("516250.SS", "工程机械ETF富国"),
    ("516290.SS", "光伏ETF汇添富"),
    ("516310.SS", "银行ETF易方达"),
    ("516350.SS", "芯片ETF易方达"),
    ("516510.SS", "云计算ETF易方达"),
    ("516570.SS", "化工行业ETF易方达"),
    ("516620.SS", "影视ETF国泰"),
    ("516640.SS", "芯片ETF富国"),
    ("516650.SS", "有色金属ETF华夏"),
    ("516670.SS", "畜牧养殖ETF招商"),
    ("516700.SS", "大数据ETF华宝"),
    ("516770.SS", "游戏ETF华泰柏瑞"),
    ("516780.SS", "稀土ETF华泰柏瑞"),
    ("516810.SS", "农业ETF华夏"),
    ("516820.SS", "医疗创新ETF平安"),
    ("516850.SS", "新能源ETF华夏"),
    ("516860.SS", "金融科技ETF博时"),
    ("516880.SS", "光伏ETF银华"),
    ("516910.SS", "物流ETF富国"),
    ("516920.SS", "芯片ETF汇添富"),
    ("516970.SS", "基建ETF广发"),
    ("517090.SS", "央企共赢ETF国泰"),
    ("517380.SS", "创新药ETF天弘"),
    ("517390.SS", "云计算ETF天弘"),
    ("517400.SS", "黄金股ETF国泰"),
    ("517520.SS", "黄金股ETF永赢"),
    ("517800.SS", "人工智能50ETF方正富邦"),
    ("517900.SS", "银行AH优选ETF招商"),
    ("560080.SS", "中药ETF汇添富"),
    ("560090.SS", "证券ETF汇添富"),
    ("560170.SS", "央企科技ETF南方"),
    ("560210.SS", "农牧渔ETF景顺"),
    ("560270.SS", "电力ETF工银"),
    ("560280.SS", "工程机械ETF广发"),
    ("560390.SS", "电网设备ETF易方达"),
    ("560400.SS", "证券ETF华泰柏瑞"),
    ("560450.SS", "电力ETF天弘"),
    ("560470.SS", "有色ETF易方达"),
    ("560710.SS", "船舶ETF富国"),
    ("560770.SS", "机器人ETF招商"),
    ("560780.SS", "半导体设备ETF广发"),
    ("560800.SS", "数字经济ETF鹏扬"),
    ("560860.SS", "工业有色ETF万家"),
    ("560980.SS", "光伏龙头ETF广发"),
    ("561100.SS", "消费电子ETF富国"),
    ("561160.SS", "电池ETF富国"),
    ("561170.SS", "绿色电力ETF富国"),
    ("561330.SS", "矿业ETF国泰"),
    ("561380.SS", "电网设备ETF国泰"),
    ("561560.SS", "电力ETF华泰柏瑞"),
    ("561580.SS", "央企红利ETF华泰柏瑞"),
    ("561600.SS", "消费电子ETF平安"),
    ("561800.SS", "稀有金属ETF华富"),
    ("561910.SS", "电池ETF招商"),
    ("562360.SS", "机器人ETF银华"),
    ("562500.SS", "机器人ETF华夏"),
    ("562510.SS", "旅游ETF华夏"),
    ("562550.SS", "绿电ETF华夏"),
    ("562570.SS", "信创ETF华夏"),
    ("562590.SZ", "半导体设备ETF华夏"),
    ("562600.SZ", "医疗器械ETF华夏"),
    ("562800.SS", "稀有金属ETF嘉实"),
    ("562820.SZ", "集成电路ETF嘉实"),
    ("562880.SZ", "电池ETF嘉实"),
    ("562900.SS", "农业ETF易方达"),
    ("562930.SZ", "软件ETF易方达"),
    ("562950.SZ", "消费电子ETF易方达"),
    ("562960.SS", "绿色电力ETF易方达"),
    ("562970.SS", "光伏ETF易方达"),
    ("563020.SS", "红利低波ETF易方达"),
    ("563210.SS", "专精特新ETF富国"),
    ("563230.SS", "卫星ETF富国"),
    ("563320.SS", "通用航空ETF华泰柏瑞"),
    ("563380.SS", "航空航天ETF华泰柏瑞"),
    ("563390.SS", "全指现金流ETF华泰柏瑞"),
    ("563530.SS", "卫星ETF易方达"),
    ("563560.SS", "科技成长ETF兴业"),
    ("563790.SS", "卫星ETF鹏华"),
    ("588000.SS", "科创50ETF华夏"),
    ("588010.SS", "科创新材料ETF博时"),
    ("588020.SS", "科创成长ETF易方达"),
    ("588170.SS", "科创半导体ETF华夏"),
    ("588200.SS", "科创芯片ETF嘉实"),
    ("588290.SS", "科创芯片ETF华安"),
    ("588410.SS", "科创创业人工智能ETF鹏华"),
    ("588420.SS", "科创创业人工智能ETF摩根"),
    ("588430.SS", "科创创业人工智能ETF工银"),
    ("588710.SS", "科创半导体设备ETF华泰柏瑞"),
    ("588750.SS", "科创芯片ETF汇添富"),
    ("588760.SS", "科创人工智能ETF广发"),
    ("588770.SS", "科创信息ETF摩根"),
    ("588780.SS", "科创芯片设计ETF国联安"),
    ("588790.SS", "科创AIETF博时"),
    ("588810.SS", "科创芯片ETF富国"),
    ("588830.SS", "科创新能源ETF鹏华"),
    ("588890.SS", "科创芯片ETF南方"),
    ("588910.SS", "科创价值ETF建信"),
    ("588920.SS", "科创芯片ETF鹏华"),
    ("588930.SS", "科创人工智能ETF银华"),
    ("588960.SS", "科创新能源ETF富国"),
    ("588990.SS", "科创芯片ETF博时"),
    ("589010.SS", "科创人工智能ETF华夏"),
    ("589020.SS", "科创半导体设备ETF鹏华"),
    ("589030.SS", "科创芯片设计ETF易方达"),
    ("589070.SS", "科创芯片设计ETF天弘"),
    ("589090.SS", "科创AIETF鹏华"),
    ("589100.SS", "科创芯片ETF国泰"),
    ("589110.SS", "科创人工智能ETF国泰"),
    ("589120.SS", "科创创新药ETF汇添富"),
    ("589130.SS", "科创芯片ETF易方达"),
    ("589139.SS", "科创创业人工智能ETF华泰柏瑞"),
    ("589142.SS", "科创创业人工智能ETF景顺"),
    ("589160.SS", "科创芯片ETF广发"),
    ("589170.SS", "科创芯片设计ETF鹏华"),
    ("589190.SS", "科创芯片ETF华宝"),
    ("589210.SS", "科创芯片设计ETF广发"),
    ("589230.SS", "科创人工智能ETF南方"),
    ("589250.SS", "科创芯片设计ETF浦银"),
    ("589260.SS", "科创芯片设计ETF国泰"),
    ("589380.SS", "科创AIETF富国"),
    ("589520.SS", "科创人工智能ETF华宝"),
    ("589560.SS", "科创人工智能ETF汇添富"),
    ("589720.SS", "科创创新药ETF国泰"),
    ("589960.SS", "科创新能源ETF易方达"),
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
