import numpy as np
from tensorflow import keras 
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Bidirectional
import pickle
from tensorflow.keras.models import load_model

# Loading model files, getting initial NLU classes and filtering them within scope

ls = ['are_you_a_bot','calendar','calendar_update','cancel','change_volume','date','definition','flip_coin','fun_fact','how_old_are_you','meaning_of_life','next_holiday','next_song','play_music','reminder','reminder_update','repeat','roll_dice','spelling','tell_joke','time','timer','what_are_your_hobbies','what_can_i_ask_you','what_is_your_name','what_song','where_are_you_from','who_do_you_work_for','who_made_you']

class IntentClassifier:
    def __init__(self,classes,model,tokenizer,label_encoder):
        self.classes = classes
        self.classifier = model
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def get_intent(self,text):
        self.text = [text]
        self.test_keras = self.tokenizer.texts_to_sequences(self.text)
        self.test_keras_sequence = pad_sequences(self.test_keras, maxlen=16, padding='post')
        self.pred = self.classifier.predict(self.test_keras_sequence)
        
        self.ls_out = []
        self.ls_pred = np.argsort(np.max(self.pred[:],axis=0))[-3:]
        
        for item in self.ls_pred:
            if self.label_encoder.inverse_transform([item])[0] in ls:
                self.ls_out.append(self.label_encoder.inverse_transform([item])[0])
            else: 
                if 'oos' not in self.ls_out:
                    self.ls_out.append('oos')
        
        return self.ls_out[::-1]

model = load_model('models/intents.h5', custom_objects={'Bidirectional': Bidirectional},compile=False)

with open('utils/classes.pkl','rb') as file:
  classes = pickle.load(file)

with open('utils/tokenizer.pkl','rb') as file:
  tokenizer = pickle.load(file)

with open('utils/label_encoder.pkl','rb') as file:
  label_encoder = pickle.load(file)
  
def infer_intent(text):
    nlu = IntentClassifier(classes,model,tokenizer,label_encoder)
    
    intent = nlu.get_intent(text)
    
    return intent