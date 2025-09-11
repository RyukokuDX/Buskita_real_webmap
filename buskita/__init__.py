from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)

    # 設定ファイルを読み込む
    app.config.from_object('config')

    # --- ここからロギング設定を追加 ---
    if not app.debug:
        # ログファイルのパスを設定
        log_dir = os.path.join(app.root_path, '..', 'logs')
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        
        # RotatingFileHandlerを設定
        # 1MBごとにファイルをローテーションし、バックアップは3つまで保持
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'), 
            maxBytes=1024 * 1024, 
            backupCount=3
        )
        
        # 詳細なログフォーマットを定義
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(formatter)
        
        # ログレベルをWARNING以上に設定
        file_handler.setLevel(logging.WARNING)
        
        # アプリケーションのロガーにハンドラを追加
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Buskita startup')
    # --- ロギング設定ここまで ---

    # ルートを登録する
    with app.app_context():
        from . import routes

    return app
