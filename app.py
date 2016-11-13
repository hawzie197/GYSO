# Authors: Michael Hawes, Tony Tran
# Date: 12 Novemebr 2016
# Hack RPI
import jinja2
import html2text
import requests
import queue
import re
import nltk
import json
from collections import Counter
from bs4 import BeautifulSoup
from google import search
from stop_words import get_stop_words
from stemming.porter2 import stem
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
from multiprocessing import Pool
from flask import Flask, render_template, request, redirect, url_for, abort, session
non_word_list = ['[',']','*', '(',')','\\','/','&']
word_count = []
lemma = WordNetLemmatizer()
stop = stopwords.words('english')

# env = jinja2.Environment()
# env.globals.update(zip=zip)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'F34TF$($e34D';





@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        session['message'] = request.form['message']  # get search text
        return redirect(url_for('gallery'))
    return render_template('index.html')








@app.route('/gallery')
def gallery():
    phrase = session['message'] # get input text from index
    top_5 = get_key_words(phrase, gen_sums = None)
    resulting_words = []
    for i in top_5:
        resulting_words += [i[0] + ' ']
    new_phrase = ''.join(resulting_words)
    #print("new phrase to search with ",new_phrase)
    urls = get_key_words(new_phrase, gen_sums = 1)
    p = Pool ()
    listy = p.map(get_summary,urls)
    return render_template('gallery.html', results=listy, urls=urls, zip=zip)
def soupify(url):
    soup = BeautifulSoup(url.text,"html.parser")
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    text = soup.get_text() # get text
    lines = (line.strip() for line in text.splitlines()) # break into lines and remove leading and trailing space on each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  ")) # break multi-headlines into a line each
    text = '\n'.join(chunk for chunk in chunks if chunk) # drop blank lines
    return text
def get_count(texts):
    for text in texts:
        for word in text.split():
            word = word.lower()
            if word not in stop:
                if word not in non_word_list:
                    if not word.isdigit():
                        stemword = lemma.lemmatize(word)
                        #stemword = stem(stemword)
                        word_count.append(stemword)
    cnt = Counter(word_count)
    queue2 = []
    #print(cnt)
    not_done = len(queue2)
    return cnt.most_common()[:6]
def get_key_words(phrase, gen_sums=None):
    url_list = []
    urls = []
    if gen_sums == None:
        for x in search(phrase, stop = 1):
            try:
                r = requests.get(x)
                urls += [r]
            except ConnectionError:
                print("Skipping over the url...")
        pool = Pool()
        texts = pool.map(soupify,urls)
        for text in texts:
            for word in text.split():
                word = word.lower()
                if word not in stop:

                    if word not in non_word_list:
                        if not word.isdigit():
                            stemword = lemma.lemmatize(word)
                            #stemword = stem(stemword)
                            word_count.append(stemword)
        cnt = Counter(word_count)
        queue2 = []
        not_done = len(queue2)
        return cnt.most_common()[:6]
    else: #done filtering
        for x in search(phrase, stop = 1):
            try:
                r = requests.get(x)
                url_list += [x]
            except ConnectionError:
                print('Skipping')
        return url_list
def get_summary(url):
    api_key = open('api_key.txt','r').readline().strip()
    params = {"url": url, "apikey":api_key}
    r = requests.get("https://api.havenondemand.com/1/api/sync/extractconcepts/v1", params = params)
    sum_list = []
    if r.status_code == 200:
        list2 = r.json()['concepts']
        for dic in list2:
            sum_list += [dic['concept'] + ' ']
        summary = ''.join(sum_list)
        return summary







@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == "POST":
        session['radios'] = request.form['radios']  # get search text
        result = session['radios']
        if result == 'true':
            session['url'] = request.form['url'] # got chosen url
            #print(session['url'])

            r = requests.get(session['url'])
            string = ''
            if r.status_code == 200:
                text = soupify(r)
                list2 = get_count([text])

                for key in list2:
                    string += key[0] + ' '
                phrase = string
                top_5 = get_key_words(phrase, gen_sums = None)
                resulting_words = []
                for i in top_5:
                    resulting_words += [i[0] + ' ']
                new_phrase = ''.join(resulting_words)
                #print("new phrase to search with ",new_phrase)
                urls = get_key_words(new_phrase, gen_sums = 1)
                p = Pool ()
                listy = p.map(get_summary,urls)
                return render_template('result.html', results=listy, urls=urls, zip=zip)



if __name__ == '__main__':
    app.run(debug=True)
