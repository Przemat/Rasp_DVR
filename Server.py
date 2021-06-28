import time
from shutil import copyfile

import requests
import setting

class Server:
    def __init__(self):
        self.token = None
        self.note_id = None
        self.setting = setting.CommandLineParser()
    async def get_token(self, pin):
        url = "http://example.com/DVR/pin/"

        payload = {'pin': int(pin['text'])}
        files = [
        ]
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload, files=files)

        if response.status_code == 200:
            pin['text'] = 'Połączono'
        else:
            pin['text'] = 'Błąd'

        self.token = response.json()['token']



    async def notification(self, file, path, notify_type=""):
        if self.token is not None:
            url = "http://example.com/DVR/notifications/"

            payload = {'type': notify_type}
            files = [
                (
                'img', (file, open(path, 'rb'), 'image/png'))
            ]
            headers = {
                'Authorization': 'Token '+self.token,
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            print(response.text)

            self.note_id = response.json()['id']
    async def video(self, file, stime):
        if self.token is not None:
            if "video" in file:
                item = file.split('/')[-1]
            else:
                item=file
                copyfile(file, '/home/project/video/'+file)
                print("Czas oczekiwania"+str(35-stime))
                time.sleep(int(self.setting.get_video()['time'])-stime)
            url = "http://example.com/DVR/video/"
            payload = {}
            files = [
                ('file',
                (item, open(file, 'rb'), 'application/octet-stream'))
            ]
            headers = {
                'Authorization': 'Token '+self.token,
            }

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            print(response.text)
            if self.note_id != None:

                url = "http://example.com/DVR/notifications/"

                payload = {'id': self.note_id, 'path_id': response.json()['id']}
                files = [

                ]
                headers = {
                    'Authorization': 'Token '+self.token,
                }

                response = requests.request("PUT", url, headers=headers, data=payload, files=files)

                print(response.status_code)

                self.note_id = None
