#!/usr/bin/env python
import kivy

kivy.require("1.0.6")  # replace with your current kivy version !

from kivy.app import App
from kivy.uix.button import Button


class MainWindow(App):
    def build(self):
        return Button(text="Hello World")

