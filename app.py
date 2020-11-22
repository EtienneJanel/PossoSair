'''
# official source:
https://covid19estamoson.gov.pt/lista-de-concelhos-nivel-de-risco/

# flask form  tutorial
https://tutorial101.blogspot.com/2020/04/python-flask-dynamic-select-box-using.html
'''

from datetime import datetime
import requests
from flask import Flask, render_template, url_for, flash, redirect, request
from forms import ConcelhosForm

# app Setup
app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

# List of conditions
## datetime(year, month, day, hour, minute, second, microsecond)
_NAO_INTER_CONCELHOS = [
    [datetime(2020, 11, 27, 23),datetime(2020, 12, 2, 5)],
    [datetime(2020, 12, 4, 23),datetime(2020, 12, 9, 5)],
]

_NAO_VIA_PUBLICA = [
    [datetime(2020, 12, 1, 13),datetime(2020, 12, 2, 5)],
    [datetime(2020, 12, 8, 13),datetime(2020, 12, 9, 5)],
]

# List of conchelos
FILE = 'lista_de_concelhos_nivel_de_risco.txt'
with open(FILE, 'r', encoding='ANSI') as f:
    raw = f.read()

moderado = raw.split('Moderado')[1].split('Elevado')[0].split('\n')[1:-1]
elevado = raw.split('Elevado')[1].split('\n')[1:-1]
muito_elevado = raw.split('Muito Elevado')[1].split('Extremamente Elevado')[0].split('\n')[1:-1]
extremamente_elevado = raw.split('Extremamente Elevado')[1].split('\n')[1:]
del(raw)
concelhos = moderado + elevado + muito_elevado + extremamente_elevado
concelhos.sort()

def lisbon_now():
    """return the utc time now of http://worldtimeapi.org"""
    try:
        response = requests.get("http://worldtimeapi.org/api/timezone/Europe/Lisbon")
        date_time_json = response.json()['datetime']
        date_time = datetime.strptime(date_time_json, "%Y-%m-%dT%H:%M:%S.%f+00:00")  
    except:
        response = requests.get("http://worldtimeapi.org/api/timezone/Europe/London")
        date_time_json = response.json()['datetime']
        date_time = datetime.strptime(date_time_json, "%Y-%m-%dT%H:%M:%S.%f+00:00")  
    return date_time

# Routes
@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = ConcelhosForm()
    form.concelho.choices = [item for item in concelhos]
    if request.method == 'POST':
        concelho = form.concelho.data
        date_time = lisbon_now()

        # IF concelho = moderado OR elevado
    	## 1.restriction: inter concelho
        inter_concelho = True
        for date_item in _NAO_INTER_CONCELHOS:
            if date_item[0] <= date_time <= date_item[1]:
                inter_concelho = False

        if concelho in muito_elevado + extremamente_elevado:
            ## 2.restriction: via publica
            if date_time.weekday() > 5:
                # if Weekend
                if 13 <= date_time.hour or date_time.hour <= 5:
                    return redirect(url_for('nao',inter_concelho=inter_concelho))
            else:
                # if Week-days
                if 23 <= date_time.hour or date_time.hour <= 5:
                    return redirect(url_for('nao',inter_concelho=inter_concelho))

            for date_item in _NAO_VIA_PUBLICA:
                if date_item[0] <= date_time <= date_item[1]:
                    return redirect(url_for('nao',inter_concelho=inter_concelho))
        
        return redirect(url_for('sim', inter_concelho=inter_concelho))

    return render_template('home.html', form=form)

@app.route("/sim<string:inter_concelho>")
def sim(inter_concelho):
    return render_template('sim.html', inter_concelho=inter_concelho)

@app.route("/nao<string:inter_concelho>")
def nao(inter_concelho):
    return render_template('nao.html', inter_concelho=inter_concelho)

if __name__ == '__main__':
    app.run(debug=True)
