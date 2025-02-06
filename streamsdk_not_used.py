import azure.cognitiveservices.speech as speechsdk
import re

# setup speech synthesizer
# IMPORTANT: MUST use the websocket v2 endpoint
speech_config = speechsdk.SpeechConfig(endpoint=f"wss://uksouth.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
                                       subscription='')

# Set audio output quality
speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
# Set a voice name
speech_config.speech_synthesis_voice_name = "en-US-JaneNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

speech_synthesizer.synthesizing.connect(lambda evt: print("[audio]", end=""))

# Function to handle streaming TTS requests
def stream_tts(text):
    """
    Streams text to Azure TTS and plays the synthesized speech.
    """

    # Create a new request for each session
    tts_request = speechsdk.SpeechSynthesisRequest(input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream)
    
    # Set custom voice pitch and rate
    tts_request.pitch = "+18.00%"
    tts_request.rate = "+12.00%"

    # Start the async TTS task
    tts_task = speech_synthesizer.speak_async(tts_request)

    # Stream text in chunks
    flag_detected = False
    chunk_counter = 0
    assistant_message_stream = ""

    for chunk in text:
        chunk_counter += 1
        assistant_message_stream += chunk

        print(assistant_message_stream)

        if not flag_detected and chunk_counter == 6:
            """
            We let the stream accumulate 6 chunks,
            this will allow us to have a streamlined system for processing.
            """
            match = re.search(r"\*fast\*", assistant_message_stream, re.IGNORECASE) # Check for flag ignoring capitalization
            if match:
                tts_request.rate = "+100.00%"
                flag_detected = True
                assistant_message_stream = re.sub(r"\*fast\*", "", assistant_message_stream, flags=re.IGNORECASE, count=1) # Remove flag
                      
        if chunk_counter > 6: 
            """
            We only write into input_stream once chunk_counter is greater than 6,
            ensuring all the flag checks have been completed.
            """
            tts_request.input_stream.write(assistant_message_stream)
            assistant_message_stream = ""

    # Close the TTS input stream to finalize processing
    tts_request.input_stream.close()

    # Wait for all audio bytes to be returned
    result = tts_task.get()

        
stream_tts("Hello, my name is Rose! Nice to meet you.")
stream_tts("*fast* This is a test of reusable TTS streaming.")
# stream_tts("Azure Speech SDK allows real-time text-to-speech conversion.")