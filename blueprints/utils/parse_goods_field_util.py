import re
import json


def parse_categories_field(field_value):
    """
    处理 categories 字段的函数，支持字符串、列表或字典类型的输入。
    :param field_value: 输入的 categories 字段值
    :return: 格式化后的列表
    """
    # 如果字段是字符串
    if isinstance(field_value, str) and field_value.strip():
        try:
            # 尝试将字符串解析为 JSON
            return json.loads(field_value)
        except json.JSONDecodeError as e:
            print(f"Warning: Unable to parse JSON from field value: {field_value}, Error: {str(e)}")
            return []
    # 如果字段是列表
    elif isinstance(field_value, list):
        # 遍历每个元素并递归处理
        return [parse_categories_field(item) if isinstance(item, (dict, list)) else item for item in field_value]
    # 如果字段是字典
    elif isinstance(field_value, dict):
        # 递归清理嵌套的 parent 字段
        cleaned_field = {}
        for key, value in field_value.items():
            cleaned_field[key] = parse_categories_field(value) if isinstance(value, (dict, list)) else value
        return cleaned_field
    # 如果字段是其他类型，返回空列表
    return []


def parse_main_pictures(field_value):
    """
    处理 mainPictures 字段，确保返回的是一个图片 URL 列表。
    :param field_value: 输入的字段值，可以是字符串或列表
    :return: 图片 URL 列表
    """
    if isinstance(field_value, str) and field_value.strip():
        try:
            # 如果是普通 JSON 字符串，尝试解析
            return json.loads(field_value)
        except json.JSONDecodeError:
            # 如果是逗号分隔的字符串，直接分割
            if ',' in field_value:
                return field_value.split(',')
            # 返回单一的 URL 作为列表
            return [field_value]
    elif isinstance(field_value, list):
        # 如果已经是列表，直接返回
        return field_value
    else:
        # 如果字段为空或其他数据类型，返回空列表
        return []


def parse_main_videos(field_value):
    """
    处理 mainVideos 字段，确保返回的是一个视频 URL 列表。
    :param field_value: 输入的字段值，可以是字符串或列表
    :return: 视频 URL 列表
    """
    if isinstance(field_value, list):
        # 如果已经是列表，直接返回
        return field_value
    elif isinstance(field_value, str) and field_value.strip():
        try:
            # 如果是普通 JSON 字符串，尝试解析
            return json.loads(field_value)
        except json.JSONDecodeError:
            # 如果是单个 URL 或逗号分隔的 URL 字符串
            if field_value.startswith('https://'):
                return field_value.split(',')  # 分割成列表
            # 返回单一的 URL 作为列表
            return [field_value]
    else:
        # 如果字段为空或其他数据类型，返回空列表
        return []


def parse_specs(specs_field):
    """
    解析 specs 字段，确保返回结构化的列表数据
    :param specs_field: 输入的字段值，可以是字典、字符串或列表
    :return: 规范化的规格列表
    """
    try:
        # 打印调试信息，帮助检查输入格式
        print(f"原始 specs_field: {specs_field}")

        # 如果是列表类型，直接解析
        if isinstance(specs_field, list):
            return [
                {
                    "id": item.get("id", ""),
                    "name": item.get("name", ""),
                    "values": [
                        {
                            "name": value.get("name", ""),
                            "picture": value.get("picture"),
                            "desc": value.get("desc", "")
                        } for value in item.get("values", [])
                    ]
                } for item in specs_field
            ]

        # 如果是字典类型，包装成列表后递归调用
        if isinstance(specs_field, dict):
            return parse_specs([specs_field])

        # 如果是字符串，尝试解析为 JSON 数据
        if isinstance(specs_field, str) and specs_field.strip():
            # 清理并解析 JSON 字符串
            cleaned_specs = specs_field.replace("'", '"').replace("None", "null")
            specs_data = json.loads(cleaned_specs)

            # 递归调用解析 JSON 数据
            return parse_specs(specs_data)

        # 如果不是上述类型，返回空列表
        print("specs_field 的类型无法解析。")
        return []

    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {specs_field}, 错误信息: {e}")
    except Exception as e:
        print(f"其他解析错误: {specs_field}, 错误信息: {e}")

    return []  # 如果解析失败，返回空列表


def clean_json_string(json_string):
    # 替换单引号为双引号
    cleaned_string = json_string.replace("'", '"')
    # 替换 None 为 null
    cleaned_string = re.sub(r'\bNone\b', 'null', cleaned_string)

    # 如果字符串中没有数组结构，强制将其包裹在一个列表中
    if not cleaned_string.startswith('[') and not cleaned_string.endswith(']'):
        cleaned_string = '[' + cleaned_string + ']'

    return cleaned_string


def parse_similar_products(field_value):
    """
    解析 similarProducts 字段，处理类似商品的数据。
    :param field_value: 输入字段，可以是字符串或列表。
    :return: 解析后的商品列表。
    """
    # 如果字段是字符串并且不为空
    if isinstance(field_value, str) and field_value.strip():
        try:
            # 尝试解析为 JSON 数组格式
            cleaned_value = clean_json_string(field_value)  # 可以考虑添加 clean_json_string 方法，清理不必要的符号
            return json.loads(cleaned_value)
        except json.JSONDecodeError as e:
            print(f"Warning: Unable to parse JSON from field value: {field_value}, Error: {str(e)}")
            return []
    # 如果字段已经是列表类型，直接返回
    elif isinstance(field_value, list):
        return field_value
    # 如果无法解析或是其他类型，返回空列表
    return []


def parse_detail_properties(detail_properties_field):
    """
    解析 detailProperties 字段并返回结构化数据。
    :param detail_properties_field: 输入字段，可以是字符串或列表。
    :return: 结构化的属性数据。
    """
    try:
        # 如果传入的是字符串类型，尝试将其转化为 JSON
        if isinstance(detail_properties_field, str):
            # 清理字段，将单引号替换为双引号
            cleaned_field = detail_properties_field.replace("'", "\"")
            properties_data = json.loads(cleaned_field)
        # 如果传入的是列表类型，直接使用
        elif isinstance(detail_properties_field, list):
            properties_data = detail_properties_field
        else:
            print("detail_properties_field 既不是字符串也不是列表格式")
            return []

        # 解析每个项
        parsed_properties = []
        for item in properties_data:
            parsed_properties.append({
                "name": item.get("name", ""),
                "value": item.get("value", "")
            })

        return parsed_properties

    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {detail_properties_field}, 错误信息: {e}")
    except Exception as e:
        print(f"解析错误: {detail_properties_field}, 错误信息: {e}")

    return []  # 如果发生错误，返回空列表


def parse_details_pictures(field_value):
    """
    解析 detailsPictures 字段，处理图片 URLs 列表。
    :param field_value: 输入字段，可以是字符串或列表。
    :return: 图片 URLs 列表。
    """
    # 如果字段是字符串并且不为空
    if isinstance(field_value, str) and field_value.strip():
        try:
            # 如果是有效的 URL 列表，且以 https:// 开头
            if field_value.startswith('https://'):
                # 直接拆分成 URL 列表
                return field_value.split(',')
            else:
                # 尝试解析为 JSON 格式的 URL 列表
                return json.loads(field_value)
        except json.JSONDecodeError as e:
            print(f"Warning: Unable to parse JSON from field value: {field_value}, Error: {str(e)}")
            return []
    # 如果字段已经是列表类型，直接返回
    elif isinstance(field_value, list):
        return field_value
    # 如果无法解析或是其他类型，返回空列表
    return []


def parse_skus(skus_field):
    try:
        if isinstance(skus_field, str):
            # 清理字符串，确保使用双引号，并且包裹为数组
            cleaned_field = skus_field.strip().replace("'", '"')

            # 包装为 JSON 数组
            if not cleaned_field.startswith("["):
                cleaned_field = f"[{cleaned_field}]"
            # 检查是否以 { 开头并且不是合法的数组
            if cleaned_field.startswith("{") and not cleaned_field.startswith("["):
                cleaned_field = "[" + cleaned_field.replace("'", '"').replace("None", "null") + "]"

            # 尝试解析为 JSON
            return json.loads(cleaned_field)

        # 如果已经是列表，直接返回
        elif isinstance(skus_field, list):
            return skus_field

        # 如果是单个字典，包裹为列表返回
        elif isinstance(skus_field, dict):
            return [skus_field]

        # 其他非法格式，返回空列表
        else:
            return []

    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing skus: {skus_field}, Error: {e}")
        return []  # 如果解析失败，返回空列表


def parse_hot_by_day(hot_by_day_field):
    """
    解析 hotByDay 字段并返回结构化数据。
    :param hot_by_day_field: 输入的字段，可以是字符串或列表。
    :return: 结构化的商品列表。
    """
    try:
        # 如果传入的是字符串格式，尝试将其转化为 JSON
        if isinstance(hot_by_day_field, str):
            # 清理字段，将单引号替换为双引号，避免解析错误
            cleaned_field = hot_by_day_field.replace("'", "\"")
            hot_by_day_data = json.loads(cleaned_field)
        # 如果传入的是列表格式，直接使用
        elif isinstance(hot_by_day_field, list):
            hot_by_day_data = hot_by_day_field
        else:
            print("hot_by_day_field 既不是字符串也不是列表格式")
            return []

        # 解析每个项
        parsed_hot_by_day = []
        for item in hot_by_day_data:
            parsed_hot_by_day.append({
                "id": item.get("id", ""),
                "name": item.get("name", ""),
                "desc": item.get("desc", ""),
                "price": item.get("price", ""),
                "picture": item.get("picture", ""),
                "orderNum": item.get("orderNum", 0)
            })

        return parsed_hot_by_day

    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {hot_by_day_field}, 错误信息: {e}")
    except Exception as e:
        print(f"解析错误: {hot_by_day_field}, 错误信息: {e}")

    return []  # 如果发生错误，返回空列表


def parse_goods_filed(goods_data):
    # 处理 brand 字段
    brand_data = goods_data.brand or {}
    if isinstance(brand_data, str):
        try:
            brand_data = json.loads(brand_data)  # 如果 brand 是字符串，尝试解析为字典
        except json.JSONDecodeError:
            brand_data = {}  # 解析失败时，设置为空字典
    elif not isinstance(brand_data, dict):
        brand_data = {}  # 如果 brand 不是字典，将其替换为空字典

    # 处理详情图片字段
    details_pictures = parse_details_pictures(goods_data.detailsPictures)
    if not isinstance(details_pictures, list):  # 如果不是列表，尝试分割
        details_pictures = str(goods_data.detailsPictures).split(',')

    result = {
        "id": str(goods_data.id),
        "name": goods_data.name,
        "spuCode": goods_data.spuCode,
        "desc": goods_data.desc,
        "price": str(goods_data.price),
        "oldPrice": str(goods_data.oldPrice) if goods_data.oldPrice else None,
        "discount": goods_data.discount if goods_data.discount else 1,
        "inventory": goods_data.inventory,
        "brand": {
            "id": brand_data.get("id", ""),
            "name": brand_data.get("name", ""),
            "nameEn": brand_data.get("nameEn", ""),
            "logo": brand_data.get("logo", ""),
            "picture": brand_data.get("picture", ""),
            "desc": brand_data.get("desc", ""),
            "place": brand_data.get("place", ""),
            "type": brand_data.get("type", "")
        },
        "salesCount": goods_data.salesCount,
        "commentCount": goods_data.commentCount,
        "collectCount": goods_data.collectCount,
        "mainVideos": parse_main_videos(goods_data.mainVideos) or [],
        "videoScale": goods_data.videoScale if goods_data.videoScale else 1,
        "mainPictures": parse_main_pictures(goods_data.mainPictures),
        "categories": parse_categories_field(goods_data.categories),
        "isPreSale": goods_data.isPreSale,
        "hotByDay": parse_hot_by_day(goods_data.hotByDay),
        "recommends": None,  # 设置为 JSON 可序列化的值
        "userAddresses": None,
        "evaluationInfo": None,
        "similarProducts": parse_similar_products(goods_data.similarProducts or []),
        "skus": parse_skus(goods_data.skus),
        "specs": parse_specs(goods_data.specs),
        "details": {
            "pictures": details_pictures,
            "properties": parse_detail_properties(goods_data.detailProperties)
        }
    }
    return result
