from flask import Flask, render_template, jsonify
import pandas as pd
import json
import time
import threading
import requests
import logging
from datetime import datetime
import os

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 获取当前文件所在目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# 全局变量存储数据
stock_data = {}

def fetch_stock_data(stock_code):
    """获取股票数据"""
    try:
        market = '1' if stock_code.startswith('sh') else '0'
        pure_code = stock_code[2:]
        
        url = f"http://push2.eastmoney.com/api/qt/stock/get"
        params = {
            'secid': f'{market}.{pure_code}',
            'fields': 'f58,f43,f170,f47,f48,f60,f46,f45,f44,f51,f168,f169',
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'http://quote.eastmoney.com/'
        }
        
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        
        if 'data' in data:
            stock_info = data['data']
            return {
                'name': stock_info.get('f58', ''),
                'price': stock_info.get('f43', 0) / 100,
                'change': stock_info.get('f170', 0) / 100,
                'volume': stock_info.get('f47', 0) / 100,
                'high': stock_info.get('f44', 0) / 100,
                'low': stock_info.get('f45', 0) / 100,
                'open': stock_info.get('f46', 0) / 100,
                'amount': stock_info.get('f48', 0) / 100,
                'turnover': stock_info.get('f168', 0) / 100,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
    except Exception as e:
        logger.error(f"Error fetching {stock_code}: {str(e)}")
    return None

def update_data():
    """更新数据的后台任务"""
    stocks = [
        'sh560090',  # 证券ETF
        'sh515060',  # 房地产ETF
        'sz159890',  # 云计算ETF
    ]
    
    while True:
        try:
            for code in stocks:
                data = fetch_stock_data(code)
                if data:
                    if code not in stock_data:
                        stock_data[code] = []
                    stock_data[code].append(data)
                    if len(stock_data[code]) > 30:
                        stock_data[code].pop(0)
                    logger.info(f"Updated {code}: {data['price']}")
                time.sleep(1)
        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            time.sleep(5)

@app.route('/')
def index():
    """主页"""
    try:
        # 准备当前数据
        current_data = {}
        for code, data_list in stock_data.items():
            if data_list:  # 确保有数据
                current_data[code] = data_list[-1]  # 获取最新数据
        
        # 传递当前数据到模板
        return render_template('index.html', stocks=current_data)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/data')
def get_data():
    """获取最新数据"""
    try:
        current_data = {}
        for code, data_list in stock_data.items():
            if data_list:
                current_data[code] = data_list[-1]
        return jsonify(current_data)
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # 启动更新线程
    update_thread = threading.Thread(target=update_data, daemon=True)
    update_thread.start()
    
    # 启动Flask服务器
    app.run(host='127.0.0.1', port=8002, debug=False) 