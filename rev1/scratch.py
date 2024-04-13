import scratchconnect
from bs4 import BeautifulSoup
import requests
from time import time, sleep
import sys, errno

#login = scratchconnect.ScratchConnect('helloworldbyeworld', 'secret')

#project = login.connect_project(project_id=667393756, access_unshared=True)
#variables = project.connect_cloud_variables()
#variables.get_variable_data(limit=100, offset=0)  # Returns the cloud variable data
# Returns the cloud variable value: variables.get_cloud_variable_value(variable_name='Name', limit=100)

def setvars(info, temp, location):
    try:
        variables.set_cloud_variable(variable_name='response: thislocation', value=encode(location))
        variables.set_cloud_variable(variable_name='response: infotext', value=encode(info.lower()))
        variables.set_cloud_variable(variable_name='response: temp', value=temp)
    except IOError as e: # Reconnect cloud variables when broken pipe error, then redo
        variables = project.connect_cloud_variables()
        setvars(info, temp, location)
    
    variables.set_cloud_variable(variable_name='request', value='')


def weather(city):
    #global variables
    print('Searching for ' + city)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    query = city.replace(' ', '+');
    res = requests.get(
        f'https://wttr.in/{query}?j1', headers=headers)

    print(res.content)

    #setvars(info, temp, city)


ALL_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789.,'- "

def decode(encoded_code):
    encoded_code = str(encoded_code)
    i = 0
    text = ''
    while i < int(len(encoded_code) - 1 / 2):
        index = int(encoded_code[i] + encoded_code[i + 1]) - 1
        text += ALL_CHARS[index]
        i += 2
    return text

def encode(text):
        number = ''
        for i in range(0, len(text)):
            char = text[i]
            index = str(ALL_CHARS.index(char) + 1)
            if int(index) < 10:
                index = '0' + index
            number += index
        return number

weather('los altos')

"""while True: # Check every second
    sleep(1 - time() % 1)
    try:
        value = variables.get_cloud_variable_value(variable_name='request', limit=200)[0]
        print(value)
        decoded = decode(value)
        if decoded != '':
            weather(decoded)
    except ValueError as e:
        print('JSONDecodeError - ignoring')
"""