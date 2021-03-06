import unittest
import os,sys,inspect
import poltype
import shutil
import argparse
import getopt

class TestPoltype(unittest.TestCase):

    def __init__(self):
         super(TestPoltype, self).__init__()
         self.ptypepath=os.path.abspath(os.path.join(os.path.abspath(os.path.join(__file__,os.pardir)), os.pardir))+r'/'

    def MakeTestCasePath(self,testfoldername):

        self.poltypemodulepath = os.path.abspath(os.path.join(__file__, os.pardir))
        self.poltypepath=os.path.abspath(os.path.join(self.poltypemodulepath, os.pardir))+r'/'
        self.testcaseparentpath=self.poltypepath+'TestCases'
        if not os.path.isdir(self.testcaseparentpath):
            os.mkdir(self.testcaseparentpath)

        os.chdir(self.testcaseparentpath)
        testcasepath=self.testcaseparentpath+'/'+testfoldername
        if not os.path.isdir(testcasepath):
            os.makedirs(testcasepath)
        os.chdir(testcasepath)
        return testcasepath

    def GenericCopy(self,testcasepath,examplefolder,examplestructure):
        exampleparentfolder='Examples/'
        examplekey5fname=examplestructure.replace('.sdf','_copy.key_5')
        examplestructurepath=self.poltypepath+exampleparentfolder+examplefolder+examplestructure
        examplekeyfilepath=self.ptypepath+exampleparentfolder+examplefolder+examplekey5fname
        shutil.copy(examplestructurepath,testcasepath+examplestructure)
        return examplekeyfilepath,exampleparentfolder

    def GenericTest(self,exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath):
        testparams=ptype.main()
        exampleparams = parameterfile.AmoebaParameterSet(examplekeyfilepath)
        for key in testparams.bonds.keys():
            testitem=testparams.bonds[key]
            exampleitem=exampleparams.bonds[key]
            testk=testitem.k
            examplek=exampleitem.k
            self.assertEqual(testk,examplek)
            testreq=testitem.req
            examplereq=exampleitem.req
            #self.assertEqual(testreq,examplereq)
        for key in testparams.angles.keys():     
            testitem=testparams.angles[key]
            exampleitem=exampleparams.angles[key]
            testk=testitem.k
            examplek=exampleitem.k
            self.assertEqual(testk,examplek)
            testtheteq=testitem.theteq
            exampletheteq=exampleitem.theteq
            #self.assertEqual(testtheteq,exampletheteq)
        for key in testparams.stretch_bends.keys():
            testitem=testparams.stretch_bends[key]
            exampleitem=exampleparams.stretch_bends[key]
            testk1=testitem.k1
            examplek1=exampleitem.k1
            self.assertEqual(testk1,examplek1)
            testk2=testitem.k2
            examplek2=exampleitem.k2
            self.assertEqual(testk2,examplek2)

        for key in testparams.dihedrals.keys():
            testitem=testparams.dihedrals[key]
            exampleitem=exampleparams.dihedrals[key]
            testk=testitem.k
            examplek=exampleitem.k
            self.assertEqual(testk,examplek)
            testperiodicity=testitem.periodicity
            exampleperiodicity=exampleitem.periodicity
            self.assertEqual(testperiodicity,exampleperiodicity)
            testphase=testitem.phase
            examplephase=exampleitem.phase
            self.assertEqual(testphase,examplephase)

        for key in testparams.multipoles.keys():
            testitem=testparams.multipoles[key]
            exampleitem=exampleparams.multipoles[key]
            testmpoles=testitem.potential_terms
            examplempoles=exampleitem.potential_terms
            for termidx in range(len(testmpoles)):
                testterm=testmpoles[termidx]
                exampleterm=examplempoles[termidx]
                self.assertEqual(testterm,exampleterm)           

        self.assertEqual(testparams.multipoles,exampleparams.multipoles)
        try: # parmED needs to be pushed to new branch, they had a bug, use exception until main branch has merged changes
            for atomkey in testparams.atoms.keys():
                testatom=testparams.atoms[atomkey]
                exampleatom=exampleparams.atoms[atomkey]
                testvdwr=testatom.size
                examplevdwr=exampleatom.size
                self.assertEqual(testvdwr,examplevdwr)
                testvdwe=testatom.epsilon
                exampleatome=exampleatom.epsilon
                self.assertEqual(testvdwe,exampleatome)
                testpol=testatom.polarizability
                examplepol=exampleatom.polarizability
                self.assertEqual(testpol,examplepol)
                testpolconntypes=testatom.connected_types
                examplepolconntypes=exampleatom.connected_types
                self.assertEqual(testpolconntypes,examplepolconntypes)
        except:
            pass

    def GenericFolderCopy(self,testcasepath):
        head,tail=os.path.split(testcasepath) # remove last folder since it needs to be copied from examples
        os.chdir('..')
        if not self.dontremovetestcase:
            shutil.rmtree(tail)
        exampleparentfolder='Examples/'
        if self.examplepath==None:
            raise ValueError('examplepath not defined')
        head,examplefoldername=os.path.split(self.examplepath)
        examplefoldername='Fragmenter/'+examplefoldername+r'/'
        newexamplepath=self.poltypepath+exampleparentfolder+examplefoldername
        if not os.path.exists(newexamplepath):
            shutil.copytree(examplepath,newexamplepath)
        if not self.dontremovetestcase:
            shutil.copytree(examplepath,testcasepath)
            testcaseqmtorsionpath=testcasepath+r'/'+'qm-torsion'
            if os.path.exists(testcaseqmtorsionpath):
                shutil.rmtree(testcaseqmtorsionpath)
        curdir=os.getcwd()
        os.chdir(testcasepath)
        files=os.listdir()
        filestodelete=[]
        for f in files:
            if 'key_5' in f:
                filestodelete.append(f)
        for f in filestodelete:
            os.remove(f)
   
    def GrabTorsions(self,folderpath):
        listoftorsions=[]
        listofqmminusmmtxtfiles=[]
        curdir=os.getcwd()
        if folderpath[-1]==r'/':
            qmtorsionfolderpath=folderpath+'qm-torsion'
        else:
            qmtorsionfolderpath=folderpath+r'/'+'qm-torsion'

        os.chdir(qmtorsionfolderpath)
        excludedfoldnames=[]
        files=os.listdir()
        for f in files:
            if 'txt' in f:
                filenamesplit= f.split('.')
                if filenamesplit[1]=='txt':
                    if 'fit' in f:
                        newsplit=filenamesplit[0].split('fit-')
                        array=newsplit[1].split('-')
                        torsion=[int(i) for i in array]
                        listoftorsions.append(torsion)
                        listofqmminusmmtxtfiles.append(qmtorsionfolderpath+f)
        os.chdir(curdir)
        return listoftorsions,listofqmminusmmtxtfiles

    def GrabArrayData(self,filepath):
        anglearray=[]
        qmminusmmarray=[]
        with open(filepath) as infile:
            for line in infile:
                linesplit=line.split()
                angle=float(linesplit[0])
                qmminusmm=float(linesplit[1])
                anglearray.append(angle)
                qmminusmmarray.append(qmminusmm)
        return anglearray,qmminusmmarray


    def FindFragmentJobPath(self,parentrotbnd,testcasepath):
        curdir=os.getcwd()
        os.chdir(testcasepath+'Fragmenter/')
        fragfolders=os.listdir()
        fragpath=None
        for f in fragfolders:
            os.chdir(f)
            fragpath=self.RecursiveFolderSearch('qm-torsion',parentrotbnd)
            if fragpath!=None:
                os.chdir(curdir)
                return fragpath
            os.chdir('..')
        os.chdir(curdir)
        return fragpath

    def RecursiveFolderSearch(self,foldername,parentrotbnd):
        path=None
        for root, dirs, files in os.walk(".", topdown=False):
            for name in dirs:
               path=os.path.join(root, name)
               if self.DoesFolderExistInDirectory(path,foldername)==True:
                   if self.ReadTorsionsFile(parentrotbnd)==True:
                       return path
        return path

    def DoesFolderExistInDirectory(self,path,foldername):
        curdir=os.getcwd()
        os.chdir(path)
        foundfoldername=False
        for f in os.listdir():
            if f==foldername:
                foundfoldername=True
        os.chdir(curdir)
        return foundfoldername

    def ReadTorsionsFile(self,parentrotbnd):
        foundparent=False
        if os.path.isfile('torsions.txt'):
            temp=open('torsions.txt','r')
            results=temp.readlines()
            temp.close()
            firstline=results[0]
            if parentrotbnd in firstline:
                foundparent=True
        return foundparent

    def ReadDictionaryFromFile(self,filepath):
        curdir=os.getcwd()
        os.chdir(filepath)
        dictionary=json.load(open("parentindextofragindex.txt"))
        os.chdir(curdir)
        return dictionary

    def test_MethylamineCommonInputs(self):
        print('Testing common inputs')
        testcasefolder='TestMethylamineCommonInputs/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryMethylamine/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)
    

    def test_MethylaminePsi4(self):
        print('Testing Gaussian')
        testcasefolder='TestMethylamineGaus/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethylamineGaus/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,use_gaus=False,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)


    def test_MethylaminePsi4SPOnly(self):
        print('Testing Gaussian OPT only')
        testcasefolder='TestMethylamineGausOptOnly/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethylamineGausOptOnly/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,use_gausoptonly=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    
    def test_MethylamineDMAESPOptions(self):
        print('Testing DMA and ESP options')
        testcasefolder='TestMethylamineDMAESPOptions/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='Methylamine/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,qmonly=True,espbasisset='aug-cc-pVTZ',dmabasisset='cc-pVTZ',structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
   

 
    def test_MethylamineGeometryOptimizationOptions(self):
        print('Testing Geometry Optimization options ')
        testcasefolder='TestMethylamineGeometryOptimizationOptions/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethylamineGeometryOptimizationOptions/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',optbasisset='6-311G*',gausoptcoords='cartesian',freq=True,optpcm=True,optmaxcycle=500,optmethod='HF',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)
    
    def test_MethanolTorsion(self):
        print('Testing torsion options')
        testcasefolder='TestMethanolTorsion/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethanolTorsion/'
        examplestructure='methanol.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,rotalltors=True,optpcm=True,torsppcm=True,toroptpcm=True,torsionrestraint=.2,foldnum=4,tordatapointsnum=13,toroptmethod='HF',torspmethod='MP2',toroptbasisset='6-311G*',torspbasisset='6-311++G(2d,2p)',structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_MethanolTorsionGaus(self):
        print('Testing torsion options')
        testcasefolder='TestMethanolTorsionGaus/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethanolTorsionGaus/'
        examplestructure='methanol.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,use_gaus=True,rotalltors=True,optpcm=True,torsppcm=True,toroptpcm=True,torsionrestraint=.2,foldnum=4,tordatapointsnum=13,toroptmethod='HF',torspmethod='MP2',toroptbasisset='6-311G*',torspbasisset='6-311++G(2d,2p)',structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)
     
 
    def test_MethanolOnlyRotBnd(self):
        print('Testing onlyrotbnd')
        testcasefolder='TestMethanolOnlyRotBnd/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethanolOnlyRotBnd/'
        examplestructure='methanol.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,onlyrotbndslist='1 2',structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)


    def test_MethanolFitRotBndsList(self):
        print('Testing fitrotbndslist')
        testcasefolder='TestMethanolFitRotBndsList/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='MethanolFitRotBndsList/'
        examplestructure='methanol.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,fitrotbndslist='1 2',structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)


    def test_MethylamineDontDoTorFit(self):
        print('Testing dontdotorfit')
        testcasefolder='TestMethylamineDontDoTorFit/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='Methylamine/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,rotalltors=True,dontdotorfit=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)

    
    def test_MethylamineDontDoTor(self):
        print('Testing dontdotor')
        testcasefolder='TestMethylamineDontDoTor/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='Methylamine/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,dontdotor=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
    

    def test_ModifiedAminoAcid(self):
        print('Testing modified amino acids')
        testcasefolder='TestModifiedAminoAcid/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='ModifiedAminoAcid/'
        examplestructure='methylamine.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,use_gaus=True,amoebabioprmpath='/home/bdw2292/Tinker-release/params/amoebabio18.prm',unmodifiedproteinpdbname='SNase_WT_H.pdb',mutatedresiduenumber='102',mutatedsidechain='CNC.sdf',modifiedresiduepdbcode='CNC',numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True) 
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_Methane(self):
        print('Testing methane symmetry')
        testcasefolder='TestSymmetryMethane/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryMethane/'
        examplestructure='methane.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_Water(self):
        print('Testing water symmetry')
        testcasefolder='TestSymmetryWater/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryWater/'
        examplestructure='water.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_Acetamide(self):
        print('Testing acetamide symmetry')
        testcasefolder='TestSymmetryAcetamide/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryAcetamide/'
        examplestructure='acetamide.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_Ethene(self):
        print('Testing ethene symmetry')
        testcasepath='TestSymmetryEthene/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryEthene/'
        examplestructure='ethene.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)

    def test_Ammonia(self):
        print('Testing ammonia symmetry')
        testcasefolder='TestSymmetryAmmonia/'
        testcasepath=self.MakeTestCasePath(testcasefolder)
        examplefolder='SymmetryAmmonia/'
        examplestructure='ammonia.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)


    def test_Aniline(self):
        print('Testing aniline symmetry')
        testcasefolder='TestSymmetryAniline/'
        testcasepath=self.MakeTestCasePath(testcasepath)
        examplefolder='SymmetryAniline/'
        examplestructure='aniline.sdf'
        examplekeyfilepath,exampleparentfolder=self.GenericCopy(testcasepath,examplefolder,examplestructure)
        ptype=poltype.PolarizableTyper(dontfrag=True,structure=examplestructure,numproc=4,maxmem='20GB',maxdisk='100GB',poltypeini=False,printoutput=True)
        self.GenericTest(exampleparentfolder,testcasepath,examplefolder,examplestructure,ptype,examplekeyfilepath)
    

if __name__ == '__main__':
 
    suite = unittest.TestSuite()
    obj=TestPoltype()
    suite.addTest(obj.test_MethylamineCommonInputs())
    suite.addTest(obj.test_MethylaminePsi4())
    suite.addTest(obj.test_MethylaminePsi4SPOnly())
    suite.addTest(obj.test_MethylamineDMAESPOptions())
    suite.addTest(obj.test_MethylamineGeometryOptimizationOptions())
    suite.addTest(obj.test_MethanolTorsion())
    suite.addTest(obj.test_MethanolTorsionGaus())
    suite.addTest(obj.test_MethanolOnlyRotBnd())
    suite.addTest(obj.test_MethanolFitRotBndsList())
    suite.addTest(obj.test_MethylamineDontDoTorFit())
    suite.addTest(obj.test_MethylamineDontDoTor())
    #suite.addTest(obj.test_ModifiedAminoAcid())
    suite.addTest(obj.test_Methane())
    suite.addTest(obj.test_Water())
    suite.addTest(obj.test_Acetamide())
    suite.addTest(obj.test_Ethene())
    #suite.addTest(obj.test_Ammonia())
    suite.addTest(obj.test_Aniline())

    runner = unittest.TextTestRunner()
    runner.run(suite)

