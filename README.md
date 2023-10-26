# diana-alexa-clone
Alexa clone built with a combination of an NLU model trained on the CLINC dataset and specific AIML responses taken from the ALICE chatbot.
This project uses the Spotify API, so this is best run on a machine with Spotify installed.
---
Run ```base.py``` to get started!

Installation note - in addition to installing any relevant packages, you may need to downgrade your setuptools to 45.2.0.

---
## Example Prompts

### Help
- 'Help'
- 'Help me'
- 'I need assistance'
- 'I need some help'
- 'I need help'

### Stop
- 'Stop talking'
- 'Quiet'
- 'Shut up' (may result in a telling off!)
- 'No one is talking to you'
- 'Nobody talking to you'
- 'Nobody said your name'
- 'No one said your name'

### Music
- 'Play spotify'
- 'Play some music'
- 'Playlists'
  - 'Play my \[playlist name] playlist'
  - 'Play \[playlist name]'
- 'Pause'
- 'Unpause'
- 'What song is this'
- 'Skip to the next track'

### Reminders
- 'Set reminder'
- 'Remind me to'
- 'What are my reminders for \[period]'

### Timers
- 'Set a timer'
- 'Cancel timer'

### Datetime
- 'What time is it'
- 'What day is it'
- 'When is the next holiday'
	
### Searches
- 'Who is \[person]'
- 'What is an \[object]'
- 'What is \[term]'
- 'Define \[singular word]'
- 'Spell \[phrase]'

### Fun
- 'Roll a dice'
- 'Flip a coin'
- 'Tell me a joke'
- 'Tell me a fun fact'

## To do:
- speed up mic adjustment
- requirements.txt
- alarms
- personalised NLU training dataset
- previous NLP processing
- sentiment extraction
- subject extraction