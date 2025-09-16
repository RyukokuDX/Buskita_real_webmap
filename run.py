import os
from buskita import create_app

# __init__.py の create_app ファクトリ関数を呼び出して、Flaskアプリケーションインスタンスを生成します。
app = create_app()

# Pythonスクリプトとして直接実行された場合にのみ、開発用のWebサーバーを起動します。
if __name__ == "__main__":
    # 環境変数からデバッグモードとポートを取得（デフォルト値も設定）
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() == "true"
    port = int(os.environ.get("FLASK_PORT", 5001))

    # 0.0.0.0 は、コンテナなどの外部からアクセスできるようにするためです。
    app.run(debug=debug_mode, host="0.0.0.0", port=port)
