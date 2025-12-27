import time
import httpx
import json
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor

class WeatherPanel:
    def __init__(self, city, language):
        with open("APIKeys.json", "r") as f:
            apikeys = json.load(f)
        self.city = city
        self.language = language
        self.API_KEY = apikeys["WeatherAPI"]

        self._last_fetch = 0
        self._cached_data = None

        self.executor = ThreadPoolExecutor(max_workers=1)

    async def getweather(self) -> list:
        placeholder = []
        DAYS_POLISH_TRANSLATIONS = {
            'Monday': 'Poniedziałek',
            'Tuesday': 'Wtorek',
            'Wednesday': 'Środa',
            'Thursday': 'Czwartek',
            'Friday': 'Piątek',
            'Saturday': 'Sobota',
            'Sunday': 'Niedziela'
        }

        url = 'http://api.weatherapi.com/v1/forecast.json'
        params = {
            'key': self.API_KEY,
            'q': self.city,
            'days': 3,
            'lang': self.language,
            'aqi': 'no',
            'alerts': 'no'
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)

                response.raise_for_status()
                data = response.json()

                current = data['current']
                forecast = data['forecast']['forecastday']

                placeholder.append(self._map_condition_to_emoji(current['condition']['text']))
                placeholder.append(f"{current['temp_c']}°C")
                placeholder.append(f"{current['condition']['text']}")

                for day_data in forecast:
                    date_obj = datetime.strptime(day_data['date'], '%Y-%m-%d')
                    day_name = date_obj.strftime('%A')

                    if self.language == 'pl':
                        placeholder.append(DAYS_POLISH_TRANSLATIONS.get(day_name, day_name))
                    else:
                        placeholder.append(day_name)

                    condition = day_data['day']['condition']
                    description = condition['text']

                    max_temp = day_data['day']['maxtemp_c']
                    min_temp = day_data['day']['mintemp_c']

                    emoji_char = self._map_condition_to_emoji(description)

                    placeholder.append(emoji_char)
                    placeholder.append(description)
                    placeholder.append(f'{min_temp} °C / {max_temp} °C')
            return placeholder
        
        except httpx.RequestError:
            return None

    def _map_condition_to_emoji(self, description):
        mapping_pl = {
            'Słonecznie': '☀️',
            'Bezchmurnie': '☀️',
            'Częściowe zachmurzenie': '⛅️',
            'Pochmurno': '☁️',
            'Zachmurzenie całkowite': '☁️',
            'Zachmurzenie': '☁️',
            'Mgła': '🌫',
            'Zamglenie': '🌫',
            'Możliwe miejscowe opady deszczu': '🌦',
            'Miejscowe opady deszczu w pobliżu': '🌦',
            'Lekki deszcz': '🌦',
            'Umiarkowany deszcz': '🌧',
            'Silny deszcz': '🌧',
            'Możliwe miejscowe opady śniegu': '🌨',
            'Wiatr ze śniegiem': '🌨',
            'Lekki śnieg': '🌨',
            'Średnie opady śniegu': '🌨',
            'Silny śnieg': '❄️',
            'Możliwe miejscowe burze': '⛈',
            'Umiarkowany lub silny deszcz z burzą': '⛈',
            'Miejscowy lekki deszcz z burzą': '⛈'
        }
        mapping_en = {
            'Sunny': '☀️',
            'Clear': '☀️',
            'Partly Cloudy': '⛅️',
            'Cloudy': '☁️',
            'Overcast': '☁️',
            'Mist': '🌫',
            'Patchy rain possible': '🌦',
            'Patchy rain nearby': '🌦',
            'Light rain': '🌦',
            'Moderate rain': '🌧',
            'Heavy rain': '🌧',
            'Patchy snow possible': '🌨',
            'Light snow': '🌨',
            'Moderate snow': '❄️',
            'Heavy snow': '❄️',
            'Thundery outbreaks possible': '⛈',
            'Moderate or heavy rain with thunder': '⛈',
            'Patchy light rain with thunder': '⛈'
        }
        mapping = mapping_pl if self.language == 'pl' else mapping_en
        return mapping.get(description, '✨')

    def fetch_weather(self):
        if time.time() - self._last_fetch < 600 and self._cached_data:
            return self._cached_data

        loop = asyncio.new_event_loop()
        future = self.executor.submit(loop.run_until_complete, self.getweather())
        self._cached_data = future.result()
        self._last_fetch = time.time()
        return self._cached_data
    

(venv) student@j4012:~/Temp/ollamaProject$ python MainApp.py
[INFO   ] [Logger      ] Record log in /home/student/.kivy/logs/kivy_25-12-27_19.txt
[INFO   ] [Kivy        ] v2.3.1
[INFO   ] [Kivy        ] Installed at "/home/student/Temp/ollamaProject/venv/lib/python3.10/site-packages/kivy/__init__.py"
[INFO   ] [Python      ] v3.10.12 (main, Nov  4 2025, 08:48:33) [GCC 11.4.0]
[INFO   ] [Python      ] Interpreter at "/home/student/Temp/ollamaProject/venv/bin/python"
[INFO   ] [Logger      ] Purge log fired. Processing...
[INFO   ] [Logger      ] Purge finished!
[INFO   ] [Factory     ] 195 symbols loaded
[INFO   ] [Image       ] Providers: img_tex, img_dds, img_sdl2 (img_pil, img_ffpyplayer ignored)
[INFO   ] [Text        ] Provider: sdl2
[INFO   ] [Window      ] Provider: sdl2
[INFO   ] [GL          ] Using the "OpenGL" graphics system
[INFO   ] [GL          ] Backend used <sdl2>
[INFO   ] [GL          ] OpenGL version <b'4.6.0 NVIDIA 540.3.0'>
[INFO   ] [GL          ] OpenGL vendor <b'NVIDIA Corporation'>
[INFO   ] [GL          ] OpenGL renderer <b'NVIDIA Tegra Orin (nvgpu)/integrated'>
[INFO   ] [GL          ] OpenGL parsed version: 4, 6
[INFO   ] [GL          ] Shading version <b'4.60 NVIDIA'>
[INFO   ] [GL          ] Texture max size <32768>
[INFO   ] [GL          ] Texture max units <32>
[INFO   ] [Window      ] auto add sdl2 input provider
[INFO   ] [Window      ] virtual keyboard not allowed, single mode, not docked
[INFO   ] [GL          ] NPOT texture support is available
[INFO   ] [Base        ] Start application main loop
LOG (VoskAPI:ReadDataFiles():model.cc:213) Decoding params beam=10 max-active=3000 lattice-beam=2
LOG (VoskAPI:ReadDataFiles():model.cc:216) Silence phones 1:2:3:4:5:6:7:8:9:10
LOG (VoskAPI:RemoveOrphanNodes():nnet-nnet.cc:948) Removed 0 orphan nodes.
LOG (VoskAPI:RemoveOrphanComponents():nnet-nnet.cc:847) Removing 0 orphan components.
LOG (VoskAPI:ReadDataFiles():model.cc:248) Loading i-vector extractor from vosk-model-small-pl-0.22/ivector/final.ie
LOG (VoskAPI:ComputeDerivedVars():ivector-extractor.cc:183) Computing derived variables for iVector extractor
LOG (VoskAPI:ComputeDerivedVars():ivector-extractor.cc:204) Done.
LOG (VoskAPI:ReadDataFiles():model.cc:282) Loading HCL and G from vosk-model-small-pl-0.22/graph/HCLr.fst vosk-model-small-pl-0.22/graph/Gr.fst
LOG (VoskAPI:ReadDataFiles():model.cc:308) Loading winfo vosk-model-small-pl-0.22/graph/phones/word_boundary.int
ALSA lib pcm_dsnoop.c:601:(snd_pcm_dsnoop_open) unable to open slave
ALSA lib pcm_dmix.c:1032:(snd_pcm_dmix_open) unable to open slave
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.rear
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.center_lfe
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.side
ALSA lib confmisc.c:1369:(snd_func_refer) Unable to find definition 'cards.0.pcm.hdmi.0:CARD=0,AES0=4,AES1=130,AES2=0,AES3=2'
ALSA lib conf.c:5178:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
ALSA lib conf.c:5701:(snd_config_expand) Evaluate error: No such file or directory
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM hdmi
ALSA lib confmisc.c:1369:(snd_func_refer) Unable to find definition 'cards.0.pcm.hdmi.0:CARD=0,AES0=4,AES1=130,AES2=0,AES3=2'
ALSA lib conf.c:5178:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
ALSA lib conf.c:5701:(snd_config_expand) Evaluate error: No such file or directory
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM hdmi
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.modem
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.modem
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.phoneline
ALSA lib pcm.c:2664:(snd_pcm_open_noupdate) Unknown PCM cards.pcm.phoneline
ALSA lib pcm_oss.c:397:(_snd_pcm_oss_open) Cannot open device /dev/dsp
ALSA lib pcm_oss.c:397:(_snd_pcm_oss_open) Cannot open device /dev/dsp
ALSA lib confmisc.c:160:(snd_config_get_card) Invalid field card
ALSA lib pcm_usb_stream.c:482:(_snd_pcm_usb_stream_open) Invalid card 'card'
ALSA lib confmisc.c:160:(snd_config_get_card) Invalid field card
ALSA lib pcm_usb_stream.c:482:(_snd_pcm_usb_stream_open) Invalid card 'card'
ALSA lib pcm_dmix.c:1005:(snd_pcm_dmix_open) The dmix plugin supports only playback stream
ALSA lib pcm_dmix.c:1032:(snd_pcm_dmix_open) unable to open slave
[DEBUG  ] [Using selector] EpollSelector
[DEBUG  ] connect_tcp.started host='api.weatherapi.com' port=80 local_address=None timeout=5.0 socket_options=None
[DEBUG  ] connect_tcp.failed exception=ConnectError(gaierror(-3, 'Temporary failure in name resolution'))
LOG (VoskAPI:UpdateGrammarFst():recognizer.cc:287) ["start", "stop", "end", "koniec", "weather", "whether", "pogoda", "wiadomo\\u015bci", "news", "rozwi\\u0144", "expand", "nast\\u0119pna", "next", "poprzednia", "previous", "[unk]"]
WARNING (VoskAPI:UpdateGrammarFst():recognizer.cc:308) Ignoring word missing in vocabulary: 'weather'
WARNING (VoskAPI:UpdateGrammarFst():recognizer.cc:308) Ignoring word missing in vocabulary: 'whether'
WARNING (VoskAPI:UpdateGrammarFst():recognizer.cc:308) Ignoring word missing in vocabulary: 'wiadomo\\u015bci'
WARNING (VoskAPI:UpdateGrammarFst():recognizer.cc:308) Ignoring word missing in vocabulary: 'rozwi\\u0144'
WARNING (VoskAPI:UpdateGrammarFst():recognizer.cc:308) Ignoring word missing in vocabulary: 'nast\\u0119pna'
LOG (VoskAPI:Estimate():language_model.cc:142) Estimating language model with ngram-order=2, discount=0.5
LOG (VoskAPI:OutputToFst():language_model.cc:209) Created language model with 12 states and 22 arcs.