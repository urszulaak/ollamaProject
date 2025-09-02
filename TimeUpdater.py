from datetime import datetime
from kivy.clock import Clock

CLOCK_EMOJIS = {
    "00:00": "🕛", "12:00": "🕛", "01:00": "🕐", "02:00": "🕑", "03:00": "🕒",
    "04:00": "🕓", "05:00": "🕔", "06:00": "🕕", "07:00": "🕖", "08:00": "🕗",
    "09:00": "🕘", "10:00": "🕙", "11:00": "🕚",
    "00:30": "🕧", "12:30": "🕧", "01:30": "🕜", "02:30": "🕝", "03:30": "🕞",
    "04:30": "🕟", "05:30": "🕠", "06:30": "🕡", "07:30": "🕢", "08:30": "🕣",
    "09:30": "🕤", "10:30": "🕥", "11:30": "🕦"
}

class TimeUpdater:
    def __init__(self, target_label, clock_label):
        self.target_label = target_label
        self.clock_label = clock_label
        self.event = None

    def start(self):
        self.update_time(0)
        self.event = Clock.schedule_interval(self.update_time, 60)

    def stop(self):
        if self.event:
            self.event.cancel
            self.event = None

    def update_time(self, dt):
        now = datetime.now()
        formatted = now.strftime("%d.%m.%Y \n%H:%M")
        self.target_label.text = formatted
        hour = now.hour % 12
        if hour == 0:
            hour = 12
        minute = now.minute

        key = f"{hour:02d}:{'30' if minute >= 30 else '00'}"
        emoji = CLOCK_EMOJIS.get(key, "🕛")
        self.clock_label.text = emoji
