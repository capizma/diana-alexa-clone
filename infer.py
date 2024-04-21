import nlu
from parse import parse_utils
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
    "cancel",
    "repeat",
    "are_you_a_bot",
    "how_old_are_you",
    "meaning_of_life",
    "what_are_your_hobbies",
    "what_can_i_ask_you",
    "what_is_your_name",
    "where_are_you_from",
    "who_do_you_work_for",
    "who_made_you",
]

kern_std = aiml.Kernel()
kern_std.setTextEncoding(None)
kern_std.bootstrap(learnFiles=["aiml/std.aiml", "aiml/rules.aiml"])

kern = aiml.Kernel()
kern.setTextEncoding(None)
kern.bootstrap(learnFiles=["aiml/rules.aiml"])

def extract_oper(text, sp):
    context = nlu.infer_intent(text)[0]
    out = "#OOS_" + text

    # Priority for any in list, these intents are likely correct
    if context in priority and context != "cancel":
        out = "#" + context.upper() + "_" + text
        
        if context != "repeat":
            aiml_out = kern_std.respond(text)
            
            if aiml_out != "DEFAULT":
                out = "#FORMALITY_" + aiml_out
        
        return out
    else:
        aiml_out = kern.respond(text)

        # If we get an immediate match
        if aiml_out != "DEFAULT":
            if "#" in aiml_out:
                out = aiml_out
                return out
            else:
                out = "#FORMALITY_" + aiml_out
                return out
        else:
            # Cancel should override everything
            if context == "cancel":
                out = "#CANCEL"

            #################### CANCEL CHECKS ####################################

            if ("cancel" in text and "timer " not in text) or "turn off" in text:
                out = "#CANCEL"
            if (
                "shut up" in text
                or "shut your" in text
                or ("shut the" in text and "up" in text)
            ):
                out = "#CANCEL_RUDE"
            for item in [
                "nobody said you",
                "nobody mentioned",
                "nobody is talking to you",
                "nobody mentioned you",
                "nobody was talking to",
            ]:
                if item in text.replace("no one", "nobody"):
                    out = "#CANCEL"
                    return out
            if (
                out == "#CANCEL"
                or out == "#CANCEL_RUDE"
                or "quiet" in text
                or "stop talking" in text
                or ("said your name" in text and "no" in text)
            ):
                if out != "#CANCEL_RUDE":
                    out = "#CANCEL"
                if (
                    "fuk" in text
                    or "fucking" in text
                    or "fuck" in text
                    or "bitch" in text
                ):
                    out = "#CANCEL_RUDE"
                return out

            #################### HELP CHECKS ######################################

            if "help" in text or "assistance" in text:
                out = "#HELP"
                return out

            if "unpause" in text:
                out = "#UNPAUSE"
                return out

            if (
                "pause" in text
                or ("stop" in text and "music" in text)
                or ("stop" in text and "spotify" in text)
            ):
                out = "#PAUSE"
                return out

            #################### WIKIPEDIA CHECKS ##################################

            if (
                context != "date"
                and context != "time"
                and context != "reminder"
                and context != "calendar"
                and context != "todo_list"
                and context != "definition"
                and context != "what_song"
                and ("spelling" not in text)
            ):
                for item in [
                    "search for",
                    "what can you say about",
                    "what can you tell me about",
                    "tell me about",
                    "search wikipedia for",
                    "can you look up",
                    "what is the",
                    "what is an",
                    "what is a",
                    "what is",
                    "who is",
                    "what are",
                ]:
                    if item in text:
                        clean = "".join(text.split(item)[1:]).strip()
                        out = "#WIKIPEDIA_" + clean
                        return out

            # In future, may potentially loop through high confidence contexts

            for item in [context]:
                # We don't want more than 1 priority item or an item out of scope
                if item in priority or item == "oos":
                    continue
                # If we have established the intent, return
                if "#OOS" not in out:
                    return out

                #################### MUSICAL CHECKS #########################################

                # Playing music gets confused with changing volume
                music_check = (
                    "set the" not in text
                    and "mute" not in text
                    and "off" not in text
                    and "down" not in text
                    and " up" not in text
                    and " max" not in text
                ) or ("up next" in text)
                n_volume = ""
                clean = re.sub("\D", " ", text).strip().split(" ")
                if len(clean) > 0 and clean[0] != "":
                    if int(clean[0]) >= 0 and int(clean[0]) <= 100:
                        n_volume = clean[0]

                if music_check and n_volume == "":
                    if item == "play_music" or item == "next_song":
                        if "skip" in text or "next" in text:
                            out = "#NEXT_SONG"
                            return out
                        else:
                            out = "#PLAY"
                            playlist_name = text.replace("playlist", "")
                            # IndexError if input is oddly worded
                            try:
                                if "play" in text:
                                    playlist_name = playlist_name.split("play")[1]
                            except:
                                pass
                            playlist_name = (
                                playlist_name.replace(" my", "")
                                .replace(" the", "")
                                .replace(" thanks", "")
                                .replace(" thank you", "")
                                .replace(" ", "")
                            )
                            playlists = sp.current_user_playlists()
                            for i in playlists["items"]:
                                if i["name"] == "diana_" + playlist_name:
                                    out = "#PLAY_" + i["uri"]
                                    break
                            if out == "#PLAY":
                                for i in playlists["items"]:
                                    if i["name"] == "diana_default":
                                        out = "#PLAY_" + i["uri"]
                                        break
                            return out

                # Issue - 'turn spotify off' becomes #CANCEL request
                if item == "change_volume" or (
                    (music_check == False or n_volume != "")
                    and (item == "play_music" or item == "change_song")
                ):
                    if "max" in text:
                        out = "#VOLUME_TO_100"
                        return out
                    if "mute" in text or "off" in text:
                        out = "#VOLUME_TO_0"
                        return out
                    else:
                        if n_volume != "":
                            out = "#VOLUME_TO_" + n_volume
                            return out

                #################### REMINDER CHECKS ####################################

                # Format : #REMINDER_UPDATE_DATE_TEXT
                if (
                    (item == "calendar_update" or item == "reminder_update")
                    or (
                        (item == "calendar" and "update" in text)
                        or (item == "reminder" and "update" in text)
                    )
                    or "remind me to" in text
                    or "remind me" in text
                ):
                    out = parse_utils.parse_calendar(text, out)
                    return out

                if item == "calendar" or item == "reminder":
                    if "clear " in text or "delete " in text or "remove " in text:
                        out = "#REMINDER_DELETE"
                        return out
                    out = "#REMINDER_WEEK"
                    if "next week" in text:
                        out = "#REMINDER_NEXTWEEK"
                    if "tomorrow" in text:
                        out = "#REMINDER_TOMORROW"
                    if "today" in text:
                        out = "#REMINDER_TODAY"
                    return out

                #################### DATETIME CHECKS ###################################

                if item == "timer" or "timer" in text:
                    out = parse_utils.parse_timer(text, out)
                    return out

                if item == "date":
                    out = "#DATE"
                    return out
                if item == "time":
                    out = "#TIME"
                    return out

                #################### FUN CHECKS ########################################

                if item == "definition":
                    if "definition of" in text:
                        clean = "".join(text.split("definition of ")[1:])
                        out = "#DEFINE_" + clean
                        return out
                    if "define" in text:
                        clean = "".join(text.split("define ")[1:])
                        out = "#DEFINE_" + clean
                        return out

                if item == "fun_fact" or (
                    ("tell " in text and "fact" in text)
                    or ("give " in text and "fact" in text)
                ):
                    # Specific facts not yet supported
                    if " about " not in text:
                        out = "#FACT"
                        return out

                if item == "tell_joke":
                    out = "#TELL_JOKE"
                    return out

                if item == "flip_coin":
                    out = "#FLIP_COIN"
                    return out

                if item == "roll_dice":
                    out = "#ROLL_DICE"
                    return out

                if item == "spelling" or "spelling" in text:
                    if "spell " in text:
                        clean = "".join(text.split("spell ")[1:])
                        out = "#SPELL_" + clean
                        return out
                    elif " spelling of " in text:
                        clean = "".join(text.split(" spelling of ")[1:])
                        out = "#SPELL_" + clean
                        return out

                if item == "what_song":
                    out = "#WHAT_SONG"
                    return out

                if item == "next_holiday":
                    out = "#NEXT_HOLIDAY"
                    return out
    return out
