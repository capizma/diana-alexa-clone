import nlu_predict
import aiml
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re
import datetime
from datetime import date, timedelta, datetime
import pandas as pd
from dateutil.relativedelta import relativedelta
time.clock = time.time
import logging

# Returns #CONTEXT value based on priority words, prioritised AIML matches, inferred intent, and post-AIML rule matches (in that order)

priority = [
'cancel'
,'repeat'
,'are_you_a_bot'
,'how_old_are_you'
,'meaning_of_life'
,'what_are_your_hobbies'
,'what_can_i_ask_you'
,'what_is_your_name'
,'where_are_you_from'
,'who_do_you_work_for'
,'who_made_you'    
]

kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles="rules.aiml")

def has_numbers(text):
    return any(char.isdigit() for char in text)

def parse_calendar(text,out):
    when = date(2001,1,1)
    dt_today = date(datetime.today().year,datetime.today().month,datetime.today().day)
    clean = re.sub('\D', ' ',text)
    
    date_context = ""
    desc_context = ""
    
    when_pos = text.find(" on the ")
    
    if 'today' in text:
        when = dt_today
        when_pos = text.find("today")
    elif 'tomorrow' in text:
        when = dt_today + timedelta(days=1)
        when_pos = text.find("tomorrow")
    elif 'next' in text:
        if 'week' in text:
            when = dt_today + timedelta(days=7)
            when_pos = text.find("next week")
        elif 'month' in text: 
            when = dt_today + relativedelta(months=+1)
            when_pos = text.find("next month")
        elif 'year' in text:
            when = dt_today + relativedelta(years=+1)
            when_pos = text.find("next year")
    elif has_numbers(text):
        set_month = datetime.today().month
        set_year = datetime.today().year
        match = re.search(r'.*([1-3][0-9]{3})', text)
        if match is not None:
            # Year in string
            set_year = match.group(1)
            
        set_day = clean.strip().split(' ')[0]
        
        for i in range(1,13):
            if datetime.strftime(date(2020,i,1),'%B').lower() in text:
                set_month = i
                break
        
        try:
            when = date(int(set_year),int(set_month),int(set_day))
            
            while (when < dt_today):
                when = when + relativedelta(years=+1) 
        except:
            pass
        
    if when != date(2001,1,1):
        date_context = datetime.strftime(when,'%Y-%m-%d')
        
        if when_pos != 0 and ' to ' in text:
            if when_pos < text.find(' to '):
                if len(text[text.find(' to '):].replace(' to ','')) > 0:
                    desc_context = text[text.find(' to '):].replace(' to ','')
            else:
                if len(text[text.find(' to '):when_pos].replace(' to ','')) > 0:
                    desc_context = text[text.find(' to '):when_pos].replace(' to ','')
                
    else:
        if ' to ' in text:
            if len(text[text.find(' to '):].replace(' to ','')) > 0:
                desc_context = text[text.find(' to '):].replace(' to ','')
                
    out = '#REMINDER_UPDATE'
    
    if date_context == "":
        out=out+'_NONE'
    else:
        out=out+'_'+date_context
    
    if desc_context == "":
        out=out+'_NONE'
    else:
        out=out+'_'+desc_context
    return out

def parse_timer(text,out):
    if 'minute' in text and 'hour' not in text:
        clean = int(re.sub('\D', ' ',text).strip())
    
        out = '#TIMER_ADD_'+str((datetime.today()+timedelta(minutes=clean)).hour)+'#'+str((datetime.today()+timedelta(minutes=clean)).minute)
        
        return out
    if 'hour' in text and 'minute' not in text:
        clean = int(re.sub('\D', ' ',text).strip())
    
        out = '#TIMER_ADD_'+str((datetime.today()+timedelta(hours=clean)).hour)+'#'+str((datetime.today()+timedelta(hours=clean)).minute)
        
        return out
    if 'cancel ' in text or 'clear ' in text or 'delete ' in text or 'remove ' in text:
        out = '#TIMER_CANCEL'
        return out
    
    return '#TIMER_ADD_NONE'

def extract_oper(text,sp):

    context = nlu_predict.infer_intent(text)    

    out = '#OOS_'+text
    
    # Priority for any in list, these intents are likely correct
    if context[0] in priority and context[0] != 'cancel':
        out = '#'+context[0].upper()+"_"+text
        return out
    else:
        
        if context[0] == 'cancel':
            out = '#CANCEL'
        
        aiml_out = kern.respond(text)
        # If we get an immediate match
        if aiml_out != "DEFAULT":
            if '#' in aiml_out:
                out = aiml_out
                return out
            else:
                out = '#FORMALITY_'+aiml_out
                return out
        else:
            
            # Cancel should override everything
            if ('cancel' in text and 'timer ' not in text) or 'turn off' in text:
                out = '#CANCEL'
            if 'shut up' in text or 'shut your' in text or ('shut the' in text and 'up' in text):
                out = '#CANCEL_RUDE' 
            for item in ['nobody said you','nobody mentioned','nobody is talking to you','nobody mentioned you','nobody was talking to']:
                if item in text.replace('no one','nobody'):
                    out = '#CANCEL'
                    return out 
            if out == '#CANCEL' or out == '#CANCEL_RUDE' or 'quiet' in text or 'stop talking' in text or ('said your name' in text and 'no' in text):
                if out != '#CANCEL_RUDE':
                    out = '#CANCEL'
                if 'fuk' in text or 'fucking' in text or 'fuck' in text or 'bitch' in text:
                    out = '#CANCEL_RUDE'
                    
                return out
            
            if 'help' in text or 'assistance' in text:
                out = "#HELP"
                return out
            
            if 'unpause' in text:
                out = '#UNPAUSE'
                return out
                
            if 'pause' in text or ('stop' in text and 'music' in text) or ('stop' in text and 'spotify' in text):
                out = '#PAUSE'
                return out
            
            # Date and time queries confuse with wikipedia search
            if context[0] != 'date' and context[0] != 'time' and context[0] != 'reminder' and context[0] != 'calendar' and context[0] != 'todo_list' and context[0] != 'definition' and context[0] != 'what_song' and ('spelling' not in text):
                for item in ['search for','what can you say about','what can you tell me about','tell me about','search wikipedia for','can you look up','what is the','what is an','what is a','what is','who is','what are']:
                    if item in text:
                        clean = "".join(text.split(item)[1:]).strip()
                    
                        out = '#WIKIPEDIA_'+clean
                        return out
            
            # In future, may potentially loop through high confidence contexts
            for item in [context[0]]:
                # We don't want more than 1 priority item or an item out of scope
                if item in priority or item == 'oos':
                    continue
                # If we have established the intent, return
                if '#OOS' not in out:
                    return out
                
                # Playing music gets confused with changing volume
                music_check = ('set the' not in text and 'mute' not in text and 'off' not in text and 'down' not in text and ' up' not in text and ' max' not in text) or ('up next' in text)
                
                n_volume = ""
                clean = re.sub('\D', ' ',text).strip().split(" ")
                if len(clean) > 0 and clean[0] != "":
                    if int(clean[0]) >= 0 and int(clean[0]) <= 100:
                        n_volume = clean[0]
                
                if music_check and n_volume == "":
                    
                    if item == 'play_music' or item == 'next_song':
                        if 'skip' in text or 'next' in text:
                            out = '#NEXT_SONG'
                            return out
                        else:                
                            out = '#PLAY'
                            
                            playlist_name = text.replace('playlist','')
                            
                            # IndexError if input is oddly worded
                            try:
                                if 'play' in text:
                                    playlist_name = playlist_name.split('play')[1]
                            except:
                                pass
                            
                            playlist_name = playlist_name.replace(' my','').replace(' the','').replace(' thanks','').replace(' thank you','').replace(' ','')
                            
                            playlists = sp.current_user_playlists()
                            
                            for i in playlists['items']:
                                if i['name'] == "diana_"+playlist_name:
                                    out = "#PLAY_"+i['uri']
                                    break
                                    
                            if out == '#PLAY':
                                for i in playlists['items']:
                                    if i['name'] == "diana_default":
                                        out = "#PLAY_"+i['uri']
                                        break
                                        
                            return out   
                    
                # Issue - 'turn spotify off' becomes #CANCEL request
                if item == 'change_volume' or ((music_check == False or n_volume != "") and (item == 'play_music' or item == 'change_song')):
                    
                    if 'max' in text:
                        out = '#VOLUME_TO_100'
                        
                        return out
                    if 'mute' in text or 'off' in text:
                        out = '#VOLUME_TO_0'
                        
                        return out
                    #if 'down' in text:
                    #    out = '#VOLUME_DOWN_10'
                    #    
                    #    if n_volume != "":
                    #        out = "#VOLUME_DOWN_"+n_volume
                    #        
                    #    return out
                    #if 'up' in text:
                    #    out = '#VOLUME_UP_10'
                    #    
                    #    if n_volume != "":
                    #        out = "#VOLUME_UP_"+n_volume
                    #        
                    #    return out
                    
                    else:
                        if n_volume != "":
                            out = '#VOLUME_TO_'+n_volume
                            return out
                        
                # Format : #REMINDER_UPDATE_DATE_TEXT
                if (item == 'calendar_update' or item == 'reminder_update') or ((item == 'calendar' and 'update' in text) or (item == 'reminder' and 'update' in text)) or 'remind me to' in text or 'remind me' in text:
                    out = parse_calendar(text,out)
                        
                    return out
                
                if item == 'calendar' or item == 'reminder':
                    
                    if 'clear ' in text or 'delete ' in text or 'remove ' in text:
                        out = '#REMINDER_DELETE'
                        return out
                    
                    out = '#REMINDER_WEEK'
                    
                    if 'next week' in text:
                        out = '#REMINDER_NEXTWEEK'
                        
                    if 'tomorrow' in text:
                        out = '#REMINDER_TOMORROW'
                        
                    if 'today' in text:
                        out = '#REMINDER_TODAY'
                
                    return out
                
                if item == 'timer' or 'timer' in text:
                    out = parse_timer(text,out)
                    
                    return out

                if item == 'date':
                    out = '#DATE'
                    return out
                if item == 'time':
                    out = '#TIME'
                    return out
                    
                if item == 'definition':
                    if 'definition of' in text:
                        clean = "".join(text.split('definition of ')[1:])
                        
                        out = '#DEFINE_'+clean
                        return out
                    if 'define' in text:
                        clean = "".join(text.split('define ')[1:])
                        
                        out = '#DEFINE_'+clean
                        return out
                    
                if item == 'fun_fact' or (('tell ' in text and 'fact' in text) or ('give ' in text and 'fact' in text)):
                    # Specific facts not yet supported
                    if ' about ' not in text:
                        out = '#FACT'
                        return out
                    
                if item == 'tell_joke':
                    out = '#TELL_JOKE'
                    return out
                
                if item == 'flip_coin':
                    out = '#FLIP_COIN'
                    return out
                
                if item == 'roll_dice':
                    out = '#ROLL_DICE'
                    return out
                
                if item == 'spelling' or 'spelling' in text:
                    if 'spell ' in text:
                        clean = "".join(text.split('spell ')[1:])
                        out = '#SPELL_'+clean
                        return out
                    elif ' spelling of ' in text:
                        clean = "".join(text.split(' spelling of ')[1:])
                        out = '#SPELL_'+clean   
                        return out
                    
                if item == 'what_song':
                    out = '#WHAT_SONG'
                    return out
                
                if item == 'next_holiday':
                    out = '#NEXT_HOLIDAY'
                    return out
    return out