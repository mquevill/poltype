%RWF=/scratch/bdw2292/Gau-ModifiedRes/,100GB
%Nosave
%Chk=ModifiedRes-opt-3-5-11-12-268.chk
%Mem=20GB
%Nproc=6
#P opt=(,maxcycle=400) HF/6-31G* MaxDisk=100GB

ModifiedRes Rotatable Bond Optimization on g2-node38.bme.utexas.edu

0 1
 C    1.927856   -1.831592    0.494886
 O    2.630658   -1.787203   -0.521507
 N    0.945871   -0.920054    0.753127
 H    0.554832   -0.895531    1.690160
 C    0.599927    0.159915   -0.187221
 H    0.714879   -0.252836   -1.199727
 C    1.575331    1.344892   -0.017752
 O    1.208110    2.349327    0.594011
 H   -1.164990    0.463662    1.068472
 H   -0.942621    1.679689   -0.201041
 C   -0.863068    0.614234    0.031141
 S   -1.994098   -0.325757   -1.082158
 C   -3.417260    0.578365   -0.855075
 N   -4.421701    1.192072   -0.713582
 N    2.803623    1.185528   -0.576336
 H    2.059153   -2.594853    1.278069
 H    3.057224    0.282578   -0.969525
 H    3.472573    1.939463   -0.495042

3 5 11 12 F
7 5 11 12 F
11 5 7 15 F
3 5 7 15 F
3 5 7 8 F
11 5 7 8 F
5 11 12 13 F

