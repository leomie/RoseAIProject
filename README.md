# ROSE/LIA AI project (python) 

<img src="images/cover.webp" width="100%">

### Video Walkthrough:
(not coming soon)

### Details

Rose is a personal project 100% based in python, made for 3.9.9 but expected to work in newer versions out of the box.

Uses a combination of local and cloud resources to run, but it can be changed to run fully locally if you have the hardware to do so. Beware that using local resources can lead to increased or reduced latency depending on your hardware.

# Resources

### Backends 
<a href="https://github.com/oobabooga/text-generation-webui">Text-generation WebUI</a> 
by oobabooga

<a href="https://github.com/m-bain/whisperX/tree/main/whisperx">WhisperX</a> 
by M-bain

<a href="https://github.com/shashikg/WhisperS2T">WhisperS2T</a>
by Shashikg

<a href="https://github.com/Azure-Samples/cognitive-services-speech-sdk">Azure speech SDK</a> 
by Microsoft

<a href="https://github.com/pyannote/pyannote-audio">Pyannote-Audio</a> 
by Pyannote


### IMPORTANT!

WhisperX and WhisperS2T have been modified to allow IOBytes for audio proccesing, this allows for faster inferance.

By default this is not possible please check <a href="/images">this link</a> to see changes in detail.

Diarization (by pyannote) model is run fully locally please follow the steps found <a href="https://github.com/pyannote/pyannote-audio/blob/develop/tutorials/community/offline_usage_speaker_diarization.ipynb">here</a> to make this work by downloading the files from the hf repository.

Azure SDK needs an API-key to work, but you can fully drop in your TTS engine of choice and modify the text-generation webUI script in order to use it.
