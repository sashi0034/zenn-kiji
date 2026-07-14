## Optics post-processing

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


### Color fringing

[TODO]

![Figure [fringing]: Example of color fringing: look at the ear on the left or the chin at the bottom.](/images/filament-md-ja/screenshot_fringing.jpg)

### Lens flares

[TODO] Notes: there is a physically based approach to generating lens flares, by tracing rays through the optical assembly of the lens, but we are going to use an image-based approach. This approach is cheaper and has a few welcome benefits such as free emitters occlusion and unlimited light sources support.

## Filmic post-processing

[TODO] Perform post-processing on the scene referred data (linear space, before tone-mapping) as much as possible

It is important to provide color correction tools to give artists greater artistic control over the final image. These tools are found in every photo or video processing application, such as Adobe Photoshop or Adobe After Effects.

### Contrast

### Curves

### Levels

### Color grading

## Light path

The light path, or rendering method, used by the engine can have serious performance implications and may impose strong limitations on how many lights can be used in a scene. There are traditionally two different rendering methods used by 3D engines forward and deferred rendering.

Our goal is to use a rendering method that obeys the following constraints:

- Low bandwidth requirements
- Multiple dynamic lights per pixel

Additionally, we would like to easily support:

- MSAA
- Transparency
- Multiple material models

Deferred rendering is used by many modern 3D rendering engines to easily support dozens, hundreds or even thousands of light source (amongst other benefits). This method is unfortunately very expensive in terms of bandwidth. With our default PBR material model, our G-buffer would use between 160 and 192 bits per pixel, which would translate directly to rather high bandwidth requirements.

Forward rendering methods on the other hand have historically been bad at handling multiple lights. A common implementation is to render the scene multiple times, once per visible light, and to blend (add) the results. Another technique consists in assigning a fixed maximum of lights to each object in the scene. This is however impractical when objects occupy a vast amount of space in the world (building, road, etc.).

Tiled shading can be applied to both forward and deferred rendering methods. The idea is to split the screen in a grid of tiles and for each tile, find the list of lights that affect the pixels within that tile. This has the advantage of reducing overdraw (in deferred rendering) and shading computations of large objects (in forward rendering). This technique suffers however from depth discontinuities issues that can lead to large amounts of extraneous work.

The scene displayed in figure [sponza] was rendered using clustered forward rendering.

![Figure [sponza]: Clustered forward rendering with dozens of dynamic lights and MSAA](/images/filament-md-ja/screenshot_sponza.jpg)

Figure [sponzaTiles] shows the same scene split in tiles (in this case, a 1280x720 render target with 80x80px tiles).

![Figure [sponzaTiles]: Tiled shading (16x9 tiles)](/images/filament-md-ja/screenshot_sponza_tiles.jpg)

### Clustered Forward Rendering

We decided to explore another method called Clustered Shading, in its forward variant. Clustered shading expands on the idea of tiled rendering but adds a segmentation on the 3rd axis. The “clustering” is done in view space, by splitting the frustum into a 3D grid.

The frustum is first sliced on the depth axis as show in figure [sponzaSlices].

![Figure [sponzaSlices]: Depth slicing (16 slices)](/images/filament-md-ja/screenshot_sponza_slices.jpg)

And the depth slices are then combined with the screen tiles to "voxelize" the frustum. We call each cluster a froxel as it makes it clear what they represent (a voxel in frustum space). The result of the "froxelization" pass is shown in figure [froxel1] and figure [froxel2].

![Figure [froxel1]: Frustum voxelization (5x3 tiles, 8 depth slices)](/images/filament-md-ja/screenshot_sponza_froxels1.jpg)

![Figure [froxel2]: Frustum voxelization (5x3 tiles, 8 depth slices)](/images/filament-md-ja/screenshot_sponza_froxels2.jpg)

Before rendering a frame, each light in the scene is assigned to any froxel it intersects with. The result of the lights assignment pass is a list of lights for each froxel. During the rendering pass, we can compute the ID of the froxel a fragment belongs to and therefore the list of lights that can affect that fragment.

The depth slicing is not linear, but exponential. In a typical scene, there will be more pixels close to the near plane than to the far plane. An exponential grid of froxels will therefore improve the assignment of lights where it matters the most.

Figure [froxelDistribution] shows how much world space unit each depth slice uses with exponential slicing.

![Figure [froxelDistribution]: Near: 0.1m, Far: 100m, 16 slices](/images/filament-md-ja/diagram_froxels1.png)

A simple exponential voxelization is unfortunately not enough. The graphic above clearly illustrates how world space is distributed across slices but it fails to show what happens close to the near plane. If we examine the same distribution in a smaller range (0.1m to 7m) we can see an interesting problem appear as shown in figure [froxelDistributionClose].

![Figure [froxelDistributionClose]: Depth distribution in the 0.1-7m range](/images/filament-md-ja/diagram_froxels2.png)

This graphic shows that a simple exponential distribution uses up half of the slices very close to the camera. In this particular case, we use 8 slices out of 16in the first 5 meters. Since dynamic world lights are either point lights (spheres) or spot lights (cones), such a fine resolution is completely unnecessary so close to the near plane.

Our solution is to manually tweak the size of the first froxel depending on the scene and the near and far planes. By doing so, we can better distribute the remaining froxels across the frustum. Figure [froxelDistributionExp] shows for instance what happens when we use a special froxel between 0.1m and 5m.

![Figure [froxelDistributionExp]: Near: 0.1, Far: 100m, 16 slices, Special froxel: 0.1-5m](/images/filament-md-ja/diagram_froxels3.png)

This new distribution is much more efficient and allows a better assignment of the lights throughout the entire frustum.

### Implementation notes

Lights assignment can be done in two different ways, on the GPU or on the CPU.

#### GPU lights assignment

This implementation requires OpenGL ES 3.1 and support for compute shaders. The lights are stored in Shader Storage Buffer Objects (SSBO) and passed to a compute shader that assigns each light to the corresponding froxels.

The frustum voxelization can be executed only once by a first compute shader (as long as the projection matrix does not change), and the lights assignment can be performed each frame by another compute shader.

The threading model of compute shaders is particularly well suited for this task. We simply invoke as many workgroups as we have froxels (we can directly map the X, Y and Z workgroup counts to our froxel grid resolution). Each workground will in turn be threaded and traverse all the lights to assign.

Intersection tests imply simple sphere/frustum or cone/frustum tests.

See the annex for the source code of a GPU implementation (point lights only).

#### CPU lights assignment

On non-OpenGL ES 3.1 devices, lights assignment can be performed efficiently on the CPU. The algorithm is different from the GPU implementation. Instead of iterating over every light for each froxel, the engine will “rasterize” each light as froxels. For instance, given a point light’s center and radius, it is trivial to compute the list of froxels it intersects with.

This technique has the added benefit of providing tighter culling than in the GPU variant. The CPU implementation can also more easily generate a packed list of lights.

#### Shading

The list of lights per froxel can be passed to the fragment shader either as an SSBO (OpenGL ES 3.1) or a texture.

#### From depth to froxel

Given a near plane $n$, a far plane $f$, a maximum number of depth slices $m$ and a linear depth value $z$ in the range [0..1], equation $\ref{zToCluster}$ can be used to compute the index of the cluster for a given position.

$$\begin{equation}\label{zToCluster}
zToCluster(z,n,f,m)=floor \left( max \left( log2(z) \frac{m}{-log2(\frac{n}{f})} + m, 0 \right) \right)
\end{equation}$$

This formula suffers however from the resolution issue mentioned previously. We can fix it by introducing $sn$, a special near value that defines the extent of the first froxel (the first froxel occupies the range [n..sn], the remaining froxels [sn..f]).

$$\begin{equation}\label{zToClusterFix}
zToCluster(z,n,sn,f,m)=floor \left( max \left( log2(z) \frac{m-1}{-log2(\frac{sn}{f})} + m, 0 \right) \right)
\end{equation}$$

Equation $\ref{linearZ}$ can be used to compute a linear depth value from `gl_FragCoord.z` (assuming a standard OpenGL projection matrix).

$$\begin{equation}\label{linearZ}
linearZ(z)=\frac{n}{f+z(n-f)}
\end{equation}$$

This equation can be simplified by pre-computing two terms $c0$ and $c1$, as shown in equation $\ref{linearZFix}$.

$$\begin{equation}\label{linearZFix}
c1 = \frac{f}{n} \\
c0 = 1 - c1 \\
linearZ(z)=\frac{1}{z \cdot c0 + c1}
\end{equation}$$

This simplification is important because we pass the linear z value to a `log2` in $\ref{zToClusterFix}$. Since the division becomes a negation under a logarithmic, we can avoid a division by using $-log2(z \cdot c0 + c1)$ instead.

All put together, computing the froxel index of a given fragment can be implemented fairly easily as shown in listing [fragCoordToFroxel].

```glsl
#define MAX_LIGHT_COUNT 16 // max number of lights per froxel

uniform uvec4 froxels; // res x, res y, count y, count y
uniform vec4 zParams;  // c0, c1, index scale, index bias

uint getDepthSlice() {
    return uint(max(0.0, log2(zParams.x * gl_FragCoord.z + zParams.y) *
            zParams.z + zParams.w));
}

uint getFroxelOffset(uint depthSlice) {
    uvec2 froxelCoord = uvec2(gl_FragCoord.xy) / froxels.xy;
    froxelCoord.y = (froxels.w - 1u) - froxelCoord.y;

    uint index = froxelCoord.x + froxelCoord.y * froxels.z +
            depthSlice * froxels.z * froxels.w;
    return index * MAX_FROXEL_LIGHT_COUNT;
}

uint slice = getDepthSlice();
uint offset = getFroxelOffset(slice);

// Compute lighting...
```
*リスト [fragCoordToFroxel]: GLSL implementation to compute a froxel index from a fragment's screen coordinates*

Several uniforms must be pre-computed for perform the index evaluation efficiently. The code used to pre-compute these uniforms can be found in listing [froxelIndexPrecomputation].

```glsl
froxels[0] = TILE_RESOLUTION_IN_PX;
froxels[1] = TILE_RESOLUTION_IN_PX;
froxels[2] = numberOfTilesInX;
froxels[3] = numberOfTilesInY;

zParams[0] = 1.0f - Z_FAR / Z_NEAR;
zParams[1] = Z_FAR / Z_NEAR;
zParams[2] = (MAX_DEPTH_SLICES - 1) / log2(Z_SPECIAL_NEAR / Z_FAR);
zParams[3] = MAX_DEPTH_SLICES;
```
[Listing [froxelIndexPrecomputation]]

#### From froxel to depth

Given a froxel index $i$, a special near plane $sn$, a far plane $f$ and a maximum number of depth slices $m$, equation $\ref{clusterToZ}$ computes the minimum depth of a given froxel.

$$\begin{equation}\label{clusterToZ}
clusterToZ(i \ge 1,sn,f,m)=2^{(i-m) \frac{-log2(\frac{sn}{f})}{m-1}}
\end{equation}$$

For $i=0$, the z value is 0. The result of this equation is in the [0..1] range and should be multiplied by $f$ to get a distance in world units.

The compute shader implementation should use `exp2` instead of a `pow`. The division can be precomputed and passed as a uniform.

## Validation

Given the complexity of our lighting system, it is important to validate our implementation. We will do so in several ways: using reference renderings, light measurements and data visualization.

[TODO] Explain light measurement validation (reading EV from the render target and comparing against values measure with light meters/cameras, etc.)

### Scene referred visualization

A quick and easy way to validate a scene's lighting is to modify the shader to output colors that provide an intuitive mapping to relevant data. This can easily be done by using a custom debug tone-mapping operator that outputs fake colors.

#### Luminance stops

With emissive materials and IBLs, it is fairly easy to obtain a scene in which specular highlights are brighter than their apparent caster. This type of issue can be difficult to observe after tone-mapping and quantization but is fairly obvious in the scene-referred space. Figure [luminanceViz] shows how the custom operator described in listing [tonemapLuminanceViz] is used to show the exposed luminance of a scene.

![Figure [luminanceViz]: Visualizing luminance by color coding the stops: cyan is middle gray, blue is 1 stop darker, green 1 stop brighter, etc.](/images/filament-md-ja/screenshot_luminance_debug.png)

```glsl
vec3 Tonemap_DisplayRange(const vec3 x) {
    // The 5th color in the array (cyan) represents middle gray (18%)
    // Every stop above or below middle gray causes a color shift
    float v = log2(luminance(x) / 0.18);
    v = clamp(v + 5.0, 0.0, 15.0);
    int index = int(floor(v));
    return mix(debugColors[index], debugColors[min(15, index + 1)], fract(v));
}

const vec3 debugColors[16] = vec3[](
     vec3(0.0, 0.0, 0.0),         // black
     vec3(0.0, 0.0, 0.1647),      // darkest blue
     vec3(0.0, 0.0, 0.3647),      // darker blue
     vec3(0.0, 0.0, 0.6647),      // dark blue
     vec3(0.0, 0.0, 0.9647),      // blue
     vec3(0.0, 0.9255, 0.9255),   // cyan
     vec3(0.0, 0.5647, 0.0),      // dark green
     vec3(0.0, 0.7843, 0.0),      // green
     vec3(1.0, 1.0, 0.0),         // yellow
     vec3(0.90588, 0.75294, 0.0), // yellow-orange
     vec3(1.0, 0.5647, 0.0),      // orange
     vec3(1.0, 0.0, 0.0),         // bright red
     vec3(0.8392, 0.0, 0.0),      // red
     vec3(1.0, 0.0, 1.0),         // magenta
     vec3(0.6, 0.3333, 0.7882),   // purple
     vec3(1.0, 1.0, 1.0)          // white
);
```
*リスト [tonemapLuminanceViz]: GLSL implementation of a custom debug tone-mapping operator for luminance visualization*

### Reference renderings

To validate our implementation against reference renderings, we will use a commercial-grade Open Source physically based offline path tracer called Mitsuba. Mitsuba offers many different integrators, samplers and material models, which should allow us to provide fair comparisons with our real-time renderer. This path tracer also relies on a simple XML scene description format that should be easy to automatically generate from our own scene descriptions.

Figure [mitsubaReference] and figure [filamentReference] show a simple scene, a perfectly smooth dielectric sphere, rendered respectively with Mitsuba and Filament.

![Figure [mitsubaReference]: Rendered in 2048x1440 in 1 minute and 42 seconds on a 12 core 2013 MacPro](/images/filament-md-ja/screenshot_ref_mitsuba.jpg)

![Figure [filamentReference]: Rendered in 2048x1440 with MSAA 4x at 60 fps on a Nexus 9 device (Tegra K1 GPU)](/images/filament-md-ja/screenshot_ref_filament.jpg)

The parameters used to render both scenes are the following:

**Filament**

- Material
  - Base color: sRGB 0.81, 0, 0
  - Metallic: 0
  - Roughness: 0
  - Reflectance: 0.5
- Indirect light: IBL
  - 256x256 cubemap generated by cmgen from office.exr
  - Multiplier: 35,000
- Direct light: directional light
  - Linear color: 1.0, 0.96, 0.95
  - Intensity: 120,000 lux
- Exposure
  - Aperture: f/16
  - Shutter speed: 1/125s
  - ISO: 100

**Mitsuba**

- BSDF: roughplastic
  - Distribution: GGX
  - Alpha: 0
  - Diffuse reflectance: sRGB 0.81, 0, 0
- Emitter: environment map
  - Source: office.exr
  - Scale: 35,000
- Emitter: directional
  - Irradiance: linear RGB 120,000 115,200 114,000
- Film: LDR
  - Exposure: -15.23, computed from log2(filamentExposure)
- Integrator: path
- Sampler: ldsampler
  - Sample count: 256

The full Mitsuba scene can be found as an annex. Both scenes were rendered at the same resolution (2048x1440).

#### Comparison

The slight differences between the two renderings come from the various approximations used by Filament: RGBM 256x256 reflection probe, RGBM 1024x1024 background map, Lambert diffuse, split-sum approximation, analytical approximation of the DFG term, etc.

Figure [referenceComparison] shows the luminance gradient of the images produced by both engines. The comparison was performed on LDR images.

![Figure [referenceComparison]: Luminance gradients from Mitsuba (left) and Filament (right)](/images/filament-md-ja/screenshot_ref_comparison.png)

The biggest difference is visible at grazing angles, which is most likely explained by Filament's use of a Lambertian diffuse term. The Disney diffuse term and its grazing retro-reflections would move Filament closer to Mitsuba.

## Coordinates systems

### World coordinates system

Filament uses a Y-up, right-handed coordinate system.

![Figure [coordinates]: Red +X, green +Y, blue +Z (rendered in Marmoset Toolbag).](/images/filament-md-ja/screenshot_coordinates.jpg)

### Camera coordinates system

Filament's Camera looks towards its local -Z axis. That is, when placing a camera in the world
without any transform applied to it, the camera looks down the world's -Z axis.

### Cubemaps coordinates system

All cubemaps used in Filament follow the OpenGL convention for face
alignment shown in figure [cubemapCoordinates].

![Figure [cubemapCoordinates]: Horizontal cross representation of a cubemap following the OpenGL faces alignment convention.](/images/filament-md-ja/screenshot_cubemap_coordinates.png)

Note that environment background and reflection probes are mirrored (see section [Mirroring]).

#### Mirroring

To simplify the rendering of reflections, IBL cubemaps are stored mirrored on the X axis. This is
the default behaviour of the `cmgen` tool. This means that an IBL cubemap used as environment 
background needs to be mirrored again at runtime. 
An easy way to achieve this for skyboxes is to use textured back faces. Filament does
this by default.

#### Equirectangular environment maps

To convert equirectangular environment maps to horizontal/vertical cross cubemaps we position the
+Z face in the center of the source rectilinear environment map.

#### World space orientation of environment maps and Skyboxes

When specifying a skybox or an IBL in Filament, the specified cubemap is oriented such that its 
-Z face points towards the +Z axis of the world (this is because filament assumes mirrored cubemaps, 
see section [Mirroring]). However, because environments and skyboxes are expected to be pre-mirrored, 
their -Z (back) face points towards the world's -Z axis as expected (and the camera looks toward that 
direction by default, see section [Camera coordinates system]).
