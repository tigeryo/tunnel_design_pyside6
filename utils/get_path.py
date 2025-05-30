import os
import sys


def get_resource_path(relative_path):
    """解决使用pyinstaller打包后文件路径问题，程序中所有相对路径都需要利用该函数包装"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)