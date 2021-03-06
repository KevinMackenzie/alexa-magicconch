"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import random


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': "<speak>" + output + "</speak>"
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


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "I'm the Magic Conch Shell.  Ask me a question"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me a question"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Bye"
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


trivial_words = ["something", "what"]
def contains_nontrivial_word(word_list, word):
    if word not in word_list:
        return False
    
    index = word_list.index(word)
    
    #return false if word is last in word list
    if index == len(word_list) - 1:
        return False
    # return false is the last_word is in trivial_words and true if it is absent from trivial_words
    elif index == len(word_list) - 2:
        last_word = word_list[-1]
        return last_word not in trivial_words
    return True

yes_no_responses = ["no", "yes", "<prosody rate='40%'>no</prosody>", "try asking again", "i don't think so", "maybe some day"]
# yes_no_responses = ["<prosody rate='40%'>no</prosody>"]
quantity_words = ["many", "much"]
should_words = ["should", "could", "would", "do"]
def process_question(intent):
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    reprompt_text = "Ask me a question."
    

    question_text = intent['slots']['Question']['value']
    speech_output = question_text

    words = question_text.split(' ')

    if len(words) < 2:
        speech_output = "Try asking again"
    elif contains_nontrivial_word(words, "or") or words[0] == "which": #"Which One" case
        speech_output = "neither"
    elif words[0] == "when":
        speech_output = "never"
    elif words[0] == "where":
        speech_output = "nowhere"
    elif words[0] == "how":
        if words[1] == "about":
            speech_output = "no"
        elif words[1] in quantity_words:
            speech_output = "none"
        elif words[1] in should_words:
            speech_output = "don't"
        else:
            speech_output = "not very"
    elif words[0] == "why":
        speech_output = "because"
    elif words[0] == "who" or words[1] == "whom":
        speech_output = "nobody"
    elif words[0] == "what":
        speech_output = "nothing"
    else:
        speech_output = yes_no_responses[random.randint(0, len(yes_no_responses)-1)]

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "QuestionIntent":
        return process_question(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
