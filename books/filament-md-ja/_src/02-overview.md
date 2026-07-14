# Overview

Filament is a physically based rendering (PBR) engine for Android. The goal of Filament is to offer a set of tools and APIs for Android developers that will enable them to create high quality 2D and 3D rendering with ease.

The goal of this document is to explain the equations and theory behind the material and lighting models used in Filament. This document is intended as a reference for contributors to Filament or developers interested in the inner workings of the engine. We will provide code snippets as needed to make the relationship between theory and practice as clear as possible.

This document is not intended as a design document. It focuses solely on algorithms and its content could be used to implement PBR in any engine. However, this document explains why we chose specific algorithms/models over others.

Unless noted otherwise, all the 3D renderings present in this document have been generated in-engine (prototype or production). Many of these 3D renderings were captured during the early stages of development of Filament and do not reflect the final quality.

## Principles

Real-time rendering is an active area of research and there is a large number of equations, algorithms and implementation to choose from for every single feature that needs to be implemented (the book *Rendering real-time shadows*, for instance, is a 400 pages summary of dozens of shadows rendering techniques). As such, we must first define our goals (or principles, to follow Brent Burley's seminal paper Physically-based shading at Disney [#Burley12]) before we can make informed decisions.

**Real-time mobile performance**

Our primary goal is to design and implement a rendering system able to perform efficiently on mobile platforms. The primary target will be OpenGL ES 3.x class GPUs.

**Quality**

Our rendering system will emphasize overall picture quality. We will however accept quality compromises to support low and medium performance GPUs.

**Ease of use**

Artists need to be able to iterate often and quickly on their assets and our rendering system must allow them to do so intuitively. We must therefore provide parameters that are easy to understand (for instance, no specular power).

    We also understand that not all developers have the luxury to work with artists. The physically based approach of our system will allow developers to craft visually plausible materials without the need to understand the theory behind our implementation.

    For both artists and developers, our system will rely on as few parameters as possible to reduce trial and error and allow users to quickly master the material model.

    In addition, any combination of parameter values should lead to physically plausible results. Physically implausible materials must be hard to create.

**Familiarity**

Our system should use physical units everywhere possible: distances in meters or centimeters, color temperatures in Kelvin, light units in lumens or candelas, etc.

**Flexibility**

A physically based approach must not preclude non-realistic rendering. User interfaces for instance will need unlit materials.

**Deployment size**

While not directly related to the content of this document, it bears emphasizing our desire to keep the rendering library as small as possible so any application can bundle it without increasing the binary to undesirable sizes.

## Physically based rendering

We chose to adopt PBR for its benefits from an artistic and production efficient standpoints, and because it is compatible with our goals.

Physically based rendering is a rendering method that provides a more accurate representation of materials and how they interact with light when compared to traditional real-time models. The separation of materials and lighting at the core of the PBR method makes it easier to create realistic assets that look accurate in all lighting conditions.
