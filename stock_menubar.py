import rumps
import requests
import time
from datetime import datetime
import threading
import json
from functools import partial


class StockMenuBar(rumps.App):
    def __init__(self):
        # 初始化默认股票列表
        self.stocks = {
            "sh000001": {"name": "上证指数"},
            "sh515060": {"name": "房地产ETF"},
            "sz159890": {"name": "云计算ETF"},
        }

        # 调用父类初始化
        super().__init__("监控")

        # 初始化其他属性
        self.is_rotating = True
        self.stock_items = {}
        self.current_index = 0  # 添加当前显示的股票索引
        self.current_stock = None  # 添加当前显示的股票代码
        self.setup_menu()

    def setup_menu(self):
        self.load_stocks()
        """设置菜单项"""
        # 清除现有菜单项
        self.menu.clear()

        # 为每个股票创建菜单项
        self.stock_items = {}
        for code in self.stocks.keys():
            print(f"设置菜单{code}")
            self.stock_items[code] = rumps.MenuItem("加载中...")
            self.menu.add(self.stock_items[code])
        print(f"设置菜单{self.stock_items}")

        # 添加分割线和更新时间
        self.menu.add(rumps.separator)
        self.update_time = rumps.MenuItem("更新时间: --:--:--")
        self.menu.add(self.update_time)

        # 添加股票管理选项
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("搜索股票", callback=self.search_stock))
        self.menu.add(rumps.MenuItem("添加股票", callback=self.add_stock))
        self.menu.add(rumps.MenuItem("删除股票", callback=self.remove_stock))

        # 添加轮播控制
        self.menu.add(rumps.separator)
        self.rotation_control = rumps.MenuItem(
            "暂停轮播", callback=self.toggle_rotation
        )
        self.menu.add(self.rotation_control)

    def fetch_stock_data(self, stock_code):
        """获取股票数据"""
        try:
            market = "1" if stock_code.startswith("sh") else "0"
            pure_code = stock_code[2:]

            url = "http://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": f"{market}.{pure_code}",
                "fields": "f58,f43,f170,f47,f48,f60,f46,f45,f44,f51,f168,f169",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "http://quote.eastmoney.com/",
            }

            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if "data" in data:
                stock_info = data["data"]
                return {
                    "name": stock_info.get("f58", ""),
                    "price": stock_info.get("f43", 0) / 100,
                    "change": stock_info.get("f170", 0) / 100,
                }
        except Exception as e:
            print(f"Error fetching {stock_code}: {str(e)}")
        return None

    def load_stocks(self):
        """从配置文件加载股票列表"""
        try:
            with open("stocks.json", "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:  # 如果文件不为空
                    loaded_stocks = json.loads(content)
                    if loaded_stocks:  # 如果解析出的数据不为空
                        self.stocks = loaded_stocks
                        return
        except (FileNotFoundError, json.JSONDecodeError):
            pass

        # 如果文件不存在、为空或解析���败，保存默认股票列表
        self.save_stocks()

    def update_stocks(self):
        """更新所有股票数据"""
        while self.is_rotating:  # 使用标志位控制循环
            try:
                stock_updates = {}
                for code in self.stocks.keys():
                    data = self.fetch_stock_data(code)
                    if data:
                        stock_updates[code] = data

                # 更新UI
                for code, data in stock_updates.items():
                    name = data["name"] or self.stocks[code]["name"]
                    price = data["price"]
                    change = data["change"]

                    # 根据涨跌设置不同的符号
                    change_symbol = "↑" if change > 0 else "↓"
                    change_text = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"

                    # 更新菜单项文本
                    text = f"{name}: {price:.2f} {change_symbol} {change_text}"
                    if code in self.stock_items:
                        self.stock_items[code].title = text

                # 更新时间
                current_time = datetime.now().strftime("%H:%M:%S")
                self.update_time.title = f"更新时间: {current_time}"

            except Exception as e:
                print(f"Update error: {str(e)}")

            time.sleep(2)  # 更新间隔

    def add_stock(self, sender):
        """添加股票"""
        window = rumps.Window(
            message="请输入股票代码：\n(例如: sh600000)",
            title="添加股票",
            default_text="",
            ok="添加",
            cancel="取消",
        )
        response = window.run()
        if response.clicked:
            code = response.text.strip()
            if code:
                if code in self.stocks:
                    rumps.alert("提示", "该股票已在监控列表中")
                else:
                    data = self.fetch_stock_data(code)
                    if data:
                        self.stocks[code] = {"name": data["name"]}
                        if self.save_stocks():  # 保存到文件
                            rumps.alert(
                                "添加成功", f"已添加 {data['name']} ({code}) 到监控列表"
                            )
                            self.setup_menu()  # 重新设置菜单
                        else:
                            rumps.alert("警告", "股票已添加，但保存配置文件失败")
                    else:
                        rumps.alert("错误", "无效的股票代码")
            else:
                rumps.alert("提示", "请输入有效的股票代码")

    def remove_stock(self, sender):
        """删除股票"""
        if not self.stocks:
            rumps.alert("提示", "监控列表为空")
            return

        # 创建选项列表
        options = []
        for code, info in self.stocks.items():
            options.append(f"{info['name']} ({code})")

        # 创建选择窗口
        window = rumps.Window(
            message="请选择要删除的股票：",
            title="删除股票",
            default_text="",
            dimensions=(200, 100),  # 设置窗口大小
            ok="删除",
            cancel="取消",
        )

        # 添加选项列表
        window.default_text = "\n".join(options)

        # 显示窗口并获取结果
        response = window.run()
        if response.clicked:
            selected_text = response.text.strip()
            if selected_text in options:
                self.on_button_click(selected_text)
            else:
                rumps.alert("错误", "请选择有效的股票")

    def save_stocks(self):
        """保存股票列表到配置文件"""
        try:
            with open("stocks.json", "w", encoding="utf-8") as f:
                json.dump(self.stocks, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存股票列表失败: {str(e)}")
            return False

    def toggle_rotation(self, sender):
        """切换轮播状态"""
        self.is_rotating = not self.is_rotating  # 切换轮播状态
        if self.is_rotating:
            sender.title = "暂停轮播"
        else:
            sender.title = "开始轮播"

    def quit_app(self, sender):
        """退出应用"""
        rumps.quit_application()

    def on_button_click(self, button_text):
        """处理按钮点击事件"""
        print(f"Button clicked: {button_text}")
        # 从按钮文本中提取股票代码
        start_index = button_text.rfind("(")
        end_index = button_text.rfind(")")
        if start_index != -1 and end_index != -1 and start_index < end_index:
            code = button_text[start_index + 1 : end_index]
            if code in self.stocks:
                del self.stocks[code]
                if self.save_stocks():
                    rumps.alert("删除成功", f"已从监控列表删除 {code}")
                    self.setup_menu()  # 重新设置菜单
                else:
                    rumps.alert("警告", "股票已删���，但保存配置文件失败")
            else:
                rumps.alert("错误", "未找到该股票")
        else:
            rumps.alert("错误", "无法解析股票代码")

    @rumps.timer(2)
    def updateStockPrice(self, sender):
        """更新股票价格"""
        if not self.stocks:
            return

        try:
            stock_codes = list(self.stocks.keys())

            # 更新当前显示的股票
            if self.is_rotating:
                self.current_stock = stock_codes[self.current_index]
                self.current_index = (self.current_index + 1) % len(stock_codes)
            elif self.current_stock is None:
                self.current_stock = stock_codes[0]

            # 获取当前显示股票的数据
            current_data = self.fetch_stock_data(self.current_stock)
            if current_data:
                name = current_data["name"] or self.stocks[self.current_stock]["name"]
                change = current_data["change"]
                change_symbol = "↑" if change > 0 else "↓"
                change_text = f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
                self.title = f"{name} {change_symbol}{change_text}"

            # 更新时间（即使菜单关闭也更新）
            current_time = datetime.now().strftime("%H:%M:%S")
            self.update_time.title = f"更新时间: {current_time}"

            # 获取并更新所有股票数据
            for code in self.stocks.keys():
                if code != self.current_stock:  # 跳过已经获取的当前股票
                    data = self.fetch_stock_data(code)
                    if data:
                        name = data["name"] or self.stocks[code]["name"]
                        price = data["price"]
                        change = data["change"]
                        change_symbol = "↑" if change > 0 else "↓"
                        change_text = (
                            f"+{change:.2f}%" if change > 0 else f"{change:.2f}%"
                        )
                        text = f"{name}: {price:.2f} {change_symbol} {change_text}"
                        if code in self.stock_items:
                            self.stock_items[code].title = text

            # 重新设置菜单以强制更新显示
            self.menu._menu.update()

        except Exception as e:
            print(f"Update error: {str(e)}")

    def search_stock(self, sender):
        """搜索股票"""
        window = rumps.Window(
            message="请输入股票代码或名称：",
            title="搜索股票",
            default_text="",
            ok="搜索",
            cancel="取消",
            dimensions=(300, 100),
        )
        response = window.run()
        if response.clicked and response.text.strip():
            keyword = response.text.strip()
            results = self.fetch_stock_search(keyword)
            if results:
                # 创建选项列表
                options = []
                for stock in results:
                    market = "sh" if stock["market"] == "1" else "sz"
                    code = f"{market}{stock['code']}"
                    options.append(f"{stock['name']} ({code})")

                # 创建选择窗口
                select_window = rumps.Window(
                    message="请选择要添加的股票：",
                    title="添加股票",
                    default_text="\n".join(options),
                    dimensions=(300, 200),
                    ok="添加",
                    cancel="取消",
                )
                select_response = select_window.run()
                if select_response.clicked:
                    selected = select_response.text.strip()
                    if selected in options:
                        # 提取股票代码
                        start_index = selected.rfind("(")
                        end_index = selected.rfind(")")
                        if start_index != -1 and end_index != -1:
                            code = selected[start_index + 1 : end_index]
                            # 调用添加股票的逻辑
                            self.add_specific_stock(code)
            else:
                rumps.alert("提示", "未找到匹配的股票")

    def fetch_stock_search(self, keyword):
        """搜索股票信息"""
        try:
            url = "http://searchapi.eastmoney.com/api/suggest/get"
            params = {
                "input": keyword,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": "50",
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "http://quote.eastmoney.com/",
            }

            response = requests.get(url, params=params, headers=headers)
            data = response.json()
            print("data", data)

            if "QuotationCodeTable" in data:
                quote_data = data["QuotationCodeTable"]
                if "Data" in quote_data and quote_data["Data"]:
                    results = []
                    for item in quote_data["Data"]:
                        # 只返回A股
                        if item["SecurityType"] in ["1", "2"]:  # 1为上证，2为深证
                            market = "1" if item["SecurityType"] == "1" else "0"
                            results.append(
                                {
                                    "code": item["Code"],
                                    "name": item["Name"],
                                    "market": market,
                                }
                            )
                    print("results", results)
                    return results
            return []
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def add_specific_stock(self, code):
        """添加特定股票"""
        if code in self.stocks:
            rumps.alert("提示", "该股票已在监控列表中")
        else:
            data = self.fetch_stock_data(code)
            if data:
                self.stocks[code] = {"name": data["name"]}
                if self.save_stocks():
                    rumps.alert(
                        "添加成功", f"已添加 {data['name']} ({code}) 到监控列表"
                    )
                    self.setup_menu()
                else:
                    rumps.alert("警告", "股票已添加，但保存配置文件失败")
            else:
                rumps.alert("错误", "无效的股票代码")


if __name__ == "__main__":
    app = StockMenuBar()
    app.run()
