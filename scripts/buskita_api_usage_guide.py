"""
buskita.com API 使用ガイド

PlaywrightによるWebスクレイピングで発見された10個のAPIエンドポイントの詳細な使用方法
"""

import requests
from typing import Dict, Any, List, Optional


class BuskitaAPIClient:
    """buskita.com APIクライアント"""

    def __init__(self):
        self.base_url = "https://api.buskita.com"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ja",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        }

    def _make_request(
        self, endpoint: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """APIリクエストを実行"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, headers=self.headers, json=data)

            if response.status_code == 200:
                return response.json()
            else:
                print(f"エラー: {endpoint} - Status: {response.status_code}")
                return None
        except Exception as e:
            print(f"リクエストエラー: {str(e)}")
            return None

    # ===== 1. バス会社情報 =====
    def get_companies_dictionary(
        self, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        バス会社辞書を取得

        Args:
            language (int): 言語設定 (1=日本語, 2=英語)

        Returns:
            List[Dict]: バス会社情報のリスト

        Example:
            companies = client.get_companies_dictionary()
            for company in companies:
                print(f"{company['name']} - {company['shortName']}")
        """
        result = self._make_request(
            "get-companies-dictionary", {"language": language})
        return result["companiesDictionary"] if result else None

    # ===== 2. ランドマーク情報 =====
    def get_landmarks_dictionary(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        ランドマーク辞書を取得

        Args:
            site_id (int): サイトID (9=滋賀帝産)
            language (int): 言語設定

        Returns:
            List[Dict]: ランドマーク情報のリスト (緯度経度含む)

        Example:
            landmarks = client.get_landmarks_dictionary()
            for landmark in landmarks:
                lat = landmark['position']['latitude']
                lng = landmark['position']['longitude']
                print(f"{landmark['name']}: ({lat}, {lng})")
        """
        result = self._make_request(
            "get-landmarks-dictionary", {"language": language,
                                         "siteId": site_id}
        )
        return result["landmarksDictionary"] if result else None

    # ===== 3. 重要なお知らせ =====
    def get_dialog_informations(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        重要なお知らせを取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            List[Dict]: お知らせ情報のリスト

        Example:
            news = client.get_dialog_informations()
            for info in news:
                print(f"【{info['title']}】")
                print(f"公開日: {info['published']}")
        """
        result = self._make_request(
            "get-dialog-informations", {"language": language,
                                        "siteId": site_id}
        )
        return result["informations"] if result else None

    # ===== 4. 祝日情報 =====
    def get_holidays(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[Dict[str, List[Dict[str, str]]]]:
        """
        祝日情報を取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            Dict: 会社別祝日情報

        Example:
            holidays = client.get_holidays()
            for company, holiday_list in holidays.items():
                print(f"{company}の祝日:")
                for holiday in holiday_list:
                    print(f"  - {holiday['date']}")
        """
        result = self._make_request(
            "get-holidays", {"language": language, "siteId": site_id}
        )
        return result["holidays"] if result else None

    # ===== 5. バス停グループ =====
    def get_busstops_group(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        バス停グループを取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            List[Dict]: バス停グループのリスト

        Example:
            groups = client.get_busstops_group()
            for group in groups:
                print(f"グループ{group['id']}: {group['group_name']}")
        """
        result = self._make_request(
            "get-busstops-group", {"language": language, "siteId": site_id}
        )
        return result["groups"] if result else None

    # ===== 6. バス停グルーピング =====
    def get_busstops_grouping(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        バス停とグループの関連付けを取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            List[Dict]: バス停グルーピング情報

        Example:
            groupings = client.get_busstops_grouping()
            for item in groupings:
                print(f"会社:{item['company_no']}, バス停:{item['bus_stop_no']}, グループ:{item['group_id']}")
        """
        result = self._make_request(
            "get-busstops-grouping", {"language": language, "siteId": site_id}
        )
        return result["groupings"] if result else None

    # ===== 7. メンテナンス情報 =====
    def get_maintenances(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        メンテナンス情報を取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            List[Dict]: メンテナンス情報のリスト

        Example:
            maintenances = client.get_maintenances()
            if maintenances:
                for maintenance in maintenances:
                    print(f"メンテナンス: {maintenance}")
            else:
                print("現在メンテナンス情報はありません")
        """
        result = self._make_request(
            "get-maintenances", {"language": language, "siteId": site_id}
        )
        return result["maintenances"] if result else None

    # ===== 8. のりば別名 =====
    def get_noriba_alias(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[List[Dict[str, Any]]]:
        """
        のりば別名を取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            List[Dict]: のりば別名のリスト
        """
        result = self._make_request(
            "get-noriba-alias", {"language": language, "siteId": site_id}
        )
        return result["aliases"] if result else None

    # ===== 9. UI辞書バージョン =====
    def get_ui_dictionary_version(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[int]:
        """
        UI辞書のバージョンを取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            int: UI辞書バージョン番号
        """
        result = self._make_request(
            "get-ui-dictionary-version", {"language": language,
                                          "siteId": site_id}
        )
        return result["uiDictionaryVersion"] if result else None

    # ===== 10. バス停辞書バージョン =====
    def get_busstops_version(
        self, site_id: int = 9, language: int = 1
    ) -> Optional[int]:
        """
        バス停辞書のバージョンを取得

        Args:
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            int: バス停辞書バージョン番号
        """
        result = self._make_request(
            "get-busstops-version", {"language": language, "siteId": site_id}
        )
        return result["busstopsDictionaryVersion"] if result else None

    # ===== 既知のエンドポイント: バス位置取得 =====
    def get_bus_location(
        self, work_no: str = "48385", site_id: int = 9, language: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        バス位置情報を取得 (既知のエンドポイント)

        Args:
            work_no (str): 作業番号
            site_id (int): サイトID
            language (int): 言語設定

        Returns:
            Dict: バス位置情報
        """
        return self._make_request(
            "get-bus", {"workNo": work_no,
                        "siteId": site_id, "language": language}
        )


def demonstrate_all_apis():
    """全APIの使用例をデモンストレーション"""
    client = BuskitaAPIClient()

    print("🚌 buskita.com API 実用例デモ")
    print("=" * 60)

    # 1. バス会社情報
    print("\n1️⃣ バス会社情報")
    companies = client.get_companies_dictionary()
    if companies:
        print(f"登録バス会社数: {len(companies)}社")
        for i, company in enumerate(companies[:3], 1):  # 最初の3社のみ表示
            print(f"  {i}. {company['name']} ({company['shortName']})")
            print(f"     カラー: 前景={company['fgcc']}, 背景={company['bgcc']}")

    # 2. ランドマーク情報
    print("\n2️⃣ ランドマーク情報")
    landmarks = client.get_landmarks_dictionary()
    if landmarks:
        print(f"登録ランドマーク数: {len(landmarks)}件")
        for i, landmark in enumerate(landmarks[:3], 1):  # 最初の3件のみ表示
            lat = landmark["position"]["latitude"]
            lng = landmark["position"]["longitude"]
            print(f"  {i}. {landmark['name']}")
            print(f"     位置: ({lat}, {lng})")

    # 3. 重要なお知らせ
    print("\n3️⃣ 重要なお知らせ")
    news = client.get_dialog_informations()
    if news:
        print(f"お知らせ件数: {len(news)}件")
        for i, info in enumerate(news, 1):
            print(f"  {i}. 【{info['title']}】")
            print(f"     公開日: {info['published']}")
            print(f"     詳細: {info['targetUrl']}")

    # 4. 祝日情報
    print("\n4️⃣ 祝日情報")
    holidays = client.get_holidays()
    if holidays:
        for company, holiday_list in holidays.items():
            print(f"  {company}の祝日 ({len(holiday_list)}日):")
            for holiday in holiday_list[:3]:  # 最初の3日のみ表示
                print(f"    - {holiday['date']}")

    # 5. バス停グループ
    print("\n5️⃣ バス停グループ")
    groups = client.get_busstops_group()
    if groups:
        print(f"グループ数: {len(groups)}個")
        for group in groups:
            print(f"  グループ{group['id']}: {group['group_name']}")

    # 6. システム情報
    print("\n6️⃣ システム情報")
    ui_version = client.get_ui_dictionary_version()
    stops_version = client.get_busstops_version()
    print(f"  UI辞書バージョン: {ui_version}")
    print(f"  バス停辞書バージョン: {stops_version}")

    # 7. バス位置情報（既知のAPI）
    print("\n7️⃣ バス位置情報")
    bus_location = client.get_bus_location()
    if bus_location:
        bus_count = len(bus_location.get("bus", []))
        print(f"  現在運行中のバス: {bus_count}台")
        is_cached = bus_location.get("isCached", False)
        print(f"  キャッシュ使用: {'はい' if is_cached else 'いいえ'}")


def create_practical_usage_examples():
    """実用的な使用例を作成"""
    examples = {
        "landmark_finder": """
# ランドマーク検索機能
def find_landmarks_near_university():
    client = BuskitaAPIClient()
    landmarks = client.get_landmarks_dictionary()
    
    universities = [lm for lm in landmarks if '大学' in lm['name']]
    
    print("大学一覧:")
    for univ in universities:
        print(f"- {univ['name']}")
        print(f"  位置: {univ['position']['latitude']}, {univ['position']['longitude']}")
        
find_landmarks_near_university()
""",
        "company_color_map": """
# バス会社カラーマップ作成
def create_company_color_map():
    client = BuskitaAPIClient()
    companies = client.get_companies_dictionary()
    
    color_map = {}
    for company in companies:
        color_map[company['company_no']] = {
            'name': company['name'],
            'colors': {
                'foreground': company['fgcc'],
                'background': company['bgcc']
            }
        }
    
    return color_map

colors = create_company_color_map()
print(f"帝産湖南交通の色: {colors['tkt']['colors']}")
""",
        "news_monitor": """
# お知らせ監視システム
def monitor_important_news():
    client = BuskitaAPIClient()
    
    while True:
        news = client.get_dialog_informations()
        
        if news:
            latest = news[0]  # 最新のお知らせ
            print(f"最新情報: {latest['title']}")
            
            # 重要なキーワードをチェック
            important_keywords = ['運賃', '運休', 'ダイヤ', '路線']
            if any(keyword in latest['title'] for keyword in important_keywords):
                print("🚨 重要なお知らせが更新されました！")
                print(f"詳細: {latest['targetUrl']}")
        
        time.sleep(3600)  # 1時間ごとにチェック
        
# monitor_important_news()  # 実際の監視を開始する場合
""",
    }

    print("\n\n💡 実用的な使用例")
    print("=" * 60)

    for title, code in examples.items():
        print(f"\n🎯 {title}")
        print("-" * 30)
        print(code)


if __name__ == "__main__":
    # 全APIのデモンストレーション
    demonstrate_all_apis()

    # 実用的な使用例
    create_practical_usage_examples()
