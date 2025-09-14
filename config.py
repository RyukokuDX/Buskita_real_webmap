import os
from dotenv import load_dotenv

load_dotenv()

# アプリケーション全体で使用する設定値を定義するファイルです。
# APIキーやデータベース接続情報など、コードから分離したい情報をここに記述します。

# バス会社APIのベースURL
API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.buskita.com")

# APIリクエスト時に使用するサイトID（9は滋賀帝産バスを示す）
SITE_ID = int(os.environ.get("SITE_ID", 9))

# APIがダウンした際に使用するバックアップファイルのパス
BACKUP_FILE = "buskita/data/last_known_buses.json"

# APIリクエスト時に送信するHTTPヘッダー
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
}

# --- キャッシュ設定 ---
# Flask-Caching の設定
# CACHE_TYPE: 使用するキャッシュのバックエンドを指定します。
#   - 'SimpleCache': 開発用のシンプルなインメモリキャッシュ。プロセス間で共有はされません。
#   - 'RedisCache': 本番環境で推奨される、Redisサーバーを使用したキャッシュ。
#   - 'FileSystemCache': ファイルシステムをバックエンドとして使用するキャッシュ。
CACHE_TYPE = os.environ.get("CACHE_TYPE", "SimpleCache")

# CACHE_DEFAULT_TIMEOUT: キャッシュアイテムのデフォルトの有効期限（秒単位）。
# バックグラウンドでのデータ更新が10秒間隔のため、それより少し長い30秒に設定。
# これにより、万が一データ更新が失敗しても、最大30秒でキャッシュが切れ、
# 古いデータが表示され続けるのを防ぎます。
CACHE_DEFAULT_TIMEOUT = int(os.environ.get("CACHE_DEFAULT_TIMEOUT", 30))

# Flaskアプリケーションの秘密鍵
SECRET_KEY = os.environ.get("SECRET_KEY", "a_default_secret_key_for_development")
