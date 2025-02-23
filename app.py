from flask import Flask,render_template
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import io
import base64

app = Flask(__name__)

def get_crypto() :
    url = "https://api.nobitex.ir/market/udf/history"
    params = {
        "symbol" : "DOGEIRT",
        "resolution": "60",
        "from" : int(pd.Timestamp.now().timestamp()) - (24 * 60 * 60),
        "to" : int(pd.Timestamp.now().timestamp())
    }
    response = requests.get(url , params=params)
    data = response.json()

    if "c" not in data :
        return "khata az server"

    df = pd.DataFrame({
        "time" : pd.to_datetime(data["t"] , unit="s" ),
        "close" : data ["c"]
    })

    df["MA_5"] = df["close"].rolling(window=5).mean()
    df["MA_10"] = df["close"].rolling(window=10).mean()

    def c_r(data , window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0 , 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0 , 0)).rolling(window=window).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))


    df["RSI"] = c_r(df["close"])

    latest_price = df["close"].iloc[-1]
    latest_ma5 = df["MA_5"].iloc[-1]
    latest_ma10 = df["MA_10"].iloc[-1]
    latest_rsi = df["RSI"].iloc[-1]

    if latest_rsi < 30 and latest_price > latest_ma5 :
        signal = "buy signal"
    elif latest_rsi > 70 and latest_price <latest_ma5 :
        signal = "sell signal"
    elif latest_ma5 < latest_ma10 :
        signal = "ehtemale kahesh"
    else :
        signal = "wait"

    
    plt.figure(figsize=(10 , 5))
    plt.plot(df["time"] , df["close"] , marker= "o" , linestyle= "-" , color= "blue" , label= "gheymat doge")
    plt.plot(df["time"] , df["MA_5"] , marker= "o" , linestyle= "--" , color= "red" , label= "MA5")
    plt.plot(df["time"] , df["MA_10"] , marker= "o" , linestyle= "--" , color= "green" , label= "MA10")
    plt.xlabel("zaman")
    plt.ylabel("gheymat")
    plt.title("doge_miangin5x10")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    

    img = io.BytesIO()
    plt.savefig(img , format="png")
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return latest_price , latest_rsi ,latest_ma5 , latest_ma10 , signal , chart_url


@app.route("/")
def home() :
    latest_price , latest_rsi ,latest_ma5 , latest_ma10 , signal , chart_url = get_crypto()

    return render_template('index.html',
                            price = latest_price,
                            rsi = latest_rsi,
                            ma5 = latest_ma5,
                            ma10 = latest_ma10,
                            signal = signal,
                            chart_url = chart_url)

if __name__ == "__main__" :
    app.run(debug=True)
