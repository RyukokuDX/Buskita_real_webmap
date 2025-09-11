from flask import Flask

def create_app():
    app = Flask(__name__)

    # 設定ファイルを読み込む
    app.config.from_object('config')

    # ルートを登録する
    with app.app_context():
        from . import routes

    return app
