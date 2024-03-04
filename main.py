import sys
import math

import pygame as pg
import moderngl as mgl

from array import array

from settings import *

pg.init()

screen = pg.display.set_mode(WIN_RES, pg.OPENGL | pg.DOUBLEBUF)
display = pg.Surface(WIN_RES)
ctx = mgl.create_context()

fake_zoom = 1.0
zoom = 1.0
camera_x = 0.0
camera_y = 0.0

clock = pg.time.Clock()

quad_buffer = ctx.buffer(data=array('f', [
    # position (x, y), uv coords (x, y)
    -1.0, 1.0, 0.0, 0.0,  # top left
    1.0, 1.0, 1.0, 0.0,   # top right
    -1.0, -1.0, 0.0, 1.0, # bottom left
    1.0, -1.0, 1.0, 1.0   # bottom right
]))

def get_shaders(shader_name):
    with open (f'./shaders/{shader_name}/{shader_name}.vert', 'r') as file:
        vert_shader = file.read()
        file.close()

    with open (f'./shaders/{shader_name}/{shader_name}.frag', 'r') as file:
        frag_shader = file.read()
        file.close()

    return vert_shader, frag_shader

vert_shader, frag_shader = get_shaders('mandelbrot')
program = ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
render_object = ctx.vertex_array(program, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (mgl.LINEAR, mgl.LINEAR)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

while True:
    # mouse_coords = pg.mouse.get_pos()
    time = pg.time.get_ticks() / 1000
    display.fill((0, 0, 0))

    camera_speed = 0.01 * zoom

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            sys.exit()

    keys = pg.key.get_pressed()

    if keys[pg.K_UP]:
        camera_y -= camera_speed

    if keys[pg.K_DOWN]:
        camera_y += camera_speed

    if keys[pg.K_RIGHT]:
        camera_x += camera_speed

    if keys[pg.K_LEFT]:
        camera_x -= camera_speed

    if keys[pg.K_EQUALS]:
        fake_zoom += 0.001

    if keys[pg.K_MINUS]:
        fake_zoom -= 0.001

    zoom = 1 / math.pow(fake_zoom, 10)

    frame_tex = surf_to_texture(display)

    frame_tex.use(0)
    program['ITERATIONS'].value = ITERATIONS

    program['zoom'].value = zoom
    program['cam_x'].value = camera_x
    program['cam_y'].value = camera_y

    sin_colors = [program['sin_x'], program['sin_y'], program['sin_z']]
    
    for i, sin_color in enumerate(sin_colors):
        sin_color.value = math.sin(time + (2 * i) * (math.pi / 3))

    print(pg.time.get_ticks() / 1000)
    print(zoom)
    print(camera_speed)
    
    render_object.render(mode=mgl.TRIANGLE_STRIP)

    pg.display.flip()

    frame_tex.release()

    delta = clock.tick(FPS)