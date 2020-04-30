## Manifest

* [Poltype Files](#poltype-files)
* [Poltype Modules](#poltype-modules)
* [Poltype Examples](#poltype-examples)

### POLTYPE Files

```
*.sdf               Input structure file.
*-opt.com           Gaussian input file for geometry optimization.
*-opt_psi.dat       Psi4 input file for geometry optimization.
*-opt.log           Gaussian output file for geometry optimization.
*-opt_psi4.log      Psi4 output file for geometry optimization.
*-opt.chk           Unreadable electron density from geometry optimization.
*-opt.fchk          Human readable electron density from geometry optimization.
*-dma.com           Gaussian input file for QM SP calculation to obtain density for running distributed multipole analysis.
*-dma_psi4.com      Psi4 input file for QM SP calculation to obtain density for running distributed multipole analysis.
*-dma.log           Gaussian output file for QM SP calculation to obtain density for running distributed multipole analysis.
*-dma_psi4.log      Psi4 output file for QM SP calculation to obtain density for running distributed multipole analysis.
*-dma.chk           Unreadable density for running distributed multipole analysis.
*-dma.fchk          Human readable density for running distributed multipole analysis.
*-esp.com           Gaussian input file for QM SP calculation to obtain density for running electrostatic potential fitting.
*-esp_psi4.dat      Psi4 input file for QM SP calculation to obtain density for running electrostatic potential fitting.
*-esp.log           Gaussian output file for QM SP calculation to obtain density for running electrostatic potetnial fitting.
*-esp_psi4.log      Psi4 output file for QM SP calculation to obtain density for running electrostatic potetnial fitting.
*-esp.chk           Unreadable density for running electrostatic potential fitting.
*-esp.fchk          Human readable density for running electrostatic potential fitting.
*.gdmain            Input for GDMA.
dma.punch           Intermediate file produced from GDMA.
*.gdmaout           Output from GDMA.
*.key               First keyfile containing atom indexes, multipoles from GDMA output and polarize terms.
*.grid              Textfile specifying coordinates of where electrostatic potential will be evaluated.
*.cube              Potential from QM SP density at specified grid coordinates, in format not recognized by Tinker.
*.pot               Potential from cube file at specified grid coordinates in Tinker readable format.
*-peditin.txt       Input for poledit to change frames as specified by POLTYPE.
RMSPD.txt           Textfile computing the root mean square potential difference between potential from QM and from MM.
*-groups.txt        Input for amvmpoles.pl to reduce atom typing.
*.xyz_2             Structure using symmetry types rather than atom index types.
*.key_2             Second keyfile using same parameters as *.key but with symmetry type numbers rather than atom index types.
*.key_3             Third keyfile containing multipole parameters from electrostatic potential fitting.
*.key_4             Fourth key file using same parameters as *.key_3 but also includes valence parameters from database.
qm-torsion          Folder containing QM,MM optimized structures and SP computations to evaluate energy along dihedral angle.
*.key_5             Fifth key file using same parameters as *.key_4 but with fitted torsion parameters.
MMDipole.txt        Contains information on MM dipole.
QMDipole.txt        Contains information on QM dipole, only written out for Gaussian currently.
ttt.xyz             Final QM optimized structure.
ttt.key             Final key file.
ttt.xyz_2           Final MM optimized structure from QM.
*-poltype.log       Poltype workflow, computations and external calls are shown in here.
residue_connect.txt Topology stored as SMART strings for every NA and AA residue. Immediately after # is the reisude
                    PDB code. The next line is the SMARTS string. The following line is the atom index corresponding to
                    the SMARTS string. There is a connect block defining bonds and bond order as well.
ModifiedResidue.prm Modified residue parameters are added to this paramter file. This is originally a copy of 
                    amoebabio18.prm and new paramters are appended.
lib.bio18_conv1.txt A library containing a map for PDB records to amoebabio18 paramter types for NA's and AA's. The 
                    first number after atom is the type number, the second number after atom is the class number. The
                    matching atom PDB label is after the class number. The residue PDB code is defined after # at the
                    top of each block in library.
SMARTSToTypeLib.txt A text file mapping each atom in the modified residue stored as a SMARTS string to its corresponding atom type. 


qm-torsion
*********************************************
*-opt-a-b-c-d_angle_preQMOPTprefit.xyz           Tinker XYZ from previous Gaussian log file,before current QM optimzation                                                   and torsion fitting.

*-opt-a-b-c-d_angle_preQMOPTprefit_xyzformat.xyz Tinker XYZ from previous Gaussian log file,before current QM optimzation                                                   and torsion fitting.

*-opt-a-b-c-d_angle_preQMOPTprefit.key           Tinker key using .key_4 parameters but with additional torsion restraints                                                  to fix other torsions during minimization, before current QM optimzation                                                   and torsion fitting.

*-opt-a-b-c-d_angle_preQMOPTprefit.xyz_2         Minimized Tinker XYZ, before current QM optimzation and torsion fitting.

*-opt-a-b-c-d_angle_preQMOPTprefit.out           Output from Tinker minimization, before current QM optimzation and torsion                                                 fitting.

*-opt-a-b-c-d_angle.com                          Gaussian input for geometry optimization.

*-opt-a-b-c-d_angle_psi4.dat                     Psi4 input for geometry optimization.
*-opt-a-b-c-d_angle.chk                          Unreadable density information from geometry optimization.
*-opt-a-b-c-d_angle.log                          Gaussian output from geometry optimization.
*-opt-a-b-c-d_angle_psi4.log                     Psi4 output from geometry optimization.

*-opt-a-b-c-d_angle_postQMOPTprefit.xyz          Tinker XYZ from previous Gaussian log file,after current QM optimzation                                                    and torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTprefit.key          Tinker key using .key_4 parameters but with additional torsion restraints                                                  to fix other torsions during minimization, after QM optimzation and                                                        torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTprefit.xyz_2        Minimized Tinker XYZ, after QM optimzation and torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTprefit.out          Output from Tinker minimization, before QM optimzation and torsion                                                         fitting.

*-opt-a-b-c-d_angle_postQMOPTprefit.alz          Output from Tinker analyze, before QM optimzation and torsion fitting.

*-sp-a-b-c-d_angle.com                           Gaussian input for single point calculation.
*-sp-a-b-c-d_angle_psi4.dat                      Psi4 input for single point calculation.
*-sp-a-b-c-d_angle.chk                           Unreadable density information from single point calculation.
*-sp-a-b-c-d_angle.log                           Gaussian output from single point calculation.
*-sp-a-b-c-d_angle_psi4.log                      Psi4 output from single point calculation.

*-opt-a-b-c-d_angle_postQMOPTpostfit.xyz         Tinker XYZ from previous Gaussian log file,after current QM optimzation                                                    and after torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTpostfit.key         Tinker key using .key_4 parameters but with additional torsion restraints                                                  to fix other torsions during minimization, after QM optimzation and                                                        after torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTpostfit.xyz_2       Minimized Tinker XYZ, after QM optimzation and after torsion fitting.

*-opt-a-b-c-d_angle_postQMOPTpostfit.out         Output from Tinker minimization, before QM optimzation and after torsion                                                   fitting.

*-opt-a-b-c-d_angle_postQMOPTpostfit.alz         Output from Tinker analyze, after QM optimzation and torsion fitting.

*-fit-b-c.png                                    Plot of QM-MM as a function of dihedral angle and the fourier fit.
*-energy-b-c.png                                 Plot of MM1 (prefit),MM2 (postfit),QM and MM1+Fit as a function of                                                         dihedral angle.
```

### Poltype Modules
```
symmetry.py                Handles detecting symmetry in input molecule.
modifiedresidues.py        Handles parameterizing new amino acid side chains and stitching parameters from amoebabio18.prm for                        parts of molecule already parameterized.

multipole.py               Handles multipole frame definitions and GDMA.
valence.py                 Database for searching valence parameters via SMART string matching to input molecule.
apicall.py                 Handles external calls for QM job submission on clusters. THE FUNCTION CallExternalAPI IN THIS                             MODULE NEEDS TO BE MODIFIED FOR SPECIFIC CLUSTER SUBMISSION METHODS.
optimization.py            Handles Gaussian,Psi4 and Tinker minimization.
electrostaticpotential.py  Handles electrostatic potential fitting and Gaussian, Psi4 SP calculations.
torsionfit.py              Handles torsion fitting.
torsiongenerator.py        Handles torsion Gaussian,Psi4 and Tinker minimization, SP and analyze.
fragmenter.py              Handles fragmenting parent molecule, paramterizing torsion and transfering paramters to parent.
test_poltype.py            Handles unittesting for POLTYPE modules.
```

### Poltype Examples
```
ExternalAPIExample                      Example Daemon for jub submission to be used with externalapi command
                                        and bashrcpath command.
MethanolTorsionGaus                     Shows example of torsion fitting with various torsion options using Gaussian.
MethylamineGaus                         Shows example using Gaussian without torsion fitting.
MethylamineGausOptOnly                  Shows example using Gaussian for optimization but Psi4 for SP.
MethanolFitRotBndsList                  Shows example of using the option fitrotbndslist.
MethanolOnlyRotBnd                      Shows example of torsion fitting using the option onlyrotbnd.
MethylamineGeometryOptimizationOptions  Shows example of using various geometry optimzation options.
MethanolTorsion                         Shows example of torsion fitting with various torsion options using Psi4.
ModifiedAminoAcid                       Shows example of replacing amino acid side chain with mutated amino acid side chain
                                        and generates parameters.
SymmetryMethylamine                     Shows example of Z-then-bisector symmetry using neighbors of neighbors.
SymmetryMethane                         Shows example of Z-only symmetry using four same neighbors.
SymmetryWater                           Shows example of Z-then-bisector symmetry using immediate neighbors.
SymmetryAcetamide                       Shows example of Z-then-x symmetry using neighbor of neighbor.
SymmetryEthene                          Shows example of Z-only symmetry with three neighbors (two are same).
SymmetryMethanol                        Shows example of Z-then-x symmetry using immediate neighbors.
SymmetryAmmonia                         Shows example of trisector symmetry.
SymmetryAniline                         Shows example of Z-only symmetry using three neighbors (two are same).
SymmetryDiMethylPhosphate0H             Shows example of bisector frame for P multipole frame.
SymmetryMethylDihydrogenPhosphate       Shows example of choosing correctly z-then-x for P multipole frame.
SymmetryDiMethylPhosphate1H             Shows example of z-then-x chosen correctly for all multipole frames.
SymmetryTriMethylPhosphate              Shows example of z-only on lone oxygen and for P as well.
SymmetryMonoMethylPhosphate1H           Shows example of correct z-then-x frame.
SymmetryMonoMethylPhosphate0H           Shows example of correct z-then-x frame.
```