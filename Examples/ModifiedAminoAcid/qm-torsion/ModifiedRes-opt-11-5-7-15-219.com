%RWF=/scratch/bdw2292/Gau-ModifiedRes/,100GB
%Nosave
%Chk=ModifiedRes-opt-11-5-7-15-219.chk
%Mem=20GB
%Nproc=6
#P opt=(,maxcycle=400) HF/6-31G* MaxDisk=100GB

ModifiedRes Rotatable Bond Optimization on g2-node38.bme.utexas.edu

0 1
 C    1.958815   -1.808952    0.467526
 O    2.604247   -1.766161   -0.585696
 N    0.962037   -0.921418    0.752786
 H    0.585081   -0.902277    1.696093
 C    0.587256    0.146835   -0.187473
 H    0.700160   -0.277138   -1.196206
 C    1.553346    1.335646   -0.020314
 O    1.333500    2.165812    0.862937
 H   -0.965509    1.080488    1.000376
 H   -1.124598    1.328433   -0.754142
 C   -0.869133    0.603161    0.021094
 S   -2.047492   -0.814643   -0.096523
 C   -3.515738    0.044262   -0.131294
 N   -4.552333    0.618925   -0.157570
 N    2.601075    1.372482   -0.884837
 H    2.150045   -2.553231    1.256325
 H    2.836409    0.528855   -1.398741
 H    3.254232    2.140821   -0.807641

11 5 7 15 F
3 5 7 15 F
3 5 7 8 F
11 5 7 8 F
3 5 11 12 F
7 5 11 12 F
5 11 12 13 F

