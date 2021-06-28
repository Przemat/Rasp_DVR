# -*- coding: utf-8 -*-
import fnmatch
import subprocess
import time

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import cv2
from PIL import Image, ImageTk
import datetime as dt
import os
import asyncio
import threading
from pijuice import PiJuice  # Import pijuice module

import setting
from Detecting import Detecting
from Server import Server
from VideoCapture import VideoCapture
from player import PyPlayer
from Obd import OBD


class App:
    def __init__(self, window, video_source=0):

        self.window = window
        self.fullScreenState = False
        self.video_source = video_source
        # Tryby
        self.is_menu = False
        self.is_obd = False
        self.is_view = False

        # Wczytanie źródła sygnału
        self.obd= OBD()
        self.setting = setting.CommandLineParser()
        self.vid = VideoCapture(self.video_source)
        self.det = Detecting()
        self.server = Server()

        self.type = ""

        # Pętle asynchroniczne
        self.event_loop_capturing = asyncio.new_event_loop()
        self.event_loop_recording = asyncio.new_event_loop()
        self.event_loop_detecting = asyncio.new_event_loop()
        self.event_loop_notification = asyncio.new_event_loop()
        self.event_loop_video = asyncio.new_event_loop()
        self.event_loop_object = asyncio.new_event_loop()
        self.event_loop_obd = asyncio.new_event_loop()

        # Definiowanie pobierania obrazu z kamery
        try:
            capturing = threading.Thread(target=self.capturing_start, args=(self.event_loop_capturing,), daemon=True)
        finally:
            capturing.start()

        # USP PiJuice
        self.pijuice = PiJuice(1, 0x14)  # Instantiate PiJuice interface object

        # Panel wyświetlacza
        self.canvas = tk.Canvas(self.window, width=700, height=480)
        self.canvas.pack(anchor=tk.NE)

        # Menu logowania
        self.login_canvas = tk.Canvas(self.window, width=350, height=240, background='#444444')
        self.login_frame = ttk.Frame(self.window)
        self.login_canvas.create_window(175, 120, anchor='center', window=self.login_frame)
        self.login_entry = ttk.Label(self.login_frame, font=("Calibri", 20))
        self.login_entry.grid(row=0, column=0, columnspan=3)
        self.login_button_0 = ttk.Button(self.login_frame, text="0", command=(lambda: self.write_pin('0'))).grid(row=4,column=1)
        self.login_button_1 = ttk.Button(self.login_frame, text="1", command=(lambda: self.write_pin('1'))).grid(row=1,column=0)
        self.login_button_2 = ttk.Button(self.login_frame, text="2", command=(lambda: self.write_pin('2'))).grid(row=1,column=1)
        self.login_button_3 = ttk.Button(self.login_frame, text="3", command=(lambda: self.write_pin('3'))).grid(row=1,column=2)
        self.login_button_4 = ttk.Button(self.login_frame, text="4", command=(lambda: self.write_pin('4'))).grid(row=2,column=0)
        self.login_button_5 = ttk.Button(self.login_frame, text="5", command=(lambda: self.write_pin('5'))).grid(row=2,column=1)
        self.login_button_6 = ttk.Button(self.login_frame, text="6", command=(lambda: self.write_pin('6'))).grid(row=2,column=2)
        self.login_button_7 = ttk.Button(self.login_frame, text="7", command=(lambda: self.write_pin('7'))).grid(row=3,column=0)
        self.login_button_8 = ttk.Button(self.login_frame, text="8", command=(lambda: self.write_pin('8'))).grid(row=3,column=1)
        self.login_button_9 = ttk.Button(self.login_frame, text="9", command=(lambda: self.write_pin('9'))).grid(row=3,column=2)
        self.login_button_rm = ttk.Button(self.login_frame, text="Usuń", command=(lambda: self.remove_pin())).grid(row=4,column=0)
        self.login_button_con = ttk.Button(self.login_frame, text="Połącz", command=(lambda: self.get_token())).grid(row=4,column=2)

        self.login_frame = ttk.Frame(self.window)
        self.login_canvas.create_window(175, 120, anchor='center', window=self.login_frame)
        self.logged_entry = ttk.Label(self.login_frame, font=("Calibri", 20))
        self.logged_entry.grid(row=0, column=0, columnspan=3)


        # Menu ustawień
        self.setting_canvas = tk.Canvas(self.window, width=700, height=240, background='#444444')
        self.setting_frame = ttk.Frame(self.window)
        self.setting_canvas.create_window(350, 120, anchor='center', window=self.setting_frame)
        self.type_label = ttk.Label(self.setting_frame, text="Format", font=("Calibri", 20)).grid(row=0, column=0, sticky='nsew')
        self.type_combobox = ttk.Combobox(self.setting_frame, font=("Calibri", 15), values=[
            "avi",
            "mp4"
        ])
        self.type_combobox.grid(row=1, column=0, sticky='nsew')
        self.type_combobox.current(self.type_combobox['values'].index(self.setting.get_video()['type']))
        self.res_label = ttk.Label(self.setting_frame, text="Rozdzielczość", font=("Calibri", 20)).grid(row=2, column=0, sticky='nsew')
        self.res_combobox = ttk.Combobox(self.setting_frame, font=("Calibri", 15), values=[
            "480p",
            "720p",
            "1080p",
            "4k"
        ])
        self.res_combobox.grid(row=3, column=0, sticky='nsew')
        self.res_combobox.current(self.res_combobox['values'].index(self.setting.get_video()['res']))
        self.frame_label = ttk.Label(self.setting_frame, text="Ilość klatek", font=("Calibri", 20)).grid(row=0, column=1, sticky='nsew')
        self.frame_combobox = ttk.Combobox(self.setting_frame, font=("Calibri", 15), values=[
            "25",
            "30"
        ])
        self.frame_combobox.grid(row=1, column=1, sticky='nsew')
        self.frame_combobox.current(self.frame_combobox['values'].index(self.setting.get_video()['frame']))
        self.time_label = ttk.Label(self.setting_frame, text="Długość nagrania", font=("Calibri", 20)).grid(row=2, column=1, sticky='nsew')
        self.time_combobox = ttk.Combobox(self.setting_frame, font=("Calibri", 15), values=[
            "2min",
            "5min",
            "10min"
        ])
        self.time_combobox.grid(row=3, column=1, sticky='nsew')
        self.time_combobox.current(self.time_combobox['values'].index(self.setting.get_video()['time']+"min"))
        self.setting_button = ttk.Button(self.setting_frame, text="Zapisz", command=lambda: self.setting.set_video(self))
        self.setting_button.grid(row=4, column=0, columnspan=2)

        # Podgląd nagrań
        self.list_canvas = tk.Canvas(self.window, width=200, height=480, background='#444444')
        self.list_frame = ttk.Frame(self.window)
        self.list_canvas.create_window(0, 0, anchor='nw', window=self.list_frame)
        self.list_label = ttk.Label(self.list_frame, text="Nagrania zwykłe")
        self.list_label.grid(row=0, column=0)
        self.list_listbox = tk.Listbox(self.list_frame, background='#444444')
        self.list_listbox.grid(row=1, column=0, sticky='ne')
        self.list_scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.list_listbox.yview)
        self.list_scrollbar.grid(row=1, column=1, sticky='ns')
        self.list_listbox.config(yscrollcommand=self.list_scrollbar.set)
        self.list_button = ttk.Button(self.list_frame, text="Odtwórz", command=lambda: self.play_video(False))
        self.list_button.grid(row=2, column=0)

        self.prot_label = ttk.Label(self.list_frame, text="Nagrania zdarzeń")
        self.prot_label.grid(row=3, column=0)
        self.prot_listbox = tk.Listbox(self.list_frame, background='#444444')
        self.prot_listbox.grid(row=4, column=0, sticky='ne')
        self.prot_scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.list_listbox.yview)
        self.prot_scrollbar.grid(row=4, column=1, sticky='ns')
        self.prot_listbox.config(yscrollcommand=self.list_scrollbar.set)
        self.prot_button = ttk.Button(self.list_frame, text="Odtwórz", command=lambda: self.play_video(True))
        self.prot_button.grid(row=5, column=0)

        self.view_canvas = tk.Canvas(self.window, width=500, height=480, background='#444444')
        self.player = PyPlayer(self.view_canvas)
        # Obd
        self.obd_canvas = tk.Canvas(self.window, width=350, height=240, background='#444444')
        self.obd_frame = ttk.Frame(self.window)
        self.obd_canvas.create_window(175, 120, anchor='center', window=self.obd_frame)
        self.status_canvas = tk.Canvas(self.window, width=700, height=240, background='#444444')
        self.status_frame = ttk.Frame(self.window)
        self.status_canvas.create_window(350, 120, anchor='center', window=self.status_frame)

        self.obd_title_status = ttk.Label(self.obd_frame, text="Połączenie: ", font=("Calibri", 15))
        self.obd_title_status.grid(row=0, column=0, sticky="nsew")
        self.obd_value_status = ttk.Label(self.obd_frame, font=("Calibri", 15))
        self.obd_value_status.grid(row=0, column=1, sticky="nsew")
        self.obd_value_status.config(text="Brak połączenia")

        self.obd_title_speed = ttk.Label(self.status_frame, text="Prędkość: ", font=("Calibri", 15))
        self.obd_title_speed.grid(row=0, column=0, sticky="nsew")
        self.obd_value_speed = ttk.Label(self.status_frame, font=("Calibri", 30))
        self.obd_value_speed.grid(row=1, column=0, sticky="nsew")
        self.obd_title_rpm = ttk.Label(self.status_frame, text="Obroty: ", font=("Calibri", 15))
        self.obd_title_rpm.grid(row=2, column=0, sticky="nsew")
        self.obd_value_rpm = ttk.Label(self.status_frame, font=("Calibri", 30))
        self.obd_value_rpm.grid(row=3, column=0, sticky="nsew")
        self.obd_title_el = ttk.Label(self.status_frame, text="Obciążenie silnika: ", font=("Calibri", 15))
        self.obd_title_el.grid(row=0, column=1, sticky="nsew")
        self.obd_value_el = ttk.Label(self.status_frame, font=("Calibri", 30))
        self.obd_value_el.grid(row=1, column=1, sticky="nsew")
        self.obd_title_coolant_temp = ttk.Label(self.status_frame, text="Temperatura płynu chłodzącego: ", font=("Calibri", 15))
        self.obd_title_coolant_temp.grid(row=2, column=1, sticky="nsew")
        self.obd_value_coolant_temp = ttk.Label(self.status_frame, font=("Calibri", 30))
        self.obd_value_coolant_temp.grid(row=3, column=1, sticky="nsew")
        self.error_label = ttk.Label(self.status_frame, text="Kody błędów")
        self.error_label.grid(row=0, column=2)
        self.error_listbox = tk.Listbox(self.status_frame, background='#444444')
        self.error_listbox.grid(row=1, column=2, rowspan=3, sticky='ne')

        # Przyciski
        # Nagrywanie
        self.rec_on = tk.PhotoImage(file='/home/project/icons/rec_on.png')
        self.rec_off = tk.PhotoImage(file='/home/project/icons/rec_off.png')
        self.btn_rec = ttk.Button(self.window, command=lambda: self.recording_thread())
        self.btn_rec.config(image=self.rec_on)
        self.btn_rec.pack(side=tk.LEFT)
        self.btn_rec.place(height=100, width=100)

        self.time_label = ttk.Label(self.window, justify=tk.CENTER, foreground="red", anchor="center", text="test")
        self.time_label.pack(side=tk.LEFT)
        self.time_label.place(width=100, height=40, y=100)
        # Zdarzenie
        self.alert_ico = tk.PhotoImage(file='/home/project/icons/alert.png')
        self.btn_alert = ttk.Button(self.window, command=lambda: self.send_video_thread(self.vid.path))
        self.btn_alert.config(image=self.alert_ico)
        self.btn_alert.pack(side=tk.LEFT)
        self.btn_alert.place(width=100, height=100, y=380)
        # Menu
        self.btn_menu = ttk.Button(self.window, text="MENU", command=lambda: self.menu_screen())
        self.btn_menu.pack(side=tk.LEFT)
        self.btn_menu.place(height=80, width=100, y=140)
        # Nagrania
        self.btn_view = ttk.Button(self.window, text="NAGRANIA", command=lambda: self.view_screen())
        self.btn_view.pack(side=tk.LEFT)
        self.btn_view.place(height=80, width=100, y=220)
        # Panel OBD
        self.btn_obd = ttk.Button(self.window, text="OBD", command=lambda: self.obd_screen())
        self.btn_obd.pack(side=tk.LEFT)
        self.btn_obd.place(height=80, width=100, y=300)
        # Zaczęcie nagrywania
        self.recording_thread()
        self.obd_thread()
        # Pętla
        self.delay = 10
        self.update()
        self.window.mainloop()

    def menu_screen(self):
        if self.is_menu:
            self.canvas.config(width=700, height=480)
            self.is_menu = False
            self.login_canvas.place_forget()
            self.setting_canvas.place_forget()
        else:
            self.is_obd = False
            self.is_view = False
            self.is_menu = True
            self.list_canvas.place_forget()
            self.view_canvas.place_forget()
            self.obd_canvas.place_forget()
            self.status_canvas.place_forget()

            self.canvas.config(width=350, height=240)
            self.login_canvas.pack()
            self.login_canvas.place(x=100, y=0)
            self.setting_canvas.pack()
            self.setting_canvas.place(x=100, y=240)

    def write_pin(self, num):
        if len(self.login_entry['text'])<6:
            self.login_entry['text']+=num

    def remove_pin(self):
        if len(self.login_entry['text'])>0:
            self.login_entry['text']= self.login_entry['text'][:-1]

    def get_token(self):
        thread = threading.Thread(target=self.token_start, args=(self.event_loop_detecting,), daemon=True)
        thread.start()

    def token_start(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.server.get_token(self.login_entry))

    def view_screen(self):
        if self.is_view:
            self.is_view = False
            self.list_canvas.place_forget()
            self.view_canvas.place_forget()
        else:
            self.is_menu = False
            self.is_obd = False
            self.is_view = True
            self.login_canvas.place_forget()
            self.setting_canvas.place_forget()
            self.obd_canvas.place_forget()
            self.status_canvas.place_forget()

            self.canvas.config(width=700, height=480)
            self.list_canvas.pack()
            self.list_canvas.place(x=100, y=0)
            self.view_canvas.pack()
            self.view_canvas.place(x=300, y=0)
            listOfFiles = os.listdir('/home/project')
            listOfFiles.sort(reverse=True)
            self.list_listbox.delete(0, 'end')
            for entry in listOfFiles:
                if fnmatch.fnmatch(entry, "*.avi") or fnmatch.fnmatch(entry, "*.mp4"):
                    self.list_listbox.insert('end', entry)
            listOfVideo = os.listdir('/home/project/video')
            listOfVideo.sort(reverse=True)
            self.prot_listbox.delete(0, 'end')
            for entry in listOfVideo:
                if fnmatch.fnmatch(entry, "*.avi") or fnmatch.fnmatch(entry, "*.mp4"):
                    self.prot_listbox.insert('end', entry)

    def play_video(self, dir):
        if dir:
            clicked_file = self.prot_listbox.get(self.prot_listbox.curselection())
            print(clicked_file)
            self.player.open(os.path.sep.join(("/home/project/video", clicked_file)))
        else:
            clicked_file = self.list_listbox.get(self.list_listbox.curselection())
            self.player.open(os.path.sep.join(("/home/project", clicked_file)))

    def obd_screen(self):
        if self.is_obd:
            self.is_obd = False
            self.obd_canvas.place_forget()
            self.status_canvas.place_forget()
            self.canvas.config(width=700, height=480)
        else:
            self.is_menu = False
            self.is_view = False
            self.is_obd = True
            self.login_canvas.place_forget()
            self.setting_canvas.place_forget()
            self.list_canvas.place_forget()
            self.view_canvas.place_forget()
            self.obd_stop()
            self.obd_thread()
            self.canvas.config(width=350, height=240)
            self.obd_canvas.pack()
            self.obd_canvas.place(x=100, y=0)
            self.status_canvas.pack()
            self.status_canvas.place(x=100, y=240)

    def obd_thread(self):
        thread = threading.Thread(target=self.obd_start, args=(self.event_loop_obd,), daemon=True)
        thread.start()

    def obd_start(self, loop):
        self.obd.connected = True
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.obd.set_obd())

    def obd_stop(self):
        self.obd.connected = False

        # Wątek przechwytywania obrazu

    def capturing_thread(self):
        thread = threading.Thread(target=self.capturing_start, args=(self.event_loop_capturing,), daemon=True)
        thread.start()

    def capturing_start(self, loop):
        print("camera opened => Start Capturing")
        self.vid.isCapturing = True
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.vid.set_frame())

    def capturing_stop(self):
        print("camera opened => Stop Capturing")
        self.vid.isCapturing = False

        # Wątek nagrywania

    def recording_thread(self):
        if (self.vid.isRecording):
            self.recording_stop()
            self.btn_rec.config(image=self.rec_off)
        else:
            thread = threading.Thread(target=self.recording_start, args=(self.event_loop_recording,), daemon=True)
            thread.start()
            self.btn_rec.config(image=self.rec_on)

    def recording_start(self, loop):
        print("camera opened => Recording")
        self.vid.record_setting()
        self.vid.isRecording = True
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.vid.recording(self))

    def recording_stop(self):
        print("camera opened => Stop Recording")
        self.vid.isRecording = False

    # Wątek detekcji
    def imageia_start(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.det.imageia_load())

    def detecting_thread(self):
        thread = threading.Thread(target=self.detecting_start, args=(self.event_loop_detecting,), daemon=True)
        thread.start()

    def detecting_start(self, loop):
        self.det.is_detecting = True
        self.det.powerdet()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.det.detecting(self))

    def detecting_stop(self):
        setting.isAlert = False
        self.det.stopdet()
        self.det.is_detecting = False

    def object_thread(self):
        thread = threading.Thread(target=self.object_start, args=(self.event_loop_object,),
                                  daemon=True)
        thread.start()

    def object_start(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.det.object_detecting(self))

        # Wątek przesyłu powiadomień

    def send_notification_thread(self, path = None):
        thread = threading.Thread(target=self.send_notification_start, args=(self.event_loop_notification, path),
                                  daemon=True)
        thread.start()

    def send_notification_start(self, loop, path=None):
        if (path == None):
            imgname = dt.datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
            p = os.path.sep.join(("/home/project/images", imgname))
            ret, frame = self.vid.get_frame()
            cv2.imwrite(p, frame)
        else:
            p = path
            imgname = path.split("/")[-1]
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.server.notification(imgname, p, self.type))

        # Wątek przesyłu nagrania

    def send_video_thread(self, path):
        thread = threading.Thread(target=self.send_video_start, args=(self.event_loop_video, path),
                                  daemon=True)
        thread.start()

    def send_video_start(self, loop, path):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.server.video(path, self.vid.get_recTime()))

    # Pętla główna
    def update(self):
        if (self.vid.isCapturing):
            if self.pijuice.status.GetStatus()['data']['powerInput'] == 'NOT_PRESENT' and setting.isAlert == False:
                subprocess.call('xset dpms force off', shell=True)
                self.recording_stop()
                self.capturing_stop()
                self.detecting_thread()
                self.obd_stop()
        else:
            if self.pijuice.status.GetStatus()['data']['powerInput'] == 'PRESENT':
                subprocess.call('xset dpms force on', shell=True)
                self.detecting_stop()
                self.capturing_thread()
                self.recording_thread()
                self.obd_thread()
        if self.obd.is_obd:
            speed, rpm, el, coolant_temp, error = self.obd.get_obd()
            print(speed)
            if(speed == "None"):
                self.obd_value_status.config(text="Brak połączenia")
            else:
                self.obd_value_status.config(text="Połączono")

            self.obd_value_speed.config(text=str(speed).split()[0])
            self.obd_value_rpm.config(text=str(rpm).split()[0]+"  ")
            self.obd_value_el.config(text=str("%.2f" %float(str(el).split()[0])))
            self.obd_value_coolant_temp.config(text=str(coolant_temp).split()[0])
                # Obraz
        # Pobranie ramki
        ret, frame = self.vid.get_frame()

        # Napisy na ekranie
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame,
                    dt.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                    (int(self.vid.width/4), self.vid.height - int(self.vid.height/144)),
                    font, self.vid.height/360,
                    (255, 255, 0),
                    1,
                    cv2.LINE_4)

        cv2.putText(frame,
                    str(self.pijuice.status.GetChargeLevel()['data'])+"%",
                    (self.vid.width - int(self.vid.width/12), int(self.vid.height/24)),
                    font, self.vid.height/720,
                    (255, 255, 0),
                    1,
                    cv2.LINE_AA)

        if self.obd.is_obd:
            cv2.putText(frame,
                        str(speed).split()[0]+"km/h",
                        (0, self.vid.height - int(self.vid.height/144)),
                        font, self.vid.height/720,
                        (255, 255, 0),
                        1,
                        cv2.LINE_AA)

        # Wyświetlenie altualnej ramki
        if ret:
            if self.is_menu or self.is_obd:
                subprocess.call('xset dpms force on', shell=True)
                size = (350, 240)
            else:
                size = (700, 480)
            resized = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(resized))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            text = str(int(self.vid.get_recTime() / 60)) + ":" + str(self.vid.get_recTime() % 60)
            if (self.vid.isRecording):
                self.time_label['text'] = text
            else:
                self.time_label['text'] = ""
        self.window.after(self.delay, self.update)


def main():
    # Create a window and pass it to the Application object
    os.environ["PYTHONUNBUFFERED"]='1'
    os.environ["DISPLAY"] = ':0'
    # Tworzenie okna i źródła obrazu
    window = ThemedTk(theme="equilux")
    window.geometry("800x480")
    window.attributes('-fullscreen', True)
    window.config(background='black', cursor='none')
    App(window)


main()
