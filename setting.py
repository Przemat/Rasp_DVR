import io
from configparser import ConfigParser

global isAlert

class CommandLineParser:

    def __init__(self):
        global isAlert
        isAlert = False

        self.config = ConfigParser()
        self.config.read('/home/project/setting.ini')

    def get_video(self):
        return {'type': self.config.get('video','type'),
                'res': self.config.get('video','res'),
                'frame': self.config.get('video','frame'),
                'time': self.config.get('video','time')
                }
    def set_video(self, main):
        self.config.set('video', 'type', main.type_combobox.get())

        self.config.set('video', 'res', main.res_combobox.get())

        self.config.set('video', 'frame', main.frame_combobox.get())

        self.config.set('video', 'time', main.time_combobox.get())

