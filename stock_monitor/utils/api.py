import requests
from ..config.settings import API_BASE_URL, API_TOKEN, HEADERS


def fetch_stock_data(stock_code):
    """获取股票数据"""
    try:
        market = "1" if stock_code.startswith("sh") else "0"
        pure_code = stock_code[2:]

        url = f"{API_BASE_URL}/get"
        params = {
            "secid": f"{market}.{pure_code}",
            "fields": "f58,f43,f170,f47,f48,f60,f46,f45,f44,f51,f168,f169",
            "ut": API_TOKEN,
        }

        response = requests.get(url, params=params, headers=HEADERS)
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


def fetch_kline_data(stock_code, period=101):
    """获取K线数据"""
    try:
        market = "1" if stock_code.startswith("sh") else "0"
        pure_code = stock_code[2:]

        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            "secid": f"{market}.{pure_code}",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": str(period),
            "fqt": "1",
            "beg": "0",
            "end": "20500101",
            "lmt": "120",
            "ut": API_TOKEN,
        }

        response = requests.get(url, params=params, headers=HEADERS)
        data = response.json()

        if "data" in data and "klines" in data["data"]:
            return data["data"]["klines"]
    except Exception as e:
        print(f"Error fetching kline data: {str(e)}")
    return None


def fetch_time_sharing_data(stock_code):
    """获取分时数据"""
    try:
        market = "1" if stock_code.startswith("sh") else "0"
        pure_code = stock_code[2:]

        url = "http://push2his.eastmoney.com/api/qt/stock/trends2/get"
        params = {
            "secid": f"{market}.{pure_code}",
            "fields1": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58",
            "ut": API_TOKEN,
            "ndays": "1",
        }

        response = requests.get(url, params=params, headers=HEADERS)
        data = response.json()

        if "data" in data and "trends" in data["data"]:
            return data["data"]
        return None
    except Exception as e:
        print(f"Error fetching time sharing data: {str(e)}")
        return None


def fetch_stock_search(keyword):
    """搜索股票信息"""
    try:
        url = "http://searchapi.eastmoney.com/api/suggest/get"
        params = {
            "input": keyword,
            "type": "14",
            "token": "D43BF722C8E33BDC906FB84D85E326E8",
            "count": "50",
        }

        response = requests.get(url, params=params, headers=HEADERS)
        data = response.json()

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
                return results
        return []
    except Exception as e:
        print(f"Search error: {str(e)}")
        return []
