import pyaudio

p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    current = p.get_device_info_by_index(i)

    if current.get('maxInputChannels') > 0:
      print("THIS SOURCE IS A MICROPHONE")
      # print(f"Microphone: {current.get('name')} , Device Index: {current.get('index')}")
      # print(current)

    else:
       print("THIS IS A SOUND SOURCE")
       print(f"Source: {current.get('name')} , Device Index: {current.get('index')}")
       print(current)
    
    print("-----------------------------------------------------------------------------")