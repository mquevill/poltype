## Torsion README


![Torsion Protocol](Images/TorsionProtocol.PNG)

* Below is more detailed flow of how files are generated

![Torsion Protocol](Images/TorsionProtocolDetailed.PNG)
<ol>
<li>	Find partial double bonds in amide/acids </li>
<ol>
    <li>	 amidesmarts='[NX3][CX3](=[OX1])' </li>
    <li>	 acidsmarts='[CX3](=O)[OX2]' </li>
    <li>	Exclude this from torsion parameter derivation (just transfer) </li>
</ol>
<li>	Generate list of torsions to derive parameters for </li>
<ol>
    <li>	Take input of missing torsions from databaseparser.py </li>
    <li>	For each bond in molecule </li>
<ol>
        <li>	Check if bond is a ring bond (sometimes we want non-aromatic ring bond for fragmenter input) </li>
        <li>	Check if any aromatic atoms in ring, if ring bond and any aromatic atoms detected in the ring then do not derive torsion parameters for bond </li>
        <li>	Determine a and d from b-c by trying to pick the first heaviest atoms a and d </li>
        <li>	If torsion a-b-c-d is in missing torsion list, then derive parameters for it </li>
        <li>	Check if b-c is in onlyrotbnds list (input for only rotating specific rotatable bond) </li>
        <li>	If rotalltors is on, rotate all possible bonds </li>
        <li>	If bond is in partial double bonds and rotalltors is turned off, then do not derive torsion parameters. </li>
        <li>	If bond is ring bond and non-aromatic puckering is turned on then add to non-aromatic torsion list (to derive parameters for). </li>
        <li>	Grab all torsions around b-c and save for fragmenter and torsiongenerator. </li>
</ol>
</ol>
<li>	Remove duplicate rotatable bond types (if same symmetry classes for b-c show up more than once in list). </li>

<li>	Default max range for each torsion is 0-360 degrees (changes for non-aromatic ring puckering). </li>
<li>	Determine number of points and angle increment needed for each torsion. </li>
<ol>
    <li>	Based on max range, number of cosine terms, number of torsion around rotatable bond. </li>
</ol>
<li>	Find main consecutive torsions. </li>
<ol>
    <li>	Remove individual torsions from torsion list and replace with tuple of two torsions. </li>
<ol>
        <li>	If tortor is in missing tortor list. </li>
</ol>
</ol>
<li>	Prefit Tinker minimize - analyze </li>
<ol>
    <li>	For each target dihedral angle for a rotatable bond, (0-180) and (-180-360) clockwise and counterclockwise </li>
<ol>
        <li>	Minimize input structure (first time from OPT QM structure) to next dihedral angle, save output to .out file </li>
        <li>	Run analyze and compute energies, save in output .alz file </li>
        <li>	Use output previous structure as input into next minimization structure, except when there is a center of the grid each row in 2D has a center for example, 6 points counterclockwise, then move back to center then 5 points clockwise. In 2D after a row is completed, return to center and move up/down 1, then repeat 5 points clockwise, then return to new center, then 6 points counterclockwise etc... </li>
</ol>
</ol>
<li>	For tortor, find energy minima spot from scan, then determine the 1D slices needed (for fitting torsion first then let tortor pick up any remaining difference between QM-MM2, where MM2 is post fit from QM-MM1 (where MM1 is prefit parameters). </li>
<ol>
    <li>	Fix these points on energy surface and do not remove. </li>
    <li>	Flatten energy array, sory by minimum energy and remove most maximum points (except on 1D slices) until reach default value of 40 (otherwise 144 QM points!) </li>
</ol>

<li>	Execute OPT jobs </li>
<ol> 
    <li>	For each tinker minimized structure </li>
<ol>
        <li>	Check for termination signal in QM output file, then create Gaussian/Psi4 input file and then will submit job </li>
        <li>	If finished grab final QM structure and save in .xyz file </li>
        <li>	If daemon specified in input file will use to submit otherwise submit serially on local host </li>
</ol>
</ol>
<li>	Create Gaussian/Psi4 OPT input file </li>
<ol>
    <li>	Same as in optimization.py but add frozen torsion restraints at bottom of COM file  </li>
<ol>
        <li>	Restrain all torsion around all bonds (with some exceptions below) </li>
        <li>	If the bond b-c has heavy atoms a, b (non-hydrogen) then pick those as restraints and don’t pick hydrogen. If there are multiple hydrogen torsions (and no heavy on both sides) then pick only one as restraint. </li>
</ol>
</ol>
<li>	For each opt job submitted </li>
<ol>
    <li>	Compare original QM bond topology to newly optimized QM topology </li>
<ol>
        <li>	If bond lengths differ by more than .2 angstroms, then resubmit the job and increase maxoptcycles +2 </li>
        <li>	Grab Final structure after each finished optimization </li>
</ol>
</ol>

<li>	Create Gaussian/Psi4 ESP input file </li>
<ol>
    <li>	Similar to electrostaticpotential.py </li>
</ol>

<li>	Execute SP Jobs </li>
<ol>
    <li>	For each QM optimized structure </li>
<ol>
        <li>	Only compute SP for opt jobs that were successful (sometimes they crash for no apparent reason, so remove these points from energy surface) </li>
        <li>	Check for termination signal of SP log file, if does not exist then create Gaussian/Psi4 input file and then will submit job </li>
        <li>	If daemon specified in input file will use to submit otherwise submit serially on local host </li>

</ol>
</ol>
</ol>
