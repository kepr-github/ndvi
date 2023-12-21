#from flask_bootstrap import Bootstrap
import json
import folium
from flask import Flask, jsonify, render_template, request 
from datetime import datetime
from json2polygon import load_polygons_from_json, add_polygons_to_map
import os
from NDVI_from_uuid import get_ndvi_image_from_uuid, add_image_to_map

app = Flask(__name__, static_folder='static')
#bootstrap = Bootstrap(app)

# グローバル変数として map_html を定義
global_map = None

@app.get("/")
def index():
    global global_map # グローバル変数を使用することを宣言

    # ベースマップを作成
    map = folium.Map(location=[42.998196652, 141.407992252], zoom_start=15)
 
    # JSONファイルが保存されているフォルダのパス
    file_path = 'JSON/2023_011053.json'  # ここに実際のパスを指定

    polygons = load_polygons_from_json(file_path)
    add_polygons_to_map(map, polygons)

    global_map = map

    # マップを HTML 文字列として取得
    map_html = map._repr_html_()

    # HTMLテンプレートにマップをレンダリング
    return render_template('index.html', map=map_html)


@app.route('/address', methods=['GET', 'POST'])
def sample_form_temp():
    global global_map # グローバル変数を使用することを宣言

    if request.method == 'POST':
         # フォームから'uuid'と'date'を取得
        uuid = request.form['pop_uuid']
        date = request.form['pop_date']  # 日付のデータをフォームから取得
        
        print(uuid, date)
        
        map = global_map

        # 関数の使用
        images = get_ndvi_image_from_uuid(uuid, date)
        overlay_map_html = add_image_to_map(map, images['ndvi_img'], uuid) 
       

        # 'index.html'にデータを渡してレンダリング
        return render_template('index.html', map=overlay_map_html,uuid = uuid, taken_date = images['taken_date'])
    else:
        return render_template('index.html')
    
# JSON データを返すエンドポイント
@app.route('/get_local_gov_data')
def get_local_gov_data():
    with open('LocalGovCode.json', 'r', encoding='utf-8') as file:
        local_gov_data = json.load(file)
    return jsonify(local_gov_data)

# 団体コードを返すエンドポイント
@app.route('/get_gov_code')
def get_gov_code():
    prefecture = request.args.get('prefecture')
    municipality = request.args.get('municipality')
    with open('LocalGovCode.json', 'r', encoding='utf-8') as file:
        local_gov_data = json.load(file)
        for item in local_gov_data:
            if item['都道府県名\n（漢字）'] == prefecture and item['市区町村名\n（漢字）'] == municipality:
                return jsonify({'団体コード': item['団体コード']})
    return jsonify({'団体コード': 'Not Found'})

# 団体コードに基づいて JSON ファイルをロードし、マップを作成するエンドポイント
@app.route('/get_map')
def get_map():
    global global_map
    gov_code = request.args.get('gov_code')
    file_path = f'JSON/2023_{gov_code}.json'

    # JSON データをロード
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # マップを作成
    lat = data['features'][0]['geometry']['coordinates'][0][0][1]
    lon = data['features'][0]['geometry']['coordinates'][0][0][0]

    map = folium.Map(location=[lat, lon], zoom_start=15)

    polygons = load_polygons_from_json(file_path)
    add_polygons_to_map(map, polygons)

    global_map = map

    # マップを HTML 文字列として取得
    map_html = map._repr_html_()

    # HTMLテンプレートにマップをレンダリング
    return render_template('map.html', map=map_html)

if __name__ == '__main__':
    app.run()