import os
import ssl
from sentinelhub import (
    SHConfig, DataCollection, SentinelHubCatalog, SentinelHubRequest, BBox, bbox_to_dimensions, CRS, MimeType
)
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg') #TkinterとMatplotlibの競合回避のためにMatplotlibの非GUIバックエンドの使用
import matplotlib.pyplot as plt
import japanize_matplotlib # 日本語を画像タイトルに表示するために必要
from concurrent.futures import ThreadPoolExecutor
from json2polygon import get_coordinates_from_uuid

# SSL証明書の検証を無視する設定（セキュリティ上のリスクがあるため注意が必要です）
ssl._create_default_https_context = ssl._create_unverified_context

# Sentinel Hubの設定
config = SHConfig()
config.sh_client_id = 'sh-a8ab20d0-6718-434f-bb63-1db6081c4ef5'
config.sh_client_secret = 'PtXBcCDFSzyh04Bmc0gHMD7SyMj9nODN'
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.save('cdse')

# 関数の定義
def find_first_matching_file(json_folder_path, polygon_uuid):
    """最初に一致するJSONファイルを探して、その座標を返す。"""
    for filename in os.listdir(json_folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder_path, filename)
            coords = get_coordinates_from_uuid(file_path, polygon_uuid)
            if coords is not None:
                print(file_path)
                return coords
    return None

def calculate_bounds(aoi_coords_wgs84):
    """座標リストから境界座標（最小値と最大値）を計算する。"""
    lons, lats = zip(*aoi_coords_wgs84[0])
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    return [[min_lon, min_lat], [max_lon, max_lat]]

def get_sentinel_data(bbox, time_interval, evalscript, data_collection):
    """Sentinel Hubからデータを取得する関数"""
    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(data_collection=data_collection, time_interval=time_interval, other_args={"dataFilter": {"mosaickingOrder": "leastCC"}})],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=bbox,
        size=bbox_to_dimensions(bbox, resolution=10),
        config=config,
    )
    return request.get_data()

def search_catalog(bbox, time_interval):
    """
    指定されたエリアと時間間隔に基づいてSentinel Hubから画像データを検索する関数
    :param bbox: バウンディングボックス
    :param time_interval: 検索する時間間隔, time_interval = "2023-07-21", "2023-07-27"
    :return: 見つかった画像の撮影日（文字列）
    """

    catalog = SentinelHubCatalog(config=config)
    search_iterator = catalog.search(
        DataCollection.SENTINEL2_L2A,
        bbox=bbox,
        time=time_interval,
        fields={"include": ["id", "properties.datetime","properties.eo:cloud_cover"], "exclude": []},
    )

    results = list(search_iterator)
    if not results:
        return None  # 画像が見つからない場合はNoneを返す

    return results

# NDVI画像取得用のEvalscript
evalscript_ndvi = """
    //VERSION=3
    function setup() {
    return {
        input: [{
        bands: [
            "B04",
            "B08",
            "dataMask"
        ]
        }],
        output: {
        bands: 1 // 出力を1バンドに変更
        }
    }
    }

    function evaluatePixel(sample) {
        let val = (sample.B08 - sample.B04) / (sample.B08 + sample.B04);
        
        // NDVI値を0から1の範囲に正規化
        let normalizedVal = (val + 1) / 2; 
        
        // dataMaskを考慮してNDVI値を返す
        return [val * sample.dataMask];
    }

    """

# True color取得用のEvalscript
evalscript_true_color = """
        //VERSION=3

        function setup() {
            return {
                input: [{
                    bands: ["B02", "B03", "B04"]
                }],
                output: {
                    bands: 3
                }
            };
        }

        function evaluatePixel(sample) {
            return [sample.B04, sample.B03, sample.B02];
        }
    """

def get_ndvi_image_from_uuid(polygon_uuid, date_start_str):
    # JSONファイルから座標を取得
    aoi_coords_wgs84 = find_first_matching_file('JSON', polygon_uuid)
    if not aoi_coords_wgs84:
        return None

    # バウンディングボックスの設定
    aoi_bbox = BBox(bbox=calculate_bounds(aoi_coords_wgs84), crs=CRS.WGS84)

    # 時間間隔の設定
    date_start = datetime.strptime(date_start_str, '%Y-%m-%d')
    date_end = date_start + timedelta(days=5)     # 衛星は5日間隔で飛ぶため最低1枚の画像を取得するために5日足す
    time_interval = (date_start, date_end.strftime('%Y-%m-%d'))

    # 時間範囲とバウンディングボックスで衛星画像を検索
    results = search_catalog(aoi_bbox, time_interval)
    print("Total number of results:", len(results))
    for result in results:
        print(result)
    temp_str = results[0]['properties']['datetime']
    taken_date = temp_str.split('T')[0]

    # DataCollectionの設定
    data_collection=DataCollection.SENTINEL2_L2A.define_from(
                    name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
                )
    
    # 並列処理でデータ取得
    with ThreadPoolExecutor() as executor:
        future_ndvi = executor.submit(get_sentinel_data, aoi_bbox, time_interval, evalscript_ndvi, data_collection)
        future_true_color = executor.submit(get_sentinel_data, aoi_bbox, time_interval, evalscript_true_color, data_collection)

        ndvi_imgs, true_color_imgs = future_ndvi.result(), future_true_color.result()
    
    # 画像表示と保存のコード
    ndvi_img = ndvi_imgs[0]
    true_img = true_color_imgs[0]
    print(
        f"Returned data is of type = {type(ndvi_imgs)} and length {len(ndvi_imgs)}."
    )
    print(
        f"Single element in the list is of type {type(ndvi_imgs[-1])} and has shape {ndvi_imgs[-1].shape}"
    )
    return {'true_img':true_img, 'ndvi_img':ndvi_img, 'taken_date': taken_date}

def save_true_and_NDVI_side_by_side(true_img, ndvi_img, polygon_uuid, taken_date):
    # Matplotlibのsubplotを使用して、TrueColorとNDVIを並べて表示
    fig, axs = plt.subplots(1,2, figsize = (12, 6))

    # Matplotlibを使用してTrueColor画像を表示
    axs[0].imshow(true_img)
    axs[0].axis('off')

    # Matplotlibを使用してカラーマップを適用
    ndvi_im = axs[1].imshow(ndvi_img, cmap='coolwarm')
    fig.colorbar(ndvi_im, ax=axs[1])  # カラーバーを表示
    plt.axis('off')  # 軸を非表示にする

    # 全体のタイトルを設定
    plt.suptitle('畑ID: ' + polygon_uuid + ' 撮影日: '+ taken_date)

    # サブプロット間と周辺の余白を調整
    fig.subplots_adjust(left=0.05, wspace=0.3)


    # 画像として保存
    image_path = 'static/image/temporary/ndvi_image.png'
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
    plt.close()  # プロットをクローズ

    return image_path

from folium import raster_layers
def add_image_to_map(map, ndvi_img, uuid):
    """
    指定されたFoliumマップにNDVI画像を追加する。

    Args:
    map (folium.Map): Foliumマップオブジェクト。
    ndvi_img: NDVI画像
    uuid: 畑ID
    """
    aoi_coords_wgs84 = find_first_matching_file('JSON', uuid)
    if not aoi_coords_wgs84:
        return None

    # バウンディングボックスの設定
    my_bbox=calculate_bounds(aoi_coords_wgs84)
    
    # ImageOverlay に適合する形式に変換
    image_overlay_bounds = [[my_bbox[0][1], my_bbox[0][0]], [my_bbox[1][1], my_bbox[1][0]]]

    

    # 画像として保存
    image_path = 'static/image/temporary/ndvi_image.png'
    plt.imshow(ndvi_img, cmap='coolwarm')
    plt.axis('off')
    plt.savefig(image_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    # ImageOverlay で画像をマップに追加
    raster_layers.ImageOverlay(
        image=image_path,
        bounds=image_overlay_bounds,
        opacity=0.99  # 透過度の設定（0.0: 完全透明, 1.0: 不透明）
    ).add_to(map)

    overlay_map_html = map._repr_html_()

    return overlay_map_html
