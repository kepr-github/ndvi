import json

def load_polygons_from_json(file_path, encoding='utf-8'):
    """
    指定されたJSONファイルからポリゴンデータを読み込み、リストに格納して返す。

    Args:
    file_path (str): JSONファイルのパス。
    encoding (str): ファイルのエンコーディング。デフォルトは 'utf-8'。

    Returns:
    list of tuple: ポリゴンの座標とUUIDを含むリスト。
    """
    try:
        
        # JSONファイルを指定されたエンコーディングで読み込む
        with open(file_path, 'r', encoding=encoding) as file:
            data = json.load(file)

        # 抽出されたポリゴンデータを格納するリスト
        polygons = []

        # JSONデータからポリゴンデータを抽出
        for feature in data['features']:
            # 経度緯度の順から緯度経度の順に変換
            coordinates = [[lat_lng[::-1] for lat_lng in polygon] for polygon in feature['geometry']['coordinates']]
            centroid_lng = feature['properties'].get('point_lng', None)
            centroid_lat = feature['properties'].get('point_lat', None)
            centroid = (centroid_lat, centroid_lng) if centroid_lat is not None and centroid_lng is not None else None
            polygon_uuid = feature['properties'].get('polygon_uuid', 'No UUID')
            local_government_cd = feature['properties'].get('local_government_cd', 'No Local Government Code')
            polygons.append((coordinates, centroid, polygon_uuid, local_government_cd))

        return polygons

    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []



import folium
def add_polygons_to_map(map, polygons):
    """
    指定されたFoliumマップにポリゴンを追加する。

    Args:
    map (folium.Map): Foliumマップオブジェクト。
    polygons (list of tuple): ポリゴンの座標、重心の座標、UUIDを含むリスト。
    """
    for coords, centroid, uuid, local_gov_cd in polygons:
        # Polygonインスタンスを作成
        polygon = folium.Polygon(
            locations=coords,
            color='blue',
            fill=True,
            fill_color='rgba(0,0,0,0)'
        )
        short_uuid = uuid[-5:]
        address = get_local_government_name_by_code_json(local_gov_cd)
        pref_city_name = address[0] + address[1]

        # ポリゴンにポップアップを追加（重心の座標を含む）
        popup_html = f"""
            <!DOCTYPE html>
            <div>
                <form action="/address" method="post" target="_top">
                    <div class="form-group">
                        <label class="control-label" for="pop_uuid">
                            {pref_city_name}<br>
                            <br>
                            畑ID 末尾 5桁:{short_uuid}<br>
                            重心座標: {centroid[0]}, {centroid[1]}<br>                           
                        </label>
                        <input type="hidden" id="pop_uuid" name = "pop_uuid" class="form-control" value={uuid}>
                    </div>
                    <!-- 日付入力フィールド -->
                    <div class="form-group">
                        <label class="control-label" for="pop_date">日付</label>
                        <input type="date" id='pop_date' name="pop_date" class="form-control">
                    </div>
                    <button type="submit" class="btn btn-primary">この畑を見る</button>
                </form>     
            </div>
        """

        popup = folium.Popup(popup_html, max_width=250)

        polygon.add_child(popup)
        # ポリゴンをマップに追加
        polygon.add_to(map)


def get_coordinates_from_uuid(file_path, polygon_uuid):
    """
    GeoJSONファイルから特定のUUIDを持つポリゴンの座標を抽出します。

    パラメータ:
    file_path (str): GeoJSONファイルへのファイルパス。
    polygon_uuid (str): 検索するポリゴンのUUID。

    戻り値:
    list: ポリゴンの座標のリスト。見つからない場合はNoneを返します。
    """
    try:
        # ファイルを開いてデータを読み込む
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        
        
        for feature in data['features']:
            # UUIDが一致するか確認
            if feature['properties'].get('polygon_uuid') == polygon_uuid:
                # UUIDが一致したら座標を返す
                return feature['geometry']['coordinates']
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    return None

# JSONファイルから地方自治体コードと対応する名称を読み込む
local_gov_file_path_json = 'LocalGovCode.json'

# JSONファイルの読み込み
with open(local_gov_file_path_json, 'r', encoding='utf-8') as file:
    local_gov_data_json = json.load(file)

def get_local_government_name_by_code_json(local_gov_cd):
    """
    指定された地方自治体コードに対応する都道府県名と市区町村名を返す（JSONバージョン）。

    Args:
    local_gov_cd : 地方自治体コード。

    Returns:
    tuple: 都道府県名と市区町村名のタプル。該当する地方自治体がない場合はメッセージを返す。
    """
    # 入力されたコードに対応するデータを検索
    for item in local_gov_data_json:
        if item['団体コード'] == local_gov_cd:
            prefecture = item['都道府県名\n（漢字）']
            city = item['市区町村名\n（漢字）']
            return prefecture, city
    return "該当する地方自治体が見つかりません。"

