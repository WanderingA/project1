from sqlalchemy.orm import Session, joinedload
from database import SessionLocal, User, Nodes, Classification
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import func, case
import json


class LoginData(BaseModel):
    username: str
    password: str


# class User(BaseModel):
#     username: str
#     password: str
#     is_admin: bool


# 密码加密上下文
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_password(plain_password, hashed_password):
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"An error occurred while verifying password: {e}")  # 打印错误信息
        return False


def authenticate_user(db: Session, username: str, password: str):
    try:
        user = db.query(User).filter(User.username == username).first()
        # print(user.username, user.is_admin)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    except Exception as e:
        print(f"An error occurred: {e}")  # 打印错误信息
        return False


def is_admin_user(user: User):
    return user.is_admin


def get_nodes_info(db: Session, skip: int = 0, limit: int = 10):
    try:
        nodes_info = db.query(Nodes).offset(skip).limit(limit).all()
        return nodes_info
    except Exception as e:
        print(f"An error occurred: {e}")  # 打印错误信息
        return False


def get_classification_node_number(db: Session):
    try:
        classifications = ['Human', 'Tracked', 'Wheeled', 'Aircraft']
        query = db.query(
            Classification.classification,
            func.count(Classification.node_id.distinct()).label('count')
        ).filter(Classification.classification.in_(classifications))
        query = query.group_by(Classification.classification)
        result = query.all()
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_node_number(db: Session):
    try:
        total_nodes = db.query(func.count(Nodes.id)).label('total_nodes')
        normal_nodes = db.query(func.count(Nodes.seismic_state == '正常')).label('normal_nodes')

        # 将两个查询合并为一个子查询
        subquery = db.query(total_nodes, normal_nodes).subquery()

        # 执行最终的查询
        result = db.query(subquery).one()
        return {'total_nodes': result[0], 'normal_nodes': result[1]}
    except Exception as e:
        print(f"An error occurred: {e}")  # 打印错误信息
        return False


def get_node_status(db: Session):
    try:
        # 使用 ORM 构建 query
        seismic_state_normal_count = db.query(func.count(Nodes.id)).filter(Nodes.seismic_state == '正常').scalar()
        gps_state_abnormal_count = db.query(func.count(Nodes.id)).filter(Nodes.gps_state != '正常').scalar()
        detector_state_abnormal_count = db.query(func.count(Nodes.id)).filter(Nodes.detector_state != '正常').scalar()
        angle_tilted_count = db.query(func.count(Nodes.id)).filter(Nodes.angle != '正常').scalar()
        # 将结果封装为一个字典或列表
        return [seismic_state_normal_count, gps_state_abnormal_count, detector_state_abnormal_count, angle_tilted_count]
    except Exception as e:
        print("数据库查询错误:", str(e))
        return []


# def get_nodes_with_classification(db: Session):
#     try:
#         # 使用 joinedload 来预加载 Classification 对象
#         query = db.query(Nodes).options(joinedload(Nodes.classification))
#
#         # 执行查询并获取结果
#         result = query.all()
#         return result
#     except Exception as e:
#         print("数据库查询错误:", str(e))
#         return []


# 构建ORM查询
def get_nodes_with_classification(db: Session):
    # 获取每个节点ID的最大时间戳的子查询
    subquery = db.query(Classification.node_id, func.max(Classification.timestamp).label("max_timestamp")) \
                .group_by(Classification.node_id) \
                .subquery()
    # 主查询，连接Nodes和Classification表，以及子查询
    query = db.query(Nodes, Classification) \
                .join(Classification, Nodes.node_id == Classification.node_id) \
                .join(subquery, subquery.c.node_id == Classification.node_id) \
                .filter(Classification.timestamp == subquery.c.max_timestamp) \
                .all()
    # 将查询结果转换为字典列表
    result = [{"node_id": nodes.node_id,
               "classification": classification.classification,
               "longitude": nodes.longitude,
               "latitude": nodes.latitude,
               "timestamp": classification.timestamp} for nodes, classification in query]
    return result

# def get_current_user(db: Session, username: str):
#     try:
#         user = db.query(User).filter(User.username == username).first()
#         print(user.username, user.is_admin)
#         if not user:
#             return False
#         return user
#     except Exception as e:
#         print(f"An error occurred: {e}")  # 打印错误信息
#         return False

# def register_user(db: Session, username: str, password: str):
#     hashed_password = pwd_context.hash(password)
#     db_user = User(username=username, hashed_password=hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user


if __name__ == '__main__':
    node_allinfo = get_nodes_with_classification(SessionLocal())
    print([node_allinfo])
