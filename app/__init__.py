# FlaskApp/app/__init__.py
# Flask 애플리케이션 인스턴스를 생성하고 초기 설정을 수행하는 모듈입니다.
import os, uuid
from flask import Flask
from flask_session import Session  # 세션 관리를 위한 Flask-Session 확장
from flask_mysqldb import MySQL  # MySQL 데이터베이스 사용을 위한 확장
from rediscluster import RedisCluster  # Redis 클러스터를 사용하기 위한 라이브러리

mysql = MySQL()
redis_cluster = None

def create_app():
    global redis_cluster
    app = Flask(__name__)
    
    #rkeys = os.urandom(24)
    rkeys = '7A815454AE006BF25152E95AEB20A93B6914CD6B'
    print("random keys = ", rkeys)
    app.secret_key = rkeys  # 세션을 위한 시크릿 키 설정
    
    # Redis 클러스터 노드 설정 (제공된 노드 정보를 바탕으로 수정)
    startup_nodes = [
        {'host': '192.168.99.101', 'port': '4406'},  # 마스터 노드
        {'host': '192.168.99.102', 'port': '4406'},  # 마스터 노드
        {'host': '192.168.99.103', 'port': '4406'},  # 마스터 노드
        {'host': '192.168.99.101', 'port': '4407'},
        {'host': '192.168.99.102', 'port': '4407'},
        {'host': '192.168.99.103', 'port': '4407'}
    ]

    # RedisCluster 객체 초기화
    redis_cluster = RedisCluster(startup_nodes=startup_nodes, decode_responses=False)

    # 세션 관리를 위한 Flask-Session 설정
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = redis_cluster
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'session:'

    # Flask-Session 확장을 앱에 초기화합니다.
    Session(app)


    # MariaDB 연결 설정
    app.config['MYSQL_HOST'] = '192.168.99.200'  # 데이터베이스 호스트
    app.config['MYSQL_PORT'] = 8888  # 데이터베이스 포트
    app.config['MYSQL_USER'] = 'test'  # 데이터베이스 사용자
    app.config['MYSQL_PASSWORD'] = 'test'  # 데이터베이스 비밀번호
    app.config['MYSQL_DB'] = 'test'  # 사용할 데이터베이스 이름
    
    # 앱 객체를 사용하여 MySQL 객체를 초기화합니다.
    mysql.init_app(app)
    
    # 라우트 모듈(블루프린트) 등록
    from app.routes.auth import auth  # 인증 관련 라우트 모듈
    from app.routes.post import post  # 포스트 관련 라우트 모듈

    app.register_blueprint(auth)  # 인증 라우트 등록
    app.register_blueprint(post)  # 포스트 라우트 등록

    return app  # 설정이 완료된 Flask 앱 객체 반환