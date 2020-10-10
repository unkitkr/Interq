from flask import Flask, render_template, request




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:SudoAdmin123@localhost/jumedb"
app.config['SECRET_KEY'] = '0817PDNTSPA'

@app.route('/', methods=['GET'])
def home_page():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True)