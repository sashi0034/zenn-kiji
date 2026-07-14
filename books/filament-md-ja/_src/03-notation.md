# Notation

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

The equations found throughout this document use the symbols described in table [symbols].

          Symbol             |           Definition
:---------------------------:|:---------------------------|
$v$                          | View unit vector
$l$                          | Incident light unit vector
$n$                          | Surface normal unit vector
$h$                          | Half unit vector between $l$ and $v$
$f$                          | BRDF
$\fDiffuse$                  | Diffuse component of a BRDF
$\fSpecular$                 | Specular component of a BRDF
$\alpha$                     | Roughness, remapped from using input `perceptualRoughness`
$\sigma$                     | Diffuse reflectance
$\Omega$                     | Spherical domain
$\fNormal$                   | Reflectance at normal incidence
$\fGrazing$                  | Reflectance at grazing angle
$\chi^+(a)$                  | Heaviside function (1 if $a > 0$ and 0 otherwise)
$n_{ior}$                    | Index of refraction (IOR) of an interface
$\left< \NoL \right>$        | Dot product clamped to [0..1]
$\left< a \right>$           | Saturated value (clamped to [0..1])
*表 [symbols]: Symbols definitions*
