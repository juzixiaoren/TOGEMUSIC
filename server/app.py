from flask import Flask
from flask_cors import CORS
from config import Config
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import dao.config as dao_config
from dao.sql_init import SQLInit
from routes.auth import auth_bp
from routes.music import music_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    
    # 初始化数据库
    database = SQLInit(dao_config.DB_PATH, dao_config.DB_NAME)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(music_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=Config.DEBUG, port=Config.SERVER_PORT)