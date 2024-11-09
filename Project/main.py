import pygame

# import the scene class
from cubeMap import FlattenCubeMap
from scene import Scene

from lightSource import LightSource

from blender import load_obj_file

from BaseModel import DrawModelFromMesh

from shaders import *

from ShadowMapping import *

from sphereModel import Sphere

from skyBox import *

from environmentMapping import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
import logging
import config  # Import the config module
from fireworks import create_fireworks, draw_fireworks


class main(Scene):
    def __init__(self):
       # Texture variables
        self.ground_texture = None
        Scene.__init__(self)

        self.light = LightSource(self, position=[3., 4., -3.])
        # self.load_textures()  # Correctly call load_textures without passing self
        self.shaders='phong'

        # for shadow map rendering
        self.shadows = ShadowMap(light=self.light)
        self.show_shadow_map = ShowTexture(self, self.shadows)
        create_fireworks()
        pioche_model = load_obj_file('models/eiffel_tower.obj')
        self.translationMatrix = np.matmul(translationMatrix([0,0,0]),scaleMatrix([0.03,0.03,0.03]))
        self.pioche_model = DrawModelFromMesh(
            scene=self, 
            M=self.translationMatrix, 
            mesh=pioche_model[0], 
            shader=ShadowMappingShader(shadow_map=self.shadows), name='pioche')
        self.animation_running = False
        self.current_angle = 0.0
        # meshes = load_obj_file('models/scene.obj')
        # self.add_models_list(
        #     [DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,-1,0]),scaleMatrix([0.5,0.5,0.5])), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='scene') for mesh in meshes]
        # )

        # table = load_obj_file('models/quad_table.obj')
        # self.table = [DrawModelFromMesh(scene=self, M=translationMatrix([0, -4, +0]), mesh=mesh, shader=ShadowMappingShader(shadow_map=self.shadows), name='table') for mesh in table]

        # box = load_obj_file('models/fluid_border.obj')
        # self.box = [DrawModelFromMesh(scene=self, M=translationMatrix([0,0,0]), mesh=mesh, shader=self.shaders, name='box') for mesh in box]

        # draw a skybox for the horizon
        self.skybox = SkyBox(scene=self)

        self.show_light = DrawModelFromMesh(scene=self, M=poseMatrix(position=self.light.position, scale=0.2), mesh=Sphere(material=Material(Ka=[10,10,10])), shader=FlatShader())

        self.environment = EnvironmentMappingTexture(width=400, height=400)
        # Load the Olympic rings model
        # Define the positions for the Olympic rings
        ring_positions = [
            [-2.1, -3, 0],   # Leftmost ring (moved further left)
            [0, -3, 0],      # Center left ring
            [2.1, -3, 0],    # Center right ring (moved further right)
            [-1.05, -4.6, 0], # Bottom left ring (moved further down and slightly left)
            [1.05, -4.6, 0]   # Bottom right ring (moved further down and slightly right)
        ]



        # Define scaling transformation for the rings
        scale_matrix = scaleMatrix([0.1, 0.1, 0.1])
        self.olympic_rings_model_mesh = load_obj_file('models/olympic_ring.obj')
        # Create each ring instance and position them accordingly
        self.olympic_rings_model = []
        for i, position in enumerate(ring_positions):
            # Calculate transformation matrix for each ring
            transformation_matrix = np.matmul(translationMatrix(position), scale_matrix)
            
            # Create the ring model with the transformation and shader
            ring_model = DrawModelFromMesh(
                scene=self,
                M=transformation_matrix,
                mesh=self.olympic_rings_model_mesh[0],  # Reuse the mesh for each ring
                shader=EnvironmentShader(map=self.environment),
                name=f'olympic_ring_{i}'
            )
            
            # Add the ring model to the list of Olympic rings
            self.olympic_rings_model.append(ring_model)
        self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(), mesh=Sphere(), shader=EnvironmentShader(map=self.environment))
        # Load ground texture
        # self.ground_texture = self.load_texture('textures/ground_texture.jpg')

        #self.sphere = DrawModelFromMesh(scene=self, M=poseMatrix(), mesh=Sphere(), shader=FlatShader())

        # bunny = load_obj_file('models/bunny_world.obj')
        # self.bunny = DrawModelFromMesh(scene=self, M=np.matmul(translationMatrix([0,0,0]), scaleMatrix([0.5,0.5,0.5])), mesh=bunny[0], shader=EnvironmentShader(map=self.environment))

        # environment box for reflections
        #self.envbox = EnvironmentBox(scene=self)

        # this object allows to visualise the flattened cube

        #self.flattened_cube = FlattenCubeMap(scene=self, cube=CubeMap(name='skybox/ame_ash'))
        self.flattened_cube = FlattenCubeMap(scene=self, cube=self.environment)

        self.show_texture = ShowTexture(self, Texture('lena.bmp'))

    def draw_shadow_map(self):
        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.pioche_model.draw()
        # # also all models from the table
        # for model in self.table:
        #     model.draw()

        # # and for the box
        # for model in self.box:
        #     model.draw()

    def draw_reflections(self):
        self.skybox.draw()
        self.pioche_model.draw()
        for model in self.models:
            model.draw()

        # # also all models from the table
        # for model in self.table:
        #     model.draw()

        # # and for the box
        # for model in self.box:
        #     model.draw()


    def draw(self, framebuffer=False):
        '''
        Draw all models in the scene
        :return: None
        '''

        # first we need to clear the scene, we also clear the depth buffer to handle occlusions
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # when using a framebuffer, we do not update the camera to allow for arbitrary viewpoint.
        if not framebuffer:
            self.camera.update()
        
        # first, we draw the skybox
        self.skybox.draw()
        # Draw the ground plane
        # self.draw_ground()
        # render the shadows
        self.shadows.render(self)
        draw_fireworks()
        # Update rotation angle if animation is running
        if self.animation_running:
            self.current_angle += np.radians(1)
            # Update the tower's model matrix to include rotation
            rotation_matrix = rotationMatrixY(self.current_angle)
            self.pioche_model.M = np.matmul(rotation_matrix,self.translationMatrix)
        

        # Draw the tower
        self.pioche_model.draw()
        # Draw each Olympic ring
        for ring in self.olympic_rings_model:
            ring.draw()
        # when rendering the framebuffer we ignore the reflective object
        if not framebuffer:
            #glEnable(GL_BLEND)
            #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
#            self.envbox.draw()
            #self.environment.update(self)
            #self.envbox.draw()

            self.environment.update(self)

            # self.bunny.draw()
            #self.sphere.draw()
            self.pioche_model.draw()
            #glDisable(GL_BLEND)

            # if enabled, show flattened cube
            self.flattened_cube.draw()

            # if enabled, show texture
            self.show_texture.draw()

            self.show_shadow_map.draw()

        # then we loop over all models in the list and draw them
        for model in self.models:
            model.draw()

        # # also all models from the table
        # for model in self.table:
        #     model.draw()

        # # and for the box
        # for model in self.box:
        #     model.draw()

        self.show_light.draw()

        # once we are done drawing, we display the scene
        # Note that here we use double buffering to avoid artefacts:
        # we draw on a different buffer than the one we display,
        # and flip the two buffers once we are done drawing.
        if not framebuffer:
            pygame.display.flip()

    def keyboard(self, event):
        '''
        Process additional keyboard events for this demo.
        '''
        Scene.keyboard(self, event)

        if event.key == pygame.K_c:
            if self.flattened_cube.visible:
                self.flattened_cube.visible = False
            else:
                print('--> showing cube map')
                self.flattened_cube.visible = True

        if event.key == pygame.K_t:
            if self.show_texture.visible:
                self.show_texture.visible = False
            else:
                print('--> showing texture map')
                self.show_texture.visible = True

        if event.key == pygame.K_m:
            if self.show_shadow_map.visible:
                self.show_shadow_map.visible = False
            else:
                print('--> showing shadow map')
                self.show_shadow_map.visible = True
        if event.key == pygame.K_s:
            print("animation_running")
            config.animation_running = True
            self.animation_running = True

        if event.key == pygame.K_f:
            print("animation_stopping")
            config.animation_running = False
            self.animation_running = False
        if event.key == pygame.K_1:
            print('--> using Flat shading')
            self.bunny.use_textures = True
            self.bunny.bind_shader('flat')

        if event.key == pygame.K_2:
            print('--> using Phong shading')
            self.bunny.use_textures = True
            self.bunny.bind_shader('phong')

        elif event.key == pygame.K_4:
            print('--> using original texture')
            self.bunny.shader.mode = 1

        elif event.key == pygame.K_6:
            self.bunny.mesh.material.alpha += 0.1
            print('--> bunny alpha={}'.format(self.bunny.mesh.material.alpha))
            if self.bunny.mesh.material.alpha > 1.0:
                self.bunny.mesh.material.alpha = 0.0

        elif event.key == pygame.K_7:
            print('--> no face culling')
            glDisable(GL_CULL_FACE)

        elif event.key == pygame.K_8:
            print('--> glCullFace(GL_FRONT)')
            glEnable(GL_CULL_FACE)
            glCullFace(GL_FRONT)

        elif event.key == pygame.K_9:
            print('--> glCullFace(GL_BACK)')
            glEnable(GL_CULL_FACE)
            glCullFace(GL_BACK)

        elif event.key == pygame.K_BACKQUOTE:
            if glIsEnabled(GL_DEPTH_TEST):
                print('--> disable GL_DEPTH_TEST')
                glDisable(GL_DEPTH_TEST)
            else:
                print('--> enable GL_DEPTH_TEST')
                glEnable(GL_DEPTH_TEST)
    # Draw the ground (a large dark grey plane)
    def draw_ground(self):
        glBindTexture(GL_TEXTURE_2D, ground_texture)
        glColor3f(1, 1, 1)
        glBegin(GL_QUADS)

        glTexCoord2f(0, 0)
        glVertex3f(-50, 0, -50)

        glTexCoord2f(10, 0)
        glVertex3f(50, 0, -50)

        glTexCoord2f(10, 10)
        glVertex3f(50, 0, 50)

        glTexCoord2f(0, 10)
        glVertex3f(-50, 0, 50)

        glEnd()

    def create_texture(self, surface, max_size=1024):
        width, height = surface.get_width(), surface.get_height()
        if width > max_size or height > max_size:
            surface = pygame.transform.scale(surface, (max_size, max_size))
            print(f"Resized texture to: {max_size}x{max_size}")

        texture_data = pygame.image.tostring(surface, "RGB", True)
        width, height = surface.get_width(), surface.get_height()

        print(f"Creating texture with dimensions: {width}x{height}")

        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        except Exception as e:
            print(f"Error during texture creation: {e}")
            raise

        return texture_id

    def load_textures():
        try:
            # Load ground texture
            texture_surface = pygame.image.load('assets/ground_texture.jpg')
            ground_texture = self.create_texture(texture_surface, max_size=1024)
        except pygame.error as e:
            print(f"Error loading textures: {e}")
            raise
        
    
if __name__ == '__main__':
    # initialises the scene object
    # scene = Scene(shaders='gouraud')
    scene = main()

    # starts drawing the scene
    scene.run()
