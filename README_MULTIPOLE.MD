## Multipoles

![Multipole Frames](Images/MpoleFrames.PNG)


* Top left: bisector
* Top middle: z-then-x
* Top right z-only
* Bottom left: bisector-then-x
* Bottom middle: z-then-x-then-y
* Bottom right: trisector

* examples of these coordinate systems can be found in README_MANIFEST, see SymmetryExamples

### Multipole Parameters
```
M1 M2 M3      q
              Dx  Dy  Dz
              Qxx
              Qxy  Qyy
              Qxz  Qyz  Qzz
```

### Z-then-X
* M1 M2 M3 

### bisector
* M1 M2 -M2, or M1 -M2 M2, or M1 -M2 -M2

### bisector-then-X
* M1 M2 -M3 -M3

* typically Dy, Qxy, Qyz components are zero, unless it is chiral such as C_alpha in protein