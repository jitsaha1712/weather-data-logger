from flask import Flask, request, render_template, flash
import requests
from datetime import datetime,timedelta

app = Flask(__name__, template_folder="weatherTemplate")
app.secret_key = "abc123"



@app.route("/", methods=['GET', 'POST'])
def home():

    file_name ='css/day.css'#by default
    if request.method == "POST":
        city_name = request.form.get("city")
        if not city_name:
            flash("You must enter a city name first")
            return render_template("home.html",css_file='css/base.css',tag=1)

        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid=703f64cd37a6b0478592312327805945&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != "200":
            flash("City not found or something went wrong.")
            return render_template("home.html",css_file = 'css/base.css',tag=1)

        current = data["list"][0]#we get a list ofboject,as current weather data appare at the  beggining so we get data from index 0

        #for weekdays...
        date_text = current["dt_txt"]
        date_obj = datetime.strptime(date_text, "%Y-%m-%d %H:%M:%S")
        current_weekday = date_obj.strftime("%a")# Mon, Tue, Wed

        # for time 
        timezone_shift = data["city"]["timezone"]  # seconds
        utc_now = datetime.utcnow()
        local_time = utc_now + timedelta(seconds=timezone_shift)
        time_12 = local_time.strftime("%I:%M %p")



        current_weather = {
            "temperature": round(current["main"]["temp"]),
            "feelslike": round(current["main"]["feels_like"]),
            "humidity": current["main"]["humidity"],
            "pressure": current["main"]["pressure"],
            "description": current["weather"][0]["description"],
            "time": time_12,
            "date": current["dt_txt"].split()[0],
            "main":current["weather"][0]["main"].lower(),
            "icon": current["weather"][0]["icon"][2],#d or n
            "wind": round(current["wind"]["speed"]*3.6),
            "visibility": round(current["visibility"]/1000),
            "pop_percent": current["pop"] * 100 #probablity of rain

        }
        if current_weather['icon'] == 'n':
            current_weather['main'] =""
            file_name = 'css/night.css'

        today_str = datetime.now().strftime("%Y-%m-%d")
        todays_forecast = []
        allowed_dates = []
        today = datetime.now().date()

        for i in range(2):
           next_date = today + timedelta(days=i)
           allowed_dates.append(next_date.strftime("%Y-%m-%d"))

        for entry in data["list"]:
            date_part = entry["dt_txt"].split()[0]#strip only date as dt_txt = "2025-11-20 12:00:00"


            if date_part in allowed_dates :
               
               time_obj = datetime.strptime(entry["dt_txt"], "%Y-%m-%d %H:%M:%S")
               time = time_obj.strftime("%I %p")

                
               #to change the image on today different time dinamically 
               if entry["weather"][0]["main"].lower()=='rain':
                   icon_info = 'rain'
               elif entry["weather"][0]["main"].lower()=='clouds':
                   icon_info = 'clouds'
               else:
                   hour = time_obj.hour   # 0–23

                   if 6 <= hour < 18:     # 6 AM to 5:59 PM
                      icon_info = 'd'    # day
                   else:
                    icon_info = 'n'    # night
 
                   
               todays_forecast.append({
               "time":time,
               "temp": round(entry["main"]["temp"]),
               "feelslike": round(entry["main"]["feels_like"]),
               "humidity": entry["main"]["humidity"],
               "description": entry["weather"][0]["description"],
               "info":icon_info
              
            })
               
        pop ="pop"#to render pop img
        return render_template("home.html", current_weather=current_weather, todays_forecast=todays_forecast,current_weekday = current_weekday,pop = pop,city_name=city_name.upper(),css_file = file_name)

    return render_template("home.html",current_weather=None, todays_forecast=None,current_weekday = None,css_file ='css/base.css',tag=1)


if __name__ == "__main__":
    app.run(debug=True)
