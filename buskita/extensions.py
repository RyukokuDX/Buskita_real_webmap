from flask_caching import Cache

# アプリケーションのグローバルなキャッシュインスタンスを作成
# 設定は create_app 内で app.config から読み込まれる
cache = Cache()
