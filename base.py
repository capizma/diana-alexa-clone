import infer
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth
import wikipedia
time.clock = time.time
import speech_recognition as sr
import pyttsx3
import wave
import datetime
from datetime import date, timedelta, datetime
import pandas as pd
import timeit
import random
import aiml
from math import pi
import numpy as np
import pyaudio
import sys
from PyDictionary import PyDictionary
import holidays
import collections
import logging
import os

# Features the main response mapping and process loop for the program

# Mute any AIML mismatch prints and Spotipy HTTPErrors as they are handled/the user is notified upon request
logging.getLogger().setLevel(logging.CRITICAL)

VERSION = 'v0.2.3'

portrait = """

"""

# Returns text response based on #CONTEXT key value and more rules for accuracy
def evoke_response(context_key):   
    global timers
    
    aiml_responses = ['#HELP',
    '#CANCEL_RUDE',
    '#ARE_YOU_A_BOT',
    '#HOW_OLD_ARE_YOU',
    '#MEANING_OF_LIFE',
    '#WHAT_ARE_YOUR_HOBBIES',
    '#WHAT_CAN_I_ASK_YOU',
    '#WHAT_IS_YOUR_NAME',
    '#WHERE_ARE_YOU_FROM',
    '#WHO_DO_YOU_WORK_FOR',
    '#WHO_MADE_YOU']
     
    if context_key == '#CANCEL':
        return ""
    if '#OOS' in context_key:
        out = kern_post.respond(context_key.replace('#OOS_',''))
        
        if out == "DEFAULT":
            
            if '--debug' in args:
                print("No response template")
            # More general response
            out = kern_post.respond("AIML CONFUSED")
            
        return out
    for prefix in aiml_responses:
        if prefix in context_key:
            #out = kern_post.respond(context_key.replace(prefix+'_',''))
            
            #if out == "" or out is None:
                
            # More general response
            out = kern_post.respond("AIML "+prefix.replace('#','').replace('_',' '))
            
            return out
    if '#FORMALITY' in context_key:
        return context_key.replace('#FORMALITY_','')
    if '#WIKIPEDIA' in context_key:
        try:
            return wikipedia.summary(context_key.replace('#WIKIPEDIA_','') , auto_suggest=False, sentences=2)
        except:
            return "Sorry, I can't find anything on Wikipedia for "+context_key.replace('#WIKIPEDIA_','')       
    if '#WHAT_SONG' in context_key:
        current = sp.current_user_playing_track()
        
        return "The song that's currently playing is "+current['item']['name']+" by "+current['item']['artists'][0]['name']
    if '#PAUSE' in context_key:
        return ""
    if '#UNPAUSE' in context_key:
        return ""
    if '#PLAY' in context_key:
        return ""
    if '#NEXT SONG' in context_key:
        return ""
    if '#VOLUME_TO' in context_key:
        sp.volume(int(context_key.replace('#VOLUME_TO_','')))
        return ""
    if '#REMINDER_UPDATE' in context_key:
        df = pd.read_csv('data/reminders.csv')
        new_dt = context_key.replace('#REMINDER_UPDATE_','').split('_')[0]
        new_desc = context_key.replace('#REMINDER_UPDATE_','').split('_')[1]
        
        new = pd.DataFrame([[new_dt,new_desc]],columns=['date','text'])
        
        df = pd.concat([df,new])
        df = df[['date','text']]
        df.to_csv('data/reminders.csv')
        
        return "Your reminder has been saved."
    elif '#REMINDER_DELETE' in context_key:
        new = pd.DataFrame(columns=['date','text'])
        new.to_csv('data/reminders.csv')
        return "Your reminders have been deleted."
    elif '#REMINDER_' in context_key:
        n_reminders = 0
        dt_today = date(datetime.today().year,datetime.today().month,datetime.today().day)
        
        df = pd.read_csv('data/reminders.csv')
        df['ds'] = df['date'].apply(lambda x: datetime.strptime(x,'%Y-%m-%d').date())
        df = df.sort_values(by='ds')
        
        if context_key == '#REMINDER_TODAY':
            subset = df[(df['ds'] == dt_today)]
            n_reminders = len(subset)
            period = 'today'
            
        if context_key == '#REMINDER_TOMORROW':
            subset = df[(df['ds'] == dt_today+timedelta(days=1))]
            n_reminders = len(subset)
            period = 'tomorrow'
            
        if context_key == '#REMINDER_WEEK':
            subset = df[(df['ds'] >= dt_today) & (df['ds'] <= dt_today+timedelta(days=7))]
            n_reminders = len(subset)
            period = 'this week'
   
        if context_key == '#REMINDER_NEXTWEEK':
            subset = df[(df['ds'] >= dt_today+timedelta(days=7)) & (df['ds'] <= dt_today+timedelta(days=14))]
            n_reminders = len(subset)
            period = 'next week'
            
        if n_reminders > 0:
            out_text = "You have "+str(n_reminders)+" scheduled for "+period+". "
            
            for i in subset['text'].values:
                out_text += i
            
            return out_text
        else:
            out_text = "You have no reminders scheduled for "+period+". "
            return out_text
    if '#TIMER_ADD' in context_key:
        # Temp timers wipe, deal with cancelling one specific timer
        timers = []
        timers.append(context_key.replace('#TIMER_ADD_',''))
        return "The timer has been set"
    if '#TIMER_CANCEL' in context_key:
        timers = []
        return "The timer has been cancelled"
    if '#TIME' in context_key:
        dt_hour = datetime.today().hour
        dt_minute = datetime.today().minute
        dt_minute_alt = str(int(datetime.strftime(datetime.today(),'%M')))
        
        if len(dt_minute_alt) < 2:
            dt_minute_alt = " oh " + dt_minute_alt
        
        if dt_hour > 12:
            out_text = 'The time is now '+str(dt_hour-12)+' '+dt_minute_alt+' P M'
        elif dt_hour > 0 and dt_hour <= 12:
            out_text ='The time is now '+str(dt_hour)+' '+dt_minute_alt+' A M'
        elif dt_hour == 0:
            out_text ='The time is '+str(dt_minute)+' minutes past midnight'
            
        return out_text
    if '#DATE' in context_key:
        dt_today = datetime.today()

        if 4 <= dt_today.day <= 20 or 24 <= dt_today.day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][dt_today.day % 10 - 1]
        
        out_text ='Today is the '+str(dt_today.day)+suffix+' of '+datetime.strftime(dt_today,'%B')+' '+datetime.strftime(dt_today,'%Y')
        
        hol_check = holiday.get(dt_today.date())
        if hol_check is not None:
            out_text = out_text + ". Today is "+hol_check+"!"
        
        return out_text
    if "#DEFINE" in context_key:
        try:
            out_text = str(dictionary.meaning(context_key.replace('#DEFINE_',''))).replace('{','').replace('}','').replace('[','').replace(']','')
        
            assert out_text != "None"
        except:
            return "Sorry, I couldn't find anything for "+context_key.replace('#DEFINE_','')+". Try asking for something less niche or using only one word."
        
        return out_text
    if '#ROLL_DICE' in context_key:
        result = random.randint(1,6)
        out_text = "I rolled a "+str(result)
            
        return out_text
    if '#FLIP_COIN' in context_key:
        result = random.randint(1,2)
        
        if result == 1:
            out_text = "Heads"
        else:
            out_text = "Tails"
            
        return out_text
    if '#TELL_JOKE' in context_key:
        jokes = pd.read_csv('data/jokes.csv')
        joke = jokes['text'].values[random.randint(0,len(jokes)-1)]
        
        return joke
    if '#FACT' in context_key:
        facts = pd.read_csv('data/facts.csv')
        fact = facts['text'].values[random.randint(0,len(facts)-1)]
        
        return fact
    if '#SPELL' in context_key:
        out_text = "The phrase "+context_key.replace('#SPELL_','')+" is spelled"
        
        for char in context_key.replace('#SPELL_',''):
            out_text = out_text+" "
            out_text = out_text+char.upper()
        
        return out_text
    if '#NEXT_HOLIDAY' in context_key:
        hols = []
        for key, val in holiday.items():
            if key > date(datetime.today().year,datetime.today().month,datetime.today().day):
                hols.append(key)
                
        hols = np.sort(hols)
        
        if 4 <= hols[0].day <= 20 or 24 <= hols[0].day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][hols[0].day % 10 - 1]
        
        return "The next holiday is "+holiday.get(hols[0])+" on the "+str(hols[0].day)+suffix+' of '+datetime.strftime(hols[0],'%B')+' '+datetime.strftime(hols[0],'%Y')
    if '#REPEAT' in context_key:
        return history[0]
    
    return ""

# Harvest the context key provided, and chase up any extra context required for a request
def context_stream(sp):
    text = listen_respond().lower()
    
    context = infer.extract_oper(text, sp)
    
    if '--debug' in args:
        print("Context key -> "+context)
    
    # Deletion warnings
    if '#REMINDER_DELETE' in context:
        say_tts('This will delete all reminders. Say yes to continue this action',False)
        
        text = listen_respond().lower()
        
        if 'yes' in text:
            context = '#REMINDER_DELETE'
        else:
            context = '#CANCEL'
    
    if '_NONE' in context:
        
        # What context is missing?
        
        if '#TIMER' in context:
            
            break_chase = False
            
            say_tts('How many minutes would you like to set your timer for?',False)
            
            while (break_chase == False):
                text = listen_respond().lower()
                
                alt_context = infer.parse_timer(text,'')
                if 'cancel' in text or '#TIMER_CANCEL' in alt_context:
                    context = '#CANCEL'
                    break_chase = True
                elif 'NONE' not in alt_context and '#TIMER_ADD' in alt_context:
                    context = alt_context
                    break_chase = True
                    
                if '#REPEAT' in alt_context and break_chase == False:
                    say_tts("How many minutes would you like to set your timer for?",False) 
                elif break_chase == False:
                    say_tts("Sorry, I didn't get that. How many minutes do you want?",False)
                    
        if '#REMINDER' in context:
            # Chase for date
            break_chase = False
            disregard = False
            
            if '#REMINDER_UPDATE_NONE' in context:
                
                say_tts('What day would you like to be reminded on?',False)
                
                while (break_chase == False):
                    text = listen_respond().lower()
                
                    alt_context = infer.parse_calendar(' ' + text,'')
                    
                    if 'cancel' in text or 'exit' in text or 'abort' in text:
                        context = '#CANCEL'
                        break_chase = True
                        disregard = True
                    elif '#REMINDER_UPDATE_NONE' not in alt_context and '#REMINDER_UPDATE' in alt_context:
                        context = alt_context[:27]+"_"+context.split('_')[-1]
                        break_chase = True
                        
                    if '#REPEAT' in alt_context and break_chase == False:
                        say_tts("What day would you like to be reminded on?",False) 
                    elif break_chase == False:
                        say_tts("Sorry, I didn't get that. Which day would this be?",False)
                        
            # Chase for description
            break_chase = False
            if disregard == False:
                if context[-5:] == "_NONE":
                    
                    say_tts('What would you like to name your reminder?',False)
                    
                    while (break_chase == False):
                        text = listen_respond().lower()
                    
                        alt_context = infer.parse_calendar('remind me to ' + text+' on the 1st january','')
                        
                        if 'cancel' in text or 'exit' in text or 'abort' in text:
                            context = '#CANCEL'
                            break_chase = True
                            disregard = True
                        elif alt_context[-5:] != "_NONE" and '#REMINDER_UPDATE' in alt_context:
                            context = context[:-5]+"_"+alt_context.split('_')[-1]
                            break_chase = True
                            
                        if '#REPEAT' in alt_context and break_chase == False:
                            say_tts('What would you like to name your reminder?',False)
                        elif break_chase == False:
                            say_tts("Sorry, I didn't get that. What is the title?",False)

                    
    return [evoke_response(context),context]
    
def say_tts(text,add_to_deque):
    text = text.replace('DEFAULT','')

    print("-> "+text)
    
    tts.say(text)
    
    if add_to_deque == True:
        history.appendleft(text)
    
    tts.runAndWait()

def playsound(fname):

    wf = wave.open('audio/'+fname, 'rb')

    p = pyaudio.PyAudio()

    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # 1024 chunk size
    data = wf.readframes(1024)

    while data:
        stream.write(data)
        data = wf.readframes(1024)

    wf.close()
    stream.close()    
    p.terminate()
    
def listen_respond():
    r = sr.Recognizer()
    r.energy_threshold = 500
    answer = ""

    with sr.Microphone() as source:
        try:
            playsound('listen_beep.wav')
            print("Listening...")
            audio = r.listen(source)
               
            try:
                before = datetime.now()
                text = r.recognize_google(audio, language='en-GB',show_all=False)
                timing = datetime.now() - before
                
                print("Phrase recognised -> " + text)
                
            except:
                text = ""
                print("Phrase recognised nothing")
        except:
            pass
    
    return text

def greeting_routine():
    # Greeting routine
    playlists = sp.current_user_playlists()
    playlist_name = "diana_default"
    greeting = "Good whatever!"
            
    if datetime.today().hour > 0 and datetime.today().hour < 12:
        greeting = "Good morning!"
        playlist_name = 'diana_goodmorning'
        
    elif datetime.today().hour >= 12 and datetime.today().hour < 17:
        greeting = "Good afternoon!"
        playlist_name = 'diana_goodafternoon'
    else:
        greeting = "Good evening!"
        playlist_name = 'diana_goodevening'
    
    for i in playlists['items']:
        if i['name'] == playlist_name:
            try:
                sp.start_playback(context_uri=i['uri'])
                break
            except:
                pass
            
    say_tts(evoke_response('#OOS_AIML INIT'),True)
    say_tts(greeting,True)
    
    say_tts(evoke_response('#DATE'),True)
    say_tts(evoke_response('#REMINDER_WEEK'),True)

if __name__ == "__main__":
    # Setting up/ initial greeting
    
    os.system("title " + "Diana "+VERSION)
    
    args = []

    if sys.argv[1:]:
        for arg in sys.argv:
            args.append(arg)
    
    timers = []
    dictionary = PyDictionary()
    holiday = holidays.UK(years=[datetime.today().year,datetime.today().year+1])
    history = collections.deque([],maxlen=5)

    tts = pyttsx3.init()
    weekdaytext = lambda x: ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][x] 

    scope = ["user-modify-playback-state","user-library-read","user-read-currently-playing","user-top-read"]
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    r = sr.Recognizer()
    r.energy_threshold = 3000

    kern_post = aiml.Kernel()
    kern_post.setTextEncoding(None)
    kern_post.bootstrap(learnFiles=["std.aiml","rules_post.aiml"])

    hols = []
    for key, val in holiday.items():
        if key > date(datetime.today().year,datetime.today().month,datetime.today().day):
            hols.append(key)
            
    hols = np.sort(hols)
    
    if 4 <= hols[0].day <= 20 or 24 <= hols[0].day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][hols[0].day % 10 - 1]
        
    os.system('cls')
    print(portrait)
    greeting_routine()
    
    # Main process loop
    while True:
        context = ""
        alarm = False
        
        for idx,item in enumerate(timers):
            if str(datetime.today().hour)+'#'+str(datetime.today().minute) == item:
                timers.pop(idx)
                alarm = True
                
        if alarm == True:
            say_tts("Your timer has ended",True)
            playsound('timer_alarm.wav')

        with sr.Microphone() as source:
            
            if '--debug' not in args:
                os.system('cls')
            
                print(portrait)
            
            print("Adjusting...")
            
            r.adjust_for_ambient_noise(source)
            
            try:
                print("Listening for wakeword...")
                audio = r.listen(source,phrase_time_limit=3)
                   
                try:
                    before = datetime.now()
                    text = r.recognize_google(audio, language='en-GB',show_all=False)
                    timing = datetime.now() - before
                    print("Wake recognised -> "+text)
                    
                    if "diana" in text.lower() or "anna" in text.lower() or "dinosaurus" in text.lower():
                        paused = False
                    
                        try:
                            sp.pause_playback()
                        except:
                            paused = True
                    
                        result = context_stream(sp)
                        response_text = result[0]
                        
                        if '#REPEAT' not in context and len(response_text) > 0:
                            say_tts(response_text,True)
                        else:
                            say_tts(response_text,False)
                        
                        # Spotify functions
                        if '#PLAY' in result[1]:
                            try:
                                sp.start_playback(context_uri=result[1].replace('#PLAY_',''))
                            except:
                                say_tts('I would love to, but your Spotify is unavailable :(',True)
                        if '#NEXT_SONG' in result[1]:
                            try:
                                sp.next_track()
                            except:
                                say_tts('I would love to, but your Spotify is unavailable :(',True)
                            try:
                                # If we're paused, play upon skip
                                sp.start_playback()
                            except:
                                pass
                        elif (paused == False and '#PAUSE' not in result[1]) or '#UNPAUSE' in result[1]:
                            sp.start_playback()
                            
                        playsound('listen_beep_off.wav')

                except:
                    text = ""
                    print("Wake recognised nothing")
                    
            except:
                pass
