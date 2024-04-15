# diana-alexa-clone
Alexa clone built with a combination of an NLU model trained on the CLINC dataset and specific AIML responses taken from the ALICE chatbot.
This project uses the Spotify API, so this is best run on a machine with Spotify installed.
---
Run ```base.py``` to get started! (For debug mode, run with --debug)

Dependencies:

```toml
tensorflow = ">=2.10.0, <=2.14.0"
tensorflow-intel = ">=2.10.0, <=2.14.0"
tensorflow-io-gcs-filesystem = [
    { version = ">= 0.23.1", markers = "platform_machine!='arm64' or platform_system!='Darwin'" },
    { version = "< 0.32.0", markers = "platform_system == 'Windows'" }
]
keras = ">=2.13.0"
scikit-learn = "^1.3.2"
```

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
- Speed up mic adjustment
- requirements.txt
- Alarms
- Personalised NLU training dataset
- More NLP
- Sentiment extraction
- Subject extraction
- Typing mode
