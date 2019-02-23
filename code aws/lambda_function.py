import boto3
import main
import datetime

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def get_welcome_response():
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Harassment Monitor. "
    reprompt_text = "welcome"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for using Harassment Monitor. "
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def analyze_speech(intent_request, session):
    intent = intent_request['intent']
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    phrase = intent['slots']['Speech']['value']

    harassment = main.is_harassment(phrase)
    if harassment == 1:
        speech_output = "Harassment detected. I heard " + phrase
        #send_alert
    else:
        speech_output = "No harassment detected"; 
    reprompt_text = "No harassment detected" 

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    if intent_name == "MonitorHarassmentIntent":
        return analyze_speech(intent_request, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    print('h5');
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return handle_session_end_request()

def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.65a293ea-7047-4dd4-be57-32d3dc717da5"):
        raise ValueError("Invalid Application ID")

    if event['session']['new']:
        print('h1');
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        print('h2');
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        print('h3');
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        print('h4');
        return on_session_ended(event['request'], event['session'])
