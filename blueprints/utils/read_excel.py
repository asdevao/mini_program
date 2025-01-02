import pandas as pd
from typing import List, Dict, Any
def read_excel(file_path: str) -> List[Dict[str, Any]]:
    """读取Excel文件并返回字典格式的数据"""
    try:
        # 使用with语句确保文件在使用后关闭
        with pd.ExcelFile(file_path) as xls:
            data = pd.read_excel(xls)
        return data.to_dict(orient='records')
    except FileNotFoundError:
        raise Exception(f"文件未找到: {file_path}")
    except Exception as e:
        raise Exception(f"读取文件时出错: {e}")