"""Kivy GUI used to display FDTD simulation animations."""

# %% Imports
# Standard system imports
from functools import partial

# Related third party imports
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
import numpy as np

# Local application/library specific imports


# %% Classes
class FDTDGrid(Widget):
    """Class representing the FDTD simulation as an animation."""

    def __init__(self, sizex, sizey, scale, frame_rate, **kwargs):
        """Init widget with a texture used to create the FDTD animation."""
        super().__init__(**kwargs)
        self.sizex = sizex
        self.sizey = sizey
        self.scale = scale
        self.frame_rate = frame_rate
        self.buf_size = sizex * sizey * 3  # RGB 3 bytes per pixel
        self.event = None
        self.init_texture()

    def init_texture(self):
        """Initialize texture used for efficient animations."""
        self.texture = Texture.create(size=(self.sizex, self.sizey),
                                      colorfmt='rgb', bufferfmt='ubyte')
        # Disable linear interpolation of texture pixels (blur effect)
        self.texture.mag_filter = 'nearest'
        buf = np.zeros(self.buf_size, dtype=np.ubyte)
        self.texture.blit_buffer(buf)
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos,
                                  size=(self.sizex*self.scale,
                                        self.sizey*self.scale))

    def update(self, dt):
        """Update canvas with new image data."""
        buf = np.random.randint(0, 256, self.buf_size, dtype=np.ubyte)
        self.texture.blit_buffer(buf)
        self.canvas.ask_update()

    def run_sim(self, val, *args):
        """Button callback to start/stop FDTD animation."""
        self.reposition_screen(self)
        if val:
            if self.event not in Clock.get_events():
                self.event = Clock.schedule_interval(self.update,
                                                     1.0/self.frame_rate)
        else:
            if self.event in Clock.get_events():
                self.event.cancel()

    def reposition_screen(self, wid, *args):
        """Move rectangle containing texture with screen widget."""
        if self.rect:
            self.rect.pos = self.pos


class MyApp(App):
    """Creates PyCEM GUI."""

    def __init__(self, sizex, sizey, scale, frame_rate):
        """Accept user parameters for FDTD app."""
        super().__init__()
        self.sizex = sizex
        self.sizey = sizey
        self.scale = scale
        self.frame_rate = frame_rate

    def build(self):
        """Build FDTD app."""
        # Define screen layout containing FDTD animation
        screenx = self.sizex * self.scale
        screeny = self.sizey * self.scale
        screen = FDTDGrid(self.sizex, self.sizey, self.scale, self.frame_rate,
                          size_hint=(None, None), size=(screenx, screeny))

        # Place screen in box layout with blank spacer widgets
        screen_layout = BoxLayout(size_hint=(1, None), height=screeny)
        screen_spacer_left = Widget(size_hint=(0.5, 1))
        screen_spacer_right = Widget(size_hint=(0.5, 1))
        screen_layout.add_widget(screen_spacer_left)
        screen_layout.add_widget(screen)
        screen_layout.add_widget(screen_spacer_right)
        # Place control buttons below screen in box layout with spacer widgets
        btn_width, btn_height = 150, 50
        btn_layout = BoxLayout(size_hint=(1, None), height=btn_height)
        btn_spacer_left = Widget(size_hint=(0.5, 1))
        btn_spacer_right = Widget(size_hint=(0.5, 1))
        btn_startsim = Button(text='Start Simulation',
                              on_press=partial(screen.run_sim, True),
                              size_hint=(None, None),
                              size=(btn_width, btn_height))
        btn_stopsim = Button(text='Stop Simulation',
                             on_press=partial(screen.run_sim, False),
                             size_hint=(None, None),
                             size=(btn_width, btn_height))
        btn_layout.add_widget(btn_spacer_left)
        btn_layout.add_widget(btn_startsim)
        btn_layout.add_widget(btn_stopsim)
        btn_layout.add_widget(btn_spacer_right)
        # Create root layout and add screen and button layouts
        root = BoxLayout(orientation='vertical')
        root.add_widget(screen_layout)
        root.add_widget(btn_layout)
        # Bind animation to any changes in GUI window width
        Window.bind(width=screen.reposition_screen)
        # Set initial GUI window size
        Window.size = (int(screenx*1.25), screeny+btn_height)
        self.title = 'PyCEM'  # App window title
        return root


if __name__ == '__main__':
    MyApp(64, 64, 10, 10).run()
