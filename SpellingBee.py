from __future__ import print_function
import random
import urllib2
import json
from string import whitespace
import xml.etree.ElementTree as ET

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    # Call new session handler
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
        
    # Otherwise call handler depending on session type
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    return get_on_launch_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    if intent_name == "SpellingBee":
        return start_spelling_bee(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_on_launch_response() 
    else:
        raise ValueError("Invalid intent")

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'] + " has ended")


# --------------- Functions that control the skill's behavior ------------------


def get_on_launch_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Words, you can start the spelling bee by saying start " \
                    "Spelling Bee, or learn a new word by saying get random word"
    reprompt_text = "Please say start spelling bee to start the spelling bee or " \
                    "say get random word to learn a new word"
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def start_spelling_bee(intent, session):
    """ Initialize spelling bee game based on users choice of difficulty, and
    provide first word of given difficulty
    """
    
    # Set up number of letters for each difficulty
    # Points are used for scoring system
    difficulty = {"easy":[3, 5], "medium":[6, 9], "hard":[10, 14], "unfair":[15, 20]}
    points = {"easy": 2, "medium": 6, "hard":10, "unfair":15}
    
    # Set up card values for alexa mobile app
    card_title = "none"
    should_end_session = False

    # Get game difficulty and latest command used by player
    spelling_bee_difficulty, spelling_bee_command = get_difficulty_and_command(intent, session)
    
    if session['new']:  
        if spelling_bee_difficulty == None:
            speech_output, reprompt_text, session_attributes = response_welcome(intent, session)
            
        elif spelling_bee_command != None:
            speech_output, reprompt_text, session_attributes = response_select_difficulty(intent, session)
            
        else:
            word, speech_output, reprompt_text = word_of_difficulty(difficulty)
            session_attributes = {'difficulty':spelling_bee_difficulty, 'currentWord':word, "score":0}
    
    else:
        # Handle the possible commands a user can invoke
        if spelling_bee_command.lower() in ["definition", "define"]:
            speech_output, reprompt_text, session_attributes = response_definition(intent, session)
            
        elif spelling_bee_command.lower() in ["skip", "next word", "get next word"]:
            speech_output, reprompt_text, session_attributes = response_next_word(intent, session)
            
        elif spelling_bee_command.lower() in ["example", "give example"]:
            speech_output, reprompt_text, session_attributes = response_new_word(intent, session)

        elif spelling_bee_command.lower() in ["repeat", "repeat word"]:
            speech_output, reprompt_text, session_attributes = response_repeat_word(intent, session)

        elif spelling_bee_command.lower() in ["finish game", "end"]:
            speech_output, reprompt_text, session_attributes = response_end_game(intent, session)
        
        elif spelling_bee_command != None and spelling_bee_command.isupper():
            speech_output, reprompt_text, session_attributes = check_spelling(spelling_bee_command, intent, session)
            
        else:
            speech_output, reprompt_text, session_attributes = response_invalid_command()

        session_attributes = session['attributes']

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def check_spelling(spelling_bee_command, intent, session):
    """ Check if spelling provided by user is correct, and give appropiate response
    """
    
    correct_spelling = list(session['attributes']['currentWord'])
    correct_word = session['attributes']['currentWord']

    # User spelling is correct and we update score
    if spelling_bee_command.lower() == correct_word.lower():
        spelling_bee_difficulty = session['attributes']['difficulty']
        session["attributes"]["score"] += points[spelling_bee_difficulty]
        length = random.randint(difficulty[spelling_bee_difficulty][0], difficulty[spelling_bee_difficulty][1])
        word, speech_output, reprompt_text = prompt_new_word(length)
        speech_output = "Correct. Next word is " + str(word) + "your point is now " + str(session["attributes"]["score"])       

    # User spelling is incorrect, give user a new word
    else:
        spelling_bee_difficulty = session['attributes']['difficulty']
        length = random.randint(difficulty[spelling_bee_difficulty][0], difficulty[spelling_bee_difficulty][1])
        word, speech_output, reprompt_text = prompt_new_word(length)
        speech_output = "Incorrect. The correct spelling is " + " .".join(list(correct_word)) + ". Next word is " + word

    # Update the corrent word stored for session
    session["attributes"]["currentWord"] = word
    session_attributes = session["attributes"]
    reprompt_text = "reprompt"

    return speech_output, reprompt_text, session_attributes

def word_of_difficulty(difficulty):
    """ Return a new random word of given difficulty
    """
    
    if spelling_bee_difficulty == "easy":
        length = random.randint(difficulty["easy"][0], difficulty["easy"][1])
        word, speech_output, reprompt_text = prompt_new_word(length, True)
        
    elif spelling_bee_difficulty == "medium":
        length = random.randint(difficulty["medium"][0], difficulty["medium"][1])
        word, speech_output, reprompt_text = prompt_new_word(length, True)
                
    elif spelling_bee_difficulty == "hard":
        length = random.randint(difficulty["hard"][0], difficulty["hard"][1])
        word, speech_output, reprompt_text = prompt_new_word(length, True)
    
    elif spelling_bee_difficulty == "unfair":
        length = random.randint(difficulty["unfair"][0], difficulty["unfair"][1])
        word, speech_output, reprompt_text = prompt_new_word(length, True)
        
    return word, speech_output, reprompt_text


def response_end_game(intent, session):
    """ Return attributes for ending game
    """

    session_attributes = {}
    speech_output = "Ending game. Goodbye"
    reprompt_text = None

     return speech_output, reprompt_text, session_attributes


def response_repeat_word(intent, session):
    """ Return attributes for ending game
    """

    session_attributes = {}
    speech_output = "The word is " + session['attributes']['currentWord']
    reprompt_text = None

    return speech_output, reprompt_text, session_attributes


def response_definition(intent, session):
    """ Return attributes for definition command
    """

    session_attributes = {}
    response = urllib2.urlopen("http://api.wordnik.com/v4/word.json/" + session['attributes']['currentWord'] + "/definitions?api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5").read()
            if response == "[]":
                speech_output = "Sorry no definition available for " + session['attributes']['currentWord']
            else:
                response = response[1:-1].replace("},", "}~")
                json_res = json.loads(response.split("~")[0])
    
                speech_output = "Definition of " + session['attributes']['currentWord'] + " is " + str(json_res['text'])
            reprompt_text = "reprompt"
            
    return speech_output, reprompt_text, session_attributes


def response_next_word(intent, session):
    """ Return attributes for next word command
    """

    spelling_bee_difficulty = session['attributes']['difficulty']
    length = random.randint(difficulty[spelling_bee_difficulty][0], difficulty[spelling_bee_difficulty][1])
    word, speech_output, reprompt_text = prompt_new_word(length)
    session["attributes"]["currentWord"] = word
    session_attributes = session["attributes"]

    return speech_output, reprompt_text, session_attributes


def response_new_word(intent, session):
    """ Return attribtes for new word command
    """

    session_attributes = {}
    response = urllib2.urlopen("http://api.wordnik.com/v4/word.json/" + session['attributes']['currentWord'] + "/examples?api_key=a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5").read()
            
    if response == "{}":
        speech_output = "Sorry no example is available for " + session['attributes']['currentWord']
    else:
        examples = json.loads(response)['examples']
        speech_output = "An example of " + session['attributes']['currentWord'] + " is " + str(examples[0]['text'])        
    reprompt_text = "reprompt"
    
    return speech_output, reprompt_text, session_attributes

    
def response_welcome(intent, session):
    """ Return attributes for games welcome response
    """
    
    speech_output = "Welcome to Spelling Bee. Please select difficulty by saying easy, medium, hard or unfair"
    reprompt_text = "Please select difficulty by saying easy, medium, hard or unfair"
    session_attributes = {}
    
    return speech_output, reprompt_text, session_attributes


def response_select_difficulty(intent, session):
    """ Return attributes for select difficulty response
    """
    
    speech_output = "No difficulty selected, please selecte difficulty by saying easy, medium, hard or unfair"
    reprompt_text = "reprompt"
    session_attributes = {}
    
    return speech_output, reprompt_text, session_attributes

def response_invalid_command(intent, session):
    """ Return attributes for an invalid command
    """
    session_attributes = {}
    speech_output = "Command not recognized. Please try a different command"
    reprompt_text = "Command not recognized. Please try a different command"
    
    return speech_output, reprompt_text, session_attributes


def is_all_chars(chars_list):
    """ Check if response given by user is all characters
    """
    
    for char in chars_list:
        if char.lower() not in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'z']:
            return False
        
    return True
        
def get_difficulty_and_command(intent, session):
    """ Return the game difficulty and latest command used by the user for the current session
    """
    
    spelling_bee_difficulty = None
    command = None
    try:
        spelling_bee_difficulty = intent["slots"]["Difficulty"]["value"]
    except Exception:
           pass
   
    try:
        command = intent["slots"]["CommandOrDifficulty"]["value"]
        # See if command is actually a difficulty value
        if command in ["easy", "medium", "hard", "unfair"]:
            spelling_bee_difficulty = command
            command = None
        if command == "":
            command = None
            
    except Exception:
        print("no command found")
   
    return spelling_bee_difficulty, command


def prompt_new_word(length, is_first_word=False):
    """ Command prompt to get a new word of given length
    """

    # Get new word using random word api
    reprompt_text = "reprompt"
    response = urllib2.urlopen("http://randomword.setgetgo.com/get.php?len=" + str(length))
    word = response.read()
    current_word = word

    # Alexa speech response for the new word
    if (is_first_word):
        speech_output = "The word is " + str(word) + ". To hear the definition please say definition, to repeat the word please say repeat, "
    else:
        speech_output = "The word is " + str(word)
        
    return word, speech_output, reprompt_text


def get_random_word(intent, session):
    """ Command prompt to retrive a random word from dictionary
    """
    
    session_attributes = {}
    card_title = "none"
    speech_output = "random word"
    reprompt_text = "reprompt"
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        


# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    """ Return response to be sent to alexa
    """
    
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
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
    """ Return session attributes and response from alexa
    """
    
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response

