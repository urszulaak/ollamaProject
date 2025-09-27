from kivy.clock import Clock

class Updater:
    def __init__(self, interval, strategy=None):
        self.interval = interval
        self.strategy = strategy
        self.event = None

    def start(self):
        self._update(0)
        self.event = Clock.schedule_interval(self._update, self.interval)

    def stop(self):
        if self.event:
            self.event.cancel()
            self.event = None

    def _update(self, dt):
        if self.strategy:
            self.strategy()
        else:
            self.update(dt)

    def update(self, dt):
        pass