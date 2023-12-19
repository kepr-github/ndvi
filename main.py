#from flask_bootstrap import Bootstrap
import folium
from flask import Flask, render_template, request 
from datetime import datetime
from json2polygon import load_polygons_from_json, add_polygons_to_map
import os
from NDVI_from_uuid import get_ndvi_image_from_uuid, save_true_and_NDVI_side_by_side

app = Flask(__name__, static_folder='./templates/image')
#bootstrap = Bootstrap(app)

# グローバル変数として map_html を定義
global_map_html = None

@app.get("/")
def index():
    global global_map_html  # グローバル変数を使用することを宣言

    # ベースマップを作成
    map = folium.Map(location=[42.998196652, 141.407992252], zoom_start=15)
 
    # JSONファイルが保存されているフォルダのパス
    json_folder_path = 'JSON'  # ここに実際のパスを指定

    # 指定されたフォルダ内のすべてのJSONファイルを処理
    for filename in os.listdir(json_folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder_path, filename)
            polygons = load_polygons_from_json(file_path)
            add_polygons_to_map(map, polygons)
    
    # マップを HTML 文字列として取得
    global_map_html = map._repr_html_()

    # HTMLテンプレートにマップをレンダリング
    return render_template('index.html', map=global_map_html)


@app.route('/address', methods=['GET', 'POST'])
def sample_form_temp():
    global global_map_html  # グローバル変数を使用することを宣言

    if request.method == 'POST':
         # フォームから'uuid'と'date'を取得
        uuid = request.form['pop_uuid']
        date = request.form['pop_date']  # 日付のデータをフォームから取得
        if date =='':
            date = '2023-07-21'

        print(uuid, date)
        # 日付の形式が正しいかチェック
        try:
            # 日付の形式を確認（'YYYY-MM-DD'形式であることを確認）
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            # 日付の形式が不正な場合はエラーメッセージとともにフォームを再表示
            error_msg = "日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。"
            return render_template('index.html', error=error_msg)
        
        # 関数の使用
        images = get_ndvi_image_from_uuid(polygon_uuid=uuid, date_start_str=date)
        image_path = save_true_and_NDVI_side_by_side(images['true_img'], images['ndvi_img'], uuid, images['taken_date'])  
        print(f"画像が保存されました: {image_path}")
        # 'map.html'にデータを渡してレンダリング
        return render_template('map.html', map=global_map_html)
    else:
        return render_template('index.html')
    
@app.get("/layout")
def layout():
    return render_template('layout.html')



if __name__ == '__main__':
    app.run()