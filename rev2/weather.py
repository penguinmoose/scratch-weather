import requests
import re
import scratchattach as sa
import time
from termcolor import colored
import logging
import warnings

with open("secret.txt", "r") as f:
    r = f.read().splitlines()

session = sa.login(r[0], r[1])
cloud = session.connect_scratch_cloud("830536684")

print(colored("\u2713 Connected to cloud", "green", attrs=["bold"]))

locname = []
chars = "~ abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLNMOPQRSTUVWXYZ0123456789!@#$%^&*()-–—=[]\\;'‘’,./_+{}|:\"“”<>?"

# turn string into number for cloud variables
def encode(string):
    encoded = ""
    for char in string:
        position = chars.index(char) + 1
        if position < 10:
            encoded += "0" + str(position)
        else:
            encoded += str(position)
    return encoded

# turn number into string for cloud variables
def decode(number):
    decoded = ""
    for i in range(0, len(number), 2):
        decoded += chars[int(number[i:i+2]) - 1]
    return decoded

# fetch the weather
def weather(location):
    url = "http://wttr.in/" + location + "?format=j1"
    headers = {'Accept': 'application/json'}
    try:
        response = requests.get(url, headers)
    except requests.exceptions.ConnectionError as e:
        logger.error(colored(f'ConnectionError while trying to fetch wttr.in response: {e}', "red"))

    try:
        json = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(colored("JSONDecodeError while trying to decode wttr.in response JSON.", "red"))
        logger.debug(f'Raw response text: {response.text}')

    statuscode = response.status_code
    result = json['nearest_area'][0]['areaName'][0]['value']
    global locname
    try:
        encode(result)
    except:
        logger.warning(f'{colored("encoding failed", "red")} for {result}, defaulting to "{location}" (request location)')
        result = location
    locname = [result]
    return json, statuscode

def currentweather(location, checkdigits):
    data, code = weather(location)
    data = data['current_condition'][0]
    output = locname
    output.append(data['weatherDesc'][0]['value'])
    output.append(data['weatherCode'])
    output.append(data['temp_C'])
    output.append(data['FeelsLikeC'])
    output.append(data['winddirDegree'])
    output.append(data['winddir16Point'])
    output.append(data['windspeedMiles'])
    output.append(data['uvIndex'])
    output.append(data['visibilityMiles'])
    output.append(data['humidity'])
    output.append(data['precipMM'])
    output.append(checkdigits)
    return output, code

def temperature(day, data, checkdigits):
    output = []
    today = data['weather'][day]['hourly']
    feelslike = [int(today[i]['FeelsLikeC']) for i in range(8)]
    temp = [str(today[i]['tempC']) for i in range(8)]
    output.append(str(sum(feelslike[3:8]) / 5)) # daytime feels like average
    output.append(str(sum(feelslike[0:3] + [feelslike[7]]) / 4)) # nighttime feels like average
    output.extend(temp) # hourly temperature
    output.append(checkdigits)
    return output

def wind(day, data, checkdigits):
    today = data['weather'][day]['hourly']
    wind = [today[i]['windspeedMiles'] for i in range(8)]
    gust = [today[i]['WindGustMiles'] for i in range(8)]
    dir = [today[i]['winddirDegree'] for i in range(8)]
    return wind + gust + dir + [checkdigits]

def precip(day, data, checkdigits):
    output = []
    today = data['weather'][day]['hourly']
    percip = [float(today[i]['precipMM']) for i in range(8)]
    rain = [today[i]['chanceofrain'] for i in range(8)]
    snow = [today[i]['chanceofsnow'] for i in range(8)]
    output.append(str(sum(percip[3:8]))) # daytime percipitation
    output.append(str(sum(percip[0:3] + [percip[7]]))) # nighttime percipitation
    output.append(str(float(data['weather'][int(day)]['totalSnow_cm']) * 10)) # snow
    output.extend(rain + snow)
    output.append(checkdigits)
    return output

def forecastastro(day, data, checkdigits):
    output = []
    today = data['weather'][day]['astronomy'][0]
    cloudcover = [data['weather'][day]['hourly'][i]['cloudcover'] for i in range(8)]
    output.append(today['sunset'])
    output.append(today['sunrise'])
    output.append(today['moon_phase'])
    output.append(today['moon_illumination'])
    output.extend(cloudcover)
    output.append(checkdigits)
    return output

def forecastother(day, data, checkdigits):
    today = data['weather'][day]['hourly']
    output = []
    output.append(today[4]['visibility'])
    output.append(today[0]['visibility'])
    output.append(today[4]['pressure'])
    output.append(today[0]['pressure'])
    output.append(today[4]['humidity'])
    output.append(today[0]['humidity'])
    output.append(today[4]['DewPointC'])
    output.append(today[0]['DewPointC'])
    output.append(data['weather'][day]['uvIndex'])
    output.append(checkdigits)
    return output

def basicweather(day, data, checkdigits):
    today = data['weather'][day]['hourly']
    output = locname
    output.append(today[4]['weatherCode'])
    output.append(today[4]['weatherDesc'][0]['value'])
    output.append(checkdigits)
    return output

def set_cloud(name, value):
    try:
        cloud.set_var(name, value)
    except IOError as e:
        logger.warning(colored("IOError, ignoring", "red"))
    time.sleep(0.2)

def clear_cloud():
    logger.debug("Clearing cloud...")
    cloud.set_vars({
    "response: current": "",
    "response: forecastbasic": "",
    "response: forecasttemp": "",
    "response: forecastwind": "",
    "response: forecastprecip": "",
    "response: forecastastro": "",
    "response: forecastother": "",
    "request": ""
    })

def get_cloud(name):
    try:
        return cloud.get_var(name)
    except ValueError as e:
        logger.warning(colored("JSONDecodeError, ignoring", "red"))
        cloud.reconnect()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Weather extension for Scratch 3.0")
    # add a debug flag
    parser.add_argument("--log-level", default='INFO', help="Log level")
    args = parser.parse_args()
    
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')

    logger = logging.getLogger(__name__)
    logger.setLevel(args.log_level)

    logger.info("hello")
    logger.debug("if you can see this debug message, the program is in debug")

    while True:
        request = get_cloud("request")
        logger.debug(colored(f'Request CV: {request}', "dark_gray"))
        if request != None and request != "" and int(request)>0:
            logger.debug(f"{colored('Request detected', 'green')}, CV: {request}")
            requestdata = str(request)[1:]
            split = re.split(';::;', decode(requestdata))
            location = split[0]
            checkdigits = split[1] # 6-digit code to verify if the response is correct
            day = int(str(request)[:1])
            logger.info(f'Location: {colored(location, "green")}, Day: {colored(day, "magenta")}, Check digits: {colored(checkdigits, "cyan")}')
            set_cloud("response: date", time.strftime("%Y%m%d"))
            code = None
            if day == 0:
                cwdata, code = currentweather(location, checkdigits)
                set_cloud("response: current", int(encode(';'.join(cwdata))))
            else:
                day = day - 1 # forecast indexes are 0 based
                data, code = weather(location)
                basicweatherdata = basicweather(day, data, checkdigits)
                tempdata = temperature(day, data, checkdigits)
                winddata = wind(day, data, checkdigits)
                precipdata = precip(day, data, checkdigits)
                astrodata = forecastastro(day, data, checkdigits)
                otherdata = forecastother(day, data, checkdigits)
                set_cloud("response: forecastbasic", encode(';'.join(basicweatherdata)))
                set_cloud("response: forecasttemp", encode(';'.join(tempdata)))
                set_cloud("response: forecastwind", encode(';'.join(winddata)))
                set_cloud("response: forecastprecip", encode(';'.join(precipdata)))
                set_cloud("response: forecastastro", encode(';'.join(astrodata)))
                set_cloud("response: forecastother", encode(';'.join(otherdata)))

            badresponse = '0' if code==200 else '1'

            set_cloud("404?", badresponse)
            clear_cloud()
            time.sleep(1) # cooldown after response
        time.sleep(1) # cooldown after checking
