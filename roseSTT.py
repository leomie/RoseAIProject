import whisper_s2t
import time
import concurrent.futures
import pyaudio
import wave
import numpy as np
import io
import asyncio

from roseLLM import *
from io import BytesIO
from whisperx import alignment, diarize
from shared_flag import allowed_to_continue

# Transcriber settings
device = 'cuda'
computetype = 'int8'
batch_size = 16

# VAD settings
lang_codes = ['en']
tasks = ['transcribe']
initial_prompts = [None]

# Loads trasncriber model
model = whisper_s2t.load_model(model_identifier="distil-small.en", 
                               backend='CTranslate2',
                               device=device, 
                               compute_type=computetype, 
                               )
# Loads alignment model
model_a, metadata = alignment.load_align_model(language_code="en", device=device)
# Loads diarization pipeline
diarize_model = diarize.DiarizationPipeline(device=device)

# Executors
def run_alignment(out, model_a, metadata, audio_file, device):
        return alignment.align(out , model_a, metadata, audio_file, device, return_char_alignments=False)

def run_diarization(audio):
        return diarize_model(audio)

def transcriber(audio):
    audio_in_memory = [audio]
    start = time.time()

    out = model.transcribe_with_vad(audio_in_memory,
                                    lang_codes=lang_codes,
                                    tasks=tasks,
                                    initial_prompts=initial_prompts,
                                    batch_size=batch_size)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_alignment = executor.submit(run_alignment, out[0], model_a, metadata, audio, device)

        audio_copy = BytesIO(audio.getvalue())
        future_diari = executor.submit(run_diarization, audio_copy)
        try:
            result = future_alignment.result()
            diarize_segments = future_diari.result()

            
        except Exception as e:
            print(f"Error occurred: {e}")

    new_result = diarize.assign_word_speakers(diarize_segments, result)

    # Assigns contents into an empty dictionary for manipulation
    speaker_transcriptions = []
    for segment in new_result['segments']:
        speaker = segment['speaker']
        text = segment['text']
        
        # if speaker not in speaker_transcriptions:
        speaker_transcriptions.append(f"{speaker}: {text}")

    output = "\n".join(speaker_transcriptions) # After second change
    end = time.time()   
    print(f"Time taken: {end-start} seconds")
    
    asyncio.run(print_response_stream(output))
    # print(output)


# Initialize PyAudio stream settings
chunk = 512
format = pyaudio.paInt16
channels = 1
rate = 16000


# Noise threshold for silence detection
silence_threshold = 600
max_silent_chunks = 40

p = pyaudio.PyAudio()
stream = p.open(format=format,
            channels=channels,
            rate=rate,
            input=True,
            # input_device_index=4,
            frames_per_buffer=chunk)

def mic_input():
    global allowed_to_continue

    frames = []
    silent_chunk_count = 0
    significant_audio_detected = False
    print("Recording...")

    try:
        while True:
            data = stream.read(chunk)
            frames.append(data)

            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.abs(audio_data).mean()

            if amplitude > silence_threshold:
                significant_audio_detected = True
                silent_chunk_count = 0
                # Set flag to false when we speak again
                with allowed_to_continue.get_lock():
                    allowed_to_continue.value = False
            else:
                silent_chunk_count += 1

            if silent_chunk_count > max_silent_chunks:
                print("Finished recording")
                break
    except:
        print("Error in the recording")

    if significant_audio_detected == True:
        audio_buffer = io.BytesIO()

        with wave.open(audio_buffer, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

        audio_buffer.seek(0)
        
        # Change the flag back to True in order to enable new voice output
        with allowed_to_continue.get_lock():
            allowed_to_continue.value = True

        transcriber(audio_buffer)

        
  
    else:
        print("No significant audio detected")

# while True:
#     mic_input()
#     time.sleep(1)
