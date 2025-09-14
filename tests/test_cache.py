import pytest
import requests
from unittest.mock import patch, MagicMock
from buskita import cache
from buskita.services import get_buses_from_cache, fetch_and_cache_bus_data

def test_cache_set_and_get(app):
    """
    キャッシュの基本的なset/get操作をテストする。
    """
    with app.app_context():
        # テスト用のダミーデータをキャッシュに保存
        test_data = [{"id": 1, "name": "Test Bus"}]
        cache.set("test_key", test_data)

        # キャッシュからデータを取得し、保存したデータと一致するか検証
        retrieved_data = cache.get("test_key")
        assert retrieved_data is not None
        assert retrieved_data[0]["name"] == "Test Bus"

def test_get_buses_from_cache(app):
    """
    get_buses_from_cache関数が正しくキャッシュからデータを取得できるかテストする。
    """
    with app.app_context():
        # 'live_bus_data' キーにダミーデータを設定
        dummy_bus_data = [{"id": "bus123", "lat": 34.9, "lng": 135.8}]
        cache.set('live_bus_data', dummy_bus_data)

        # 関数を実行してデータを取得
        buses = get_buses_from_cache()

        # 取得したデータがキャッシュの内容と一致するか検証
        assert buses is not None
        assert len(buses) == 1
        assert buses[0]["id"] == "bus123"

@patch('buskita.services.requests.post')
def test_fetch_and_cache_bus_data_success(mock_post, app):
    """
    APIからのデータ取得が成功した場合に、fetch_and_cache_bus_data関数が
    正しくデータを取得し、キャッシュに保存することをテストする。
    """
    # APIからのレスポンスをモック（偽造）する
    mock_response_get_buses = MagicMock()
    mock_response_get_buses.status_code = 200
    mock_response_get_buses.json.return_value = {
        "buses": [{"workNo": "1", "position": {"latitude": 34.0, "longitude": 135.0}}]
    }

    mock_response_get_bus_detail = MagicMock()
    mock_response_get_bus_detail.status_code = 200
    mock_response_get_bus_detail.json.return_value = {
        "bus": [{"routeNames": {"1": "瀬田"}, "delayMinutes": 5}]
    }
    
    # requests.postが呼ばれた際に、上記で作成したモックレスポンスを返すように設定
    # 1回目の呼び出し(get-buses)と2回目以降の呼び出し(get-bus)で異なる値を返す
    mock_post.side_effect = [mock_response_get_buses, mock_response_get_bus_detail]

    with app.app_context():
        # キャッシュが空であることを確認
        assert cache.get('live_bus_data') is None

        # テスト対象の関数を実行
        fetch_and_cache_bus_data()

        # キャッシュにデータが正しく保存されたか検証
        cached_data = cache.get('live_bus_data')
        assert cached_data is not None
        assert len(cached_data) == 1
        assert cached_data[0]["workNo"] == "1"
        assert cached_data[0]["routeNames"]["1"] == "瀬田"
        assert cached_data[0]["delayMinutes"] == 5


@patch('buskita.services.requests.post')
def test_fetch_and_cache_bus_data_api_error(mock_post, app):
    """
    APIからのデータ取得が失敗した場合に、キャッシュが更新されないことをテストする。
    """
    # APIからのレスポンスをモック（RequestExceptionを発生させる）
    mock_post.side_effect = requests.exceptions.RequestException

    with app.app_context():
        # 事前にダミーデータをキャッシュに入れておく
        initial_data = [{"id": "old_bus"}]
        cache.set('live_bus_data', initial_data)

        # テスト対象の関数を実行
        fetch_and_cache_bus_data()

        # APIエラーが発生しても、キャッシュは古いデータのまま変わっていないことを確認
        cached_data = cache.get('live_bus_data')
        assert cached_data is not None
        assert cached_data[0]["id"] == "old_bus"
