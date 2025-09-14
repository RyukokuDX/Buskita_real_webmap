import pytest
from buskita import create_app, cache

@pytest.fixture
def app():
    """
    テスト用のFlaskアプリケーションインスタンスを作成するフィクスチャ。
    - TESTINGモードを有効にする。
    - バックグラウンドスレッドはテストに不要なため無効化する。
    """
    app = create_app(init_background_thread=False)
    app.config.update({
        "TESTING": True,
    })

    with app.app_context():
        cache.clear() # 各テストの前にキャッシュをクリア

    yield app

@pytest.fixture
def client(app):
    """
    テストクライアントを作成するフィクスチャ。
    これにより、実際にサーバーを起動せずにリクエストをシミュレートできる。
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    FlaskのCLIコマンドをテストするためのフィクスチャ。
    """
    return app.test_cli_runner()
