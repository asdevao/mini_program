def get_region_name_by_codes(province_code, city_code, area_code, json_data):
    """
    根据省、市、区编码获取对应的省、市、区名称

    :param province_code: 省的编码
    :param city_code: 市的编码
    :param area_code: 区县的编码
    :param json_data: 省市县的JSON数据
    :return: 返回一个格式化的字符串，例如 '山西省 太原市 尖草坪区'
    """
    for province in json_data:
        if province['code'] == province_code:
            # 找到匹配的省份
            province_name = province['name']

            # 先尝试查找市
            city_name = None
            area_name = None

            # 查找市
            for city in province['cityList']:
                if city['code'] == city_code:
                    city_name = city['name']
                    # 查找区县
                    for area in city['areaList']:
                        if area['code'] == area_code:
                            area_name = area['name']
                    break

            # 如果没有找到匹配的市，回退到使用省的名称
            if not city_name:
                city_name = province_name  # 使用省的名称代替市的名称
                # 查找区县
                for city in province['cityList']:
                    for area in city['areaList']:
                        if area['code'] == area_code:
                            area_name = area['name']
                            break
                    if area_name:
                        break

            if not area_name:
                return None  # 如果仍然找不到区县，则返回 None

            # 返回格式化的字符串（省 市 区）
            return f"{province_name} {city_name} {area_name}"

    return None  # 如果找不到匹配的省，则返回 None
