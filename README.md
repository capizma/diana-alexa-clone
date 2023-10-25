# diana-alexa-clone
Alexa clone built with a combination of an NLU model trained on the CLINC dataset and specific AIML responses taken from the ALICE chatbot.
This project uses the Spotify API, so this is best run on a machine with Spotify installed.

Run base.py to get started!

Some example prompts:

help
	'help'
	'help me'
	'i need assistance'
	'i need some help'
	'i need help'

stop
	'stop talking'
	'quiet'
	'shut up' (may result in a telling off!)
	'no one is talking to you'
	'nobody talking to you'
	'nobody said your name'
	'no one said your name'

music
	'play spotify'
	'play some music'
	'playlists'
		'play my [playlist name] playlist'
		'play [playlist name]'
	'pause'
	'unpause'
	'what song is this'
	'skip to the next track'

reminders
	'set reminder'
	'remind me to'
	'what are my reminders for [period]'

timers
	'set a timer'
	'cancel timer'

datetime
	'what time is it'
	'what day is it'
	'when is the next holiday'
	
searches
	'who is [person]'
	'what is an [object]'
	'what is [term]'
	'define [singular word]'
	'spell [phrase]'

fun
	'roll a dice'
	'flip a coin'
	'tell me a joke'
	'tell me a fun fact'

Notes - in addition to installing any relevant packages, you may need to downgrade your setuptools to 45.2.0.

To do:
	speed up mic adjustment
	requirements.txt
	alarms
	personalised NLU training dataset
	previous NLP processing
	sentiment extraction
	subject extraction
