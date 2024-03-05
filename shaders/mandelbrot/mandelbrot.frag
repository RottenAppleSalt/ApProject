#version 330 core

in vec2 uvs;
out vec4 f_color;

uniform int ITERATIONS;

uniform float zoom;
uniform float cam_x;
uniform float cam_y;

uniform float wh_bl;
uniform float col_x;
uniform float col_y;
uniform float col_z;

void main() {
    // Normalized pixel coordinates (from 0 to 1)
    vec2 uv = uvs;
    
    // Constants
    float THRESHOLD = 4.;
    
    // Change coordinates
    float a = -1.95 * zoom;
    float b = 1.95 * zoom;
    float c = -1.1 * zoom;
    float d = 1.1 * zoom;
    
    uv.x = uv.x*abs(a-b)+a + cam_x;
    uv.y = uv.y*abs(c-d)+c + cam_y;

    // Z0
    vec2 z = vec2(0,0);
    
    // Curent pixel in mandelbrot?
    bool is_bounded = true;
    float age = 0.0;
    for(int i=0; i<ITERATIONS; i++) {
        if(z.x*z.x + z.y*z.y > THRESHOLD) {
            is_bounded = false;
            break;
        }
        
        // Calculate Zn+1
        vec2 z_new;
        
        z_new.x = z.x*z.x - z.y*z.y;
        z_new.y = 2.*z.x*z.y;
        
        z_new += uv;
        
        // Update z
        z = z_new;
        age++;
    }
    
    
    // Pixel color
    vec3 col = vec3(wh_bl);
    if(!is_bounded) {
        col = vec3(pow(age/float(ITERATIONS)*20., 0.75));
        col = vec3(col.x * col_x, col.y * col_y, col.z * col_z);
    }

    // Output to screen
    f_color = vec4(col,1.0);
}