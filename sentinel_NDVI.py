# -*- coding: utf-8 -*-

# 必要なライブラリをインストールするためのコメントです。実際のインストールはコマンドラインで実行する必要があります。
#pip install rasterio shapely mapclassify rioxarray japanize_matplotlib geopandas geojson sentinelhub

import os

import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import folium

import urllib.parse

import ssl

# SSL証明書の検証を無視する設定（セキュリティ上のリスクがあるため注意が必要です）
ssl._create_default_https_context = ssl._create_unverified_context

# ユーザーに日本の市町村名の入力を求める
aoi = input("日本の市町村名を入力（例：「八代市古閑下町」）：")

# 入力された市町村名の地理情報を取得し、Geopandasのデータフレームに読み込む
aoi_gdf = gpd.read_file(f"https://uedayou.net/loa/{urllib.parse.quote(aoi)}.geojson")



# Foliumを使用して地理情報を地図上に表示
m = folium.Map(location = [aoi_gdf.total_bounds[1],aoi_gdf.total_bounds[0]], zoom_start=12)

folium.GeoJson(aoi_gdf).add_to(m)
m 
'''ここでマップ上に切り取り範囲を表示したいけどわからない'''


from typing import Any, Optional, Tuple
# 画像表示用のユーティリティ関数
def plot_image(
    image: np.ndarray,
    factor: float = 1.0,
    clip_range: Optional[Tuple[float, float]] = None,
    cmap: str = 'coolwarm',  # カラーマップを追加
    **kwargs: Any
) -> None:
    """Utility function for plotting RGB images."""
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15, 15))
    if clip_range is not None:
        image_data = np.clip(image * factor, *clip_range)
    else:
        image_data = image * factor
    # カラーマップを使用して画像を表示
    ax.imshow(image_data, cmap=cmap, **kwargs)
    ax.set_xticks([])
    ax.set_yticks([])


# Sentinel Hubからのデータ取得に関する設定
from sentinelhub import (
    SHConfig,
    DataCollection,
    SentinelHubCatalog,
    SentinelHubRequest,
    SentinelHubStatistical,
    BBox,
    bbox_to_dimensions,
    CRS,
    MimeType,
    Geometry,
)

# Sentinel Hubへの認証情報
ID = 'sh-a8ab20d0-6718-434f-bb63-1db6081c4ef5'
OAuth = 'PtXBcCDFSzyh04Bmc0gHMD7SyMj9nODN'


config = SHConfig()
config.sh_client_id = ID
config.sh_client_secret = OAuth
config.sh_token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
config.sh_base_url = "https://sh.dataspace.copernicus.eu"
config.save("cdse")

# 選択された市町村の座標
aoi_coords_wgs84 = tuple(aoi_gdf.total_bounds)

# 解像度とバウンディングボックスの設定
resolution = 10
aoi_bbox = BBox(bbox=aoi_coords_wgs84, crs=CRS.WGS84)
aoi_size = bbox_to_dimensions(aoi_bbox, resolution=resolution)

catalog = SentinelHubCatalog(config=config)

# 日付の入力と日付範囲の設定
from datetime import datetime, timedelta
date_start_str = input("日付を半角入力（例：2023-10-01）")

#Stringからdatetimeに変換
date_start = datetime.strptime(date_start_str, '%Y-%m-%d')

#衛星は5日間隔で飛ぶため最低1枚の画像を取得するために5日足す
date_end = date_start + timedelta(days=5)

#stringに変換しなおす
date_end_str = date_end.strftime('%Y-%m-%d')



# 時間範囲とバウンディングボックスで衛星画像を検索
time_interval = date_start, date_end_str

search_iterator = catalog.search(
    DataCollection.SENTINEL2_L2A,
    bbox=aoi_bbox,
    time=time_interval,
    fields={"include": ["id", "properties.datetime"], "exclude": []},
)

results = list(search_iterator)
print("Total number of results:", len(results))

for result in results:
    print(result)

# True Color画像取得用のEvalscript
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
# True Color画像のリクエスト
request_true_color = SentinelHubRequest(
    evalscript=evalscript_true_color,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
            ),
            time_interval=time_interval,
            other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=aoi_bbox,
    size=aoi_size,
    config=config,
)

# データの取得と表示
true_color_imgs = request_true_color.get_data()

print(
    f"Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}."
)
print(
    f"Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}"
)

image = true_color_imgs[0]
print(f"Image type: {image.dtype}")

# plot function
# factor 1/255 to scale between 0-1
# factor 3.5 to increase brightness
plot_image(image, factor=3.5 / 255, clip_range=(0, 1))

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
# NDVI画像のリクエストと表示
request_ndvi_img = SentinelHubRequest(
    evalscript=evalscript_ndvi,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L2A.define_from(
                name="s2l2a", service_url="https://sh.dataspace.copernicus.eu"
            ),
            time_interval=time_interval,
            other_args={"dataFilter": {"mosaickingOrder": "leastCC"}},
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=aoi_bbox,
    size=aoi_size,
    config=config,
)

ndvi_img = request_ndvi_img.get_data()

print(
    f"Returned data is of type = {type(true_color_imgs)} and length {len(true_color_imgs)}."
)
print(
    f"Single element in the list is of type {type(true_color_imgs[-1])} and has shape {true_color_imgs[-1].shape}"
)

image = ndvi_img[0]
print(f"Image type: {image.dtype}")

# plot function
plot_image(image, factor=1 / 255, cmap='coolwarm')
plt.show()

'''
一つの大きな関数として、引数が住所と日付
リターンがカラーとNDVIのpng
'''