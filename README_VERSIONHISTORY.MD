## Version History

2.0.0
*     Poltype is modularized for code organization.
*     Unittesting is available for maintaining code robustness.
*     Updated documentation, Examples folder is included.
*     Various high symmetry molecules are handles, see Example folder.
*     Torsion spinning is parallelizable.
*     Modified Amino Acids can be swapped with canonical amino acids in protein PDBs and parameters can be generated for side chain then automatically stitched together with protein forcefield.

2.0.1
* Fix bug in scratch directory assignment for Gaussian

2.0.2
* rdkit does not handle sanitization of some aromatic compounds during torsion spining. This has been turned off.

2.0.3
* Fix bug that prevented post fitting of multiple torsion in molecule (unittesting only tested for small molecules ~ 1 torsion).

2.0.4
* Now when quantum log file exists but is blank, POLTYPE will skip this data point from torsion fitting
* Previously it was assumed if optimization log file exists, then the rest of quantum (SP) finished as well. This assumption has been removed
* function for generating SP for torsion was referecing espmethod and espbasisset instead of torspmethod and torspbasisset

2.0.5
* If RMSPD.txt already existed then this file was not recreated, this is an isssue if the first time created, tinker crashed. This assumption has been removed.

2.0.6
* Now when Tinker version number is not correct a ValueError will be raised
* Now if an external command (for example calling Gaussian, Psi4 etc..) fails, poltype will crash with an error instead of attempting to continue
* Changing default optmethod and toropmethod to wB97X-D
* fragmenter not working yet, add dontfrag to poltype.ini files, need to push updates though to keep poltype.py consistent with other changes

2.0.7
* Default SP for torsion is set back to MP2 for accuracy

2.0.8
* Fragmenter turned off by default
* anglep not assigned unless middle atom is connected to three atoms to be consistent with TINKER
* Using relative error for QM and MM Dipole comparison since the MMDipole scales worse for larger molecules
* Fix bug related to making QM logs blank files and skipping them

2.0.9
* If bond is a ring bond or at least one atom in a bond is a ring atom, cannot spin dihedral angle according to rdkit, so just transfer from database
* Bug fix with charged molecules, solvate GK was turned on during ESP fitting, this is turned on only during torsion fitting

2.1.0
* If running torsion serially on local host instead of crashing poltype when Gaussian/Psi4 job fails, just continue and attempt to do torsion fitting without that data point

2.1.1
* Added TARGET-DIPOLE dipole from ESP QM data to better reproduce MM QM dipole agreement. Gaussian uses center of nuclear charge frame which we convert to center of mass coordinates (Tinker is in COM Frame). Psi4 default is COM frame.

2.1.2
* Bug fix for TARGET-DIPOLE keyword being used before ESP QM generated

2.1.3
* Added SOLUTE keyword for GK and DD-COSMO eletrostatic radii

2.1.4
* Check RMSPD root mean square potential difference and raise error before checking dipoles, (previously supposed to do this but there was a bug)

2.1.5
* When extracting dipole from gaussian dipole is flipped in wrong direction, this is fixed

2.1.6
* Error with generating opt.com file for modifiedresidue library with first poltype run, this has been fixed. Now when poltype finishes,ttt.xyz_2 is deleted so if rerunning ttt.xyz_3 ... isnt created, also *.chk files are deleted if job is successful.

2.1.7
* Torsion parameters are transfered from database if not in rotatable bond list(bug fix from previous edits of rotatable bond definition and transferable torsion in database)
2.1.8
* Bug fix, solvate GK term removed from ttt.key for charged molecules to compute dipoles (ESP fitting done in gas phase, quantum done in gas phase)
2.1.9
* Input structure for mutated residues can have hydrogens on back bone now. Bug for finding all transferable torsions is fixed. See Example ModifiedAminoAcid
* Instead of using babel to predict bonds from PDB via distances a library with SMART strings for amino acids and nucleic acids (residue_connect.txt) is used to match to PDB guess via distances but only keep matched bonds and also bonds connecting residues. The babel guess will sometimes but bonds between sidechains if they are too close to each other in the PDB file so a libarary was needed instead.
2.2.0
* PSI4 error for torsion SP quantum jobs computing Wiberg Bond Index, forgot to pass wavefunction to oeprop class
2.2.1
* Fix error in -pedit.txt where a space was delayed before being written out to text file causing space to be in wrong place, fixed by flushing system buffer
2.2.2 
* Updates to README files as well as fragmenter, torsion libraries, unittesting library.
2.2.3
* Bug in TINKER 8.7 POLEDIT.X, POLTYPE now supports TINKER 8.2 and TINKER >=8.7
2.2.4
* Bug is okay now, continue using TINKER >=8.7
2.2.5
* multipole scaling turned off for alcohols
2.2.6
* fixed symmetry frames bug, added new Symmetry molecules cases to Examples folder, see README.MANIFEST
2.2.7
* Torsion QM jobs parralelized for all torsion as opposed to for a given torsion previously. Example daemon is in Examples folder, see README.MANIFEST.
2.2.8
* Fix bug in parralel torsion
2.2.9
* First working version of torsion fragmenter, this is turned on by default. All optimization have maxcycles of 5, since bond and angle degrees of freedom converge more rapidly than conformation. MMFF94 is used in openbable to minimize geometry before QM optimization is done.