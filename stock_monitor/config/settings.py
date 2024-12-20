# API 配置
API_BASE_URL = "http://push2.eastmoney.com/api/qt/stock"
API_TOKEN = "fa5fd1943c7b386f172d6893dbfba10b"

# 应用设置
UPDATE_INTERVAL = 2  # 更新间隔（秒）
CHART_SAVE_DIR = "~/.stock_monitor"  # 图表保存目录

# 请求头设置
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "http://quote.eastmoney.com/",
}

# 默认股票列表
DEFAULT_STOCKS = {
    "sh000001": {"name": "上证指数"},
    "sh515060": {"name": "房地产ETF"},
    "sz159890": {"name": "云计算ETF"},
}
