"""Contains scenarios of various transmission lines for FDA analysis."""
# %% Imports
# Standard system imports

# Related third party imports
import numpy as np
from numba import njit

# Local application/library specific imports
from pycem.fda_pyvista import save_mesh_png


# %% Scenarios
class FDAScenario:
    """Parent class with methods to be inherited by child classes."""

    def __init__(self):
        """Initialize physical constants."""
        self.u0 = 1.2566370614e-6   # Permeability of free space
        self.e0 = 8.8541878176e-12  # Permittivity of free space
        self.c0 = 299792458         # Speed of light in free space
        self.n0 = (self.u0 / self.e0)**0.5  # Impedance of free space
        self.differential = False   # Default single-ended transmission lines
        self.diff_mode = 'diff'     # Default differential mode analysis
        # Placeholder variables
        self.Nx = None
        self.Ny = None
        self.dx = None
        self.dy = None
        self.Er = None
        self.z0 = None
        self.voltages = None
        self.name = None
        self.er_mat = None
        self.signal_mat = None
        self.ground_mat = None
        self.capacitance = None
        self.capacitance_h = None
        self.inductance = None
        self.Ex_mat = None
        self.Ey_mat = None

    @staticmethod
    @njit(cache=True)
    def _calculate_e_field(Nx, Ny, dx, dy, Ex_mat, Ey_mat, v_mat):
        """Calculate electric field from voltages."""
        for i in range(Ny):
            for j in range(Nx):
                # Y-direction
                if i == Ny - 1 or i == 0:
                    Ey_mat[i, j] = 0
                else:
                    Ey_mat[i, j] = -(v_mat[i+1, j]-v_mat[i, j])/dy
                # X-direction
                if j == Nx - 1 or j == 0:
                    Ex_mat[i, j] = 0
                else:
                    Ex_mat[i, j] = -(v_mat[i, j+1]-v_mat[i, j])/dx
        return Ex_mat, Ey_mat

    def run_sim(self, filepath=None):
        """Run single-ended or differential simulation."""
        if self.differential:
            # Calculate differential impedance
            diff_C, diff_L, diff_z0 = self._run_sim()
            if filepath:
                self._plot_matrices(filepath, prefix=self.diff_mode)
            # Calculate common mode impedance
            self.diff_mode = 'comm'
            comm_C, comm_L, comm_z0 = self._run_sim()
            if filepath:
                self._plot_matrices(filepath, prefix=self.diff_mode)
            self.diff_mode = 'diff'      # Reset to diff mode impedance
            odd_z0 = 0.5 * diff_z0      # Odd mode impedance
            even_z0 = 2 * comm_z0       # Even mode impedance
            return (diff_C, diff_L, diff_z0, comm_C, comm_L, comm_z0, odd_z0,
                    even_z0)
        else:
            capacitance, inductance, z0 = self._run_sim()
            if filepath:
                self._plot_matrices(filepath)
            return capacitance, inductance, z0

    def _run_sim(self):
        """Calculate transmission line parameters.

        Capacitance calculation assumes 1V applied voltage.
        """
        self._draw_geometry()           # Draw geometry to be simulated
        self._construct_matrices()      # Construct matrices for FDA
        Nx = self.Nx
        Ny = self.Ny
        dx = self.dx
        dy = self.dy
        v_mat = self.voltages.reshape((Ny, Nx))
        Ex_mat = np.zeros((Ny, Nx))     # Electric field in X-direction
        Ey_mat = np.zeros((Ny, Nx))     # Electric field in Y-direction
        FDAScenario._calculate_e_field(Nx, Ny, dx, dy, Ex_mat, Ey_mat, v_mat)
        self.Ex_mat = Ex_mat
        self.Ey_mat = Ey_mat
        Dx_mat = Ex_mat * self.er_mat   # Displacement field in X-direction
        Dy_mat = Ey_mat * self.er_mat   # Displacement field in Y-direction
        # Calculate distributed capacitance
        self.capacitance = (np.sum(Dx_mat * Ex_mat) +
                            np.sum(Dy_mat * Ey_mat)) * self.e0 * dx * dy
        # Calculate homogenous capacitance
        self.capacitance_h = (np.sum(Ex_mat * Ex_mat) +
                              np.sum(Ey_mat * Ey_mat)) * self.e0 * dx * dy
        # Calculate distributed inductance
        self.inductance = 1 / (self.c0**2 * self.capacitance_h)
        # Calculate characteristic impedance
        self.z0 = np.sqrt(self.inductance / self.capacitance)
        return self.capacitance, self.inductance, self.z0

    @staticmethod
    @njit(cache=True)
    def _create_eqns(Nx, Ny, dx, dy, laplacian_mat, b_mat, signal_mat,
                     ground_mat, neg_mat, differential=False):
        """Create simultaneous equations for FDA."""
        coef_i = 1 / (dy ** 2)         # Y-difference coefficients
        coef_j = 1 / (dx ** 2)         # X-difference coefficients
        coef_self = -(2*coef_i + 2*coef_j)  # Self-term coefficents
        for i in range(Ny):
            for j in range(Nx):
                if signal_mat[i, j] > 0:
                    # Force known potentials for signal
                    laplacian_mat[i*Nx+j, i*Nx+j] = 1
                    b_mat[i*Nx + j] = signal_mat[i, j]
                elif ground_mat[i, j] > 0:
                    # Force known potentials for ground
                    laplacian_mat[i*Nx+j, i*Nx+j] = 1
                    b_mat[i*Nx + j] = 0
                elif differential and neg_mat[i, j] != 0:
                    # Force potentials for negative conductor of diff pair
                    laplacian_mat[i*Nx+j, i*Nx+j] = 1
                    b_mat[i*Nx + j] = neg_mat[i, j]
                else:
                    # Assign finite-difference equation coeffients
                    temp_mat = np.zeros((Ny, Nx))
                    if i > 0:
                        temp_mat[i-1, j] = coef_i
                    if i < (Ny - 1):
                        temp_mat[i+1, j] = coef_i
                    if j > 0:
                        temp_mat[i, j-1] = coef_j
                    if j < (Nx - 1):
                        temp_mat[i, j+1] = coef_j
                    temp_mat[i, j] = coef_self
                    laplacian_mat[i*Nx+j] = temp_mat.flatten()

    def _construct_matrices(self):
        """Construct matrices used for finite difference analysis."""
        Nx = self.Nx
        Ny = self.Ny
        dx = self.dx
        dy = self.dy
        # Construct Laplacian matrix
        b_mat = np.zeros((Nx*Ny,))          # Forced potentials
        laplacian_mat = np.zeros((Nx*Ny, Nx*Ny))
        if self.differential:
            FDAScenario._create_eqns(Nx, Ny, dx, dy, laplacian_mat, b_mat,
                                     self.signal_mat, self.ground_mat,
                                     self.neg_mat, differential=True)
        else:
            FDAScenario._create_eqns(Nx, Ny, dx, dy, laplacian_mat, b_mat,
                                     self.signal_mat, self.ground_mat,
                                     np.zeros((Ny, Nx)), differential=False)
        # Solve for voltages
        self.voltages = np.linalg.solve(laplacian_mat, b_mat)

    def _plot_matrices(self, filepath, prefix=''):
        """Save PNG images of matrix data using PyVista."""
        if prefix != '':
            prefix += '_'
        fp = filepath / self.name
        fp.mkdir(parents=True, exist_ok=True)
        save_mesh_png(self.signal_mat.flatten(), self.Nx, self.Ny, self.dx,
                      self.dy, fp / f'{prefix}signal.png', cmap='binary')
        save_mesh_png(self.ground_mat.flatten(), self.Nx,
                      self.Ny, self.dx, self.dy,  fp / f'{prefix}ground.png',
                      cmap='binary')
        save_mesh_png(self.er_mat.flatten(), self.Nx, self.Ny, self.dx,
                      self.dy, fp / f'{prefix}er.png', clim=[0, self.Er])
        save_mesh_png(self.voltages, self.Nx, self.Ny, self.dx, self.dy,
                      fp / f'{prefix}voltage.png',
                      clim=[np.min(self.voltages), np.max(self.voltages)],
                      show_edges=False)
        save_mesh_png(np.abs(self.Ex_mat.flatten()), self.Nx, self.Ny, self.dx,
                      self.dy, fp / f'{prefix}Ex.png',
                      clim=[np.min(self.Ex_mat), np.max(self.Ex_mat)],
                      show_edges=False, log=True)
        save_mesh_png(np.abs(self.Ey_mat.flatten()), self.Nx, self.Ny, self.dx,
                      self.dy, fp / f'{prefix}Ey.png',
                      clim=[np.min(self.Ey_mat), np.max(self.Ey_mat)],
                      show_edges=False, log=True)
        if self.differential:
            save_mesh_png(np.abs(self.neg_mat.flatten()), self.Nx,
                          self.Ny, self.dx, self.dy,
                          fp / f'{prefix}negative.png', cmap='binary')
            cond = (self.signal_mat+self.neg_mat+0.5*self.ground_mat).flatten()
            save_mesh_png(cond, self.Nx, self.Ny, self.dx, self.dy,
                          fp / f'{prefix}conductors.png', clim=[-1, 1],
                          cmap='Set1')

        else:
            save_mesh_png((self.signal_mat+-1*self.ground_mat).flatten(),
                          self.Nx, self.Ny, self.dx, self.dy,
                          fp / f'{prefix}conductors.png', clim=[-1, 1],
                          cmap='seismic')

    def _draw_geometry(self):
        """Override this placehold method in child class."""
        return


class SymmetricStripline(FDAScenario):
    """Finite difference analysis of a symmetric stripline."""

    name = 'SymmetricStripline'     # Scenario name
    href = '/symmetric_stripline'   # Webapp URL
    title = "Symmetric Stripline"
    description = """
        This scenario simulates a symmetric stripline.  The signal conductor
        is centered in the dielectric with two PEC ground planes - one above
        one and below.
        """

    def __init__(self, Er=4, sub_thk=0.9e-3, trace_w=0.35e-3, dx=0.025e-3,
                 dy=0.025e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = SymmetricStripline.name
        self.Nx = round(trace_w * 6 / dx)  # Domain width 6 times trace width
        self.Ny = round(sub_thk / dy) + 2  # Two extra rows for ground planes
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of stripline substrate
        self.trace_w = trace_w      # Stripline trace width
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        Ny = self.Ny
        tr_w = round(self.trace_w / self.dx)    # Trace width in cells
        idx1 = Nx//2-tr_w//2                    # Start idx of stripline trace
        idx2 = idx1 + tr_w                      # End index of trace
        self.signal_mat[Ny//2, idx1:idx2] = 1   # 1V applied to stripline trace
        self.ground_mat[0, :] = 1               # Top ground plane
        self.ground_mat[-1, :] = 1              # Bottom ground plane
        self.er_mat = self.Er * self.er_mat     # Set dielectric constant

    def _calculate_z0(self):
        """Calculate transmission line impedance using analytical formula."""
        w = self.trace_w
        Er = self.Er
        t = self.dy
        b = self.sub_thk
        h = self.sub_thk / 2
        if w / b < 0.35:
            # Narrow signal conductor
            m = 6*h / (3*h + t)
            quant1 = t / (4*h + t)
            quant2 = np.pi * t / (4*(w + 1.1*t))
            w_eff = w + t/np.pi * np.log(Er / (quant1**2 + quant2**m)**0.5)
            quant4 = 8*h / (np.pi*w_eff)
            quant5 = 16*h / (np.pi*w_eff)
            quant6 = 16*h/(np.pi*w_eff)
            z0 = 60 / Er**0.5 * \
                np.log(1 + quant4*(quant5 + (quant6**2 + 6.27)**0.5))
        elif w / b >= 0.35:
            # Wide signal conductor
            quant1 = 2*b / (b-t)
            quant2 = b/(b-t) + 1
            quant3 = t / (b-t)
            quant4 = 1 / (1-t/b)**2 - 1
            cf = quant1*(np.log(quant2) - quant3*np.log(quant4))
            z0 = 94.15 / (Er**0.5 * (w/(b-t) + cf/np.pi))
        return z0


class Microstrip(FDAScenario):
    """Finite difference analysis of a symmetric stripline."""

    name = 'Microstrip'             # Scenario name
    href = '/microstrip'            # Webapp URL
    title = "Microstrip"
    description = """
        This scenario simulates a microstrip transmission line.  The signal
        conductor rests on top of a substrate.  The ground plane is on the
        bottom of the substrate.
        """

    def __init__(self, Er=4.4, sub_thk=1e-3, trace_w=1.9e-3, dx=0.1e-3,
                 dy=0.1e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = Microstrip.name
        self.Nx = round(trace_w * 5 / dx)  # Domain width 5 times trace width
        self.Ny = round(sub_thk * 6 / dy)  # Domain height in cells
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of microstrip substrate
        self.trace_w = trace_w      # Microstrip trace width
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        tr_w = round(self.trace_w / self.dx)     # Trace width in cells
        tr_h = round(self.sub_thk / self.dy)+1   # Trace y-offset in cells
        idx1 = Nx//2-tr_w//2                     # Start idx of trace
        idx2 = idx1 + tr_w                       # End index of trace
        self.signal_mat[-tr_h-1, idx1:idx2] = 1  # 1V applied to trace
        self.ground_mat[-1, :] = 1               # Bottom ground plane
        self.er_mat[-tr_h:, :] = self.Er         # Define substrate

    def _calculate_z0(self):
        """Calculate transmission line impedance using analytical formula."""
        w = self.trace_w
        Er = self.Er
        h = self.sub_thk
        if w / h < 1:
            quant1 = 1 / (1+12*(h/w))**0.5
            quant2 = (1 - w/h)
            eps_eff = (Er+1)/2 + (Er-1)/2*(quant1 + 0.04*quant2**2)
            z0 = 60 / eps_eff**0.5 * np.log(8*h/w + 0.25*w/h)
        elif w / h >= 1:
            quant3 = 1 + 12*h/w
            eps_eff = (Er+1)/2 + (Er-1) / (2*quant3**0.5)
            quant4 = w/h + 1.393 + 2/3*np.log(w/h+1.444)
            z0 = 120 * np.pi / (eps_eff**0.5*quant4)
        return z0


class Coaxial(FDAScenario):
    """Finite difference analysis of a symmetric stripline."""

    name = 'Coaxial'                # Scenario name
    href = '/coaxial'               # Webapp URL
    title = "Coaxial"
    description = """
        This scenario simulates a coaxial transmission line.  The center
        conductor is encased in Teflon dielectric and surrounded by the outer
        conductor.  The dimensions are based on an SMA female connector.
        """

    def __init__(self, Er=2.2, inner_rad=1.3e-3/2, outer_rad=4.6e-3/2,
                 dx=0.05e-3, dy=0.05e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = Coaxial.name
        self.Nx = round(1.3*(outer_rad*2)/dx)  # Size of domain in X-direction
        self.Ny = round(1.3*(outer_rad*2)/dy)  # Size of domain in Y-direction
        self.Er = Er                    # Relative dielectric constant
        self.inner_rad = inner_rad      # Inner conductor radius
        self.outer_rad = outer_rad      # Outer conductor radius
        self.dx = dx                    # Physical size of cell in X-direction
        self.dy = dy                    # Physical size of cell in Y-direction

    def _define_coax(self):
        """Define inner and outer conductors of coaxial transmission line."""
        Nx = self.Nx
        Ny = self.Ny
        dx = self.dx
        dy = self.dy
        center_x = Nx // 2
        center_y = Ny // 2
        for i in range(Ny):
            for j in range(Nx):
                dist = (((i-center_y)*dy)**2 + ((j-center_x)*dx)**2)**0.5
                if dist >= self.outer_rad:
                    self.ground_mat[i, j] = 1
                if dist <= self.inner_rad:
                    self.signal_mat[i, j] = 1

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        Ny = self.Ny
        self.signal_mat = np.zeros((Ny, Nx))    # Center (inner) conductor
        self.ground_mat = np.zeros((Ny, Nx))    # Outer conductor
        er_mat = np.ones((Ny, Nx))              # Dielectric material
        # Draw geometry
        self._define_coax()                 # Create inner and outer conductors
        self.er_mat = er_mat * self.Er      # Teflon dielectric

    def _calculate_z0(self):
        """Calculate transmission line impedance using analytical formula."""
        Er = self.Er
        D = self.outer_rad  # Factor of 2 for diameter/radius cancels out
        d = self.inner_rad
        z0 = 138 * np.log10(D/d) / Er**0.5
        return z0


class AsymmetricStripline(FDAScenario):
    """Finite difference analysis of asymmetric stripline."""

    name = 'AsymmetricStripline'    # Scenario name
    href = '/asymmetric_stripline'  # Webapp URL
    title = "Asymmetric Stripline"
    description = """
        This scenario simulates asymmetric stripline.  The signal conductor
        is closer to one ground plane than the other.
        """

    def __init__(self, Er=4, sub_thk=0.9e-3, trace_w=0.35e-3,
                 offset=0.2e-3, dx=0.025e-3, dy=0.025e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = AsymmetricStripline.name
        self.Nx = round(trace_w * 6 / dx)  # Domain width 6 times trace width
        self.Ny = round(sub_thk / dy) + 2  # Two extra rows for ground planes
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of stripline substrate
        self.trace_w = trace_w      # Stripline trace width
        self.offset = offset        # Trace offset from top ground plane
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        offs = round(self.offset / self.dy)     # Trace offset in cells
        yidx = 1 + offs                         # Trace vertical start index
        tr_w = round(self.trace_w / self.dx)    # Trace width in cells
        idx1 = Nx//2-tr_w//2                    # Start idx of stripline trace
        idx2 = idx1 + tr_w                      # End index of trace
        self.signal_mat[yidx, idx1:idx2] = 1    # 1V applied to stripline trace
        self.ground_mat[0, :] = 1               # Top ground plane
        self.ground_mat[-1, :] = 1              # Bottom ground plane
        self.er_mat = self.Er * self.er_mat     # Set dielectric constant

    def _calculate_z0(self):
        """Calculate transmission line impedance using analytical formula."""
        Er = self.Er
        w = self.trace_w
        t = self.dy
        b = self.sub_thk
        h1 = self.offset
        h2 = b - h1
        # Impedance of symmetric stripline with b = b and Er = 1
        z0_ss = self._symm_stripline(w, 1, t, b)
        # Impedance of stripline with b = h1 and Er = 1
        z0_ss1 = self._symm_stripline(w, 1, t, h1)
        # Impedance of stripline with b = h2 and Er = 1
        z0_ss2 = self._symm_stripline(w, 1, t, h2)
        z0_air = 2 * (z0_ss1 * z0_ss2) / (z0_ss1 + z0_ss2)
        quant1 = 0.0325*np.pi*z0_air**2
        quant2 = 0.5 - 0.5 * (2*h1 + t) / (h1 + h2 + t)
        quant3 = (t + w) / (h1 + h2 + t)
        delta_z0_air = quant1 * quant2**2.2 * quant3**2.9
        z0 = 1 / Er**0.5 * (z0_ss - delta_z0_air)
        return z0

    def _symm_stripline(self, w, Er, t, b):
        """Return impedance of symmetric stripline."""
        h = b / 2
        if w / b < 0.35:
            # Narrow signal conductor
            m = 6*h / (3*h + t)
            quant1 = t / (4*h + t)
            quant2 = np.pi * t / (4*(w + 1.1*t))
            w_eff = w + t/np.pi * np.log(Er / (quant1**2 + quant2**m)**0.5)
            quant4 = 8*h / (np.pi*w_eff)
            quant5 = 16*h / (np.pi*w_eff)
            quant6 = 16*h/(np.pi*w_eff)
            z0 = 60 / Er**0.5 * \
                np.log(1 + quant4*(quant5 + (quant6**2 + 6.27)**0.5))
        elif w / b >= 0.35:
            # Wide signal conductor
            quant1 = 2*b / (b-t)
            quant2 = b/(b-t) + 1
            quant3 = t / (b-t)
            quant4 = 1 / (1-t/b)**2 - 1
            cf = quant1*(np.log(quant2) - quant3*np.log(quant4))
            z0 = 94.15 / (Er**0.5 * (w/(b-t) + cf/np.pi))
        return z0


class DifferentialMicrostrip(FDAScenario):
    """Finite difference analysis of a microstrip differential pair."""

    name = 'DifferentialMicrostrip'         # Scenario name
    href = '/differential_microstrip'    # Webapp URL
    title = "Differential Microstrip"
    description = """
        This scenario simulates a microstrip differential pair.
        The differential impedance is calculated by applying a 1V differential
        voltage to the two conductors.  The common impedance is calculated by
        applying a common 1V voltage to the two conductors.
        """

    def __init__(self, Er=4.4, sub_thk=1e-3, trace_w=1.9e-3, spacing=0.2e-3,
                 dx=0.1e-3, dy=0.1e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = DifferentialMicrostrip.name
        self.Nx = round(trace_w * 6 / dx)  # Domain width 6 times trace width
        self.Ny = round(sub_thk * 6 / dy)  # Domain height in cells
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of stripline substrate
        self.trace_w = trace_w      # Stripline trace width
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        self.spacing = spacing      # Spacing between pair in mm
        self.differential = True
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Pos signal conductors
        self.neg_mat = np.zeros((self.Ny, self.Nx))     # Neg signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        spacing_idx = round(self.spacing / self.dx)   # Num grid cells spacing
        tr_w = round(self.trace_w / self.dx)          # Trace width in cells
        tr_h = round(self.sub_thk / self.dy)+1        # Trace y-offset in cells
        idx1 = Nx//2-int(np.ceil(spacing_idx/2))-tr_w   # Left trace start idx
        idx2 = idx1 + tr_w                              # Left trace stop idx
        idx3 = Nx//2+int(np.floor(spacing_idx/2))+1   # Right microstrip trace
        idx4 = idx3 + tr_w                            # Right trace stop idx
        if self.diff_mode == 'diff':
            self.signal_mat[-tr_h-1, idx1:idx2] = 0.5  # Pos microstrip trace
            self.neg_mat[-tr_h-1, idx3:idx4] = -0.5    # Neg microstrip trace
        else:
            self.signal_mat[-tr_h-1, idx1:idx2] = 1  # Pos microstrip trace
            self.neg_mat[-tr_h-1, idx3:idx4] = 1     # Pos (common) voltage
        self.ground_mat[-1, :] = 1                   # Bottom ground plane
        self.er_mat[-tr_h:, :] = self.Er             # Define substrate

    def _calculate_z0(self):
        """Calculate transmission line impedance using analytical formula."""
        er_eff, er_effo, er_effe, z0_surf, q4, q10 = self._calc_quantities()
        z0_odd = z0_surf * (er_eff / er_effo)**0.5 / \
            (1 - z0_surf/self.n0*q10*er_eff**0.5)
        z0_even = z0_surf * (er_eff / er_effe)**0.5 / \
            (1 - z0_surf/self.n0*q4*er_eff**0.5)
        z0_diff = 2 * z0_odd
        z0_comm = 0.5 * z0_even
        return z0_diff, z0_comm, z0_odd, z0_even

    def _calc_quantities(self):
        """Calculate quantities used in differential microstrip lines.

        Equations from "Accurate Wide-Range Design Equations for the Frequency-
        Dependent Characteristic of Parallel Coupled Microstrip Lines" by
        Kirschning and Jansen.
        """
        Er = self.Er
        w = self.trace_w
        t = self.dy
        h = self.sub_thk
        s = self.spacing
        if w/h < 1:
            er_eff = (Er+1)/2 + (Er-1)/2 * \
                ((w/(w+12*h))**0.5 + 0.04*(1-w/h)**2)
        elif w/h >= 1:
            er_eff = (Er+1)/2 + (Er-1)/2 * (w/(w+12*h))**0.5
        quant1 = t/(w*np.pi+1.1*t*np.pi)
        quant2 = 4*np.exp(1) / ((t/h)**2 + quant1**2)**0.5
        quant3 = (er_eff+1)/(2*er_eff)
        w_eff = w + t/np.pi*np.log(quant2)*quant3
        u = w/h
        a0 = 0.7287 * (er_eff - (Er+1)/2)*(1-np.exp(-0.179*u))**0.5
        b0 = 0.747*Er/(0.15 + Er)
        c0 = b0 - (b0 - 0.207)*np.exp(-0.414*u)
        d0 = 0.593 + 0.694*np.exp(-0.562*u)
        g = s/h
        v = u * (20 + g**2) / (10 + g**2) + g*np.exp(-g)
        quant1 = (v**4+(v/52)**2)/(v**4 + 0.432)
        quant2 = 1+(v/18.1)**3
        ae = 1+np.log(quant1)/49 + np.log(quant2)/18.7
        be = 0.564*((Er-0.9)/(Er+3))**0.053
        er_effe = (Er+1)/2 + (Er-1)/2*(1+10/v)**(-ae*be)
        er_effo = ((0.5*(Er+1)+a0-er_eff)*np.exp(-c0*g**d0)) + er_eff
        q1 = 0.8695*u**0.194
        q2 = 1 + 0.7519*g + 1.89*g**2.31
        q3 = 0.1975 + (16.6 + (8.4/g)**6)**-0.387 + 1 / \
            241 * np.log(g**10/(1+(g/3.4)**10))
        q4 = 2*(q1/q2)/(np.exp(-g)*u**q3+(2-np.exp(-g))*u**-q3)
        q5 = 1.794 + 1.14*np.log(1+(0.638/(g+0.517*g**2.43)))
        quant1 = g**10 / (1+(g/5.8)**10)
        quant2 = 1 + 0.598 * g**1.154
        q6 = 0.2305 + 1/281.3 * np.log(quant1) + 1/5.1 * np.log(quant2)
        q7 = (10 + 190*g**2) / (1 + 82.3*g**3)
        q8 = np.exp(-6.5-0.95*np.log(g)-(g/0.15)**5)
        q9 = np.log(q7) * (q8 + 1/16.5)
        q10 = (1/q2) * (q2*q4 - q5*np.exp(np.log(u)*q6*u**-q9))
        quant1 = self.n0 / (2*np.pi*2**0.5*(er_eff+1)**0.5)
        quant2 = 4*h / w_eff
        quant3 = (14*er_eff + 8)/(11*er_eff)
        quant4 = (er_eff+1)/(2*er_eff)
        temp = (16*(h/w_eff)**2 * quant3**2 + quant4*np.pi**2)**0.5
        z0_surf = quant1*np.log(1+quant2*(quant2*quant3+temp))
        return er_eff, er_effo, er_effe, z0_surf, q4, q10


class DifferentialStripline(FDAScenario):
    """Finite difference analysis of edge-coupled differential stripline."""

    name = 'DifferentialStripline'      # Scenario name
    href = '/differential_stripline'    # Webapp URL
    title = "Differential Stripline"
    description = """
        This scenario simulates edge-coupled differential stripline.
        A +0.5V voltage is applied to the top stripline, and a -0.5V voltage is
        applied to the bottom stripline.
        """

    def __init__(self, Er=4, sub_thk=0.9e-3, trace_w=0.35e-3, spacing=0.2e-3,
                 dx=0.025e-3, dy=0.025e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = DifferentialStripline.name
        self.Nx = round(trace_w * 6 / dx)  # Domain width 6 times trace width
        self.Ny = round(sub_thk / dy) + 2  # Two extra rows for ground planes
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of stripline substrate
        self.trace_w = trace_w      # Stripline trace width
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        self.spacing = spacing      # Spacing between pair in mm
        self.differential = True
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Signal conductors
        self.neg_mat = np.zeros((self.Ny, self.Nx))     # Neg signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        Ny = self.Ny
        spacing_idx = round(self.spacing / self.dx)  # Num grid cells spacing
        tr_w = round(self.trace_w / self.dx)         # Trace width in cells
        tr_h = Ny // 2                               # Trace y-offset in cells
        idx1 = Nx//2-int(np.ceil(spacing_idx/2))-tr_w   # Left trace start idx
        idx2 = idx1 + tr_w                           # Left trace stop idx
        idx3 = Nx//2+int(np.floor(spacing_idx/2))    # Right microstrip trace
        idx4 = idx3 + tr_w                           # Right trace stop idx
        if self.diff_mode == 'diff':
            self.signal_mat[tr_h, idx1:idx2] = 0.5   # Pos microstrip trace
            self.neg_mat[tr_h, idx3:idx4] = -0.5     # Neg microstrip trace
        else:
            self.signal_mat[tr_h, idx1:idx2] = 1     # Pos microstrip trace
            self.neg_mat[tr_h, idx3:idx4] = 1        # Pos (common) voltage
        self.ground_mat[0, :] = 1               # Top ground plane
        self.ground_mat[-1, :] = 1              # Bottom ground plane
        self.er_mat = self.Er * self.er_mat     # Set dielectric constant

    def _calculate_z0(self):
        """Return impedances of finite thickness edge-coupled stripline."""
        t = self.dy
        b = self.sub_thk
        s = self.spacing
        Er = self.Er
        z0_zero = self._zero_stripline()
        z0_finite = self._finite_stripline()
        z0_odd0, z0_even0 = self._zero_coupled_stripline()
        q1 = 1 / (1-t/b)
        q2 = 0.0885*Er/np.pi
        cf_finite = q2*(2*q1*np.log(q1+1) - (q1-1)*np.log(q1**2-1))
        cf_zero = q2*2*np.log(2)
        q3 = cf_finite/cf_zero
        z0_even = (z0_finite**-1 - q3*(z0_zero**-1 - z0_even0**-1))**-1
        if s/t >= 5:
            z0_odd = (z0_finite**-1 + q3*(z0_odd0**-1 - z0_zero**-1))**-1
        elif s/t < 5:
            z0_odd = (
                z0_odd0**-1
                + (z0_finite**-1 - z0_zero**-1)
                - 2/self.n0*(cf_finite/(0.0885*Er) - cf_zero/(0.0885*Er))
                + 2*t/(self.n0*s)
            )**-1
        z0_diff = 2 * z0_odd
        z0_comm = 0.5 * z0_even
        return z0_diff, z0_comm, z0_odd, z0_even

    def _elliptic(self, k, k_p):
        """Return approximation of elliptic integral function K/K'."""
        if k**2 < 0.5:
            elliptic = np.pi / np.log(2*(1+k_p**0.5)/(1-k_p**0.5))
        elif k**2 >= 0.5:
            elliptic = (1/np.pi)*np.log(2*(1+k**0.5)/(1-k**0.5))
        return elliptic

    def _zero_stripline(self):
        """Return characteristic impedance of zero thickness stripline."""
        w = self.trace_w
        b = self.sub_thk
        Er = self.Er
        if w/b < 0.35:
            w_eff_b = w/b - (0.35-w/b)**2
        elif w/b >= 0.35:
            w_eff_b = w/b
        z0 = (30*np.pi/Er**0.5) * (w_eff_b + 0.441)**-1
        return z0

    def _finite_stripline(self):
        """Return characteristic impedance of finite thickness stripline."""
        t = self.dy
        b = self.sub_thk
        w = self.trace_w
        Er = self.Er
        q1 = (1-(t/b))**-1 + 1
        q2 = 1 / (1-(t/b))**2 - 1
        c_f = (2/np.pi)*np.log(q1) - (t/(np.pi*b))*np.log(q2)
        if w/b < 0.35:
            w_eff_b = w/b - (0.35-w/b)**2 / (1 + 12*t/b)
        elif w/b >= 0.35:
            w_eff_b = w/b
        z0 = (30*np.pi/Er**0.5) * (1-t/b) / (w_eff_b + c_f)
        return z0

    def _zero_coupled_stripline(self):
        """Return impedances of zero thickness edge-coupled stripline."""
        b = self.sub_thk
        w = self.trace_w
        s = self.spacing
        Er = self.Er
        x = np.pi*(w+s)/(2*b)
        ke = np.tanh(np.pi*w/(w*b))*np.tanh(x)
        ko = np.tanh(np.pi*w/(2*b))/np.tanh(x)
        ke_p = (1-ke**2)**0.5
        ko_p = (1-ko**2)**0.5
        z0_even = 30*np.pi/Er**0.5 / self._elliptic(ke, ke_p)
        z0_odd = 30*np.pi/Er**0.5 / self._elliptic(ko, ko_p)
        return z0_odd, z0_even


class BroadsideStripline(FDAScenario):
    """Finite difference analysis of broadside differential stripline."""

    name = 'BroadsideStripline'    # Scenario name
    href = '/broadside_stripline'  # Webapp URL
    title = "Broadside Stripline"
    description = """
        This scenario simulates broadside-coupled differential stripline.
        A +0.5V voltage is applied to the top stripline, and a -0.5V voltage is
        applied to the bottom stripline.
        """

    def __init__(self, Er=4, sub_thk=0.9e-3, trace_w=0.35e-3, spacing=0.2e-3,
                 dx=0.025e-3, dy=0.025e-3):
        """Initialize constants for finite difference analysis of TL."""
        super().__init__()
        self.name = BroadsideStripline.name
        self.Nx = round(trace_w * 6 / dx)  # Domain width 6 times trace width
        self.Ny = round(sub_thk / dy) + 2  # Two extra rows for ground planes
        self.Er = Er                # Relative dielectric constant
        self.sub_thk = sub_thk      # Thickness of stripline substrate
        self.trace_w = trace_w      # Stripline trace width
        self.dx = dx                # Physical size of cell in X-direction
        self.dy = dy                # Physical size of cell in Y-direction
        self.spacing = spacing      # Spacing between pair in mm
        self.differential = True
        # Define geometry matrices
        self.signal_mat = np.zeros((self.Ny, self.Nx))  # Signal conductors
        self.neg_mat = np.zeros((self.Ny, self.Nx))     # Neg signal conductors
        self.ground_mat = np.zeros((self.Ny, self.Nx))  # Ground conductors
        self.er_mat = np.ones((self.Ny, self.Nx))       # Dielectric material

    def _draw_geometry(self):
        """Draw conductor and dielectric geometries."""
        Nx = self.Nx
        Ny = self.Ny
        spacing_idx = round(self.spacing / self.dy)  # Num grid cells spacing
        tr_w = round(self.trace_w / self.dx)         # Trace width in cells
        idx1 = Nx//2-round(tr_w/2)                   # Trace horiz start idx
        idx2 = idx1 + tr_w + 1                       # Trace horiz stop idx
        tr_h1 = Ny//2+int(np.ceil(spacing_idx/2))+1  # Bot trace vertical idx
        tr_h2 = Ny//2-int(np.floor(spacing_idx/2))   # Top trace vert idx
        if self.diff_mode == 'diff':
            self.signal_mat[tr_h1, idx1:idx2] = 0.5  # Positive stripline trace
            self.neg_mat[tr_h2, idx1:idx2] = -0.5    # Negative (diff) voltage
        else:
            self.signal_mat[tr_h1, idx1:idx2] = 1  # Positive microstrip trace
            self.neg_mat[tr_h2, idx1:idx2] = 1     # Positive (common) voltage
        self.ground_mat[0, :] = 1               # Top ground plane
        self.ground_mat[-1, :] = 1              # Bottom ground plane
        self.er_mat = self.Er * self.er_mat     # Set dielectric constant

    def _calculate_z0(self):
        """Calculate quantities used in broadside stripline.

        Bhartia, P., & Pramanick, P. (1988). Computer-aided design models for
        broadside-coupled striplines and millimeter-wave suspended substrate
        microstrip lines.
        """
        s = self.spacing
        b = self.sub_thk
        Er = self.Er
        z0_a, delta_z0_a = self._calc_quantities()
        z0_odd = (z0_a-delta_z0_a)/Er**0.5
        k = np.tanh(293.9*s/b/(z0_odd * Er**0.5))
        k_p = (1-k**2)**0.5
        if k**2 < 0.5:
            elliptic = np.pi / np.log(2*(1+k_p**0.5)/(1-k_p**0.5))
        elif k**2 >= 0.5:
            elliptic = (1/np.pi)*np.log(2*(1+k**0.5)/(1-k**0.5))
        z0_even = 60*np.pi/(Er**0.5*elliptic)
        z0_diff = 2 * z0_odd
        z0_comm = 0.5 * z0_even
        return z0_diff, z0_comm, z0_odd, z0_even

    def _calc_quantities(self):
        """Calculate quantities used in broadside striplines."""
        s = self.spacing
        b = self.sub_thk
        w = self.trace_w
        z0_a = self.n0 / (2*np.pi) * np.log(3*s/w + ((s/w)**2+1)**0.5)
        P = 270*(1-np.tanh(0.28+1.2*((b-s)/s)**0.5))
        quant1 = 0.48*(2*w/s-1)**0.5
        quant2 = (1+(b-s)/s)**2
        Q = 1 - np.arctanh(quant1/quant2)
        if w/s < 0.5:
            delta_z0_a = P
        elif w/s >= 0.5:
            delta_z0_a = P*Q
        return z0_a, delta_z0_a
