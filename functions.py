from pyowm import OWM
from pyowm.utils.config import get_default_config
from pyowm.commons.exceptions import NotFoundError, InvalidSSLCertificateError, APIRequestError

import requests


def check_city_existence(city: str):
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    owm = OWM('97150f95dc173b86e58b20c0754d2634', config_dict)
    mgr = owm.weather_manager()
    try:
        observation = mgr.weather_at_place(city)
    except NotFoundError:
        return -1
    except InvalidSSLCertificateError:
        return -2
    except APIRequestError:
        return -3
    return 1


def get_moscow_time_and_weekdaynum():
    req = requests.get("http://worldtimeapi.org/api/timezone/Europe/Moscow")
    data = req.json()

    datetime = data['datetime']
    weekdaynum = data['day_of_week']
    date, time = datetime.split('T')
    time = time[:5]

    return date, time, weekdaynum


def get_current_weather(city: str):
    config_dict = get_default_config()
    config_dict['language'] = 'ru'

    owm = OWM('97150f95dc173b86e58b20c0754d2634', config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place(city)
    w = observation.weather

    t = w.temperature("celsius")
    t1 = t['temp']
    t2 = t['feels_like']

    wi = w.wind()['speed']
    humi = w.humidity
    dt = w.detailed_status
    pr = int(w.pressure['press'] // 1.333)

    return {'temp': t1, 'feels_like': t2, 'speed': wi, 'pressure': pr, 'humidity': humi, 'description': dt}


def get_forecast(city: str):
    key = 'a31bb58438d38934a0b311f5d8a03503'
    cnt = 40
    res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={key}'
                       f'&units=metric&lang=ru&cnt={cnt}')

    data = res.json()
    data = data['list']

    keys = {'main': ['temp', 'temp_min', 'temp_max', 'feels_like', 'pressure', 'humidity'],
            'weather': ['description'], 'wind': ['speed']}

    new_data = dict()
    for elem in data:
        date, time = elem['dt_txt'].split()
        if date not in new_data:
            new_data[date] = {time: {}}
        else:
            new_data[date][time] = {}

        for key, val in keys.items():
            for val_1 in val:
                if val_1 == 'description':
                    new_data[date][time][val_1] = elem[key][0][val_1]
                elif val_1 == 'pressure':
                    new_data[date][time][val_1] = int(elem[key][val_1] // 1.333)
                else:
                    new_data[date][time][val_1] = elem[key][val_1]

    for date, val in new_data.items():
        min_temps = list()
        max_temps = list()
        description = str()
        speeds = list()
        for time, val_1 in val.items():
            min_temps.append(val_1['temp_min'])
            max_temps.append(val_1['temp_max'])
            if time[:5] == '15:00':
                description = val_1['description']
            speeds.append(val_1['speed'])

        new_data[date]['common'] = {'temp_min': round(min(min_temps)), 'temp_max': round(max(max_temps)),
                                    'description': description, 'speed': round(sum(speeds) / len(speeds))}

    return new_data
