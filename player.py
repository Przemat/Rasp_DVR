#! /usr/bin/python
# -*- coding: utf-8 -*-
"""vlc media player; based off example in vlc repo:
`http://git.videolan.org/?p=vlc/bindings/python.git;a=commit;h=HEAD`
See also:
`http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/menu.html`
`http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/menu-coptions.html`
"""
import os

import vlc
import tkinter as tk
from tkinter import ttk
from tkinter.font import Font


class PyPlayer:
    def __init__(self,container_instance):
        self.container_instance = container_instance
        self.default_font = Font(family="Times New Roman", size=16)

        # create vlc instance
        self.vlc_instance, self.vlc_media_player_instance = self.create_vlc_instance()

        # vlc video frame
        self.video_panel = ttk.Frame(self.container_instance, width=500, height=480)
        self.canvas = tk.Canvas(self.video_panel, background='black', width=500, height=445)
        self.canvas.pack(fill=tk.BOTH, expand=1)
        self.video_panel.pack(fill=tk.BOTH, expand=1)

        # controls
        self.create_control_panel()

    def create_control_panel(self):
        """Add control panel."""
        control_panel = ttk.Frame(self.container_instance)
        pause = ttk.Button(control_panel, text="Pause", command=self.pause)
        play = ttk.Button(control_panel, text="Play", command=self.play)
        stop = ttk.Button(control_panel, text="Stop", command=self.stop)
        pause.pack(side=tk.LEFT)
        play.pack(side=tk.LEFT)
        stop.pack(side=tk.LEFT)
        control_panel.pack(side=tk.BOTTOM)

    def create_vlc_instance(self):
        """Create a vlc instance; `https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.MediaPlayer-class.html`"""
        vlc_instance = vlc.Instance('--no-xlib --quiet')
        vlc_media_player_instance = vlc_instance.media_player_new()
        self.container_instance.update()
        return vlc_instance, vlc_media_player_instance

    def get_handle(self):
        return self.video_panel.winfo_id()

    def play(self):
        """Play a file."""
        if not self.vlc_media_player_instance.get_media():
            self.open()
        else:
            if self.vlc_media_player_instance.play() == -1:
                pass

    def pause(self):
        """Pause the player."""
        self.vlc_media_player_instance.pause()

    def stop(self):
        """Stop the player."""
        self.vlc_media_player_instance.stop()

    def open(self, file):
        """New window allowing user to select a file and play."""
        print(file)
        if isinstance(file, tuple):
            return
        if os.path.isfile(file):
            self.play_film(file)

    def play_film(self, file):
        """Invokes the `play` method on the vlc instance for the current file."""
        directory_name = os.path.dirname(file)
        file_name = os.path.basename(file)
        self.Media = self.vlc_instance.media_new(
            str(os.path.join(directory_name, file_name))
        )
        self.vlc_media_player_instance.set_media(self.Media)
        self.vlc_media_player_instance.set_xwindow(self.get_handle())
        self.play()

    @staticmethod
    def get_film_name(film) -> str:
        """Removes directory from film name."""
        return film.split('/')[-1]
