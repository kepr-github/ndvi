#from flask_bootstrap import Bootstrap
import folium
from flask import Flask, render_template, request 
from datetime import datetime
from sentinel_NDVI import save_ndvi_image
from json2polygon import load_polygons_from_json, add_polygons_to_map
import os

app = Flask(__name__, static_folder='./templates/image')
#bootstrap = Bootstrap(app)

@app.get("/")
def index():
    # ベースマップを作成
    map = folium.Map(location=[43.873597078, 145.05133317], zoom_start=15)
 
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
    req1 = request.form['address']
    print(req1)
    if request.method == 'POST':
         # フォームから'address'と'date'を取得
        req1 = request.form['address']
        req2 = request.form['date']  # 日付のデータをフォームから取得
        # 日付の形式が正しいかチェック
        try:
            # 日付の形式を確認（'YYYY-MM-DD'形式であることを確認）
            datetime.strptime(req2, '%Y-%m-%d')
        except ValueError:
            # 日付の形式が不正な場合はエラーメッセージとともにフォームを再表示
            error_msg = "日付の形式が正しくありません。YYYY-MM-DD形式で入力してください。"
            return render_template('index.html', error=error_msg)
        
        # 関数の使用
        image_path = save_ndvi_image(aoi=req1, date_start_str=req2)  
        print(f"画像が保存されました: {image_path}")
        # 'map.html'にデータを渡してレンダリング
        return render_template('map.html', address=req1, date=req2, image_path=image_path)
    else:
        return render_template('index.html')
    
@app.get("/layout")
def layout():
    return render_template('layout.html')



if __name__ == '__main__':
    app.run()