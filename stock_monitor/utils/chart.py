import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os
from ..config.settings import CHART_SAVE_DIR


def setup_chart_style():
    """设置图表样式"""
    plt.rcParams["font.sans-serif"] = [
        "PingFang HK",
        "PingFang SC",
        "Heiti TC",
        "Heiti SC",
        "Microsoft YaHei",
        "SimHei",
    ]
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["font.size"] = 10
    plt.style.use("dark_background")


def calculate_ma(data, window):
    """计算移动平均线"""
    return np.convolve(data, np.ones(window) / window, mode="valid")


def save_chart(fig, filename):
    """保存图表"""
    save_dir = os.path.expanduser(CHART_SAVE_DIR)
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    fig.savefig(
        save_path,
        facecolor="#1C1C1C",
        edgecolor="none",
        bbox_inches="tight",
        dpi=200,
    )
    plt.close(fig)

    return save_path
