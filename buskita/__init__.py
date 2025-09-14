# buskitaパッケージの初期化を行うファイルです。
# このパッケージがインポートされた際に、アプリケーションのインスタンスを生成する役割を持ちます。
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from threading import Thread
import time

from buskita.extensions import cache


def update_bus_data_periodically(app):
    """
    5秒ごとにバスデータを取得し、キャッシュを更新するバックグラウンドタスク。
    """
    from buskita.services import fetch_and_cache_bus_data

    with app.app_context():
        while True:
            try:
                print("【Background Thread】バス情報を更新します...")
                fetch_and_cache_bus_data()
                print("【Background Thread】バス情報の更新が完了しました。")
            except Exception as e:
                # バックグラウンドタスクでのエラーはコンソールに出力
                print(f"【Background Thread】エラーが発生しました: {e}")
            time.sleep(10)  # 10秒待機


def register_logging(app):
    """ロギングを設定する"""
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/buskita.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Buskita startup')


def start_background_tasks(app):
    """バックグラウンドタスクを開始する"""
    thread = Thread(target=update_bus_data_periodically, args=(app,), daemon=True)
    thread.start()


def create_app(init_background_thread=True):
    """
    アプリケーションファクトリ関数。
    Flaskアプリケーションのインスタンスを生成し、各種設定を行った上で返します。
    これにより、テスト時などに異なる設定のアプリケーションを動的に作成できます。
    """
    app = Flask(__name__)

    # config.py から設定値を読み込みます。
    app.config.from_object("config")

    # キャッシュをアプリケーションに初期化・登録
    cache.init_app(app)

    # ロギング設定
    register_logging(app)

    # Blueprint を登録します。
    from buskita.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # アプリケーションの初回起動時にのみバックグラウンドスレッドを開始
    if init_background_thread:
        start_background_tasks(app)

    return app
