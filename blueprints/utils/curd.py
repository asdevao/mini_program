from flask import request
from datetime import datetime
from apps.blueprints import db
from ..utils.response_util import ResponseUtil  # 导入响应工具类


class Curd:
    def __init__(self, model):
        # 引入模型
        self.model = model

    # 查找详细信息函数
    def select_more(self):
        more_id = request.json.get('more_id')
        records = self.model.query.filter_by(id=more_id).all()
        more_inf = []
        for record in records:
            record.__dict__.pop('_sa_instance_state')
            more_inf.append(record.__dict__)
        return more_inf

    # 序列化处理数据函数
    def serialize_model(self, instance):
        serialized_data = instance.__dict__.copy()
        serialized_data.pop('_sa_instance_state', None)  # 移除不必要的键
        for key, value in serialized_data.items():
            if isinstance(value, datetime):
                serialized_data[key] = value.strftime('%Y-%m-%d')
        return serialized_data

    # 显示前端页面数据函数
    def query_data(self):
        records = self.model.query.all()
        # 将查询结果转换为字典列表
        result = [self.serialize_model(record) for record in records]
        return result

    # 增加信息函数
    def create_data(self):
        # 从请求中获取前端发送的表单数据
        form_data = request.json.get('formData')
        # 创建新的Model 记录并添加到数据库中
        new_record = self.model()
        for key, value in form_data.items():
            setattr(new_record, key, value)
        db.session.add(new_record)
        db.session.commit()
        return form_data

    # 删除信息函数
    def delete_data(self):
        delete_id = request.json.get('delete_id')
        delete_val = self.model.query.filter_by(id=delete_id).first()
        db.session.delete(delete_val)
        db.session.commit()
        return ResponseUtil.success('删除成功')

    # 修改信息函数
    def update_data(self):
        tempdata = request.json.get('tempData')
        update_info = self.model.query.filter_by(id=tempdata['id']).first()
        for key, value in tempdata.items():
            setattr(update_info, key, value)
        db.session.commit()
