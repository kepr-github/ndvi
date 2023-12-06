# from fastapi import FastAPI

# app = FastAPI()

from flask import Flask, render_template
app = Flask(__name__)

@app.get("/")
def index():
    return render_template('index.html')

@app.route('/address', methods=['POST'])
def sample_form_temp():
    print('POSTデータ受け取ったので処理します')
    return 'POST受け取ったよ'

if __name__ == '__main__':
    app.run()