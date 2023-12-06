from flask_bootstrap import Bootstrap
from flask import Flask, render_template, request 

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.get("/")
def index():
    return render_template('index.html')

@app.route('/address', methods=['GET', 'POST'])
def sample_form_temp():
    req1 = request.form['address']
    print(req1)
    if request.method == 'POST':
        return render_template('map.html', address=req1)
    else:
        return render_template('index.html')
    


if __name__ == '__main__':
    app.run()