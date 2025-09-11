# アプリケーション全体で使用する設定値を定義するファイルです。
# APIキーやデータベース接続情報など、コードから分離したい情報をここに記述します。

# バス会社APIのベースURL
API_BASE_URL = "https://api.buskita.com"

# APIリクエスト時に使用するサイトID（9は滋賀帝産バスを示す）
SITE_ID = 9

# APIがダウンした際に使用するバックアップファイルのパス
BACKUP_FILE = 'buskita/archive/last_known_buses.json'

# APIリクエスト時に送信するHTTPヘッダー
HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
}
