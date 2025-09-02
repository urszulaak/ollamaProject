from datetime import datetime
from kivy.clock import Clock

class TimeUpdater:
    def __init__(self, target_label):
        self.target_label = target_label
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