import rumps
import requests
import time
from datetime import datetime
import threading
import json


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
        self.setup_menu()
        # 启动更新线程
        self.update_thread = threading.Thread(target=self.update_stocks, daemon=True)
        self.update_thread.start()

    def setup_menu(self):
        self.load_stocks()
        """设置菜单项"""
        # 清除现有菜单项
        while len(self.menu) > 0:
            self.menu.pop()

        # 为每个股票创建菜单项
        self.stock_items = {}
        for code in self.stocks.keys():
            print(f"设置菜单{code}")
            self.stock_items[code] = rumps.MenuItem("加载中...")
            self.menu.add(self.stock_items[code])

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

        # 添加退出选项
        # self.menu.add(rumps.MenuItem("退出", callback=self.quit_app))

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

        window = rumps.Window(
            message="请选择要删除的股票：",
            title="删除股票",
            default_text="",
            ok="删除",
            cancel="取消",
        )

        # 添加所有股票作为选项
        for code, info in self.stocks.items():
            window.add_button(f"{info['name']} ({code})")

        response = window.run()
        if response.clicked and response.text:
            try:
                # 从选择的文本中提取股票代码
                start_index = response.text.rfind("(")
                end_index = response.text.rfind(")")

                if start_index != -1 and end_index != -1 and start_index < end_index:
                    code = response.text[start_index + 1 : end_index]
                    if code in self.stocks:
                        name = self.stocks[code]["name"]
                        del self.stocks[code]
                        if self.save_stocks():
                            rumps.alert(
                                "删除成功", f"已从监控列表中删除 {name} ({code})"
                            )
                            self.setup_menu()  # 重新设置菜单
                        else:
                            rumps.alert("警告", "股票已删除，但保存配置文件失败")
                    else:
                        rumps.alert("错误", "未找到该股票")
                else:
                    rumps.alert("错误", "无法解析股票代码")
            except Exception as e:
                rumps.alert("错误", f"删除失败: {str(e)}")

    def fetch_stock_data(self, stock_code):
        """获取股票数据"""
        try:
            market = "1" if stock_code.startswith("sh") else "0"
            pure_code = stock_code[2:]

            url = f"http://push2.eastmoney.com/api/qt/stock/get"
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

        # 如果文件不存在、为空或解析失败，保存默认股票列表
        self.save_stocks()

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
        """换轮播状态"""
        if sender.title == "暂停轮播":
            sender.title = "开始轮播"
        else:
            sender.title = "暂停轮播"

    def quit_app(self, sender):
        """退出应用"""
        rumps.quit_application()

    def search_stock(self, sender):
        """搜索股票"""
        window = rumps.Window(
            message="请输入股票名称或代码：",
            title="搜索股票",
            default_text="",
            ok="搜索",
            cancel="取消",
        )
        response = window.run()
        if response.clicked:
            keyword = response.text.strip()
            if keyword:
                # 这里可以实现搜索逻辑，例如调用API搜索股票
                try:
                    # 假设有一个API可以根据关键字搜索股票
                    search_results = self.fetch_search_results(keyword)
                    if search_results:
                        # 显示搜索结果并让用户选择
                        choice_window = rumps.Window(
                            message="请选择要添加的股票：",
                            title="搜索结果",
                            default_text="",
                            ok="添加",
                            cancel="取消",
                        )
                        for result in search_results:
                            choice_window.add_button(
                                f"{result['name']} ({result['code']})"
                            )

                        choice_response = choice_window.run()
                        if choice_response.clicked and choice_response.text:
                            selected_text = choice_response.text
                            start_index = selected_text.rfind("(")
                            end_index = selected_text.rfind(")")

                            if (
                                start_index != -1
                                and end_index != -1
                                and start_index < end_index
                            ):
                                code = selected_text[start_index + 1 : end_index]
                                if code not in self.stocks:
                                    data = self.fetch_stock_data(code)
                                    if data:
                                        self.stocks[code] = {"name": data["name"]}
                                        if self.save_stocks():
                                            rumps.alert(
                                                "添加成功",
                                                f"已添加 {data['name']} ({code}) 到监控列表",
                                            )
                                            self.setup_menu()
                                        else:
                                            rumps.alert(
                                                "警告", "股票已添加，但保存配置文件失败"
                                            )
                                    else:
                                        rumps.alert("错误", "无法获取股票数据")
                                else:
                                    rumps.alert("提示", "股票已在监控列表中")
                            else:
                                rumps.alert("错误", "无法解析股票代码")
                    else:
                        rumps.alert("提示", f"未找到与 '{keyword}' 相关的股票")
                except Exception as e:
                    rumps.alert("错误", f"搜索失败: {str(e)}")
            else:
                rumps.alert("提示", "请输入有效的股票名称或代码")

    def update_stocks(self):
        """更新所有股票数据"""
        while True:
            try:
                if self.is_rotating:
                    stock_updates = {}
                    for code in self.stocks.keys():
                        data = self.fetch_stock_data(code)
                        if data:
                            stock_updates[code] = data

                    @rumps.timer(1)
                    def update_ui(_):
                        try:
                            for code, data in stock_updates.items():
                                name = data["name"] or self.stocks[code]["name"]
                                price = data["price"]
                                change = data["change"]

                                # 根据涨跌设置不同的符号
                                change_symbol = "↑" if change > 0 else "↓"
                                change_text = (
                                    f"+{change:.2f}%"
                                    if change > 0
                                    else f"{change:.2f}%"
                                )

                                # 更新菜单项文本
                                text = (
                                    f"{name}: {price:.2f} {change_symbol} {change_text}"
                                )
                                if code in self.stock_items:
                                    self.stock_items[code].title = text

                            # 更新时间
                            current_time = datetime.now().strftime("%H:%M:%S")
                            self.update_time.title = f"更新时间: {current_time}"

                            # 停止定时器
                            _.stop()
                        except Exception as e:
                            print(f"UI update error: {str(e)}")

                    time.sleep(2)  # 主循环间隔

            except Exception as e:
                print(f"Update error: {str(e)}")
                time.sleep(5)


if __name__ == "__main__":
    app = StockMenuBar()
    app.run()
