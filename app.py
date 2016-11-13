# Authors: Michael Hawes, Tony Tran
# Date: 12 Novemebr 2016
# Hack RPI

import time
import requests
from flask import Flask, render_template, request, redirect, url_for, abort, session


app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == "POST":
            session['message'] = request.form['message']
            return redirect(url_for('gallery'))
        else:
            return redirect(url_for('signup'))
    except Exception as error:
        return render_template('index.html')
    return render_template('index.html')



@app.route('/gallery')
def gallery():

    return render_template('gallery.html', message=session['message'])


@app.route('/result', methods=['GET', 'POST'])
def result():
    return render_template('result.html')





if __name__ == '__main__':
    app.run(debug=True)
