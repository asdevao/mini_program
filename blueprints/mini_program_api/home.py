import os
from flask import jsonify, Blueprint, request, send_from_directory
from werkzeug.utils import secure_filename
from blueprints import db
from ..Models.HomeModel import BannerData, MutliData, HotMutliData, NewData, GuessLikeData, VideoGroup, \
    Video
import ast
# 获取当前脚本所在的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 配置上传文件存储路径，通过 os.path.join 动态构建路径
UPLOAD_FOLDER = os.path.join(current_dir, 'static', 'video')

bp = Blueprint('home', __name__)


# 广告区域-小程序 轮播图
@bp.route('/banner', methods=['GET'])
def get_banner_data():
    try:
        # 从数据库中查询所有的轮播图数据
        banner_data = BannerData.query.all()

        # 转换数据格式为前端需要的格式
        result = [{
            "id": str(item.id),  # 将id转为字符串
            "imgUrl": item.imgUrl,
            "hrefUrl": item.hrefUrl,
            "type": item.type
        } for item in banner_data]

        print('小程序请求轮播图')

        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": result
        })

    except Exception as e:
        # 如果发生异常，返回错误信息
        return jsonify({'error': str(e)}), 500


# 前台分类-小程序
@bp.route('/category/mutli', methods=['GET'])
def get_mutli_data():
    try:
        # 从数据库中查询所有分类数据
        category_data = MutliData.query.all()

        # 将查询结果转换为前端需要的格式
        result = [{
            "id": str(item.id),  # 将id转为字符串
            "name": item.name,
            "icon": item.icon
        } for item in category_data]

        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": result
        })

    except Exception as e:
        # 如果发生异常，返回错误信息
        return jsonify({'error': str(e)}), 500


# 热门推荐-小程序
@bp.route('/hot/mutli', methods=['GET'])
def get_hot_mutli_data():
    try:
        # 使用 SQLAlchemy ORM 查询数据库中的所有记录
        category_data = HotMutliData.query.all()

        # 格式化数据
        result = []
        for item in category_data:
            # 将数据库中的 pictures 字段从字符串转换为列表
            pictures = ast.literal_eval(item.pictures)  # 假设 pictures 存储为字符串，需要转换为列表
            result.append({
                "id": str(item.id),  # 将 id 转为字符串
                "pictures": pictures,
                "title": item.title,
                "alt": item.alt,
                "target": str(item.target),  # 将 target 转为字符串
                "type": item.type
            })

        # 返回结果
        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 新鲜好物
@bp.route('/new', methods=['GET'])
def get_new_data():
    try:
        # 获取 limit 参数，默认为 10
        limit = int(request.args.get('limit', 10))

        # 从数据库查询数据
        new_data_list = NewData.query.limit(limit).all()

        # 格式化返回数据
        result = [{
            "id": item.id,
            "name": item.name,
            "desc": item.desc,
            "price": str(item.price),  # 将价格转换为字符串以确保精度
            "picture": item.picture,
            "order_num": item.order_num,
            "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": item.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        } for item in new_data_list]

        # 返回成功响应
        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": result
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 猜你喜欢-小程序
@bp.route('/goods/guessLike', methods=['GET'])
def get_guessLike_data():
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))

        # 查询 GuessLikeData 表的数据，分页查询
        query = GuessLikeData.query

        # 获取统计信息
        counts = query.count()  # 总记录数
        pages = (counts // page_size) + (1 if counts % page_size > 0 else 0)  # 计算总页数

        # 获取当前页数据
        guess_like_data = query.offset((page - 1) * page_size).limit(page_size).all()

        items_list = []
        for item in guess_like_data:
            # 处理 items 字段，假设存储为 JSON 格式，直接使用
            items_list.extend(item.items)

        # 返回结果
        return jsonify({
            "code": "1",
            "msg": "操作成功",
            "result": {
                "counts": counts,
                "pageSize": page_size,
                "pages": pages,
                "page": page,
                "items": items_list
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500




# 允许的视频文件扩展名
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 路由：提供视频文件访问
@bp.route('/video/<filename>', methods=['GET'])
def get_video(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({'message': 'Video not found'}), 404


# 查询视频和视频组
@bp.route('/videos', methods=['GET'])
def get_home_videos():
    # 查询所有视频组数据
    video_groups = VideoGroup.query.all()

    # 如果没有视频数据
    if not video_groups:
        return jsonify({
            'message': 'No video groups found.',
            'result': []
        }), 404

    # 构造视频组及其视频数据的列表
    video_group_list = []
    for group in video_groups:
        # 获取每个视频组下的视频
        video_list = [{
            'id': video.id,
            'title': video.title,
            'url': f"http://127.0.0.1:5000/home/video/{os.path.basename(video.url)}"  # 使用相对路径映射到前端
        } for video in group.videos]

        video_group_list.append({
            'id': group.id,
            'title': group.title,
            'videos': video_list
        })

    response = {
        'message': '视频数据获取成功',
        'result': video_group_list,
        'status': 200
    }
    print(response)

    return jsonify(response)


# 上传视频文件
@bp.route('/upload/videos', methods=['POST'])
def upload_videos():
    files = request.files.getlist('file')  # 获取多个文件
    titles = request.form.get('title', '')  # 获取视频标题
    group_id = request.form.get('group_id', 1)  # 从表单中获取 group_id，默认值为 1

    if not files:
        return jsonify({'message': '没有选择视频文件', 'status': 400}), 400

    # 检查是否已经存在相同 group_id 的记录
    existing_videos = Video.query.filter_by(group_id=group_id).all()
    if existing_videos:
        # 删除已有记录并从存储中移除对应的视频文件
        for video in existing_videos:
            video_path = os.path.join(UPLOAD_FOLDER, video.url.split('/')[-1])
            if os.path.exists(video_path):
                os.remove(video_path)  # 删除文件
            db.session.delete(video)  # 删除数据库记录
        db.session.commit()  # 提交删除操作

    saved_files = []  # 存储已保存的视频文件信息

    for file in files:
        if file and allowed_file(file.filename):
            # 安全的文件名
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            # 保存视频文件到本地
            file.save(file_path)

            # 将视频的文件路径保存到数据库
            new_video = Video(
                title=titles,
                url=f"/video/{filename}",  # 返回相对路径
                group_id=group_id
            )
            db.session.add(new_video)
            db.session.commit()

            saved_files.append({
                'id': new_video.id,
                'title': new_video.title,
                'url': f"/video/{filename}"  # 返回视频路径
            })
        else:
            return jsonify({'message': '不支持的文件类型', 'status': 400}), 400

    return jsonify({
        'message': '视频上传成功',
        'status': 200,
        'result': saved_files
    }), 200
