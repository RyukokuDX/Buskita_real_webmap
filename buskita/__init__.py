# buskitaパッケージの初期化を行うファイルです。
# このパッケージがインポートされた際に、アプリケーションのインスタンスを生成する役割を持ちます。
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_caching import Cache
from threading import Thread
import time

# アプリケーションのグローバルなキャッシュインスタンスを作成
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

def update_bus_data_periodically():
    """
    5秒ごとにバスデータを取得し、キャッシュを更新するバックグラウンドタスク。
    """
    from buskita.services import fetch_and_cache_bus_data
    
    # create_app()からアプリケーションコンテキストを取得しないと動作しないため、
    # この関数内で create_app を呼び出してコンテキストを作成します。
    # これは少し変則的ですが、バックグラウンドスレッドでFlaskの機能を利用するための一般的な手法です。
    app = create_app(init_background_thread=False)

    with app.app_context():
        while True:
            try:
                print("【Background Thread】バス情報を更新します...")
                fetch_and_cache_bus_data()
                print("【Background Thread】バス情報の更新が完了しました。")
            except Exception as e:
                # バックグラウンドタスクでのエラーはコンソールに出力
                print(f"【Background Thread】エラーが発生しました: {e}")
            time.sleep(10) # 10秒待機


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

    # --- ここからロギング設定を追加 ---
    # `debug=False`（本番モード）の場合にのみ、ファイルへのログ出力を有効にします。
    # 開発中はコンソール出力のみとなり、ログファイルは作成されません。
    if not app.debug:
        # ログファイルを保存する 'logs' ディレクトリを作成します。
        log_dir = os.path.join(app.root_path, "..", "logs")
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)

        # RotatingFileHandler: ログファイルが肥大化しすぎないように、
        # サイズが1MBを超えたら自動で新しいファイルに切り替えます。(バックアップは3つまで)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "app.log"), maxBytes=1024 * 1024, backupCount=3
        )

        # ログのフォーマットを定義します。
        # (日時) (レベル): (メッセージ) [ファイルパス:行番号]
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        )
        file_handler.setFormatter(formatter)

        # ログファイルには、WARNINGレベル以上の重要なログのみを記録します。
        file_handler.setLevel(logging.WARNING)

        # 設定したファイルハンドラを、Flaskアプリケーションのロガーに追加します。
        app.logger.addHandler(file_handler)
        # アプリケーション全体のログレベルはINFOに設定し、コンソールにはINFOレベル以上が表示されるようにします。
        app.logger.setLevel(logging.INFO)
        app.logger.info("Buskita application startup")
    # --- ロギング設定ここまで ---

    # routes.py に定義されたURLルーティングをアプリケーションに登録します。
    with app.app_context():
        from . import routes  # noqa: F401

    # アプリケーションの初回起動時にのみバックグラウンドスレッドを開始
    if init_background_thread:
        # daemon=True にすることで、メインスレッドが終了すると共にバックグラウンドスレッドも終了する
        thread = Thread(target=update_bus_data_periodically, daemon=True)
        thread.start()

    return app
