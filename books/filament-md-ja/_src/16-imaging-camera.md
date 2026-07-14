# Imaging pipeline

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


The lighting section of this document describes how light interacts with surfaces in the scene in a physically based manner. To achieve plausible results, we must go a step further and consider the transformations necessary to convert the scene luminance, as computed by our lighting equations, into displayable pixel values.

The series of transformations we are going to use form the following imaging pipeline:

*************************************************************************************
* .-------------.      .--------------.      .---------------.                      *
* |    Scene    |      |  Normalized  |      |               |                      *
* |  luminance  +----->|  luminance   +----->| White balance |                      *
* |             |      |    (HDR)     |      |               |                      *
* '-------------'      '--------------'      '-------+-------'                      *
*                                                    |                              *
*                                                    v                              *
*                                            .---------------.                      *
*                                            |               |                      *
*                                            | Color grading |                      *
*                                            |               |                      *
*                                            '-------+-------'                      *
*                                                    |                              *
*                                                    v                              *
*                                            .---------------.                      *
*                                            |               |                      *
*                                            | Tone mapping  |                      *
*                                            |               |                      *
*                                            '-------+-------'                      *
*                                                    |                              *
*                                                    v                              *
*                                            .---------------.      .-------------. *
*                                            |               |      |    Pixel    | *
*                                            |     OETF      +----->|    value    | *
*                                            |               |      |    (LDR)    | *
*                                            '---------------'      '-------------' *
*************************************************************************************

**Note**: the *OETF* step is the application of the opto-electronic transfer function of the target color space. For clarity this diagram does not include post-processing steps such as vignette, bloom, etc. These effects will be discussed separately.

[TODO] Color spaces (ACES, sRGB, Rec. 709, Rec. 2020, etc.), gamma/linear, etc.

## Physically based camera

The first step in the image transformation process is to use a physically based camera to properly expose the scene's outgoing luminance.

### Exposure settings

Because we use photometric units throughout the lighting pipeline, the light reaching the camera is an energy expressed in luminance $L$, in $cd.m^{-2}$. Light incident to the camera sensor can cover a large range of values, from $10^{-5}cd.m^{-2}$ for starlight to $10^{9}cd.m^{-2}$ for the sun. Since we obviously cannot manipulate and even less record such a large range of values, we need to remap them.

This range remapping is done in a camera by exposing the sensor for a certain time. To maximize the use of the limited range of the sensor, the scene's light range is centered around the "middle gray", a value halfway between black and white. The exposition is therefore achieved by manipulating, either manually or automatically, 3 settings:

- Aperture
- Shutter speed
- Sensitivity (also called gain)

**Aperture**

Noted $N$ and expressed in f-stops ƒ, this setting controls how open or closed the camera system's aperture is. Since an f-stop indicate the ratio of the lens' focal length to the diameter of the entrance pupil, high-values (ƒ/16) indicate a small aperture and small values (ƒ/1.4) indicate a wide aperture. In addition to the exposition, the aperture setting controls the depth of field.

**Shutter speed**

Noted $t$ and expressed in seconds $s$, this setting controls how long the aperture remains opened (it also controls the timing of the sensor shutter(s), whether electronic or mechanical). In addition to the exposition, the shutter speed controls motion blur.

**Sensitivity**

Noted $S$ and expressed in ISO, this setting controls how the light reaching the sensor is quantized. Because of its unit, this setting is often referred to as simply the "ISO" or "ISO setting". In addition to the exposition, the sensitivity setting controls the amount of noise.

### Exposure value

Since referring to these 3 settings in our equations would be unwieldy, we instead summarize the “exposure triangle” by an exposure value, noted EV[^reciprocity].

The EV is expressed in a base-2 logarithmic scale, with a difference of 1 EV called a stop. One positive stop (+1 EV) corresponds to a factor of two in luminance and one negative stop (-1 EV) corresponds to a factor of half in luminance.

Equation $ \ref{ev} $ shows the [formal definition of EV](https://en.wikipedia.org/wiki/Exposure_value).

$$\begin{equation}\label{ev}
EV = log_2(\frac{N^2}{t})
\end{equation}$$

Note that this definition is only function of the aperture and shutter speed, but not the sensitivity. An exposure value is by convention defined for ISO 100, or $ EV_{100} $, and because we wish to work with this convention, we need to be able to express $ EV_{100} $ as a function of the sensitivity.

Since we know that EV is a base-2 logarithmic scale in which each stop increases or decreases the brightness by a factor of 2, we can formally define $ EV_{S} $, the exposure value at given sensitivity (equation $\ref{evS}$).

$$\begin{equation}\label{evS}
{EV}_S = EV_{100} + log_2(\frac{S}{100})
\end{equation}$$

Calculating the $ EV_{100} $ as a function of the 3 camera settings is trivial, as shown in $\ref{ev100}$.

$$\begin{equation}\label{ev100}
{EV}_{100} = EV_{S} - log_2(\frac{S}{100}) = log_2(\frac{N^2}{t}) - log_2(\frac{S}{100})
\end{equation}$$

Note that the operator (photographer, etc.) can achieve the same exposure (and therefore EV) with several combinations of aperture, shutter speed and sensitivity. This allows some artistic control in the process (depth of field vs motion blur vs grain).

[^reciprocity]: We assume a digital sensor, which means we don't need to take reciprocity failure into account

#### Exposure value and luminance

A camera, similar to a spot meter, is able to measure the average luminance of a scene and convert it into EV to achieve automatic exposure, or at the very least offer the user exposure guidance.

It is possible to define EV as a function of the scene luminance $L$, given a per-device calibration constant $K$ (equation $ \ref{evK} $).

$$\begin{equation}\label{evK}
EV = log_2(\frac{L \times S}{K})
\end{equation}$$

That constant $K$ is the reflected-light meter constant, which varies between manufacturers. We could find two common values for this constant: 12.5, used by Canon, Nikon and Sekonic, and 14, used by Pentax and Minolta. Given the wide availability of Canon and Nikon cameras, as well as our own usage of Sekonic light meters, we will choose to use $ K = 12.5 $.

Since we want to work with $ EV_{100} $, we can substitute $K$ and $S$ in equation $ \ref{evK} $ to obtain equation $ \ref{ev100L} $.

$$\begin{equation}\label{ev100L}
EV = log_2(L \frac{100}{12.5})
\end{equation}$$

Given this relationship, it would be possible to implement automatic exposure in our engine by first measuring the average luminance of a frame. An easy way to achieve this is to simply downsample a luminance buffer down to 1 pixel and read the remaining value. This technique is unfortunately rarely stable and can easily be affected by extreme values. Many games use a different approach which consists in using a luminance histogram to remove extreme values.

For validation and testing purposes, the luminance can be computed from a given EV:

$$\begin{equation}
L = 2^{EV_{100}} \times \frac{12.5}{100} = 2^{EV_{100} - 3}
\end{equation}$$

#### Exposure value and illuminance

It is possible to define EV as a function of the illuminance $E$, given a per-device calibration constant $C$:

$$\begin{equation}\label{evC}
EV = log_2(\frac{E \times S}{C})
\end{equation}$$

The constant $C$ is the incident-light meter constant, which varies between manufacturers and/or types of sensors. There are two common types of sensors: flat and hemispherical. For flat sensors, a common value is 250. With hemispherical sensors, we could find two common values: 320, used by Minolta, and 340, used by Sekonic.

Since we want to work with $ EV_{100} $, we can substitute $S$ $ \ref{evC} $ to obtain equation $ \ref{ev100C} $.

$$\begin{equation}\label{ev100C}
EV = log_2(E \frac{100}{C})
\end{equation}$$

The illuminance can then be computed from a given EV. For a flat sensor with $ C = 250 $ we obtain equation $ \ref{eFlatSensor} $.

$$\begin{equation}\label{eFlatSensor}
E = 2^{EV_{100}} \times 2.5
\end{equation}$$

For a hemispherical sensor with $ C = 340 $ we obtain equation $ \ref{eHemisphereSensor} $

$$\begin{equation}\label{eHemisphereSensor}
E = 2^{EV_{100}} \times 3.4
\end{equation}$$

#### Exposure compensation

Even though an exposure value actually indicates combinations of camera settings, it is often used by photographers to describe light intensity. This is why cameras let photographers apply an exposure compensation to over or under-expose an image. This setting can be used for artistic control but also to achieve proper exposure (snow for instance will be exposed for as 18% middle-gray).

Applying an exposure compensation $EC$ is a simple as adding an offset to the exposure value, as shown in equation $ \ref{ec} $.

$$\begin{equation}\label{ec}
EV_{100}' = EV_{100} - EC
\end{equation}$$

This equation uses a negative sign because we are using $EC$ in f-stops to adjust the final exposure. Increasing the EV is akin to closing down the aperture of the lens (or reducing shutter speed or reducing sensitivity). A higher EV will produce darker images.

### Exposure

To convert the scene luminance into normalized luminance, we must use the [photometric exposure](https://en.wikipedia.org/wiki/Exposure_value#Camera_settings_vs._photometric_exposure) (or luminous exposure), or amount of scene luminance that reaches the camera sensor. The photometric exposure, expressed in lux seconds and noted $H$, is given by equation $ \ref{photometricExposure} $.

$$\begin{equation}\label{photometricExposure}
H = \frac{q \cdot t}{N^2} L
\end{equation}$$

Where $L$ is the luminance of the scene, $t$ the shutter speed, $N$ the aperture and $q$ the lens and vignetting attenuation (typically $ q = 0.65 $[^lensAttenuation]). This definition does not take the sensor sensitivity into account. To do so, we must use one of the three ways to relate photometric exposure and sensitivity: saturation-based speed, noise-based speed and standard output sensitivity.

We choose the saturation-based speed relation, which gives us $ H_{sat} $, the maximum possible exposure that does not lead to clipped or bloomed camera output (equation $ \ref{hSat} $).

$$\begin{equation}\label{hSat}
H_{sat} = \frac{78}{S_{sat}}
\end{equation}$$

We combine equations $ \ref{hSat} $ and $ \ref{photometricExposure} $ in equation $ \ref{lmax} $ to compute the maximum luminance $ L_{max} $ that will saturate the sensor given exposure settings $S$, $N$ and $t$.

$$\begin{equation}\label{lmax}
L_{max} = \frac{N^2}{q \cdot t} \frac{78}{S}
\end{equation}$$

This maximum luminance can then be used to normalize incident luminance $L$ as shown in equation $ \ref{normalizedLuminance} $.

$$\begin{equation}\label{normalizedLuminance}
L' = L \frac{1}{L_{max}}
\end{equation}$$

$ L_{max} $ can be simplified using equation $ \ref{ev} $, $ S = 100 $ and $ q = 0.65 $:

$$\begin{align*}
L_{max} &= \frac{N^2}{t} \frac{78}{q \cdot S} \\
L_{max} &= 2^{EV_{100}} \frac{78}{q \cdot S} \\
L_{max} &= 2^{EV_{100}} \times 1.2
\end{align*}$$

Listing [fragmentExposure] shows how the exposure term can be applied directly to the pixel color computed in a fragment shader.

```glsl
// Computes the camera's EV100 from exposure settings
// aperture in f-stops
// shutterSpeed in seconds
// sensitivity in ISO
float exposureSettings(float aperture, float shutterSpeed, float sensitivity) {
    return log2((aperture * aperture) / shutterSpeed * 100.0 / sensitivity);
}

// Computes the exposure normalization factor from
// the camera's EV100
float exposure(float ev100) {
    return 1.0 / (pow(2.0, ev100) * 1.2);
}

float ev100 = exposureSettings(aperture, shutterSpeed, sensitivity);
float exposure = exposure(ev100);

vec4 color = evaluateLighting();
color.rgb *= exposure;
```
*リスト [fragmentExposure]: Implementation of exposure in GLSL*

In practice the exposure factor can be pre-computed on the CPU to save shader instructions.

[^lensAttenuation]: See *Film Speed, Measurements and calculations* on Wikipedia (https://en.wikipedia.org/wiki/Film_speed)

### Automatic exposure

The process described above relies on artists setting the camera exposure settings manually. This can prove cumbersome in practice since camera movements and/or dynamic effects can greatly affect the scene's luminance. Since we know how to compute the exposure value from a given luminance (see section [Exposure value and luminance]), we can transform our camera into a spot meter. To do so, we need to measure the scene's luminance.

There are two common techniques used to measure the scene's luminance:

- **Luminance downsampling**, by downsampling the previous frame successively until obtaining a 1x1 log luminance buffer that can be read on the CPU (this could also be achieved using a compute shader). The result is the average log luminance of the scene. The first downsampling must extract the luminance of each pixel first. This technique can be unstable and its output should be smoothed over time.
- **Using a luminance histogram**, to find the average log luminance. This technique has an advantage over the previous one as it allows to ignore extreme values and offers more stable results.

Note that both methods will find the average luminance after multiplication by the albedo. This is not entirely correct but the alternative is to keep a luminance buffer that contains the luminance of each pixel before multiplication by the surface albedo. This is expensive both computationally and memory-wise.

These two techniques also limit the metering system to average metering, where each pixel has the same influence (or weight) over the final exposure. Cameras typically offer 3 modes of metering:

**Spot metering**

In which only a small circle in the center of the image contributes to the final exposure. That circle is usually 1 to 5% of the total image size.

**Center-weighted metering**

Gives more influence to scene luminance values located in the center of the screen.

**Multi-zone or matrix metering**

A metering mode that differs for each manufacturer. The goal of this mode is to prioritize exposure for the most important parts of the scene. This is often achieved by splitting the image into a grid and by classifying each cell (using focus information, min/max luminance, etc.). Advanced implementations attempt to compare the scene to a known dataset to achieve proper exposure (backlit sunset, overcast snowy day, etc.).

#### Spot metering

The weight $w$ of each luminance value to use when computing the scene luminance is given by equation $ \ref{spotMetering} $.

$$\begin{equation}\label{spotMetering}
w(x,y) = \begin{cases} 1 & \left| p_{x,y} - s_{x,y} \right| \le s_r \\ 0 & \left| p_{x,y} - s_{x,y} \right| \gt s_r \end{cases}
\end{equation}$$

Where $p$ is the position of the pixel, $s$ the center of the spot and $ s_r $ the radius of the spot.

#### Center-weighted metering

$$\begin{equation}\label{centerMetering}
w(x,y) = smooth(\left| p_{x,y} - c \right| \times \frac{2}{width} )
\end{equation}$$

Where $c$ is the center of the time and $ smooth() $ a smoothing function such as GLSL's `smoothstep()`.

#### Adaptation

To smooth the result of the metering, we can use equation $ \ref{adaptation} $, an exponential feedback loop as described by Pattanaik et al. in [Pattanaik00].

$$\begin{equation}\label{adaptation}
L_{avg} = L_{avg} + (L - L_{avg}) \times (1 - e^{-\Delta t \cdot \tau})
\end{equation}$$

Where $ \Delta t $ is the delta time from the previous frame and $\tau$ a constant that controls the adaptation rate.

### Bloom

Because the EV scale is almost perceptually linear, the exposure value is also often used as a light unit. This means we could let artists specify the intensity of lights or emissive surfaces using exposure compensation as a unit. The intensity of emitted light would therefore be relative to the exposure settings. Using exposure compensation as a light unit should be avoided whenever possible but can be useful to force (or cancel) a bloom effect around emissive surfaces independently of the camera settings (for instance, a lightsaber in a game should always bloom).

![Figure [bloom]: Saturated photosites on a sensor create a blooming effect in the bright parts of the scene](/images/filament-md-ja/screenshot_bloom.jpg)

With $c$ the bloom color and $ EV_{100} $ the current exposure value, we can easily compute the luminance of the bloom value as show in equation $ \ref{bloomEV} $.

$$\begin{equation}\label{bloomEV}
EV_{bloom} = EV_{100} + EC \\
L_{bloom} = c \times 2^{EV_{bloom} - 3}
\end{equation}$$

Equation $ \ref{bloomEV} $ can be used in a fragment shader to implement emissive blooms, as shown in listing [fragmentEmissive].

```glsl
vec4 surfaceShading() {
    vec4 color = evaluateLights();
    // rgb = color, w = exposure compensation
    vec4 emissive = getEmissive();
    color.rgb += emissive.rgb * pow(2.0, ev100 + emissive.w - 3.0);
    color.rgb *= exposure;
    return color;
}
```
*リスト [fragmentEmissive]: Implementation of emissive bloom in GLSL*
