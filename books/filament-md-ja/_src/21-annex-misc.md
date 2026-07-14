## Sample validation scene for Mitsuba

$$
\newcommand{NoL}{n \cdot l}
\newcommand{NoV}{n \cdot v}
\newcommand{NoH}{n \cdot h}
\newcommand{VoH}{v \cdot h}
\newcommand{LoH}{l \cdot h}
\newcommand{fNormal}{f_{0}}
\newcommand{fDiffuse}{f_d}
\newcommand{fSpecular}{f_r}
\newcommand{fX}{f_x}
\newcommand{aa}{\alpha^2}
\newcommand{fGrazing}{f_{90}}
\newcommand{schlick}{F_{Schlick}}
\newcommand{nior}{n_{ior}}
\newcommand{Ed}{E_d}
\newcommand{Lt}{L_{\bot}}
\newcommand{Lout}{L_{out}}
\newcommand{cosTheta}{\left< \cos \theta \right> }
$$


```glsl
&lt;scene version="0.5.0"&gt;
    &lt;integrator type="path"/&gt;

    &lt;shape type="serialized" id="sphere_mesh"&gt;
        &lt;string name="filename" value="plastic_sphere.serialized"/&gt;
        &lt;integer name="shapeIndex" value="0"/&gt;

        &lt;bsdf type="roughplastic"&gt;
            &lt;string name="distribution" value="ggx"/&gt;
            &lt;float name="alpha" value="0.0"/&gt;
            &lt;srgb name="diffuseReflectance" value="0.81, 0.0, 0.0"/&gt;
        &lt;/bsdf&gt;
    &lt;/shape&gt;

    &lt;emitter type="envmap"&gt;
        &lt;string name="filename" value="../../environments/office/office.exr"/&gt;
        &lt;float name="scale" value="35000.0" /&gt;
        &lt;boolean name="cache" value="false" /&gt;
    &lt;/emitter&gt;

    &lt;emitter type="directional"&gt;
        &lt;vector name="direction" x="-1" y="-1" z="1" /&gt;
        &lt;rgb name="irradiance" value="120000.0, 115200.0, 114000.0" /&gt;
    &lt;/emitter&gt;

    &lt;sensor type="perspective"&gt;
        &lt;float name="farClip" value="12.0"/&gt;
        &lt;float name="focusDistance" value="4.1"/&gt;
        &lt;float name="fov" value="45"/&gt;
        &lt;string name="fovAxis" value="y"/&gt;
        &lt;float name="nearClip" value="0.01"/&gt;
        &lt;transform name="toWorld"&gt;

            &lt;lookat target="0, 0, 0" origin="0, 0, -3.1" up="0, 1, 0"/&gt;
        &lt;/transform&gt;

        &lt;sampler type="ldsampler"&gt;
            &lt;integer name="sampleCount" value="256"/&gt;
        &lt;/sampler&gt;

        &lt;film type="ldrfilm"&gt;
            &lt;integer name="height" value="1440"/&gt;
            &lt;integer name="width" value="2048"/&gt;
            &lt;float name="exposure" value="-15.23" /&gt;
            &lt;rfilter type="gaussian"/&gt;
        &lt;/film&gt;
    &lt;/sensor&gt;
&lt;/scene&gt;
```

## Light assignment with froxels

Assigning lights to froxels can be implemented on the GPU using two compute shaders. The first one, shown in listing [froxelGeneration], creates the froxels data (4 planes + a min Z and max Z per froxel) in an SSBO and needs to be run only once. The shader requires the following uniforms:

**Projection&nbsp;matrix**

The projection matrix used to render the scene (view space to clip space transformation).

**Inverse&nbsp;projection&nbsp;matrix**

The inverse of the projection matrix used to render the scene (clip space to view space transformation).

**Depth&nbsp;parameters**

$-log2(\frac{z_{lighnear}}{z_{far}}) \frac{1}{maxSlices-1}$, maximum number of depth slices, Z near and Z far.

**Clip&nbsp;space&nbsp;size**

$\frac{F_x \times F_r}{w} \times 2$, with $F_x$ the number of tiles on the X axis, $F_r$ the resolution in pixels of a tile and w the width in pixels of the render target.

```glsl
#version 310 es

precision highp float;
precision highp int;

#define FROXEL_RESOLUTION 80u

layout(local_size_x = 1, local_size_y = 1, local_size_z = 1) in;

layout(location = 0) uniform mat4 projectionMatrix;
layout(location = 1) uniform mat4 projectionInverseMatrix;
layout(location = 2) uniform vec4 depthParams; // index scale, index bias, near, far
layout(location = 3) uniform float clipSpaceSize;

struct Froxel {
    // NOTE: the planes should be stored in vec4[4] but the
    // Adreno shader compiler has a bug that causes the data
    // to not be read properly inside the loop
    vec4 plane0;
    vec4 plane1;
    vec4 plane2;
    vec4 plane3;
    vec2 minMaxZ;
};

layout(binding = 0, std140) writeonly restrict buffer FroxelBuffer {
    Froxel data[];
} froxels;

shared vec4 corners[4];
shared vec2 minMaxZ;

vec4 projectionToView(vec4 p) {
    p = projectionInverseMatrix * p;
    return p / p.w;
}

vec4 createPlane(vec4 b, vec4 c) {
    // standard plane equation, with a at (0, 0, 0)
    return vec4(normalize(cross(c.xyz, b.xyz)), 1.0);
}

void main() {
    uint index = gl_WorkGroupID.x + gl_WorkGroupID.y * gl_NumWorkGroups.x +
            gl_WorkGroupID.z * gl_NumWorkGroups.x * gl_NumWorkGroups.y;

    if (gl_LocalInvocationIndex == 0u) {
        // first tile the screen and build the frustum for the current tile
        vec2 renderTargetSize = vec2(FROXEL_RESOLUTION * gl_NumWorkGroups.xy);
        vec2 frustumMin = vec2(FROXEL_RESOLUTION * gl_WorkGroupID.xy);
        vec2 frustumMax = vec2(FROXEL_RESOLUTION * (gl_WorkGroupID.xy + 1u));

        corners[0] = vec4(
            frustumMin.x / renderTargetSize.x * clipSpaceSize - 1.0,
            (renderTargetSize.y - frustumMin.y) / renderTargetSize.y
			    * clipSpaceSize - 1.0,
            1.0,
            1.0
        );
        corners[1] = vec4(
            frustumMax.x / renderTargetSize.x * clipSpaceSize - 1.0,
            (renderTargetSize.y - frustumMin.y) / renderTargetSize.y
			    * clipSpaceSize - 1.0,
            1.0,
            1.0
        );
        corners[2] = vec4(
            frustumMax.x / renderTargetSize.x * clipSpaceSize - 1.0,
            (renderTargetSize.y - frustumMax.y) / renderTargetSize.y
			    * clipSpaceSize - 1.0,
            1.0,
            1.0
        );
        corners[3] = vec4(
            frustumMin.x / renderTargetSize.x * clipSpaceSize - 1.0,
            (renderTargetSize.y - frustumMax.y) / renderTargetSize.y
			    * clipSpaceSize - 1.0,
            1.0,
            1.0
        );

        uint froxelSlice = gl_WorkGroupID.z;
        minMaxZ = vec2(0.0, 0.0);
        if (froxelSlice > 0u) {
            minMaxZ.x = exp2((float(froxelSlice) - depthParams.y) * depthParams.x)
                    * depthParams.w;
        }
        minMaxZ.y = exp2((float(froxelSlice + 1u) - depthParams.y) * depthParams.x)
                * depthParams.w;
    }

    if (gl_LocalInvocationIndex == 0u) {
        vec4 frustum[4];
        frustum[0] = projectionToView(corners[0]);
        frustum[1] = projectionToView(corners[1]);
        frustum[2] = projectionToView(corners[2]);
        frustum[3] = projectionToView(corners[3]);

        froxels.data[index].plane0 = createPlane(frustum[0], frustum[1]);
        froxels.data[index].plane1 = createPlane(frustum[1], frustum[2]);
        froxels.data[index].plane2 = createPlane(frustum[2], frustum[3]);
        froxels.data[index].plane3 = createPlane(frustum[3], frustum[0]);
        froxels.data[index].minMaxZ = minMaxZ;
    }
}
```
*リスト [froxelGeneration]: GLSL implementation of froxels data generation (compute shader)*

The second compute shader, shown in listing [froxelEvaluation], runs every frame (if the camera and/or lights have changed) and assigns all the lights to their respective froxels. This shader relies only on a couple of uniforms (the number of point/spot lights and the view matrix) and four SSBOs:

**Light index buffer**

For each froxel, the index of each light that affects said froxel. The indices for point lights are written first and if there is enough space left, the indices for spot lights are written as well. A sentinel of value 0x7fffffffu separates point and spot lights and/or marks the end of the froxel's list of lights. Each froxel has a maximum number of lights (point + spot).

**Point lights buffer**

Array of structures describing the scene's point lights.

**Spot lights buffer**

Array of structures describing the scene's spot lights.

**Froxels buffer**

The list of froxels represented by planes, created by the previous compute shader.

```glsl
#version 310 es
precision highp float;
precision highp int;

#define LIGHT_BUFFER_SENTINEL 0x7fffffffu
#define MAX_FROXEL_LIGHT_COUNT 32u

#define THREADS_PER_FROXEL_X 8u
#define THREADS_PER_FROXEL_Y 8u
#define THREADS_PER_FROXEL_Z 1u
#define THREADS_PER_FROXEL (THREADS_PER_FROXEL_X * \
        THREADS_PER_FROXEL_Y * THREADS_PER_FROXEL_Z)

layout(local_size_x = THREADS_PER_FROXEL_X,
       local_size_y = THREADS_PER_FROXEL_Y,
       local_size_z = THREADS_PER_FROXEL_Z) in;

// x = point lights, y = spot lights
layout(location = 0) uniform uvec2 totalLightCount;
layout(location = 1) uniform mat4 viewMatrix;

layout(binding = 0, packed) writeonly restrict buffer LightIndexBuffer {
    uint index[];
} lightIndexBuffer;

struct PointLight {
    vec4 positionFalloff; // x, y, z, falloff
    vec4 colorIntensity;  // r, g, b, intensity
    vec4 directionIES;    // dir x, dir y, dir z, IES profile index
};

layout(binding = 1, std140) readonly restrict buffer PointLightBuffer {
    PointLight lights[];
} pointLights;

struct SpotLight {
    vec4 positionFalloff; // x, y, z, falloff
    vec4 colorIntensity;  // r, g, b, intensity
    vec4 directionIES;    // dir x, dir y, dir z, IES profile index
    vec4 angle;           // angle scale, angle offset, unused, unused
};

layout(binding = 2, std140) readonly restrict buffer SpotLightBuffer {
    SpotLight lights[];
} spotLights;

struct Froxel {
    // NOTE: the planes should be stored in vec4[4] but the
    // Adreno shader compiler has a bug that causes the data
    // to not be read properly inside the loop
    vec4 plane0;
    vec4 plane1;
    vec4 plane2;
    vec4 plane3;
    vec2 minMaxZ;
};

layout(binding = 3, std140) readonly restrict buffer FroxelBuffer {
    Froxel data[];
} froxels;

shared uint groupLightCounter;
shared uint groupLightIndexBuffer[MAX_FROXEL_LIGHT_COUNT];

float signedDistanceFromPlane(vec4 p, vec4 plane) {
    // plane.w == 0.0, simplify computation
    return dot(plane.xyz, p.xyz);
}

void synchronize() {
    memoryBarrierShared();
    barrier();
}

void main() {
    if (gl_LocalInvocationIndex == 0u) {
        groupLightCounter = 0u;
    }
    memoryBarrierShared();

    uint froxelIndex = gl_WorkGroupID.x + gl_WorkGroupID.y * gl_NumWorkGroups.x +
            gl_WorkGroupID.z * gl_NumWorkGroups.x * gl_NumWorkGroups.y;
    Froxel current = froxels.data[froxelIndex];

    uint offset = gl_LocalInvocationID.x +
	        gl_LocalInvocationID.y * THREADS_PER_FROXEL_X;
    for (uint i = 0u; i < totalLightCount.x &&
		    groupLightCounter < MAX_FROXEL_LIGHT_COUNT &&
            offset + i < totalLightCount.x; i += THREADS_PER_FROXEL) {

        uint currentLight = offset + i;

        vec4 center = pointLights.lights[currentLight].positionFalloff;
        center.xyz = (viewMatrix * vec4(center.xyz, 1.0)).xyz;
        float r = inversesqrt(center.w);

        if (-center.z + r > current.minMaxZ.x &&
                -center.z - r <= current.minMaxZ.y) {
            if (signedDistanceFromPlane(center, current.plane0) < r &&
                signedDistanceFromPlane(center, current.plane1) < r &&
                signedDistanceFromPlane(center, current.plane2) < r &&
                signedDistanceFromPlane(center, current.plane3) < r) {

                uint index = atomicAdd(groupLightCounter, 1u);
                groupLightIndexBuffer[index] = currentLight;
            }
        }
    }

    synchronize();

    uint pointLightCount = groupLightCounter;
    offset = froxelIndex * MAX_FROXEL_LIGHT_COUNT;

    for (uint i = gl_LocalInvocationIndex; i < pointLightCount;
            i += THREADS_PER_FROXEL) {
        lightIndexBuffer.index[offset + i] = groupLightIndexBuffer[i];
    }

    if (gl_LocalInvocationIndex == 0u) {
        if (pointLightCount < MAX_FROXEL_LIGHT_COUNT) {
            lightIndexBuffer.index[offset + pointLightCount] = LIGHT_BUFFER_SENTINEL;
        }
    }
}
```
*リスト [froxelEvaluation]: GLSL implementation of assigning lights to froxels (compute shader)*
