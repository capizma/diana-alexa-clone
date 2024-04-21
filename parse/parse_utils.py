import nlu
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