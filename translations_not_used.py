# from deep_translator import GoogleTranslator
# import re

# def TranslationsFinal(text, src, dest):
#     translated = GoogleTranslator(source=src, target=dest).translate(text)
#     translated_t = re.sub(r'\bRosa[.,!?]*\b', 'Rose', translated)
#     return translated_t

import googletrans
import re

translator = googletrans.Translator()

replacement_dict = {
    'Rosa': 'Rose',
    'transmisor': 'streamer',
    'transmisora': 'streamer',
    'amigo': 'güheon',
    'transmitiendo': 'stremeando',
    'aleatoria': 'random'
}

pattern = r'\b(?:' + '|'.join(re.escape(word) for word in replacement_dict.keys()) + r')[.,!?]*\b'

def TranslationsFinal(text, src, dest): #Some args were hardcoded into the funct
    translation = translator.translate(text, src=src, dest=dest)
    translation.text = re.sub(pattern, lambda match: replacement_dict[match.group(0)], translation.text)
    return translation.text