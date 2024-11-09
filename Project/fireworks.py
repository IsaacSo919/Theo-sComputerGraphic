# fireworks.py

from OpenGL.GL import *
import random
import config  # Import the config module

def random_color():
    """Generate a random color with RGB values between 0.7 and 1.0 for red, and 0.0 to 1.0 for green and blue."""
    return (
        random.uniform(0.7, 1.0),  # Red component
        random.uniform(0.0, 1.0),  # Green component
        random.uniform(0.0, 1.0)   # Blue component
    )

def create_fireworks():
    """Initialize the fireworks array with random firework objects."""
    config.fireworks = []

    for _ in range(config.num_fireworks):
        start_x = random.uniform(-10, 10)
        start_y = random.uniform(5, 8)
        start_z = random.uniform(-60, -40)  # Adjust Z range as necessary

        color = random_color()

        config.fireworks.append({
            'x': start_x,
            'y': start_y,
            'z': start_z,
            'dx': random.uniform(-0.6, 0.6),
            'dy': random.uniform(0.4, 0.6),
            'dz': random.uniform(-0.2, 0.2),
            'exploding': False,
            'particles': [],
            'color': color
        })

def create_explosion(firework):
    """Create an explosion effect for a firework."""
    firework['particles'] = []
    for _ in range(config.explosion_particles):
        particle_color = firework['color']  # Use the firework's color for particles
        firework['particles'].append({
            'x': firework['x'],
            'y': firework['y'],
            'z': firework['z'],
            'dx': random.uniform(-0.2, 0.2),
            'dy': random.uniform(-0.2, 0.2),
            'dz': random.uniform(-0.2, 0.2),
            'life': config.particle_life,
            'color': particle_color  # Store the color in each particle
        })

def draw_fireworks():
    """Draw and animate fireworks in the scene."""
    # Save OpenGL state before making changes
    glPushAttrib(GL_ALL_ATTRIB_BITS)

    # Set up OpenGL state specifically for fireworks
    setup_fireworks_state()

    for firework in config.fireworks:
        if not firework['exploding']:
            glBegin(GL_LINES)
            glColor4f(*firework['color'], 1.0)  # Use the firework's color
            glVertex3f(firework['x'], firework['y'], firework['z'])
            glVertex3f(
                firework['x'] + firework['dx'],
                firework['y'] + firework['dy'],
                firework['z'] + firework['dz']
            )
            glEnd()

            if config.animation_running:
                firework['x'] += firework['dx']
                firework['y'] += firework['dy']
                firework['z'] += firework['dz']

                if firework['y'] > config.max_height:
                    firework['exploding'] = True
                    create_explosion(firework)

        else:
            glPointSize(2.0)
            glBegin(GL_POINTS)
            for particle in firework['particles']:
                alpha = particle['life'] / config.particle_life  # Fade out effect
                glColor4f(*particle['color'], alpha)  # Set color with alpha
                glVertex3f(particle['x'], particle['y'], particle['z'])
            glEnd()

            if config.animation_running:
                for particle in firework['particles']:
                    particle['x'] += particle['dx']
                    particle['y'] += particle['dy']
                    particle['z'] += particle['dz']
                    particle['life'] -= 1

                # Remove expired particles
                firework['particles'] = [p for p in firework['particles'] if p['life'] > 0]

                if not firework['particles']:
                    config.fireworks.remove(firework)
                    config.fireworks.append(create_new_firework())  # Create a new firework

    # Restore OpenGL state after rendering fireworks
    glPopAttrib()

def create_new_firework():
    """Create a new firework object for display."""
    start_x = random.choice([-15, 15])
    color = config.BRIGHT_ORANGE  # Use a defined color for consistency
    return {
        'x': start_x,
        'y': random.uniform(5, 8),
        'z': random.uniform(-60, -40),  # Adjust Z range
        'dx': random.uniform(-0.2, 0.2),
        'dy': random.uniform(0.5, 0.7),   # Adjust vertical movement
        'dz': random.uniform(-0.1, 0.1),
        'exploding': False,
        'particles': [],
        'color': color
    }

def setup_fireworks_state():
    """Set up OpenGL state specifically for rendering fireworks."""
    glEnable(GL_BLEND)  # Enable blending for transparency
    glBlendFunc(GL_SRC_ALPHA, GL_ONE)  # Additive blending for vibrant colors
    glDisable(GL_LIGHTING)  # Disable lighting for fireworks
    glDisable(GL_TEXTURE_2D)
