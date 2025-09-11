# このファイルがアプリケーションの実行エントリーポイント（起動スクリプト）です。
# `python3 run.py` コマンドでWebサーバーが起動します。
from buskita import create_app

# __init__.py の create_app ファクトリ関数を呼び出して、Flaskアプリケーションインスタンスを生成します。
app = create_app()

# Pythonスクリプトとして直接実行された場合にのみ、開発用のWebサーバーを起動します。
if __name__ == "__main__":
    # 0.0.0.0 は、コンテナなどの外部からアクセスできるようにするためです。
    # port=5001 で、5001番ポートを使用するよう指定しています。
    app.run(debug=True, host="0.0.0.0", port=5001)
