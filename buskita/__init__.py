# buskitaパッケージの初期化を行うファイルです。
# このパッケージがインポートされた際に、アプリケーションのインスタンスを生成する役割を持ちます。
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os


def create_app():
    """
    アプリケーションファクトリ関数。
    Flaskアプリケーションのインスタンスを生成し、各種設定を行った上で返します。
    これにより、テスト時などに異なる設定のアプリケーションを動的に作成できます。
    """
    app = Flask(__name__)

    # config.py から設定値を読み込みます。
    app.config.from_object("config")

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

    return app
