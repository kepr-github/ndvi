#from flask_bootstrap import Bootstrap
import folium
from flask import Flask, render_template, request 
from datetime import datetime
from json2polygon import load_polygons_from_json, add_polygons_to_map
import os
from NDVI_from_uuid import save_ndvi_image_from_uuid
import json

app = Flask(__name__, static_folder='./templates/image')
#bootstrap = Bootstrap(app)

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

                <button type="button" onclick="setFormData('{label}', '2023-08-01')" class="btn btn-primary">コピー＆詳細を見る</button>
            </div>
        """
        iframe = folium.IFrame(popup_html, width=250, height=150)
        popup = folium.Popup(iframe, max_width=250)

        polygon.add_child(popup)
        # ポリゴンをマップに追加
        polygon.add_to(map)

@app.get("/")
def index():
    # ベースマップを作成
    map = folium.Map(location=[42.983880196, 141.371933788], zoom_start=15)
 
    # JSONファイルが保存されているフォルダのパス
    json_folder_path = 'JSON'  # ここに実際のパスを指定

    # 指定されたフォルダ内のすべてのJSONファイルを処理
    for filename in os.listdir(json_folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder_path, filename)
            polygons = load_polygons_from_json(file_path)
            add_polygons_to_map(map, polygons)
    
    # マップを HTML 文字列として取得
    map_html = map._repr_html_()

    # HTMLテンプレートにマップをレンダリング
    return render_template('index.html', map=map_html)


@app.route('/address', methods=['GET', 'POST'])
def sample_form_temp():

    if request.method == 'POST':
         # フォームから'uuid'と'date'を取得
        req1 = request.form['uuid']
        if req1 =='':
            req1 = '4f3c5e84-0178-4f81-aa6e-5033c696d0ae'
        req2 = request.form['date']  # 日付のデータをフォームから取得
        if req2 =='':
            req2 = '2023-07-21'

        print(req1, req2)
        # 日付の形式が正しいかチェック
        try:
            # 日付の形式を確認（'YYYY-MM-DD'形式であることを確認）
            datetime.strptime(req2, '%Y-%m-%d')
        except ValueError:
            # 日付の形式が不正な場合はエラーメッセージとともにフォームを再表示
            error_msg = "日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。"
            return render_template('index.html', error=error_msg)
        
        # 関数の使用
        image_path = save_ndvi_image_from_uuid(polygon_uuid=req1, date_start_str=req2)  
        print(f"画像が保存されました: {image_path}")
        # 'map.html'にデータを渡してレンダリング
        return render_template('map.html', polygon_uuid=req1, date=req2, image_path=image_path)
    else:
        return render_template('index.html')
    
@app.get("/layout")
def layout():
    return render_template('layout.html')



if __name__ == '__main__':
    app.run()