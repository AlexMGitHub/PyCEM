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
from kivy.utils import escape_markup
from kivy.uix.widget import Widget
from matplotlib import cm
import numpy as np
import numba as nb

# Local application/library specific imports
from pycem.fdtd import Grid, grid_init
from pycem.utilities import get_project_root


# %% Classes
class FDTDScreen(Widget):
    """Class representing the FDTD simulation as an animation."""

    def __init__(self, sizex, sizey, scale, max_time, frame_rate,
                 progress_label, **kwargs):
        """Init widget with a texture used to create the FDTD animation."""
        super().__init__(**kwargs)
        self.sizex = sizex
        self.sizey = sizey
        self.scale = scale
        self.max_time = max_time
        self.frame_rate = frame_rate
        self.progress_label = progress_label
        self.buf_size = sizex * sizey * 3  # RGB 3 bytes per pixel
        self.event = None
        self.clim = (-3, 0)
        self.frame = 0
        self.sim_complete = False
        self.rect = None

    def run_sim(self, *args):
        """Run C code to perform FDTD simulation."""
        if not self.sim_complete:
            root = get_project_root()
            lib_path = root / 'src/C/lib/libtmzdemo.so'
            c_lib = ctypes.CDLL(lib_path)
            tmzdemo = c_lib.tmzdemo
            tmzdemo.argtypes = [ctypes.POINTER(Grid)]
            tmzdemo.restype = None  # C function returns void
            self.g = Grid()
            self.arr = grid_init(self.g, self.sizex, self.sizey,
                                 self.max_time)  # Contains Numpy arrays
            sim_progress = Clock.schedule_interval(self.check_sim_progress,
                                                   1.0/2.0)
            tmzdemo(self.g)
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
        buf = self.arr_to_rgb(self.arr.Ez[self.frame].T)  # Tranpose of array
        self.texture.blit_buffer(buf)
        self.canvas.ask_update()

    def play_animation(self, wid, *args):
        """Button callback to start/stop FDTD animation."""
        self.reposition_screen(self)
        if self.sim_complete:
            if self.event not in Clock.get_events():
                self.event = Clock.schedule_interval(self.update,
                                                     1.0/self.frame_rate)
                wid.text = "Pause Animation"
            else:
                self.event.cancel()
                wid.text = "Play Animation"

    def reposition_screen(self, wid, *args):
        """Move rectangle containing texture with screen widget."""
        if self.rect:
            self.rect.pos = self.pos


class PyCEM(App):
    """Creates PyCEM GUI."""

    def __init__(self, sizex, sizey, scale, max_time, frame_rate):
        """Accept user parameters for FDTD app."""
        super().__init__()
        self.sizex = sizex
        self.sizey = sizey
        self.scale = scale
        self.max_time = max_time
        self.frame_rate = frame_rate

    def build(self):
        """Build FDTD app."""
        # Add label widgets above screen with spacer widgets
        lbl_height = 50
        lbl_layout = BoxLayout(size_hint=(1, None), height=lbl_height)
        lbl_spacer_left = Widget(size_hint=(0.5, 1))
        lbl_spacer_right = Widget(size_hint=(0.5, 1))
        lbl_sim_progress = Label(
            text='[b]Progress: 0%[/b]', markup=True,
            font_size='20sp')
        lbl_layout.add_widget(lbl_spacer_left)
        lbl_layout.add_widget(lbl_sim_progress)
        lbl_layout.add_widget(lbl_spacer_right)
        # Define screen layout containing FDTD animation
        screenx = self.sizex * self.scale
        screeny = self.sizey * self.scale
        screen = FDTDScreen(self.sizex, self.sizey, self.scale, self.max_time,
                            self.frame_rate, lbl_sim_progress,
                            size_hint=(None, None),
                            size=(screenx, screeny))
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
        btn_startsim = Button(text='Run Simulation',
                              on_press=partial(screen.run_sim),
                              size_hint=(None, None),
                              size=(btn_width, btn_height))
        btn_stopsim = Button(text='Play Animation',
                             on_press=partial(screen.play_animation),
                             size_hint=(None, None),
                             size=(btn_width, btn_height))
        btn_layout.add_widget(btn_spacer_left)
        btn_layout.add_widget(btn_startsim)
        btn_layout.add_widget(btn_stopsim)
        btn_layout.add_widget(btn_spacer_right)
        # Create root layout and add label, screen, and button layouts
        root = BoxLayout(orientation='vertical')
        root.add_widget(lbl_layout)
        root.add_widget(screen_layout)
        root.add_widget(btn_layout)
        # Set initial GUI window size
        Window.size = (int(screenx*1.25), lbl_height+screeny+btn_height)
        # Bind animation to any changes in GUI window width
        Window.bind(width=screen.reposition_screen)
        self.title = 'PyCEM'  # App window title
        return root


if __name__ == '__main__':
    PyCEM(101, 81, 4, 300, 30).run()
