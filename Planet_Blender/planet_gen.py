import bpy
import math
import random
import hashlib
from mathutils import Vector
from pathlib import Path

pl_rade = 12.7     
pl_eqt = 210.84          
st_lum= 0.1939
pl_orbsmax = 2.2*20
st_teff=5945.0
P_TYPE = 'Jovian'
P_TYPE_TEMP = 'Hot'
P_NAME = 'HD 2039 b'

#Generate seed based on planet name
def get_seed(P_NAME):
    hash_bytes = hashlib.sha256(
        P_NAME.encode("utf-8")
    ).digest()

    return int.from_bytes(hash_bytes[:8], "big")

seed = get_seed(P_NAME)
rng = random.Random(seed)

#Color Palettes based on Planet Type
PALETTES = {
    "Terran": [
        (0.76, 0.11, 0.1, 1.0),
        (0.6431, 0.2471, 0.1843, 1.0),
        (0.8471, 0.3686, 0.2353, 1.0)
    ],

    "Superterran": [
        (0.28, 0.10, 0.08, 1.0),  
        (0.7412, 0.6000, 0.5412, 1.0), 
        (0.65, 0.45, 0.18, 1.0), 
        (0.25, 0.20, 0.18, 1.0),  
    ],

    "Subterran": [
        (0.0784, 0.0863, 0.1725, 1.0),
        (0.42, 0.25, 0.12, 1.0),
        (0.0784, 0.0863, 0.1725, 1.0),
        (0.7176, 0.7882, 0.8157, 1.0),
    ],

    "Neptunian": [
        (0.9137, 0.3529, 0.3255, 1.0),
        (0.0627, 0.1725, 0.3529, 1.0),
        (0.2431, 0.2667, 0.9412, 1.0),
        (0.3686, 0.5882, 0.9569, 1.0),
    ],

    "Jovian": [
        (0.3412, 0.1843, 0.1569, 1.0),  
        (0.8431, 0.4431, 0.2000, 1.0),  
        (0.8471, 0.7608, 0.6941, 1.0),  
        (0.75, 0.65, 0.38, 1.0),
    ],
}

#Color Palette modifications based on Temperature
planet_palette  = PALETTES[P_TYPE]
temperature = pl_eqt

def vary_color(color, rng, amount=0.15):

    r, g, b, a = color

    r *= rng.uniform(1.0 - amount, 1.0 + amount)
    g *= rng.uniform(1.0 - amount, 1.0 + amount)
    b *= rng.uniform(1.0 - amount, 1.0 + amount)

    return (min(1.0, max(0.0, r)),min(1.0, max(0.0, g)),min(1.0, max(0.0, b)),a)

temperature_factor = max(0.0,min(1.0, (temperature - 600.0) / 1000.0))

def temperature_shift(color, factor):

    r, g, b, a = color

    r += 0.2 * factor
    b -= 0.2 * factor

    return (min(1.0, max(0.0, r)),min(1.0, max(0.0, g)),min(1.0, max(0.0, b)),a)

final_palette = [temperature_shift(vary_color(color, rng),temperature_factor) for color in PALETTES[P_TYPE]]
selected_palette = rng.choice(final_palette)

#REMOVE OBJECTS
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

#BACKGROUND
image = bpy.data.images.load(
    bpy.path.abspath("//Img/Space.jpg")
)

scene = bpy.context.scene
scene.world.use_nodes = True

nodes = scene.world.node_tree.nodes
links = scene.world.node_tree.links

nodes.clear()

output = nodes.new("ShaderNodeOutputWorld")
bg = nodes.new("ShaderNodeBackground")
tex = nodes.new("ShaderNodeTexEnvironment")

tex.image = image

links.new(tex.outputs["Color"], bg.inputs["Color"])
links.new(bg.outputs["Background"], output.inputs["Surface"])

bg.inputs["Strength"].default_value = 1.0

#PLANET

bpy.ops.mesh.primitive_uv_sphere_add(
    segments=64,
    ring_count=32,
    radius=pl_rade,
    location=(0, 0, 0)
)

planet = bpy.context.object
planet.name = "Planet"
obj = bpy.context.active_object
bpy.ops.object.shade_smooth()

#Camera
camera_distance = pl_rade * 20.0
bpy.ops.object.camera_add()
camera = bpy.context.object
camera.name = "Camera"
camera.location = (
    planet.location.x + camera_distance,
    planet.location.y + camera_distance,
    planet.location.z + camera_distance
)
direction = planet.location - camera.location
camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

camera.data.lens = 300

bpy.context.scene.camera = camera

#LIGHT FROM SUN

def kelvin_to_rgb(kelvin):
    k = kelvin / 100.0

    if k <= 66:
        r = 255
        g = 99.4708025861 * math.log(k) - 161.1195681661
        b = 0 if k <= 19 else 138.5177312231 * math.log(k - 10) - 305.0447927307
    else:
        r = 329.698727446 * ((k - 60) ** -0.1332047592)
        g = 288.1221695283 * ((k - 60) ** -0.0755148492)
        b = 255

    return (
        max(0, min(255, r)) / 255,
        max(0, min(255, g)) / 255,
        max(0, min(255, b)) / 255,
    )


L = st_lum

bpy.ops.object.light_add(
    type='POINT',
    location=(pl_orbsmax, 0, 0)
)

light = bpy.context.object
light.name = "Star Light"

light.data.energy = L * 100000

light.data.color = kelvin_to_rgb(st_teff)
constraint = light.constraints.new(type='TRACK_TO')
constraint.target = planet
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'


# Atmosphere Generation
def generateAtmosphere(planet):

    bpy.ops.object.empty_add( type='PLAIN_AXES', location=(0, 0, 0) )
    empty = bpy.context.object
    empty.name = "Planet_Empty"
    constraint = empty.constraints.new(type='TRACK_TO')
    constraint.target = light
    planet_matrix = planet.matrix_world.copy()
    planet.parent = empty
    bpy.ops.mesh.primitive_ico_sphere_add( radius=pl_rade * 1.01-0.02*temperature_factor, location=planet.location, subdivisions=6 )
    atmosphere = bpy.context.object
    bpy.ops.object.shade_smooth()
    atmosphere_matrix = atmosphere.matrix_world.copy()
    mat=bpy.data.materials.new(name='Atmosphere Materials')
    mat.use_nodes = True
    planet.parent = empty
    atmosphere.parent = empty
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    #Nodes
    texcoord_atm = nodes.new("ShaderNodeTexCoord")
    seperate_xyz_atm=nodes.new("ShaderNodeSeparateXYZ")
    color_ramp_atm = nodes.new("ShaderNodeValToRGB")
    color_ramp_atm2 = nodes.new("ShaderNodeValToRGB")
    layer_weight =nodes.new("ShaderNodeLayerWeight")
    emission_atm =nodes.new("ShaderNodeEmission")
    mix_atm_darken=nodes.new('ShaderNodeMixRGB')
    mix_atm = nodes.new("ShaderNodeMixShader")
    mix_atm_darken.blend_type = 'DARKEN'
    transparent_bsdf = nodes.new("ShaderNodeBsdfTransparent")
    output_atm = nodes.new("ShaderNodeOutputMaterial")
    mat.blend_method = 'BLEND'
    #Node Links
    links.new(texcoord_atm.outputs['Object'],seperate_xyz_atm.inputs['Vector'])
    links.new(seperate_xyz_atm.outputs['Z'],color_ramp_atm.inputs['Fac'])
    links.new(color_ramp_atm.outputs['Color'],mix_atm_darken.inputs['Fac'])
    links.new(color_ramp_atm2.outputs['Color'],mix_atm_darken.inputs['Color1'])
    links.new(layer_weight.outputs['Facing'],color_ramp_atm2.inputs['Fac'])
    links.new(mix_atm_darken.outputs['Color'],mix_atm.inputs[0])
    links.new(emission_atm.outputs['Emission'],mix_atm.inputs[2])
    links.new(transparent_bsdf.outputs['BSDF'],mix_atm.inputs[1])
    links.new(mix_atm.outputs['Shader'],output_atm.inputs['Surface'])
    
    ramp_atm=color_ramp_atm.color_ramp
    right_slider_atm=ramp_atm.elements[1]
    right_slider_atm.position=0.1
    layer_weight.inputs["Blend"].default_value = 0.1
    mix_atm_darken.inputs['Color2'].default_value=(0,0,0,1.0)
    texcoord_atm.object = empty
    emission_atm.inputs["Color"].default_value=selected_palette
    emission_atm.inputs["Strength"].default_value=25
    mix_atm.inputs["Fac"].default_value=0.4
    ramp_atm2=color_ramp_atm2.color_ramp
    left_slider_atm2=ramp_atm2.elements[0]
    right_slider_atm2=ramp_atm2.elements[1]
    right_slider_atm2.color=(0.06,0.06,0.06,1)
    left_slider_atm2.position=0.065
    
    atmosphere.data.materials.append(mat)


# Rocky Planet Generation

def createRockyPlanet(planet):
    old_empty = bpy.data.objects.get("Planet_Texture_Empty")
    if old_empty: 
        bpy.data.objects.remove(old_empty, do_unlink=True)
    old_atmosphere = bpy.data.objects.get("Atmosphere")
    if old_atmosphere:
        bpy.data.objects.remove(old_atmosphere, do_unlink=True)
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Icosphere"):
            bpy.data.objects.remove(obj, do_unlink=True)
    mat=bpy.data.materials.new(name='Planet Materials')
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    #Nodes
    texcoord = nodes.new("ShaderNodeTexCoord")
    output_planet_texture = nodes.new("ShaderNodeOutputMaterial")
    
    bump = nodes.new("ShaderNodeBump")
    bump_second = nodes.new("ShaderNodeBump")
    
    noise_main_surface = nodes.new("ShaderNodeTexNoise")
    color_ramp_main_surface = nodes.new("ShaderNodeValToRGB")
    mix_main_surface=nodes.new('ShaderNodeMixRGB')
    
    noise_land_detail = nodes.new("ShaderNodeTexNoise")
    color_ramp_land_detail =nodes.new("ShaderNodeValToRGB")
    bump_land_detail = nodes.new("ShaderNodeBump")
    magic_texture_land_detail = nodes.new("ShaderNodeTexMagic")

    noise_mountains=nodes.new("ShaderNodeTexNoise")
    voronoi_mountains = nodes.new("ShaderNodeTexVoronoi")
    math_mountains=nodes.new('ShaderNodeMath')
    
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    
    noise_small_craters=nodes.new("ShaderNodeTexNoise")
    mix_small_craters=nodes.new('ShaderNodeMixRGB')
    voronoi_small_craters = nodes.new("ShaderNodeTexVoronoi")
    bump_small_craters = nodes.new("ShaderNodeBump")
    color_ramp_small_craters=nodes.new("ShaderNodeValToRGB")
    color_ramp_small_craters2=nodes.new("ShaderNodeValToRGB")
    
    hsv_water=nodes.new("ShaderNodeHueSaturation")
    color_ramp_water=nodes.new("ShaderNodeValToRGB")
    mix_main_water=nodes.new('ShaderNodeMixRGB')
    bsdf_water = nodes.new("ShaderNodeBsdfPrincipled")
    mix_shader_water = nodes.new("ShaderNodeMixShader")
    
    noise_large_craters=nodes.new("ShaderNodeTexNoise")
    voronoi_large_craters = nodes.new("ShaderNodeTexVoronoi")
    mix_large_craters=nodes.new('ShaderNodeMixRGB')
    bump_large_craters = nodes.new("ShaderNodeBump")
    color_ramp_large_craters=nodes.new("ShaderNodeValToRGB")
    color_ramp_large_craters2=nodes.new("ShaderNodeValToRGB")

    bsdf_clouds = nodes.new("ShaderNodeBsdfPrincipled")
    noise_clouds=nodes.new("ShaderNodeTexNoise")
    color_ramp_clouds=nodes.new("ShaderNodeValToRGB")
    hsv_clouds=nodes.new("ShaderNodeHueSaturation")
    noise_clouds2=nodes.new("ShaderNodeTexNoise")
    color_ramp_clouds2=nodes.new("ShaderNodeValToRGB")
    hsv_clouds2=nodes.new("ShaderNodeHueSaturation")
    mix_darken_clouds=nodes.new("ShaderNodeMix")
    mix_darken_clouds.data_type = 'RGBA'
    mix_darken_clouds.blend_type = 'DARKEN'
    mix_shader_clouds = nodes.new("ShaderNodeMixShader")
    #viewer=nodes.new("ShaderNodeViewer")
    
    #Node Links
    links.new(texcoord.outputs['Object'],noise_main_surface.inputs['Vector'])
    links.new(noise_main_surface.outputs['Fac'],color_ramp_main_surface.inputs['Fac'])
    links.new(color_ramp_main_surface.outputs['Color'],bsdf.inputs['Base Color'])
    links.new(texcoord.outputs['Object'],noise_mountains.inputs['Vector'])
    links.new(noise_mountains.outputs['Color'],voronoi_mountains.inputs['Vector'])
    links.new(voronoi_mountains.outputs['Distance'],math_mountains.inputs['Value'])
    links.new(math_mountains.outputs['Value'],mix_main_surface.inputs['Fac'])
    links.new(color_ramp_main_surface.outputs['Color'],mix_main_surface.inputs['Color2'])
    links.new(mix_main_surface.outputs['Color'],bsdf.inputs['Base Color'])
    links.new(voronoi_small_craters.outputs['Distance'],color_ramp_small_craters.inputs['Fac'])
    links.new(texcoord.outputs['Object'],voronoi_small_craters.inputs['Vector'])
    links.new(texcoord.outputs['Object'],noise_small_craters.inputs['Vector'])
    links.new(noise_small_craters.outputs['Fac'],color_ramp_small_craters2.inputs['Fac'])
    links.new(color_ramp_small_craters2.outputs['Color'],mix_small_craters.inputs['Color2'])
    links.new(color_ramp_small_craters.outputs['Color'],mix_small_craters.inputs['Color1'])
    links.new(texcoord.outputs['Object'],noise_land_detail.inputs['Vector'])
    links.new(noise_land_detail.outputs['Color'],magic_texture_land_detail.inputs['Vector'])
    links.new(magic_texture_land_detail.outputs['Color'],color_ramp_land_detail.inputs['Fac'])
    links.new(texcoord.outputs['Object'],voronoi_large_craters.inputs['Vector'])
    links.new(texcoord.outputs['Object'],noise_large_craters.inputs['Vector'])
    links.new(voronoi_large_craters.outputs['Distance'],color_ramp_large_craters.inputs['Fac'])
    links.new(noise_large_craters.outputs['Fac'],color_ramp_large_craters2.inputs['Fac'])
    links.new(color_ramp_large_craters2.outputs['Color'],mix_large_craters.inputs['Fac'])
    links.new(color_ramp_large_craters.outputs['Color'],mix_large_craters.inputs['Color1'])
    links.new(bsdf.outputs['BSDF'],mix_shader_water.inputs[2])
    #Cloud Links
    links.new(texcoord.outputs['Object'],noise_clouds.inputs['Vector'])
    links.new(noise_clouds.outputs['Factor'],hsv_clouds.inputs['Color'])
    links.new(hsv_clouds.outputs['Color'],color_ramp_clouds.inputs['Factor'])
    links.new(texcoord.outputs['Object'],noise_clouds2.inputs['Vector'])
    links.new(noise_clouds2.outputs['Factor'],hsv_clouds2.inputs['Color'])
    links.new(hsv_clouds2.outputs['Color'],color_ramp_clouds2.inputs['Factor'])
    links.new(color_ramp_clouds.outputs['Color'],mix_darken_clouds.inputs['A'])
    links.new(color_ramp_clouds2.outputs['Color'],mix_darken_clouds.inputs['B'])
    links.new(bsdf_clouds.outputs['BSDF'],mix_shader_clouds.inputs[1])
    links.new(mix_darken_clouds.outputs['Result'],mix_shader_clouds.inputs['Factor'])
    links.new(mix_shader_clouds.outputs[0],output_planet_texture.inputs['Surface'])
    #Bump Links
    links.new(bump_land_detail.outputs['Normal'],bump_second.inputs['Normal'])
    links.new(bump.outputs['Normal'],bump_large_craters.inputs['Normal'])
    links.new(bump_second.outputs['Normal'],bump.inputs['Normal'])
    links.new(math_mountains.outputs['Value'],bump.inputs['Height'])
    links.new(mix_main_surface.outputs['Color'],bump_second.inputs['Height'])
    links.new(mix_small_craters.outputs['Color'],bump_small_craters.inputs['Height'])
    links.new(bump_small_craters.outputs['Normal'],bump_land_detail.inputs['Normal'])
    links.new(color_ramp_land_detail.outputs['Color'],bump_land_detail.inputs['Height'])
    links.new(bump_large_craters.outputs['Normal'],bsdf.inputs['Normal'])
    links.new(mix_large_craters.outputs['Color'],bump_large_craters.inputs['Height'])
    #Water Links
    links.new(magic_texture_land_detail.outputs['Color'],hsv_water.inputs['Color'])
    links.new(hsv_water.outputs['Color'],color_ramp_water.inputs['Factor'])
    links.new(color_ramp_water.outputs['Color'],mix_main_water.inputs['Factor'])
    links.new(mix_main_water.outputs['Color'],bsdf_water.inputs['Base Color'])
    links.new(bsdf_water.outputs['BSDF'],mix_shader_water.inputs[1])
    links.new(color_ramp_land_detail.outputs['Color'],mix_shader_water.inputs[0])
    links.new(mix_shader_water.outputs['Shader'],mix_shader_clouds.inputs[2])
    #Roughness
    bsdf.inputs["Roughness"].default_value=0.7
    
    #Water/Lava
    lava_factor = max(0.0, min(1.0, (pl_eqt - 800.0) / 400.0))
    water_color = (0.1020, 0.1608, 0.7373, 1.0)
    lava_color = (1.0000, 0.0627, 0.0000, 1.0)
    min_emission = 3
    max_emission = 20.0
    
    emission_strength = (
    min_emission
    + (max_emission - min_emission) * temperature_factor
    )
    if(pl_eqt>1200):
        links.new(mix_main_water.outputs['Color'],bsdf_water.inputs['Emission Color'])
        bsdf_water.inputs["Emission Strength"].default_value = emission_strength
        
    
    def lerp_color(c1, c2, factor):
        return tuple(
            c1[i] + (c2[i] - c1[i]) * factor
            for i in range(4)
        )

    mix_main_water.inputs[1].default_value = lerp_color(
        water_color,
        lava_color,
        lava_factor
    )
 
    hsv_water.inputs['Value'].default_value=random.uniform(0.5,1.7)
    mix_main_water.inputs[1].default_value=lerp_color(water_color,lava_color,lava_factor)
    mix_main_water.inputs[2].default_value=lerp_color(water_color,lava_color,lava_factor)
    ##Color Ramp
    ramp_water=color_ramp_water.color_ramp
    left_slider_water=ramp_water.elements[0]
    right_slider_water=ramp_water.elements[1]
    right_slider_water.position=0.5
    left_slider_water.position=0.44
    
    #Mountains
    voronoi_mountains.distance='MINKOWSKI'
    voronoi_mountains.inputs['Scale'].default_value=random.uniform(1.0,2.0)
    noise_mountains.inputs['Scale'].default_value=2.0
    noise_mountains.inputs['Detail'].default_value=15.0
    math_mountains.operation = 'TANH'
    mix_main_surface.inputs['Color2'].default_value=(1.0, 0.5, 0.0, 1.0)
    bump.inputs['Strength'].default_value=random.uniform(0.1,1)
    bump.inputs['Distance'].default_value=random.uniform(1,3)
    bump.invert = True
    bump_second.inputs['Strength'].default_value=random.uniform(0.1,bump.inputs['Strength'].default_value)
    bump_second.inputs['Distance'].default_value=random.uniform(1,bump.inputs['Strength'].default_value)
    ##Color Ramp
    ramp_mountains=color_ramp_main_surface.color_ramp
    right_slider_mountains=ramp_mountains.elements[1]
    right_slider_mountains.position=0.5
    right_slider_mountains.color = selected_palette
    second_stop=ramp_mountains.elements.new(random.uniform(right_slider_mountains.position,1))
    noise_small_craters.inputs['Detail'].default_value=15.0
    noise_small_craters.inputs['Roughness'].default_value=0.6
    noise_small_craters.inputs['Scale'].default_value=5.0
    #Small Craters
    voronoi_small_craters.inputs['Scale'].default_value=random.uniform(140,200)
    mix_small_craters.blend_type="LIGHTEN"
    mix_small_craters.inputs['Fac'].default_value=1.0
    bump_small_craters.inputs['Strength'].default_value=random.uniform(0.1,0.3)
    bump_small_craters.inputs['Distance'].default_value=random.uniform(1,2)
    ##Color Ramp
    ramp_small_craters=color_ramp_small_craters.color_ramp
    left_slider=ramp_small_craters.elements[0]
    right_slider=ramp_small_craters.elements[1]
    right_slider.position=random.uniform(0.3,0.5)
    left_slider.position=random.uniform(0.1,0.3)
    
    ramp_small_craters2=color_ramp_small_craters2.color_ramp
    left_slider2=ramp_small_craters2.elements[0]
    right_slider2=ramp_small_craters2.elements[1]
    right_slider2.position=random.uniform(0.5,0.55)
    left_slider2.position=random.uniform(0.45,0.5)
    
    #Land Detail
    magic_texture_land_detail.turbulence_depth =random.randint(6,14)
    magic_texture_land_detail.inputs['Scale'].default_value=random.uniform(1.5,4.0)
    noise_land_detail.inputs['Scale'].default_value=random.uniform(4.0,7.0)
    noise_land_detail.inputs['Detail'].default_value=15.0
    noise_land_detail.inputs['Roughness'].default_value=0.6
    bump_land_detail.inputs['Strength'].default_value=bump_second.inputs['Strength'].default_value*0.15
    bump_land_detail.inputs['Distance'].default_value=bump_second.inputs['Distance'].default_value*0.15
    ##Color Ramp
    ramp_land_detail =color_ramp_land_detail.color_ramp
    left_slider_land_detail=ramp_land_detail.elements[0]
    right_slider_land_detail=ramp_land_detail.elements[1]
    left_slider_land_detail.position=random.uniform(0.5,0.55)
    right_slider_land_detail.position=random.uniform(0.6,0.9)
    

    
    #Large Craters
    mix_large_craters.blend_type="LIGHTEN"
    voronoi_large_craters.inputs['Scale'].default_value=random.uniform(20,70)
    noise_large_craters.inputs['Scale'].default_value=random.uniform(14,30)
    mix_large_craters.inputs['Color2'].default_value=(1.0, 1.0, 1.0, 1.0)
    bump_large_craters.inputs['Strength'].default_value=random.uniform(0.3,0.6)
    ##Color Ramp
    ramp_large_craters=color_ramp_large_craters.color_ramp
    left_slider_large_craters=ramp_large_craters.elements[0]
    right_slider_large_craters=ramp_large_craters.elements[1]
    right_slider_large_craters.position=random.uniform(0.3,0.5)
    left_slider_large_craters.position=random.uniform(0.1,0.3)
    
    ramp_large_craters2=color_ramp_large_craters2.color_ramp
    left_slider_large_craters2=ramp_large_craters2.elements[0]
    right_slider_large_craters2=ramp_large_craters2.elements[1]
    right_slider_large_craters2.position=random.uniform(0.5,0.55)
    left_slider_large_craters2.position=random.uniform(0.45,0.5)
    
    #Clouds
    temp_factor = 1.0 / (
    1.0 + math.exp((temperature - 600.0) / 150.0)
    )

    base_coverage = 0.30 + 0.80 * temp_factor

    cloud_coverage = base_coverage + rng.uniform(-0.15, 0.15)
    cloud_coverage = max(0.0, min(1.0, cloud_coverage))
    noise_clouds.noise_dimensions='4D'
    noise_clouds2.noise_dimensions='4D'
    noise_clouds.inputs['W'].default_value=random.uniform(0,10)
    noise_clouds.inputs['Scale'].default_value=random.uniform(10,20)
    noise_clouds.inputs['Detail'].default_value=random.uniform(13,20)
    noise_clouds.inputs['Roughness'].default_value=random.uniform(0.8,1)
    noise_clouds.inputs['Distortion'].default_value=random.uniform(0.5,0.7)
    noise_clouds2.inputs['W'].default_value=random.uniform(0,10)
    noise_clouds2.inputs['Scale'].default_value=random.uniform(10,13)
    noise_clouds2.inputs['Detail'].default_value=random.uniform(10,20)
    noise_clouds2.inputs['Roughness'].default_value=random.uniform(0.6,0.8)
    noise_clouds2.inputs['Lacunarity'].default_value=random.uniform(3,5)
    noise_clouds2.inputs['Distortion'].default_value=random.uniform(0.8,1)
    bsdf_clouds.inputs['Base Color'].default_value=(1.0,1.0,1.0,1.0)
    bsdf_clouds.inputs['Roughness'].default_value=1.0
    hsv_clouds.inputs['Value'].default_value =cloud_coverage
    hsv_clouds2.inputs['Value'].default_value =cloud_coverage
    ##Color Ramp
    ramp_clouds=color_ramp_clouds.color_ramp
    left_slider_clouds=ramp_clouds.elements[0]
    left_slider_clouds.color= (1,1,1,1)
    right_slider_clouds=ramp_clouds.elements[1]
    right_slider_clouds.color= (0,0,0,1)
    right_slider_clouds.position=random.uniform(0.6,0.7)
    left_slider_clouds.position=random.uniform(0.5,0.6)
    ramp_clouds2=color_ramp_clouds2.color_ramp
    left_slider_clouds2=ramp_clouds2.elements[0]
    left_slider_clouds2.color= (1,1,1,1)
    right_slider_clouds2=ramp_clouds2.elements[1]
    right_slider_clouds2.color= (0,0,0,1)
    right_slider_clouds2.position=random.uniform(0.3,0.4)
    left_slider_clouds2.position=random.uniform(0.1,0.2)
    
    
    #Land Detail Frame
    frame_land_detail = nodes.new("NodeFrame")
    frame_land_detail.name = "Land Detail"
    frame_land_detail.label = "Land Detail"
    noise_land_detail.parent = frame_land_detail
    color_ramp_land_detail.parent=frame_land_detail
    bump_land_detail.parent = frame_land_detail
    magic_texture_land_detail.parent =frame_land_detail
    
    #Main Surface Frame
    frame_main_surface = nodes.new("NodeFrame")
    frame_main_surface.name = "Main Surface"
    frame_main_surface.label = "Main Surface"
    noise_main_surface.parent = frame_main_surface
    color_ramp_main_surface.parent = frame_main_surface
    mix_main_surface.parent = frame_main_surface
    
    #Mountains Frame
    frame_mountains = nodes.new("NodeFrame")
    frame_mountains.name = "Mountains"
    frame_mountains.label = "Mountains"
    noise_mountains.parent = frame_mountains
    voronoi_mountains.parent = frame_mountains
    math_mountains.parent = frame_mountains

    #Small Craters Frame
    frame_small_craters = nodes.new("NodeFrame")
    frame_small_craters.name = "Small Craters"
    frame_small_craters.label = "Small Craters"
    noise_small_craters.parent = frame_small_craters
    mix_small_craters.parent = frame_small_craters
    voronoi_small_craters.parent = frame_small_craters
    bump_small_craters.parent = frame_small_craters
    color_ramp_small_craters.parent = frame_small_craters
    color_ramp_small_craters2.parent = frame_small_craters
    
    #Large Craters Frame
    frame_large_craters = nodes.new("NodeFrame")
    frame_large_craters.name = "Large Craters"
    frame_large_craters.label = "Large Craters"
    noise_large_craters.parent = frame_large_craters
    voronoi_large_craters.parent = frame_large_craters
    mix_large_craters.parent = frame_large_craters
    bump_large_craters.parent = frame_large_craters
    color_ramp_large_craters.parent = frame_large_craters
    color_ramp_large_craters2.parent = frame_large_craters
    
    #Clouds Frame
    frame_clouds = nodes.new("NodeFrame")
    frame_clouds.name = "Clouds"
    frame_clouds.label = "Clouds"
    bsdf_clouds.parent = frame_clouds
    noise_clouds.parent = frame_clouds   
    color_ramp_clouds.parent = frame_clouds   
    hsv_clouds.parent = frame_clouds   
    noise_clouds2.parent = frame_clouds   
    color_ramp_clouds2.parent = frame_clouds   
    hsv_clouds2.parent = frame_clouds   
    mix_darken_clouds.parent = frame_clouds    
    mix_shader_clouds.parent = frame_clouds 
    
    #Water Frame
    frame_water = nodes.new("NodeFrame")
    frame_water.name = "Water"
    frame_water.label = "Water"
    hsv_water.parent = frame_water
    color_ramp_water.parent = frame_water
    mix_main_water.parent = frame_water
    bsdf_water.parent = frame_water
    mix_shader_water.parent = frame_water
 
    
    planet = bpy.data.objects['Planet']
    planet.data.materials.append(mat)
    generateAtmosphere(planet)

# Gas Planet Generation

def createGasGiant(planet):
    old_empty = bpy.data.objects.get("Planet_Texture_Empty")
    if old_empty: 
        bpy.data.objects.remove(old_empty, do_unlink=True)
    old_atmosphere = bpy.data.objects.get("Atmosphere")
    if old_atmosphere:
        bpy.data.objects.remove(old_atmosphere, do_unlink=True)
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Icosphere"):
            bpy.data.objects.remove(obj, do_unlink=True)
    mat=bpy.data.materials.new(name='Planet Materials')
    mat.use_nodes = True
    
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    
    nodes.clear()
    
    #Nodes
    noise_gas_giant = nodes.new("ShaderNodeTexNoise")
    noise_gas_giant2 = nodes.new("ShaderNodeTexNoise")
    noise_gas_giant3 = nodes.new("ShaderNodeTexNoise")
    noise_gas_giant4 = nodes.new("ShaderNodeTexNoise")
    texcoord_gas_giant = nodes.new("ShaderNodeTexCoord")
    mapping_gas_giant = nodes.new("ShaderNodeMapping")
    multiply_gas_giant = nodes.new("ShaderNodeVectorMath")
    mix_gas_giant = nodes.new("ShaderNodeMixRGB")
    mix_gas_giant_color_dodge = nodes.new("ShaderNodeMixRGB")
    mix_gas_giant_color_dodge.blend_type = 'DODGE'
    mix_gas_giant_multiply = nodes.new("ShaderNodeMixRGB")
    mix_gas_giant_multiply.blend_type = 'MULTIPLY'
    multiply_gas_giant.operation = 'MULTIPLY'
    multiply_gas_giant.inputs[1].default_value = (0.01, 0.01, 1.0)
    color_ramp_gas_giant = nodes.new("ShaderNodeValToRGB")
    color_ramp_gas_giant2 = nodes.new("ShaderNodeValToRGB")
    color_ramp_gas_giant3 = nodes.new("ShaderNodeValToRGB")
    color_ramp_gas_giant4 = nodes.new("ShaderNodeValToRGB")
    bsdf_gas_giant = nodes.new("ShaderNodeBsdfPrincipled")
    output_planet_texture = nodes.new("ShaderNodeOutputMaterial")
    #Node Links
    links.new(texcoord_gas_giant.outputs['Object'],multiply_gas_giant.inputs['Vector'])
    links.new(multiply_gas_giant.outputs['Vector'],mapping_gas_giant.inputs['Vector'])
    links.new(mapping_gas_giant.outputs['Vector'],mix_gas_giant.inputs['Color1'])
    links.new(mix_gas_giant.outputs['Color'],noise_gas_giant.inputs['Vector'])
    links.new(noise_gas_giant.outputs['Fac'],color_ramp_gas_giant.inputs['Fac'])
    links.new(noise_gas_giant2.outputs['Fac'],mix_gas_giant.inputs['Color2'])
    links.new(noise_gas_giant3.outputs['Fac'],color_ramp_gas_giant2.inputs['Fac'])
    links.new(noise_gas_giant4.outputs['Fac'],color_ramp_gas_giant3.inputs['Fac'])
    links.new(color_ramp_gas_giant2.outputs['Color'],mix_gas_giant_multiply.inputs['Color1'])
    links.new(color_ramp_gas_giant3.outputs['Color'],mix_gas_giant_multiply.inputs['Color2'])
    links.new(mix_gas_giant_multiply.outputs['Color'],mix_gas_giant_color_dodge.inputs['Color2'])
    links.new(color_ramp_gas_giant .outputs['Color'],mix_gas_giant_color_dodge.inputs['Color1'])
    links.new(mix_gas_giant_color_dodge.outputs['Color'],color_ramp_gas_giant4.inputs['Fac'])
    links.new(color_ramp_gas_giant4.outputs['Color'],bsdf_gas_giant.inputs['Base Color'])
    links.new(bsdf_gas_giant.outputs['BSDF'],output_planet_texture.inputs['Surface'])
    
    noise_gas_giant.inputs['Scale'].default_value=random.uniform(2.7,10)
    noise_gas_giant.inputs['Detail'].default_value=random.uniform(5,8)
    noise_gas_giant.inputs['Roughness'].default_value=random.uniform(0.2,0.7)
    mix_gas_giant.inputs['Factor'].default_value=default_value=random.uniform(0.6,0.8)
    
    noise_gas_giant2.inputs['Scale'].default_value=random.uniform(7,30)
    noise_gas_giant2.inputs['Detail'].default_value=random.uniform(5,8)
    noise_gas_giant2.inputs['Roughness'].default_value=random.uniform(0.2,0.9)
    
    noise_gas_giant3.inputs['Scale'].default_value=random.uniform(12,18)
    noise_gas_giant3.inputs['Detail'].default_value=random.uniform(3,7)
    noise_gas_giant3.inputs['Roughness'].default_value=random.uniform(0.5,0.7)
    
    noise_gas_giant4.inputs['Scale'].default_value=random.uniform(12,18)
    noise_gas_giant4.inputs['Detail'].default_value=random.uniform(3,7)
    noise_gas_giant4.inputs['Roughness'].default_value=random.uniform(0.5,0.7)
    
    mix_gas_giant_multiply.inputs[0].default_value=1.0
    mix_gas_giant_color_dodge.inputs[0].default_value=1.0
    bsdf_gas_giant.inputs['Roughness'].default_value=0.8
    
    def darken_color(color, factor):
        return (
            color[0] * factor,
            color[1] * factor,
            color[2] * factor,
            color[3]
        )

    base_color = selected_palette
    dark_color_1 = darken_color(base_color, 0.90)
    dark_color_2 = darken_color(base_color, 0.65)
    
    
    ramp_gas_giant=color_ramp_gas_giant.color_ramp
    left_slider_gas_giant=ramp_gas_giant.elements[0]
    left_slider_gas_giant.position=random.uniform(0.39,0.52)
    
    ramp_gas_giant2=color_ramp_gas_giant2.color_ramp
    left_slider_gas_giant2=ramp_gas_giant2.elements[0]
    left_slider_gas_giant2.position=random.uniform(0.42,0.52)
    
    ramp_gas_giant3=color_ramp_gas_giant3.color_ramp
    left_slider_gas_giant3=ramp_gas_giant3.elements[0]
    right_slider_gas_giant3=ramp_gas_giant3.elements[1]
    left_slider_gas_giant3.position=random.uniform(0.42,0.52)
    right_slider_gas_giant3.position=random.uniform(0.53,0.67)
    
    ramp_gas_giant4=color_ramp_gas_giant4.color_ramp
    left_slider_gas_giant4=ramp_gas_giant4.elements[0]
    left_slider_gas_giant4.color=dark_color_2
    
    middle_slider_gas_giant4=ramp_gas_giant4.elements[1]
    middle_slider_gas_giant4.color=dark_color_1
    middle_slider_gas_giant4.position=random.uniform(0.25,0.35)
    
    right_slider_gas_giant4=ramp_gas_giant4.elements.new(random.uniform(left_slider_gas_giant4.position,0.66))
    right_slider_gas_giant4.color=selected_palette
    
    planet = bpy.data.objects['Planet']
    planet.data.materials.append(mat)

if P_TYPE=='Terran' or P_TYPE=='Superterran' or P_TYPE=='Superterran':
    createRockyPlanet(P_TYPE,P_TYPE_TEMP)
elif P_TYPE=='Jovian' or P_TYPE=='Neptunian':
    createGasGiant(planet)

#Compositor

scene = bpy.context.scene
tree = scene.compositing_node_group
tree.nodes.clear()

nodes = tree.nodes
links = tree.links

# Render Layers
render_layers = nodes.new("CompositorNodeRLayers")
render_layers.name = "Render Layers"
render_layers.label = "Render Layers"
render_layers.location = (-400, 0)

render_layers.scene = scene

# Viewer
viewer = nodes.new("CompositorNodeViewer")
viewer.name = "Viewer"
viewer.label = "Viewer"
viewer.location = (200, 100)

# Group Output
group_output = nodes.new("NodeGroupOutput")
group_output.name = "Group Output"
group_output.label = "Group Output"
group_output.location = (200, -100)

if not tree.interface.items_tree.get("Image"):
    tree.interface.new_socket(name="Image",in_out='OUTPUT',socket_type='NodeSocketColor')

# Links
links.new(render_layers.outputs["Image"],viewer.inputs["Image"])
links.new(render_layers.outputs["Image"],group_output.inputs["Image"])