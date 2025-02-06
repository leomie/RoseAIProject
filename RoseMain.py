import time
import threading
import keyboard
import asyncio

from twitchio.channel import Channel
from twitchio.ext import commands

from RoseSTT import *
from TextOutput import *

# Other Values useful for general functioning
# left out as no necessary within functs
leer_active = False
rose_flag = True

class Bot(commands.Bot):
    history = list()

    def follower_detection():
        lista = []
        new_followers = []
        while True:
            try:
                with open("follower.txt", "r") as file:
                    content = file.read() # Leemos archivo
                    if not content: # Si archivo esta vacio...
                        continue

                    names = content.strip().split(" ")
                        
                    for name in names:
                        if name not in lista: # Comparamos lista de nombres en texto con lista de nombres procesados
                            new_followers.append(name)
                            lista.append(name)
                            
                            if len(lista) == 5:
                                lista = lista[5:]

                    if new_followers:
                        if len(new_followers) >= 2:
                            formatted_names = new_followers[:3]

                        if len(new_followers) == 1:
                            formatted_names = new_followers[:1]

                        reaction = ", ".join(formatted_names)
                        prompt = f"{reaction}, Gracias por el follow!"
                        print(prompt)
                        new_followers = [] # Limpia lista new_followers
                        time.sleep(10) # Damos tiempo a que lleguen followers
                    
            except  FileNotFoundError:
                print("no file found")
                pass

    # Iniciamos la detectecion de un nuevo follower
    # Cuando se detecta el archivo accedemos a el y mandamos el resultado al queue
    follower_thread = threading.Thread(target=follower_detection).start()

    def leer():  # Funcion que captura el microfono y genera respuesta
        global leer_active
        global rose_flag

        while True:
            connection.open(True)
            if leer_active is True:       
                try:
                        mic_input()
                        # print("")
                except:
                    print("Error en el recognizer...")
            else:
                time.sleep(1)

    #Iniciamos el thread encargado de procesar voz
    voice1_thread = threading.Thread(target=leer).start()

    def Rose_independant():
        global rose_flag
        
        timer_check = None

        while True:

            if rose_flag:
                timer_check = None
                time.sleep(2)

            else:
                if timer_check is None:
                    timer_check = time.time()
                else:
                    if time.time() - timer_check >= 15:
                        interact = "continue"
                        ###asyncio.run(print_response_stream(interact)) # Respuesta de Rose
                        timer_check = None
                        time.sleep(1)

    #Iniciamos thread que interactua independientemente tras 8 segundos de inactividad
    rose_thread = threading.Thread(target=Rose_independant).start()

    ###Seccion de threats termina aqui, pasamos a seccion de chat###

    def __init__(self):
        super().__init__(token=os.getenv('TWITCH_TOKEN'), prefix='?', initial_channels=['ldeleou'])
        self.mensajes_active = True

    def handle_key_press(self, event):  # Funcion que controla que tecla usaras para activar el microfono
        global leer_active
        global rose_flag

        if event.name == '[':
            if rose_flag:
                rose_flag = False
            else:
                rose_flag = True

        if event.name == ']':
            if leer_active:
                leer_active = False
                print("Mic off")
            else:
                leer_active = True
                print("Mic on")

        if event.name == '#':
            if self.mensajes_active:
                self.mensajes_active = False
                print("Rose no esta leyendo el chat")
            else:
                self.mensajes_active = True
                print("Rose esta leyendo el chat")

    async def event_ready(self):  #funcion que inicia el bot e inicia funcion leer()
        print(f'Logeado con exito al canal | {self.nick}')

    async def event_message(self, message):  #detecta el evento de mesajes en el chat de twitch y genera respuestas
        global rose_flag

        #rose_flag = True

        if self.mensajes_active == False: #Detecta flag de activacion para leer el chat
            return
        if message.echo: #No responde a si misma
            return
        
        if len(message.content) > 80:   #\
            return                      # longitud de mensaje
        if len(message.content) == 1:   #/
            return
        
        print('----------------------NUEVO CHAT-----------------------------------')
        
        #Recibimos el mensaje de twitch y lo mandamos al LLM
        print(message.author.name + ": " + message.content)
        content = message.content.encode(encoding='ASCII',errors='ignore').decode()
        # new_content = message.author.name + ": " + TranslationsFinal(content, "es", "en") # Traducimos mensaje del chat a ingles
        
        ###await print_response_stream(new_content) # Respuesta de Rose/mandamos pregunta al LLM
        
        print('----------------------FIN DEL CHAT--------------------------------')
        time.sleep(4)
        #rose_flag = False
        
        await self.handle_commands(message)

    def run_with_keyboard_input(self):  #funcion que inicia el bot con la funcion de tecla
        keyboard.on_press(self.handle_key_press)
        self.run()



bot = Bot()
bot.run_with_keyboard_input()


   