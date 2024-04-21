import numpy as np
from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Bidirectional
import pickle
from tensorflow.keras.models import load_model

# Loading model files, getting initial NLU classes and filtering them within scope

class IntentClassifier:
    def __init__(self, classes, model, tokenizer, label_encoder):
        self.classes = classes
        self.classifier = model
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def get_intent(self, text):
        self.text = [text]
        self.test_keras = self.tokenizer.texts_to_sequences(self.text)
        self.test_keras_sequence = pad_sequences(
            self.test_keras, maxlen=16, padding="post"
        )
        self.pred = self.classifier.predict(self.test_keras_sequence)

        self.ls_out = []
        self.ls_pred = np.argsort(np.max(self.pred[:], axis=0))[-3:]

        return [self.label_encoder.inverse_transform([x])[0] for x in self.ls_pred]


model = load_model(
    "models/intents.h5", custom_objects={"Bidirectional": Bidirectional}, compile=False
)

with open("utils/classes.pkl", "rb") as file:
    classes = pickle.load(file)

with open("utils/tokenizer.pkl", "rb") as file:
    tokenizer = pickle.load(file)

with open("utils/label_encoder.pkl", "rb") as file:
    label_encoder = pickle.load(file)


def infer_intent(text):
    nlu = IntentClassifier(classes, model, tokenizer, label_encoder)

    intent = nlu.get_intent(text)

    return intent
