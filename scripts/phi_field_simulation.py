import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class PhiFieldSimulation:

    def __init__(self, grid_size=100, num_particles=10, num_rays=5):

        self.grid_size = grid_size
        self.center = grid_size // 2
        self.x = np.linspace(-1, 1, grid_size)
        self.y = np.linspace(-1, 1, grid_size)
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.R = np.sqrt(self.X**2 + self.Y**2)

        self.num_particles = num_particles
        self.particle_pos = np.random.uniform(-0.9, 0.9, (num_particles, 2))
        self.particle_vel = np.zeros_like(self.particle_pos)

        # Light ray setup (rays will be shown as red circles)
        self.num_rays = num_rays
        ray_y = np.linspace(-0.8, 0.8, num_rays)
        ray_x = -1 * np.ones_like(ray_y)
        self.ray_pos = np.stack((ray_x, ray_y), axis=1)

        # Initial velocity for rays; magnitude will be normalized
        self.initial_ray_speed = 0.02
        self.ray_vel = np.tile(np.array([self.initial_ray_speed, 0.0]), (num_rays, 1))

        self.fig, self.ax = plt.subplots()
        self.ax.set_title("\u03a6-Field: Gravity and Light Interaction")
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        # Initialize image and plots with labels for the legend
        self.im = self.ax.imshow(
            self.phi_field(0), cmap="viridis", origin="lower", extent=(-1, 1, -1, 1)
        )
        (self.particles_plot,) = self.ax.plot(
            [], [], "wo", markersize=4, label="Particle"
        )
        (self.rays_plot,) = self.ax.plot(
            [], [], "ro", markersize=4, label="Light Particle"
        )
        self.legend = self.ax.legend(loc="upper right")

    def phi_field(self, t):
        """Phi-field density function: lower near center (simulating mass)."""
        A = 1  # amplitude of field displacement
        return 1 - A / (self.R + 0.05) + 0.05 * np.sin(2 * np.pi * t / 50)

    def phi_gradient(self, t):
        """Compute the gradient of the phi_field at time t."""
        field = self.phi_field(t)
        dPhi_dx, dPhi_dy = np.gradient(field)
        return dPhi_dx, dPhi_dy

    def update(self, t):
        # Update background field
        field = self.phi_field(t)
        self.im.set_array(field)

        # Get time-dependent gradient
        dPhi_dx, dPhi_dy = self.phi_gradient(t)

        # Update particle motion with reflecting boundaries
        for i in range(self.num_particles):
            xi = int((self.particle_pos[i, 0] + 1) / 2 * (self.grid_size - 1))
            yi = int((self.particle_pos[i, 1] + 1) / 2 * (self.grid_size - 1))
            if 0 <= xi < self.grid_size and 0 <= yi < self.grid_size:
                ax_force = dPhi_dx[yi, xi] * 0.02
                ay_force = dPhi_dy[yi, xi] * 0.02
                self.particle_vel[i] += np.array([ax_force, ay_force])
            self.particle_pos[i] += self.particle_vel[i]
            for j in range(2):
                if self.particle_pos[i, j] < -1:
                    self.particle_pos[i, j] = -1
                    self.particle_vel[i, j] *= -1
                elif self.particle_pos[i, j] > 1:
                    self.particle_pos[i, j] = 1
                    self.particle_vel[i, j] *= -1
        self.particles_plot.set_data(self.particle_pos[:, 0], self.particle_pos[:, 1])

        # Update light rays with reflecting boundaries and normalize speed
        new_ray_pos = []
        for i in range(self.num_rays):
            xi = int((self.ray_pos[i, 0] + 1) / 2 * (self.grid_size - 1))
            yi = int((self.ray_pos[i, 1] + 1) / 2 * (self.grid_size - 1))
            if 0 <= xi < self.grid_size and 0 <= yi < self.grid_size:
                bend_y = dPhi_dy[yi, xi] * 0.01
                self.ray_vel[i, 1] += bend_y
            norm = np.linalg.norm(self.ray_vel[i])
            if norm != 0:
                self.ray_vel[i] = (self.ray_vel[i] / norm) * self.initial_ray_speed
            self.ray_pos[i] += self.ray_vel[i]
            for j in range(2):
                if self.ray_pos[i, j] < -1:
                    self.ray_pos[i, j] = -1
                    self.ray_vel[i, j] *= -1
                elif self.ray_pos[i, j] > 1:
                    self.ray_pos[i, j] = 1
                    self.ray_vel[i, j] *= -1
            new_ray_pos.append(self.ray_pos[i].copy())
        new_ray_pos = np.array(new_ray_pos)
        self.rays_plot.set_data(new_ray_pos[:, 0], new_ray_pos[:, 1])

        # Return updated artists, including the legend, so blit draws them
        return [self.im, self.particles_plot, self.rays_plot, self.legend]

    def run(self, frames=200, interval=50):
        # Either disable blit or include legend in returned artists as above
        self.ani = animation.FuncAnimation(
            self.fig, self.update, frames=frames, interval=interval, blit=True
        )
        plt.show()


if __name__ == "__main__":
    sim = PhiFieldSimulation()
    sim.run()
