from django.shortcuts import render
import requests
import datetime
import plotly.express as px

class CustomTimeZone(datetime.tzinfo):
    def __init__(self, offset):
        self.offset = offset

    def utcoffset(self, dt):
        return datetime.timedelta(seconds=self.offset)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return f"UTC{self.offset}"

def index(request):
    API_KEY = open("C:\\_studia\\wather-app-django\\weather_app\\my_weather_app\\api_key.txt", "r").read()
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}"
    forecast_weather_url = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}"

    if request.method == "POST": 
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecasts1, temp_plot_data1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_weather_url)

        fig1 = px.line(
            temp_plot_data1,
            x='day',
            y='temp',
            title='Forecast plot for ' + weather_data1['city'] + ', ' + weather_data1['country'],
            labels={'day':'Date','temp':'Temperature °C'}
        )
        plot_div1 = fig1.to_html(full_html=False)

        if city2:
            weather_data2, daily_forecasts2, temp_plot_data2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_weather_url)
            
            fig2 = px.line(
            temp_plot_data2,
            x='day',
            y='temp',
            title='Forecast plot for ' + weather_data2['city'] + ', ' + weather_data2['country'],
            labels={'day':'Date','temp':'Temperature °C'}
        )
            plot_div2 = fig2.to_html(full_html=False)
        else:
            weather_data2, daily_forecasts2, temp_plot_data2, plot_div2 = None, None, None, None

        context = {
            "weather_data1": weather_data1,
            "daily_forecasts1": daily_forecasts1,
            "weather_data2": weather_data2,
            "daily_forecasts2": daily_forecasts2,
            "plot1": plot_div1,
            "plot2": plot_div2
        }

        return render(request, "weather_app/index.html", context)
    else:
        return render(request, "weather_app/index.html")
    

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_url):
    response = requests.get(current_weather_url.format(city, api_key)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']
    forecast_response = requests.get(forecast_url.format(lat, lon, api_key)).json()

    time_zone = CustomTimeZone(forecast_response['city']['timezone'])

    dt = datetime.datetime.fromtimestamp(response['dt'], tz=time_zone)
    tz_day = dt.strftime("%A")
    tz_time = dt.strftime("%H:%M") 

    weather_data = {
        "city": city,
        "country": response['sys']['country'],
        "temperature": round(response['main']['temp'] - 273.15, 2),
        "humidity": response['main']['humidity'],
        "wind": response['wind']['speed'],
        "description": response['weather'][0]['description'],
        "icon": response['weather'][0]['icon'],
        "time": tz_day + ' ' + tz_time
    }

    daily_forecasts = []
    for daily_data in forecast_response['list'][:5]: 
        day = datetime.datetime.fromtimestamp(daily_data['dt'], tz=time_zone)
        formatted_day = day.strftime("%A")
        formatted_time = day.strftime("%H:%M")
        
        daily_forecasts.append({
            "day": formatted_day + " " + formatted_time,
            "min_temp": round(daily_data['main']['temp_min'] - 273.15, 2),
            "max_temp": round(daily_data['main']['temp_max'] - 273.15, 2),
            "humidity": daily_data['main']['humidity'],
            "wind": daily_data['wind']['speed'],
            "description": daily_data['weather'][0]['description'],
            "icon": daily_data['weather'][0]['icon']
        })

    forecast_temp = []
    for daily in forecast_response['list'][:5]:
        day = datetime.datetime.fromtimestamp(daily['dt'], tz=time_zone)
        formatted_day = day.strftime("%A")
        formatted_time = day.strftime("%H:%M")

        forecast_temp.append({
            "day": formatted_day + " " + formatted_time,
            "temp": round(daily['main']['temp'] - 273.15, 2),
        })

    return weather_data, daily_forecasts, forecast_temp