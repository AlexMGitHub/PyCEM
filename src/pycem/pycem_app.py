"""Kivy GUI used to display FDTD simulation animations."""
# %% Imports
# Standard system imports
from functools import partial
import ctypes

# Related third party imports
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.utils import escape_markup
from kivy.uix.widget import Widget
from matplotlib import cm
import numpy as np
import numba as nb

# Local application/library specific imports
from pycem.fdtd import Grid, RickerTMz2D


# %% Classes
class FDTDScreen(Widget):
    """Class representing the FDTD simulation as an animation."""

    def __init__(self, scale, frame_rate,
                 progress_label, slider, **kwargs):
        """Init widget with a texture used to create the FDTD animation."""
        super().__init__(**kwargs)

        self.frame_rate = frame_rate
        self.progress_label = progress_label
        self.slider = slider
        self.scale = scale
        self.event = None
        self.clim = (-3, 0)
        self.frame = 0
        self.sim_complete = False
        self.rect = None

    def init_sim_params(self):
        """Initialize parameters related to simulation."""
        self.sizex = self.g.sizeX
        self.sizey = self.g.sizeY
        self.max_time = self.g.max_time
        self.buf_size = self.sizex * self.sizey * 3  # RGB 3 bytes per pixel
        self.slider.max = self.max_time - 1

    def run_sim(self, *args):
        """Run C code to perform FDTD simulation."""
        if not self.sim_complete:
            self.g = Grid()
            scenario = RickerTMz2D(self.g)
            self.arr = scenario.arr
            self.init_sim_params()
            sim_progress = Clock.schedule_interval(self.check_sim_progress,
                                                   1.0/2.0)
            # tmzdemo(self.g)
            scenario.run_sim()
            sim_progress.cancel()
            self.check_sim_progress(None)
            self.sim_complete = True
            self.init_texture()  # Initialize texture for animmation

    def check_sim_progress(self, dt):
        """Update label with current sim progress as percentage."""
        progress = self.g.time / self.g.max_time * 100
        self.progress_label.text = f"[b]Progress: {progress:.1f}%[/b]"

    def init_cmap(self):
        """Scale Jet colormap tuples to RGB values. """
        def to_rgb(x): return np.round(
            np.interp(x, [0, 1], [0, 255]), 0).astype(np.ubyte)
        self.cmap = []
        for x in range(cm.jet.N):
            self.cmap.append(to_rgb(cm.jet(x)[0:3]))
        self.cmap = np.array(self.cmap)

    def cm_indices(self, arr):
        """Map array value to colormap index."""
        return np.round(
            np.interp(arr, self.clim, [0, 255]), 0).astype(int)

    def log_norm(self, data, z_norm=1):
        """Return log normalized matrix."""
        return np.log10(np.abs((data)/z_norm)+np.nextafter(0, 1))

    @staticmethod
    @nb.njit
    def fill_buf(buf, cm_arr, cmap):
        """Fill texture buffer with three RGB values for each array value."""
        for idx, val in enumerate(cm_arr):
            buf[idx*3:3*idx+3] = cmap[val]
        return buf

    def arr_to_rgb(self, arr):
        """Map array values to appropriate RGB colormap values."""
        cm_arr = self.cm_indices(self.log_norm(arr)).flatten()
        buf = np.empty(self.buf_size, dtype=np.ubyte)
        return self.fill_buf(buf, cm_arr, self.cmap)

    def init_texture(self):
        """Initialize texture used for efficient animations."""
        self.init_cmap()
        self.texture = Texture.create(size=(self.sizex, self.sizey),
                                      colorfmt='rgb', bufferfmt='ubyte')
        # Disable linear interpolation of texture pixels (blur effect)
        # self.texture.mag_filter = 'nearest'
        buf = self.arr_to_rgb(self.arr.Ez[self.frame])
        self.texture.blit_buffer(buf)
        with self.canvas:
            self.rect = Rectangle(texture=self.texture, pos=self.pos,
                                  size=(self.sizex*self.scale,
                                        self.sizey*self.scale))
        self.reposition_screen(self)

    def update(self, dt):
        """Update canvas with new image data."""
        self.frame += 1
        if self.frame >= self.max_time:
            self.frame = 0
        self.slider.value = self.frame
        buf = self.arr_to_rgb(self.arr.Ez[self.frame].T)  # Tranpose of array
        self.texture.blit_buffer(buf)
        self.canvas.ask_update()

    def select_frame(self, wid, *args):
        """Select current frame of FDTD animation."""
        if self.sim_complete:
            self.frame = int(wid.value-1)
            self.update(self.frame)

    def play_animation(self, wid, *args):
        """Button callback to start/stop FDTD animation."""
        self.reposition_screen(self)
        if self.sim_complete:
            if self.event not in Clock.get_events():
                self.event = Clock.schedule_interval(self.update,
                                                     1.0/self.frame_rate)
                wid.background_normal = 'icons/pause.png'
                wid.background_down = 'icons/pause_down.png'
            else:
                self.event.cancel()
                wid.background_normal = 'icons/play.png'
                wid.background_down = 'icons/play_down.png'

    def reposition_screen(self, wid, *args):
        """Move rectangle containing texture with screen widget."""
        if self.rect:
            self.rect.pos = self.pos


class PyCEM(App):
    """Creates PyCEM GUI."""

    def __init__(self, scale, frame_rate):
        """Accept user parameters for FDTD app."""
        super().__init__()
        self.sizex = 100  # Set arbitrary defaults for screen and slider size
        self.sizey = 100
        self.max_time = 100
        self.scale = scale
        self.frame_rate = frame_rate

    def build(self):
        """Build FDTD app."""
        # Define widget dimensions
        screenx = self.sizex * self.scale
        screeny = self.sizey * self.scale
        screen_spacer = 50
        play_width, play_height = 36, 36
        panel_width = 200
        console_height = 150
        # Define widgets used in GUI
        slider_anim = Slider(min=0, max=self.max_time-1, value=0,
                             step=1, value_track=True,
                             value_track_color=[1, 0, 0, 1],
                             size_hint=(1, None), height=play_height)
        console = Label(
            text='[b]Progress: 0%[/b]', markup=True,
            font_size='20sp', size_hint=(1, None), height=console_height)
        screen = FDTDScreen(self.scale,
                            self.frame_rate, console, slider_anim,
                            size_hint=(None, None),
                            size=(screenx, screeny))
        btn_playanim = Button(on_press=screen.play_animation,
                              size_hint=(None, None),
                              size=(play_width, play_height))
        # Place control buttons below screen in box layout
        slider_anim.bind(value=screen.select_frame)
        btn_playanim.background_normal = 'icons/play.png'
        btn_playanim.background_down = 'icons/play_down.png'
        ctrl_layout = BoxLayout(orientation='horizontal',
                                size_hint=(None, None),
                                size=(screenx, play_height))
        ctrl_layout.add_widget(btn_playanim)
        ctrl_layout.add_widget(slider_anim)
        # Add a tabbed panel to the left side of the GUI
        tp = TabbedPanel(size_hint=(None, 1),
                         width=panel_width)
        tp.default_tab_text = 'Simulation'
        tp.default_tab.background_color = (1, 0, 0, 1)
        sim_tab = BoxLayout(orientation='vertical')
        btn_runsim = Button(text='Run Simulation',
                            on_press=screen.run_sim,
                            size_hint=(None, None),
                            size=(150, 50))
        sim_tab.add_widget(btn_runsim)
        tp.content = btn_runsim
        # Add multiline label as bottom console panel

        # Define screen layout containing FDTD animation and control buttons
        screen_layout = BoxLayout(orientation='vertical', size_hint=(None, 1),
                                  width=screenx)
        screen_spacer_top = Widget(size_hint=(1, 0.5))
        screen_spacer_bot = Widget(size_hint=(1, 0.5))
        screen_layout.add_widget(screen_spacer_top)
        screen_layout.add_widget(screen)
        screen_layout.add_widget(ctrl_layout)
        screen_layout.add_widget(screen_spacer_bot)
        # Place screen and controls in box layout with blank spacer widgets
        anim_layout = BoxLayout(orientation='horizontal')
        screen_spacer_left = Widget(size_hint=(0.5, 1))
        screen_spacer_right = Widget(size_hint=(0.5, 1))
        anim_layout.add_widget(screen_spacer_left)
        anim_layout.add_widget(screen_layout)
        anim_layout.add_widget(screen_spacer_right)
        # Create root layout
        root = BoxLayout(orientation='horizontal')
        right_layout = BoxLayout(
            orientation='vertical', size_hint=(1, 1))  # (None, None),
        # size=(screenx+screen_spacer, screeny+play_height))
        right_layout.add_widget(anim_layout)
        right_layout.add_widget(console)
        root.add_widget(tp)
        root.add_widget(right_layout)
        # Set initial GUI window size
        window_width = panel_width + screenx + screen_spacer
        window_height = console_height+screeny+play_height + screen_spacer
        Window.size = (window_width, window_height)
        # Bind animation to any changes in GUI window width
        Window.bind(width=screen.reposition_screen)
        self.title = 'PyCEM'  # App window title
        return root


if __name__ == '__main__':
    PyCEM(4, 30).run()
