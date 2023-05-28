import requests
from flask import Flask, request, jsonify, render_template
import json
from datetime import date
import geocoder

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

#get current location
def get_current_location():
    g = geocoder.ip('me')
    if g.ok:
        return g.city
    else:
        return None
    

def extract_location_and_date(user_input):
    # Split the user input by spaces
    words = user_input.split()

    # Initialize variables
    location = ""
    date = ""

    # Iterate over the words to find the location and date
    for i in range(len(words)):
        # Check for location keywords
        if words[i].lower() == "in":
            if i + 1 < len(words):
                location = words[i + 1]
                break

    # Iterate over the words to find the date
    for i in range(len(words)):
        # Check for date keywords
        if words[i].lower() == "on":
            if i + 1 < len(words):
                date = words[i + 1]
                break

    return location, date


def search_date(data,date):
    for data in data:
        if data["valid_date"] == date:
            return(data)
    print("sad")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    response=[]
    user_input = request.form.get('user_input')
    API_KEY = 'e53223036df84911894fff99d315ab67'


    #greetings
    if user_input.lower() in ['hi', 'hello', 'hey']:
        response.append({'user': user_input, 'bot': "Hello! How can I assist you today?"})
    #pages
    elif user_input.lower() == 'show me the available pages':
        response.append({'user': user_input, 'bot': "Sure! Here are the available pages: [List of pages]. Which page are you interested in?"})
    #weather
    elif user_input.lower() == 'weather':
        response.append({'user': user_input, 'bot': "Please provide the full details (eg: weather in Delhi on 2023-05-29 )"})
    elif 'weather' in user_input.lower():
        location, date = extract_location_and_date(user_input)

        # Make API request to retrieve weather information for a specific date
        API_KEY = 'e53223036df84911894fff99d315ab67'

        url = f'https://api.weatherbit.io/v2.0/forecast/daily'
        params = {
            'city': location,
            'key': API_KEY,
        }
        response_json = requests.get(url, params=params).json()
        data=search_date(response_json["data"],date)
        
        if data:
            weather_data = data
            temperature = weather_data['temp']
            description = weather_data['weather']['description']
            weather_response = f"The weather in {location} on {date} was {description} with a temperature of {temperature}°C."
        else:
            weather_response = 'Sorry, I could not retrieve the weather information.'

        response.append({'user': user_input, 'bot': weather_response})
    
    #monument details
    elif 'tell me about' in user_input.lower():
        historical_site = user_input.split('tell me about')[1].strip()
        print(historical_site)
        with open('monuments.json', 'r') as file:
            data = json.load(file)
        monuments = data['monuments']
        name = historical_site  
        flag=False
        for monument in monuments:
            if monument['name'] == name:
                flag=True
                description = monument['description']
                break
        if flag==False:
            description="Sorry no information found"
            response.append({'user': user_input, 'bot': description})
        else:
            response.append({'user': user_input, 'bot': "Here is some information : "+ description})
    #other
    else:
            response.append({'user': user_input, 'bot': "Sorry I didn't got your question please repeat"})

    # return render_template('index.html', response=response)
    return jsonify(response) 

if __name__ == '__main__':
    app.run(debug=True)

