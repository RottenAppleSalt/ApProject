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
iterations = ITERATIONS
filter_names = ['rainbow', 'sun', 'purple', 'inverted']
selected_filter = 0
selected_fractal = 0 

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

vert_shader_m, frag_shader_m = get_shaders('mandelbrot')
program_m = ctx.program(vertex_shader=vert_shader_m, fragment_shader=frag_shader_m)
render_object_m = ctx.vertex_array(program_m, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

vert_shader_j, frag_shader_j = get_shaders('julia')
program_j = ctx.program(vertex_shader=vert_shader_j, fragment_shader=frag_shader_j)
render_object_j = ctx.vertex_array(program_j, [(quad_buffer, '2f 2f', 'vert', 'texcoord')])

def surf_to_texture(surf):
    tex = ctx.texture(surf.get_size(), 4)
    tex.filter = (mgl.LINEAR, mgl.LINEAR)
    tex.swizzle = 'BGRA'
    tex.write(surf.get_view('1'))
    return tex

def apply_filter(time, filter, colors):
    try:
        # rainbow
        if filter == 0:
            colors[0].value = 0.0
            colors[1].value = math.sin(time)
            colors[2].value = math.sin(time + 2 * (math.pi / 3))
            colors[3].value = math.sin(time + 4 * (math.pi / 3))

        # sun
        elif filter == 1:
            colors[0].value = 0.05 * math.sin(2 * time) + 0.95
            colors[1].value = 0.1 * math.sin(3 * time + 2 * (math.pi / 3)) + 0.9
            colors[2].value = 0.1 * math.sin(4 * time + 4 * (math.pi / 3)) + 0.35
            colors[3].value = 0.07

        # purple
        elif filter == 2:
            colors[0].value = 0.03 * math.sin(time) + 0.05
            colors[1].value = 0.2 * math.sin(3 * time + 2 * (math.pi / 3)) + 0.6
            colors[2].value = 0.12
            colors[3].value = 0.1 * math.sin(4 * time + 4 * (math.pi / 3)) + 0.94

        # inverted
        elif filter == 3:
            colors[0].value = 1.0
            colors[1].value = math.sin(time + 4 * (math.pi / 3))
            colors[2].value = math.sin(time + 2 * (math.pi / 3))
            colors[3].value = math.sin(time)
    except:
        print('Your filter doesn\'t exist')

while True:
    # mouse_coords = pg.mouse.get_pos()
    time = pg.time.get_ticks() / 1000

    # program['time'].value = time

    camera_speed = 0.01 * zoom

    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            sys.exit()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q and iterations > 0:
                iterations -= 1

            if event.key == pg.K_e:
                iterations += 1

            if event.key == pg.K_1:
                selected_filter = 0  # rainbow

            if event.key == pg.K_2:
                selected_filter = 1  # sun

            if event.key == pg.K_3:
                selected_filter = 2  # purple

            if event.key == pg.K_4:
                selected_filter = 3  # inverted

            if event.key == pg.K_z:
                selected_fractal = 0 # mandelbrot

            if event.key == pg.K_x:
                selected_fractal = 1 # julia

    colors = [program_m['wh_bl'], program_m['col_x'], program_m['col_y'], program_m['col_z']]

    apply_filter(time, selected_filter, colors)

    keys = pg.key.get_pressed()

    if keys[pg.K_UP] or keys[pg.K_w]:
        camera_y -= camera_speed

    if keys[pg.K_DOWN] or keys[pg.K_s]:
        camera_y += camera_speed

    if keys[pg.K_RIGHT] or keys[pg.K_d]:
        camera_x += camera_speed

    if keys[pg.K_LEFT] or keys[pg.K_a]:
        camera_x -= camera_speed

    if keys[pg.K_EQUALS]:
        fake_zoom += 0.001

    if keys[pg.K_MINUS]:
        fake_zoom -= 0.001

    zoom = 1 / math.pow(fake_zoom, 10)

    print(zoom)

    frame_tex = surf_to_texture(display)

    frame_tex.use(0)
    program_m['ITERATIONS'].value = iterations

    program_m['zoom'].value = zoom
    program_m['cam_x'].value = camera_x
    program_m['cam_y'].value = camera_y

    if selected_fractal == 0:
        render_object_m.render(mode=mgl.TRIANGLE_STRIP)
    elif selected_fractal == 1:
        program_j['tex'].value == frame_tex
        render_object_j.render(mode=mgl.TRIANGLE_STRIP)

    pg.display.flip()

    frame_tex.release()

    delta = clock.tick(FPS)