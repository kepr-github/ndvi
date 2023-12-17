from json2polygon import get_coordinates_from_uuid
import os


polygon_uuid = '4f3c5e84-0178-4f81-aa6e-5033c696d0ae'


# JSONファイルが保存されているフォルダのパス
json_folder_path = 'JSON'  

# 指定されたフォルダ内のすべてのJSONファイルを処理
aoi_coords_wgs84 = None
for filename in os.listdir(json_folder_path):
    if aoi_coords_wgs84 == None:
        if filename.endswith('.json'):
            file_path = os.path.join(json_folder_path, filename)    
            aoi_coords_wgs84 = get_coordinates_from_uuid(file_path, polygon_uuid) # polygon_uuidが一致したら座標をえる
            this_file = file_path
            


print(this_file)
print(aoi_coords_wgs84)