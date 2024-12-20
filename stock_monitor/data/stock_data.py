import json
import os
from ..config.settings import DEFAULT_STOCKS


class StockData:
    def __init__(self, config_file="stocks.json"):
        self.config_file = config_file
        self.stocks = self.load_stocks()

    def load_stocks(self):
        """从配置文件加载股票列表"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # 如果文件不为空
                    loaded_stocks = json.loads(content)
                    if loaded_stocks:  # 如果解析出的数据不为空
                        return loaded_stocks
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        # 如果文件不存在、为空或解析失败，返回默认股票列表
        return DEFAULT_STOCKS.copy()

    def save_stocks(self):
        """保存股票列表到配置文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.stocks, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存股票列表失败: {str(e)}")
            return False

    def add_stock(self, code, name):
        """添加股票"""
        self.stocks[code] = {"name": name}
        return self.save_stocks()

    def remove_stock(self, code):
        """删除股票"""
        if code in self.stocks:
            del self.stocks[code]
            return self.save_stocks()
        return False

    def get_stock_list(self):
        """获取股票列表"""
        return self.stocks.copy()
