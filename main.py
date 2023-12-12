#from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request 
from sentinel_NDVI import save_ndvi_image

app = Flask(__name__, static_folder='./templates/image')
#bootstrap = Bootstrap(app)

@app.get("/")
def index():
    return render_template('index.html')

@app.route('/address', methods=['GET', 'POST'])
def sample_form_temp():
    req1 = request.form['address']
    print(req1)
    if request.method == 'POST':
        # 関数の使用例
        image_path = save_ndvi_image(aoi = req1)  
        print(f"画像が保存されました: {image_path}")
        return render_template('map.html', address=req1)
    else:
        return render_template('index.html')
    
@app.get("/layout")
def layout():
    return render_template('layout.html')



if __name__ == '__main__':
    app.run()