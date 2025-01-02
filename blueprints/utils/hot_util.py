def load_data_from_db(model, sub_type=None, page_size=10, page=1):
    """
    从数据库加载数据，并根据查询参数进行筛选和分页处理。
    """
    # 初始化结果结构
    result = {
        "title": "",
        "id": None,
        "bannerPicture": "",
        "subTypes": []
    }

    # 查询活动的主信息：取第一个活动的标题和活动 ID
    first_record = model.query.first()
    if first_record:
        result["title"] = first_record.title
        result["id"] = first_record.activity_id
        result["bannerPicture"] = first_record.banner_picture

    # 查询所有符合条件的记录
    query = model.query
    if sub_type:
        # 筛选符合 sub_type 的数据（按子类别 ID 和 sub_type 匹配）
        query = query.filter(
            model.sub_id.startswith(str(sub_type)[:-1]),
            model.sub_id < sub_type
        )

    # 获取所有记录
    records = query.all()

    # 按 `sub_id` 分组记录
    sub_groups = {}
    for record in records:
        sub_id = record.sub_id
        if sub_id not in sub_groups:
            sub_groups[sub_id] = []
        sub_groups[sub_id].append(record)

    # 遍历每个子类分组
    for sub_id, records in sub_groups.items():
        subType = {
            "id": sub_id,
            "title": records[0].sub_title if records else "",
            "goodsItems": {
                "items": []
            }
        }

        # 商品总数和分页信息
        total_items = len(records)
        pages = (total_items + page_size - 1) // page_size  # 计算总页数
        start = (page - 1) * page_size
        end = start + page_size
        paged_records = records[start:end]

        # 添加商品数据
        for record in paged_records:
            goods_item = {
                "id": record.goods_id,
                "name": record.goods_name,
                "desc": record.goods_desc,
                "price": record.goods_price,
                "picture": record.goods_picture,
                "orderNum": record.order_num,
            }
            subType["goodsItems"]["items"].append(goods_item)

        # 填充分页相关信息
        subType["goodsItems"]["counts"] = total_items
        subType["goodsItems"]["pageSize"] = page_size
        subType["goodsItems"]["pages"] = pages
        subType["goodsItems"]["page"] = page

        # 添加非空商品项
        if subType["goodsItems"]["items"]:
            result["subTypes"].append(subType)

    return result