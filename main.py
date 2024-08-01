# project: p4
# submitter: damin
# partner: none
# hours: 20


# link to source of data set: https://www.kaggle.com/datasets/rajeevw/ufcdata

# import statements

import pandas as pd
from flask import Flask, request, jsonify, Response
import flask
import re
import time
from io import BytesIO
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg')

#used this source to help learn how to properly implement "to_html":
# https://www.geeksforgeeks.org/python-pandas-dataframe-to_html-method/
def show_table(file):
    ufc_df = pd.read_csv(file)
    table_html = ufc_df.to_html(index = False)
    return table_html
    

#simple flask app:
app = Flask("ufc application")
# df = pd.read_csv("main.csv")

counter = 0
@app.route('/')
def home():
    global counter
    
    counter += 1
    if counter <= 10:
        
        if counter % 2 == 0:
            with open("indexA.html") as f:
                htmlA = f.read()
            return htmlA
        
        if counter % 2 != 0:
            with open("indexB.html") as f:
                htmlB = f.read()
            return htmlB
    if counter > 10:
        if clicks_A > clicks_B:
            with open("indexA.html") as f:
                htmlA = f.read()
            return htmlA
        
        if clicks_B > clicks_A:
            with open("indexB.html") as f:
                htmlB = f.read()
            return htmlB
        
    # return "<html><a href = {}>browse</a><html>".format("/browse.html")

@app.route('/browse.html')
def browse():
    browse_header = "<h1>Feel Free to Browse a Variety of UFC Data!!</h1>"
    table_html = show_table('main.csv')
    return browse_header + table_html

ufc_df = pd.read_csv('main.csv')
last_visit = {}
IP_list = []

@app.route('/browse.json')
def browse_json():
    user_IP = request.remote_addr
    IP_list.append(request.remote_addr)
    
    if user_IP not in last_visit:
        last_visit[user_IP] = time.time()
        return jsonify(ufc_df.to_dict())
    
    if user_IP in last_visit:
        if time.time() - last_visit[user_IP] <= 60:
            return Response("<b>go away</b>",
                              status=429,
                              headers={"Retry-After": "60"})

        if time.time() - last_visit[user_IP] > 60:
            last_visit[user_IP] = time.time()
            return jsonify(ufc_df.to_dict())
        
@app.route('/visitors.json')
def visitors():
    return IP_list


@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if len(re.findall(r"^[a-z0-9]+@\w*\.com", email)) > 0: # 1 
        #[\w.]+\@[\w.^@]+\.com
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
    
        with open("emails.txt") as f:
            num_subscribed = len(f.readlines())
            

        return jsonify(f"thanks, your subscriber number is {num_subscribed}!")
    return jsonify("Stop messing with me and give me an actual valid email address! ") # 3


clicks_A = 0 
clicks_B = 0
@app.route('/donate.html')
def donate():
    global clicks_A
    global clicks_B
    
    with open('donate.html') as f:
        html = f.read()
        
    if "from" in request.args:
        if request.args["from"] == "A":
            clicks_A += 1
            
        if request.args["from"] == "B":
            clicks_B += 1
    return html
  
@app.route('/knockdowns.svg') #histogram of correlation between which corner the fighter is and their wins
def knockdowns():
    blue_kd = ufc_df["Blue avg knockdowns"][10:]
    b = ufc_df["Blue Fighter"][10:]
    fig = plt.figure(figsize = (8, 4))
    plt.bar(b, blue_kd, align = "center")
    plt.xticks(rotation = 90)
    plt.xlabel("Fighter Name")
    plt.ylabel("Number of Knockdowns in Most Recent Fight")
    plt.title("Number of Knockdowns by Fighter")
    
    fake_file = BytesIO()
    fig.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})


@app.route('/strikes.svg')
def strikes():
    if "bins" in flask.request.args:
        num_of_bins = int(flask.request.args["bins"])
    
    else:
        num_of_bins = 9
        
    date = ufc_df["Date"]
    sig_strike = ufc_df["Blue avg sig strike pct"] * 100
    fig = plt.figure(figsize=(6,4))
    plt.hist(date, bins=num_of_bins)
    plt.xlabel("Date")
    plt.ylabel("Number of Fights")
    plt.title("Number of Fights by Date")
    plt.show()


    fake_file = BytesIO()
    fig.get_figure().savefig(fake_file, format="svg", bbox_inches="tight")
    return Response(fake_file.getvalue(),
                    headers={"Content-Type": "image/svg+xml"})
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!

# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.