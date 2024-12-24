import rumps
import requests
import time
from datetime import datetime
import threading
import json
from functools import partial
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import DateFormatter
import matplotlib
import os
import logging

matplotlib.use("Agg")  # 使用Agg后端，避免GUI相关问题

# 日志配置
LOG_DIR = os.path.expanduser("~/.stock_monitor/logs")
LOG_FILE = os.path.join(LOG_DIR, "stock_monitor.log")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_LEVEL = "DEBUG"


class StockMenuBar(rumps.App):
    def __init__(self):
        # 设置日志
        os.makedirs(LOG_DIR, exist_ok=True)
        logging.basicConfig(
            filename=LOG_FILE, level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("应用启动")

        # 初始化配置目录
        self.config_dir = os.path.expanduser("~/.stock_monitor")
        self.config_file = os.path.join(self.config_dir, "stocks.json")
        self.logger.info(f"配置目录: {self.config_dir}")
        self.logger.info(f"配置文件: {self.config_file}")

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
        self.last_chart_update = 0  # 添加最后更新时间戳
        self.setup_menu()

    def setup_menu(self):
        self.load_stocks()
        """设置菜单项"""
        # 清除现有菜单项
        self.menu.clear()

        # 为每个股票创建菜单
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

        # 添加股票管理项
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

        # 添加均线图选项
        self.menu.add(rumps.separator)
        self.menu.add(rumps.MenuItem("显示均线图", callback=self.show_ma_chart))
        self.menu.add(
            rumps.MenuItem("显示分时图", callback=self.show_time_sharing_chart)
        )
        self.menu.add(rumps.MenuItem("退出", callback=self.quit_app))

    def quit_app(self, _):
        """退出应用"""
        self.logger.info("应用退出")
        rumps.quit_application()

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
            if os.path.exists(self.config_file):
                self.logger.info(f"正在加载配置文件: {self.config_file}")
                with open(self.config_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:  # 如果文件不为空
                        loaded_stocks = json.loads(content)
                        if loaded_stocks:  # 如果解析出的数据不为空
                            self.stocks = loaded_stocks
                            self.logger.info("成功加载配置")
                            return
            self.logger.warning("配置文件不存在或为空，使用默认配置")
        except Exception as e:
            self.logger.error(f"加载配置失败: {str(e)}")

        # 如果文件不存在、为空或解析失败，保存默认股票列表
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

                    # 根据涨跌设置不同的
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
                print(f"Update error2: {str(e)}")

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
            self.logger.info("开始保存配置...")
            self.logger.info(f"股票列表: {self.stocks}")

            # 确保目录存在
            os.makedirs(self.config_dir, exist_ok=True)

            # 临时文件保存
            temp_file = f"{self.config_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(self.stocks, f, ensure_ascii=False, indent=4)

            # 设置权限
            os.chmod(temp_file, 0o666)

            # 安全替换
            os.replace(temp_file, self.config_file)

            self.logger.info("配置保存成功")
            return True

        except Exception as e:
            self.logger.error(f"保存失败: {str(e)}", exc_info=True)
            self.logger.error(
                f"目录权限: {oct(os.stat(self.config_dir).st_mode & 0o777)}"
            )
            if os.path.exists(self.config_file):
                self.logger.error(
                    f"文件权限: {oct(os.stat(self.config_file).st_mode & 0o777)}"
                )
            self.logger.error(f"用户ID: {os.getuid()}")
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
                    rumps.alert("警告", "股票已删除，但保存配置文件失败")
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

            # 重新设置菜单以显示
            self.menu._menu.update()

            # 更新分时图
            # self.update_time_sharing_chart()

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

    def fetch_kline_data(self, stock_code, period=101):
        """获取K线数据"""
        try:
            market = "1" if stock_code.startswith("sh") else "0"
            pure_code = stock_code[2:]

            url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
            params = {
                "secid": f"{market}.{pure_code}",
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "klt": "101",  # 日K
                "fqt": "1",  # 前复权
                "end": "20500101",
                "lmt": "120",  # 最近120个交易日数据
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "http://quote.eastmoney.com/",
            }

            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if "data" in data and "klines" in data["data"]:
                return data["data"]["klines"]
        except Exception as e:
            print(f"Error fetching kline data: {str(e)}")
        return None

    def show_ma_chart(self, sender):
        """显示均线图"""
        try:
            # 设置中文字体，按优先级尝试不同的字体
            plt.rcParams["font.sans-serif"] = [
                "PingFang HK",
                "PingFang SC",
                "Heiti TC",
                "Heiti SC",
                "Microsoft YaHei",
                "SimHei",
            ]
            plt.rcParams["axes.unicode_minus"] = False
            # 设置字体大小
            plt.rcParams["font.size"] = 10

            # 获取K线数据
            klines = self.fetch_kline_data("sh000001")
            if not klines:
                rumps.alert("错误", "无法获取数据")
                return

            # 解数据
            dates = []
            opens = []
            closes = []
            highs = []
            lows = []
            volumes = []
            for kline in klines:
                date_str, open_price, close, high, low, volume, *rest = kline.split(",")
                dates.append(datetime.strptime(date_str, "%Y-%m-%d"))
                opens.append(float(open_price))
                closes.append(float(close))
                highs.append(float(high))
                lows.append(float(low))
                volumes.append(float(volume))

            # 创建图表
            fig, (ax1, ax2) = plt.subplots(
                2,
                1,
                figsize=(12, 8),
                height_ratios=[2.5, 1],
                gridspec_kw={"hspace": 0.1},
            )
            plt.style.use("dark_background")

            # 设置x轴为交易日序号
            x = np.arange(len(dates))

            # 绘制K线图
            bar_width = 0.6
            for i in x:
                if closes[i] >= opens[i]:
                    color = "#FF4444"
                else:
                    color = "#00B800"

                # 绘制K线实体
                ax1.add_patch(
                    plt.Rectangle(
                        (i - bar_width / 2, min(opens[i], closes[i])),
                        bar_width,
                        abs(closes[i] - opens[i]),
                        facecolor=color,
                        alpha=1.0,
                    )
                )
                # 绘制上下影线
                ax1.plot([i, i], [lows[i], highs[i]], color=color, linewidth=1)

            # 计算并绘制均线
            def calculate_ma(data, window):
                return np.convolve(data, np.ones(window) / window, mode="valid")

            ma5 = calculate_ma(closes, 5)
            ma10 = calculate_ma(closes, 10)
            ma20 = calculate_ma(closes, 20)

            # 补充均线数据前面的空值
            ma5 = np.concatenate([np.full(4, np.nan), ma5])
            ma10 = np.concatenate([np.full(9, np.nan), ma10])
            ma20 = np.concatenate([np.full(19, np.nan), ma20])

            # 绘制均线
            ax1.plot(x, ma5, label="MA5", color="#FFFF00", linewidth=1)
            ax1.plot(x, ma10, label="MA10", color="#FF00FF", linewidth=1)
            ax1.plot(x, ma20, label="MA20", color="#00FFFF", linewidth=1)

            # 设置x轴刻度和标签
            xticks = np.arange(0, len(dates), 10)  # 每10天显示一个刻度
            ax1.set_xticks(xticks)
            ax1.set_xticklabels([dates[i].strftime("%m-%d") for i in xticks])

            # 设置图表标题和样式
            change = closes[-1] - closes[-2]
            change_pct = (change / closes[-2]) * 100
            title_color = "#FF4444" if change >= 0 else "#00B800"
            ax1.set_title(
                f'上证指数 {closes[-1]:.2f} {"↑" if change >= 0 else "↓"}{abs(change_pct):.2f}%',
                color=title_color,
                fontsize=12,
                pad=15,
            )

            # 设置网格
            ax1.grid(True, linestyle="--", alpha=0.2)
            ax1.legend(loc="upper left", framealpha=0.3)

            # 绘制成交量
            for i in range(len(dates)):
                if closes[i] >= opens[i]:
                    color = "#FF4444"
                else:
                    color = "#00B800"
                ax2.bar(i, volumes[i], color=color, width=0.8, alpha=0.8)

            # 设置成交量图样式
            ax2.grid(True, linestyle="--", alpha=0.2)
            ax2.set_xticks(xticks)
            ax2.set_xticklabels([dates[i].strftime("%m-%d") for i in xticks])

            # 调整布局
            plt.tight_layout()

            # 保存图表
            save_path = os.path.expanduser("~/Desktop/ma_chart.png")
            plt.savefig(
                save_path,
                facecolor="#1C1C1C",
                edgecolor="none",
                bbox_inches="tight",
                dpi=200,
            )
            plt.close()

            # 使用系统默认程序打开图片
            os.system(f'open "{save_path}"')

        except Exception as e:
            print(f"Error showing chart: {str(e)}")
            rumps.alert("错误", "显示图表出错")

    def fetch_time_sharing_data(self, stock_code):
        """获取分时数据"""
        try:
            market = "1" if stock_code.startswith("sh") else "0"
            pure_code = stock_code[2:]

            url = "http://push2his.eastmoney.com/api/qt/stock/trends2/get"
            params = {
                "secid": f"{market}.{pure_code}",
                "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b",
                "ndays": "1",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "http://quote.eastmoney.com/",
            }

            response = requests.get(url, params=params, headers=headers)
            data = response.json()

            if "data" in data and "trends" in data["data"]:
                return data["data"]
            return None
        except Exception as e:
            print(f"Error fetching time sharing data: {str(e)}")
            return None

    def show_time_sharing_chart(self, sender):
        """显示分时图"""
        try:
            plt.rcParams["font.sans-serif"] = ["PingFang HK"]
            plt.rcParams["axes.unicode_minus"] = False

            # 获取当前显示的股票代码
            if not self.current_stock:
                rumps.alert("错误", "请先选择一个股票")
                return

            # 获取分时数据
            data = self.fetch_time_sharing_data(self.current_stock)
            if not data or "trends" not in data:
                rumps.alert("错误", "无法获取分时数据")
                return

            # 解析数据
            times = []
            prices = []
            volumes = []
            avg_prices = []

            for trend in data["trends"]:
                try:
                    time_str, price, avg_price, volume, *rest = trend.split(",")
                    times.append(datetime.strptime(time_str, "%Y-%m-%d %H:%M"))
                    prices.append(float(price))
                    avg_prices.append(float(avg_price))
                    volumes.append(float(volume))
                except (ValueError, IndexError) as e:
                    print(f"Error parsing trend data: {str(e)}, data: {trend}")
                    continue

            if not times:
                rumps.alert("错误", "数据解析失败")
                return

            # 创建图表
            fig, (ax1, ax2) = plt.subplots(
                2, 1, figsize=(12, 8), height_ratios=[2.5, 1]
            )
            fig.patch.set_facecolor("#1C1C1C")

            # 绘制价格走势
            ax1.set_facecolor("#1C1C1C")
            ax1.plot(times, prices, label="价格", linewidth=1, color="white")
            ax1.plot(
                times, avg_prices, label="均价", linewidth=1, color="yellow", alpha=0.8
            )

            # 设置x轴标签
            ax1.set_xticks(times[:: len(times) // 8])  # 显示8个时间点
            ax1.set_xticklabels(
                [t.strftime("%H:%M") for t in times[:: len(times) // 8]], rotation=45
            )

            # 添加��格和图例
            ax1.grid(True, linestyle="--", alpha=0.3)
            ax1.legend(loc="upper left")

            # 获取基准价格用于计算涨跌
            base_price = data.get("prePrice", prices[0])
            up_color = "#FF4444"
            down_color = "#00B800"

            # 设置价格区间
            price_min = min(min(prices), min(avg_prices))
            price_max = max(max(prices), max(avg_prices))
            price_range = price_max - price_min
            ax1.set_ylim(price_min - price_range * 0.1, price_max + price_range * 0.1)

            # 添加基准价格线
            ax1.axhline(y=base_price, color="gray", linestyle="--", alpha=0.5)

            # 设置标题
            change = prices[-1] - base_price
            change_pct = (change / base_price) * 100
            title_color = up_color if change >= 0 else down_color
            ax1.set_title(
                f'{self.stocks[self.current_stock]["name"]} {prices[-1]:.2f} {"↑" if change >= 0 else "↓"}{abs(change_pct):.2f}%',
                color=title_color,
                fontsize=12,
                pad=15,
            )

            # 绘制成交量图
            ax2.set_facecolor("#1C1C1C")
            volume_colors = [
                up_color if p >= base_price else down_color for p in prices
            ]
            ax2.bar(
                times, volumes, width=0.8 * (times[1] - times[0]), color=volume_colors
            )

            # 设置成交量图的x轴标签
            ax2.set_xticks(times[:: len(times) // 8])
            ax2.set_xticklabels(
                [t.strftime("%H:%M") for t in times[:: len(times) // 8]], rotation=45
            )

            # 添加网格
            ax2.grid(True, linestyle="--", alpha=0.3)

            # 调整布局
            plt.tight_layout()

            # 保存图表到用户的临时目录
            temp_dir = os.path.expanduser("~/.stock_monitor")
            os.makedirs(temp_dir, exist_ok=True)
            save_path = os.path.join(temp_dir, "time_sharing_chart.png")

            plt.savefig(
                save_path,
                facecolor="#1C1C1C",
                edgecolor="none",
                bbox_inches="tight",
                dpi=200,
            )
            plt.close()

            # 使用系统默认程序打开图片
            os.system(f'open "{save_path}"')

        except Exception as e:
            print(f"Error showing time sharing chart: {str(e)}")
            rumps.alert("错误", "显示分时图时出错")


if __name__ == "__main__":
    app = StockMenuBar()
    app.run()
