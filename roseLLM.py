import requests
import sseclient 
import json
import urllib3
import re
import os
import asyncio
import azure.cognitiveservices.speech as speechsdk

from shared_flag import allowed_to_continue

# Loads API keys and is callable from other files that import * from this file.
from dotenv import load_dotenv
load_dotenv('.env')

urllib3.disable_warnings()

# setup speech synthesizer
# IMPORTANT: MUST use the websocket v2 endpoint or it wont work.
speech_config = speechsdk.SpeechConfig(endpoint=f"wss://uksouth.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                       subscription=os.getenv('AZURE_KEY'))

# Set audio output quality
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
# Set a voice name
speech_config.speech_synthesis_voice_name = "en-US-JaneNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
connection = speechsdk.Connection.from_speech_synthesizer(speech_synthesizer)

# LLM API endpoint
#url = "http://127.0.0.1:5000/v1/chat/completions" - FORMAT
url = "https://bpq4c3slm85ykg-5000.proxy.runpod.net/v1/chat/completions"


headers = {
    "Content-Type": "application/json"
}

history = []

async def print_response_stream(text):
    # LLM POST request
    history.append({"role": "user", "content": text})
    data = {
        "mode": "chat-instruct",
        "character": "Rose",
        "messages": history,
        "instruction_template": "",
        "stream": True,
        "present": "min_p",
        "chat_instruct_command": """You are <|character|>! Engage in a chat with user and provide a brief and simple response in a manner that is true to <|character|>'s personality, preferences, tone and language.

                                    Draw from <|character|>'s profile and stored knowledge for specific details about <|character|>'s appearance, style, diction, syntax, and backstory.

                                    Do not act, behave, or speak like an assistant and should never provide assistance of any sort as this is highly discouraged.

                                    <|prompt|>""",
        
        }
    
    stream_response = requests.post(url, headers=headers, json=data, verify=False, stream=True)
    client = sseclient.SSEClient(stream_response)

    flag_detected = False
    flag_checked = False
    assistant_message_stream = ""
    assistant_history = ""
    chunk_counter = 0
    
    for event in client.events():
        payload = json.loads(event.data)
        chunk = payload['choices'][0]['delta']['content']
        """
        Payload produces empty chunks at the begining and end of each stream
        so we only process chunks with content in them.
        """
        if chunk:
            chunk_counter += 1
            assistant_message_stream += chunk
            assistant_history += chunk

            if not flag_detected and chunk_counter == 3:
                match = re.search(r"\*fast\*", assistant_message_stream, re.IGNORECASE) # Check for flag ignoring capitalization
                if match:
                    flag_detected = True
                    assistant_message_stream = re.sub(r"\*fast\*", "", assistant_message_stream, flags=re.IGNORECASE, count=1)
                    print("-------FLAG DETECTED------")

                flag_checked = True # Ensures we checked for flags

            if chunk_counter == 3:
                """
                Streams from LLM to Azure TTS and plays the synthesized speech.
                We create the request after we checked for any flags.
                """

                # Create a new request for each session
                tts_request = speechsdk.SpeechSynthesisRequest(input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream)

                # Set custom voice pitch and rate
                tts_request.pitch = "+18.00%"
                tts_request.rate = "+100.00%" if flag_detected else "+12.00%"
                
                # Start the async TTS task
                tts_task = speech_synthesizer.speak_async(tts_request)
                
            if flag_checked and chunk_counter > 3:
                tts_request.input_stream.write(assistant_message_stream)
                assistant_message_stream = ""

    print("Rose said:", assistant_history)
    tts_request.input_stream.close()
    result = tts_task.get()

    print()
    history.append({"role": "assistant", "content": assistant_history})