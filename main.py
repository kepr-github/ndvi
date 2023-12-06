# from fastapi import FastAPI

# app = FastAPI()

from flask import Flask, render_template, request 
app = Flask(__name__)

@app.get("/")
def index():
    return render_template('index.html')

@app.route('/address', methods=['POST'])
def sample_form_temp():
    req1 = request.form['data1']
    print(req1)
    return render_template('map.html', address=req1)
    


if __name__ == '__main__':
    app.run()