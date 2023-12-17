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
            polygons.append((coordinates, centroid, polygon_uuid))

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
    for coords, centroid, label in polygons:
        # Polygonインスタンスを作成
        polygon = folium.Polygon(
            locations=coords,
            color='blue',
            fill=True,
            fill_color='blue'
        )
        # ポリゴンにポップアップを追加（重心の座標を含む）
        popup_html = f"""
            <!DOCTYPE html>
            <div>
                畑ID: {label}<br>
                重心座標: {centroid[0]}, {centroid[1]}
                <form>
                    <input type="date" id='date-{label}' name="date" value="2023-07-21">
                </form>     
                <button onclick="window.parent.setFormData('{label}', document.getElementById('date-{label}').value)" class="btn btn-primary">この畑を見る</button>
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
