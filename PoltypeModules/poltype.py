################################################################
#
# Title: Poltype
# Description: Atomic typer for the polarizable AMOEBA force field
#
# Copyright:            Copyright (c) Johnny C. Wu,
#                   Gaurav Chattree, & Pengyu Ren 2010-2011
#
# Poltype is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation.
#
# Poltype is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
##################################################################

import os
import sys
from socket import gethostname
import subprocess
from openbabel import openbabel
import shutil
import time
import copy
import getopt
import databaseparser
import torsiongenerator as torgen
import modifiedresidues as modres
import symmetry as symm
import torsionfit as torfit
import optimization as opt
import electrostaticpotential as esp
import multipole as mpole
import fragmenter as frag
import rings
from packaging import version
from rdkit import Chem
from rdkit.Chem import rdmolfiles,AllChem,rdmolops
from rdkit.Geometry import Point3D
import vdwfit

class PolarizableTyper():
    def __init__(self,boltzmantemp=8,dontdovdwscan=True,vdwprobepathname=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/VdwProbes/',vdwprobenames=['water'],firsttoroptbasisset='3-21G',firsttoroptmethod='HF',use_gausgeomoptonly=False,maxtorRMSPDRel=.2,vdwmissingfilename='missingvdw.txt',databaseprmfilename='database.prm',tortor=False,torfit2Drotonly=False,torfit1Drotonly=False,skipsecondopt=False,externalparameterdatabase=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/'+'externalparameterdatabase.txt',fitfirsttorsionfoldphase=False,keyfiletoaddtodatabase=None,skipgridsearch=True,torsionprmguessfilename='torsionprmguess.txt',defaultmaxtorsiongridpoints=40,torsionsmissingfilename='torsionsmissing.txt',smallmoleculemm3prmlib=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/'+'mm3.prm',smallmoleculesmartstomm3descrip=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/'+'smartstomm3typedescrip.txt',absdipoletol=.5,transferanyhydrogentor=True,smallmoleculesmartstotinkerdescrip=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/'+'smartstoamoebatypedescrip.txt',smallmoleculeprmlib=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/'+'amoeba09.prm',torspbasissetfile='6-311+g_st_.0.gbs',toroptbasissetfile='6-311g_st_.0.gbs',optbasissetfile='6-311g_st_.0.gbs',dmabasissetfile='6-311g_st__st_.0.gbs',espbasissetfile='aug-cc-pvtz.1.gbs',iodinetorspbasissetfile='def2-svp.1.gbs',iodinetoroptbasissetfile='def2-svp.1.gbs',iodineoptbasissetfile='def2-svp.1.gbs',iodinedmabasissetfile='def2-svp.1.gbs',iodineespbasissetfile='def2-tzvpp.1.gbs',basissetpath=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/'+'BasisSets/',refinenonaroringtors=False,maxgrowthcycles=4,use_gauPCM=False,fitqmdipole=False,allownonaromaticringscanning=False,scfmaxiter=500,suppresstorfiterr=False,obminimizeexe='obminimize',readinionly=False,suppressdipoleerr=False,topologylib='residue_connect.txt',poltypepath=os.path.split(__file__)[0],WBOtol=.05,dontfrag=False,isfragjob=False,dipoletol=.1,externalapi=None,printoutput=False,poltypeini=True,structure=None,prmstartidx=401,numproc="1",maxmem="700MB",maxdisk="100GB",gausdir=None,gdmadir=None,tinkerdir=None,scratchdir="/scratch",paramhead=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+ "/ParameterFiles/amoebabio18_header.prm",gausexe=None,formchkexe='formchk',cubegenexe='cubegen',gdmaexe='gdma',avgmpolesexe=os.path.abspath(os.path.join(os.path.abspath(os.path.join(__file__, os.pardir)), os.pardir)) + "/PoltypeModules/avgmpoles.pl",peditexe='poledit.x',potentialexe='potential.x',minimizeexe='minimize.x',analyzeexe='analyze.x',superposeexe='superpose.x',defopbendval=0.20016677990819662,Hartree2kcal_mol=627.5095,optbasisset='6-31G*',toroptbasisset='6-31G*',dmabasisset='6-311G**',espbasisset="aug-cc-pVTZ",torspbasisset="6-311+G*",optmethod='HF',toroptmethod='wB97X-D',torspmethod='wB97X-D',dmamethod='MP2',espmethod='MP2',qmonly = False,espfit = True,parmtors = True,foldnum=3,foldoffsetlist = [ 0.0, 180.0, 0.0, 180.0, 0.0, 180.0 ],torlist = None,rotbndlist = None,maxRMSD=.1,maxRMSPD=1,maxtorRMSPD=1.8,tordatapointsnum=None,gentorsion=False,gaustorerror=False,torsionrestraint=.1,onlyrotbndslist=None,rotalltors=False,dontdotor=False,dontdotorfit=False,toroptpcm=False,optpcm=False,torsppcm=False,use_gaus=False,use_gausoptonly=False,freq=False,postfit=False,bashrcpath=None,amoebabioprmpath=None,libpath=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+ "/ModifiedResidueLibraries/lib.bio18_conv1.txt",SMARTSToTypelibpath=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ModifiedResidueLibraries/SMARTSToTypeLib.txt',ModifiedResiduePrmPath=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+'/ParameterFiles/ModifiedResidue.prm',modifiedproteinpdbname=None,unmodifiedproteinpdbname=None,mutatedsidechain=None,mutatedresiduenumber=None,modifiedresiduepdbcode=None,optmaxcycle=3,torkeyfname=None,gausoptcoords='',forcefield="AMOEBA",helpfile='README.md',versionfile='version.md',sleeptime=30):
        self.boltzmantemp=boltzmantemp
        self.dontdovdwscan=dontdovdwscan
        self.vdwprobepathname=vdwprobepathname
        self.vdwprobenames=vdwprobenames
        self.firsttoroptmethod=firsttoroptmethod
        self.firsttoroptbasisset=firsttoroptbasisset
        self.use_gausgeomoptonly=use_gausgeomoptonly
        self.maxtorRMSPDRel=maxtorRMSPDRel
        self.vdwmissingfilename=vdwmissingfilename
        self.databaseprmfilename=databaseprmfilename
        self.tortor=tortor
        self.torfit2Drotonly=torfit2Drotonly
        self.torfit1Drotonly=torfit1Drotonly
        self.skipsecondopt=skipsecondopt
        self.externalparameterdatabase=externalparameterdatabase
        self.fitfirsttorsionfoldphase=fitfirsttorsionfoldphase
        self.keyfiletoaddtodatabase=keyfiletoaddtodatabase
        self.skipgridsearch=skipgridsearch
        self.torsionprmguessfilename=torsionprmguessfilename
        self.defaultmaxtorsiongridpoints=defaultmaxtorsiongridpoints
        self.torsionsmissingfilename=torsionsmissingfilename
        self.smallmoleculemm3prmlib=smallmoleculemm3prmlib
        self.smallmoleculesmartstomm3descrip=smallmoleculesmartstomm3descrip
        self.transferanyhydrogentor=transferanyhydrogentor

        self.absdipoletol=absdipoletol
        self.torspbasissetfile=torspbasissetfile
        self.toroptbasissetfile=toroptbasissetfile
        self.optbasissetfile=optbasissetfile
        self.dmabasissetfile=dmabasissetfile
        self.espbasissetfile=espbasissetfile
        self.iodinetorspbasissetfile=iodinetorspbasissetfile
        self.iodinetoroptbasissetfile=iodinetoroptbasissetfile
        self.iodineoptbasissetfile=iodineoptbasissetfile
        self.iodinedmabasissetfile=iodinedmabasissetfile
        self.iodineespbasissetfile=iodineespbasissetfile
        self.basissetpath=basissetpath
        self.smallmoleculeprmlib=smallmoleculeprmlib
        self.smallmoleculesmartstotinkerdescrip=smallmoleculesmartstotinkerdescrip
        self.refinenonaroringtors=refinenonaroringtors
        self.fitqmdipole=fitqmdipole
        self.maxgrowthcycles=maxgrowthcycles
        self.use_gauPCM=use_gauPCM
        self.allownonaromaticringscanning=allownonaromaticringscanning
        self.scfmaxiter=scfmaxiter
        self.suppresstorfiterr=suppresstorfiterr
        self.obminimizeexe=obminimizeexe
        self.readinionly=readinionly
        self.suppressdipoleerr=suppressdipoleerr
        self.use_gaus=use_gaus
        self.use_gausoptonly=use_gausoptonly
        self.topologylibpath=os.path.abspath(os.path.join(poltypepath, '..'))+r'/'+topologylib
        self.WBOtol=WBOtol
        self.isfragjob=isfragjob
        self.dontfrag=dontfrag
        self.dipoletol=dipoletol
        self.externalapi=externalapi
        self.printoutput=printoutput
        self.poltypepath=poltypepath
        self.molstructfname=structure
        self.poltypeini=poltypeini
        self.prmstartidx = prmstartidx
        self.numproc = numproc
        self.maxmem = maxmem
        self.maxdisk = maxdisk
        self.gausdir = gausdir
        self.gdmadir = gdmadir
        self.tinkerdir = tinkerdir
        self.scratchdir = scratchdir
        self.paramhead = paramhead
        self.gausexe =  gausexe
        self.formchkexe =  formchkexe
        self.cubegenexe =  cubegenexe
        self.gdmaexe = gdmaexe
        self.avgmpolesexe = avgmpolesexe
        self.peditexe = peditexe
        self.potentialexe = potentialexe
        self.minimizeexe = minimizeexe
        self.analyzeexe = analyzeexe
        self.superposeexe = superposeexe
        self.defopbendval = defopbendval
        self.Hartree2kcal_mol = Hartree2kcal_mol
        self.optbasisset = optbasisset             
        self.toroptbasisset = toroptbasisset         
        self.dmabasisset = dmabasisset             
        self.espbasisset = espbasisset         
        self.torspbasisset = torspbasisset
        self.qmonly = qmonly
        self.sleeptime = sleeptime
        self.espfit = espfit
        self.parmtors = parmtors
        self.foldnum=foldnum
        self.nfoldlist =  list(range(1,self.foldnum+1))
        self.foldoffsetlist = foldoffsetlist
        self.parentdir=os.getcwd()
        if torlist==None:
            self.torlist = []
        else:
            self.torlist=torlist
        if rotbndlist==None:
            self.rotbndlist = []
        else:
            self.rotbndlist=rotbndlist
           
            
        self.maxRMSD=maxRMSD
        self.maxRMSPD=maxRMSPD
        self.maxtorRMSPD=maxtorRMSPD
        self.tordatapointsnum=tordatapointsnum
        self.gentorsion=gentorsion
        self.gaustorerror=gaustorerror
        self.torsionrestraint=torsionrestraint
        if onlyrotbndslist==None:
            self.onlyrotbndslist=[]
        else:
           
            self.onlyrotbndslist=onlyrotbndslist.split(',')
            templist=[]
            for ele in self.onlyrotbndslist:
                nums=ele.lstrip().rstrip().split()
                temp=[]
                for e in nums:
                    temp.append(int(e))
                templist.append(temp)
            self.onlyrotbndslist=templist
        self.rotalltors=rotalltors
        self.dontdotor=dontdotor
        self.dontdotorfit=dontdotorfit
        self.toroptpcm=toroptpcm
        self.optpcm=optpcm
        self.torsppcm=torsppcm
        self.freq=freq
        self.postfit=postfit
        self.bashrcpath=bashrcpath
        self.amoebabioprmpath=amoebabioprmpath
        self.libpath=libpath
        self.SMARTSToTypelibpath=SMARTSToTypelibpath
        self.ModifiedResiduePrmPath=ModifiedResiduePrmPath
        self.modifiedproteinpdbname=modifiedproteinpdbname
        self.unmodifiedproteinpdbname=unmodifiedproteinpdbname
        self.mutatedsidechain=mutatedsidechain
        self.mutatedresiduenumber=mutatedresiduenumber
        self.modifiedresiduepdbcode=modifiedresiduepdbcode
        self.optmaxcycle=optmaxcycle
        self.torkeyfname=torkeyfname
        self.gausoptcoords=gausoptcoords
        self.forcefield=forcefield
        self.helpfile=helpfile
        self.versionfile=versionfile 
        self.optmethod=optmethod               
        self.toroptmethod=toroptmethod              
        self.torspmethod=torspmethod                   
        self.dmamethod=dmamethod                    
        self.espmethod=espmethod                 
        
        opts, xargs = getopt.getopt(sys.argv[1:],'h',["help"])

        for o, a in opts:
            if o in ("-h", "--help"):
                self.copyright()
                self.usage()
                sys.exit(2)
                            
        if self.poltypeini==True:
            temp=open(os.getcwd()+r'/'+'poltype.ini','r')
            results=temp.readlines()
            temp.close()
            for line in results:
                if '#' not in line and line!='\n':
                    if '=' in line:
                        linesplit=line.split('=',1)
                        a=linesplit[1].replace('\n','').rstrip().lstrip()
                        newline=linesplit[0]
                        if a=='None':
                            continue
                    else:
                        newline=line

                    if "rotalltors" in newline:
                        if '=' not in line:
                            self.rotalltors = True
                        else:
                            self.rotalltors=self.GrabBoolValue(a)

                    elif "use_gausgeomoptonly" in newline:
                        if '=' not in line:
                            self.use_gausgeomoptonly = True
                        else:
                            self.use_gausgeomoptonly=self.GrabBoolValue(a)

                    elif "tortor" in newline:
                        if '=' not in line:
                            self.tortor = True
                        else:
                            self.tortor=self.GrabBoolValue(a)

                    elif "keyfiletoaddtodatabase" in newline:
                        self.keyfiletoaddtodatabase=a

                    elif "refinenonaroringtors" in newline:
                        if '=' not in line:
                            self.refinenonaroringtors = True
                        else:
                            self.refinenonaroringtors=self.GrabBoolValue(a)
                    elif "fitfirsttorsionfoldphase" in newline:
                        if '=' not in line:
                            self.fitfirsttorsionfoldphase = True
                        else:
                            self.fitfirsttorsionfoldphase=self.GrabBoolValue(a)
                    elif "skipsecondopt" in newline:
                        if '=' not in line:
                            self.skipsecondopt = True
                        else:
                            self.skipsecondopt=self.GrabBoolValue(a)

                    elif "fitqmdipole" in newline:
                        if '=' not in line:
                            self.fitqmdipole = True
                        else:
                            self.fitqmdipole=self.GrabBoolValue(a)
                    elif "maxgrowthcycles" in newline:
                        self.maxgrowthcycles=int(a)
                    elif "boltzmantemp" in newline:
                        self.boltzmantemp=float(a)
                    elif "use_gauPCM" in newline:
                        if '=' not in line:
                            self.use_gauPCM = True
                        else:
                            self.use_gauPCM=self.GrabBoolValue(a)

                    elif 'allownonaromaticringscanning' in newline:
                        if '=' not in line:
                            self.allownonaromaticringscanning=True
                        else:
                            self.allownonaromaticringscanning=self.GrabBoolValue(a)

                    elif 'poltypepath' in newline:
                        self.poltypepath=a
                    elif 'paramhead' in newline:
                        self.paramhead = a
                    elif 'WBOtol' in newline:
                        self.WBOtol=float(a)

                    elif 'scfmaxiter' in newline:
                        self.scfmaxiter=a
                    elif 'printoutput' in newline:
                        if '=' not in line:
                            self.printoutput=True
                        else:
                            self.printoutput=self.GrabBoolValue(a)
                    elif 'suppressdipoleerr' in newline:
                        if '=' not in line:
                            self.suppressdipoleerr=True
                        else:
                            self.suppressdipoleerr=self.GrabBoolValue(a)
                    elif 'isfragjob' in newline:
                        if '=' not in line:
                            self.isfragjob=True
                        else:
                            self.isfragjob=self.GrabBoolValue(a)
                    elif "dontfrag" in newline:
                        if '=' not in line:
                            self.dontfrag=True
                        else:
                            self.dontfrag=self.GrabBoolValue(a)
                    elif "externalapi" in newline and a!='None':
                        self.externalapi=a
                    elif "gausoptcoords" in newline:
                        self.gausoptcoords = a
                    elif "suppresstorfiterr" in newline:
                        if '=' not in line:
                            self.suppresstorfiterr=True
                        else:
                            self.suppresstorfiterr=self.GrabBoolValue(a)
                    elif "toroptbasisset" in newline:
                        self.toroptbasisset = a
                    elif "modifiedresiduepdbcode" in newline:
                        self.modifiedresiduepdbcode = a
                    elif "mutatedsidechain" in newline:
                        self.mutatedsidechain = a
                    elif "mutatedresiduenumber" in newline:
                        self.mutatedresiduenumber = a
                    elif "unmodifiedproteinpdbname" in newline:
                        self.unmodifiedproteinpdbname = a
                        self.molstructfname='ModifiedRes.sdf'
                    elif "dmamethod" in newline:
                        self.dmamethod =a
                    elif "bashrcpath" in newline and a!='None':
                        self.bashrcpath = a
                    elif "modifiedproteinpdbname" in newline:
                        self.modifiedproteinpdbname = a
                        self.molstructfname='ModifiedRes.sdf'
                    elif "amoebabioprmpath" in newline:
                        self.amoebabioprmpath = a
                    elif "structure" in newline:
                        self.molstructfname = a
                    elif "torsppcm" in newline:
                        if '=' not in line:
                            self.torsppcm = True
                        else: 
                            self.torsppcm=self.GrabBoolValue(a)
                    elif "freq" in newline:
                        if '=' not in line:
                            self.freq = True
                        else:
                            self.freq=self.GrabBoolValue(a)
                    elif "optpcm" in newline and 'tor' not in line:
                        if '=' not in line:
                            self.optpcm = True
                        else:
                            self.optpcm=self.GrabBoolValue(a)
                    elif "toroptpcm" in newline:
                        if '=' not in line:
                            self.optpcm = True
                        else:
                            self.optpcm=self.GrabBoolValue(a)
                    elif "use_gaus" in newline and 'opt' not in newline:
                        if '=' not in line:
                            self.use_gaus = True
                        else:
                            self.use_gaus=self.GrabBoolValue(a)
                    elif "use_gausoptonly" in newline:
                        if '=' not in line:
                            self.use_gausoptonly = True
                        else:
                            self.use_gausoptonly=self.GrabBoolValue(a)
                    elif "dontdotor" in newline:
                        if '=' not in line:
                            self.dontdotor = True
                        else:
                            self.dontdotor=self.GrabBoolValue(a)

                    elif "dontdovdwscan" in newline:
                        if '=' not in line:
                            self.dontdovdwscan = True
                        else:
                            self.dontdovdwscan=self.GrabBoolValue(a)


                    elif "dontdotorfit" in newline:
                        if '=' not in line:
                            self.dontdotorfit = True
                        else:
                            self.dontdotorfit=self.GrabBoolValue(a)
                    elif "optmaxcycle" in newline:
                        self.optmaxcycle = int(a)
                    elif "torsionrestraint" in newline:
                        self.torsionrestraint=float(a)
                    elif "foldnum" in newline:
                        self.foldnum=int(a)
                        self.nfoldlist =  list(range(1,self.foldnum+1))

                    elif "tordatapointsnum" in newline:
                        self.tordatapointsnum=int(a)
                    elif "onlyrotbndslist" in newline:
                        self.onlyrotbndslist=a.split(',')
                        templist=[]
                        for ele in self.onlyrotbndslist:
                            nums=ele.lstrip().rstrip().split()
                            temp=[]
                            for e in nums:
                                temp.append(int(e))
                            templist.append(temp)
                        self.onlyrotbndslist=templist

                    elif "optmethod" in newline and 'tor' not in newline:
                        self.optmethod = a
                    elif "espmethod" in newline and 'tor' not in newline:
                        self.espmethod = a
                    elif "torspmethod" in newline:
                        self.torspmethod = a
                    elif "toroptmethod" in newline:
                        self.toroptmethod = a
                    elif "numproc" in newline:
                        self.numproc = a
                    elif "maxmem" in newline:
                        self.maxmem = a
                    elif "maxdisk" in newline:
                        self.maxdisk = a
                    elif "atmidx" in newline:
                        self.prmstartidx = int(a)
                    elif "optbasisset" in newline and 'tor' not in newline:
                        self.optbasisset = a
                    elif "dmabasisset" in newline:
                        self.dmabasisset = a
                    elif "popbasisset" in newline:
                        self.popbasisset = a
                    elif "espbasisset" in newline:
                        self.espbasisset = a
                    elif "torspbasisset" in newline:
                        self.torspbasisset = a
                    elif "optlog" in newline:
                        self.logoptfname = a
                    elif "dmalog" in newline:
                        self.logdmafname = a
                    elif "esplog" in newline:
                        self.logespfname = a
                    elif "dmafck" in newline:
                        self.fckdmafname = a
                    elif "espfck" in newline:
                        self.fckespfname = a
                    elif "dmachk" in newline:
                        self.chkdmafname = a
                    elif "espchk" in newline:
                        self.chkespfname = a
                    elif "formchk" in newline:
                        self.fname = a
                    elif "gdmaout" in newline:
                        self.gdmafname = a
                    elif "gbindir" in newline:
                        self.gausdir = a
                    elif "forcefield" in newline:
                        self.forcefield = a
                    elif "qmonly" in newline:
                        if '=' not in line:
                            self.qmonly = True
                        else:
                            self.qmonly = self.GrabBoolValue(a)
                    elif "sleeptime" in newline:
                        self.sleeptime = int(a)
                    elif "help" in newline:
                        self.copyright()
                        self.usage()
                        sys.exit(2)
                    else:
                        print('Unrecognized '+line)
                        self.usage()
                        print('Unrecognized '+line)
                        sys.exit()
        self.secondtoroptbasisset=self.toroptbasisset
        self.secondtoroptmethod=self.toroptmethod 
        self.SanitizeAllQMMethods()
        if self.readinionly==True:
            return
        self.SanitizeMMExecutables()
        self.copyright()
        self.initialize()
        self.init_filenames()
 
        # Use openbabel to create a 'mol' object from the input molecular structure file. 
        # Openbabel does not play well with certain molecular structure input files,
        # such as tinker xyz files. (normal xyz are fine)
    
        
        if not __name__ == '__main__':
            params=self.main()

    def SanitizeAllQMMethods(self):
        self.optmethod=self.SanitizeQMMethod(self.optmethod,True)                 
        self.toroptmethod=self.SanitizeQMMethod(self.toroptmethod,True)                  
        self.torspmethod=self.SanitizeQMMethod(self.torspmethod,False)                    
        self.dmamethod=self.SanitizeQMMethod(self.dmamethod,False)                      
        self.espmethod=self.SanitizeQMMethod(self.espmethod,False)     
       
    def GrabBoolValue(self, value):
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        raise ValueError('Could not convert "{}" into a boolean!'.format(value))

    def SanitizeQMMethod(self,method,optmethodbool):
        if method[-1]=='D': # assume DFT, gaussian likes D, PSI4 likes -D
            if method[-2]=='-':
                if self.use_gaus or self.use_gausoptonly and optmethodbool==True:
                    method=method.replace('-D','D')
                if self.use_gaus and optmethodbool==False:
                    method=method.replace('-D','D')

            else:
                if not self.use_gaus and not self.use_gausoptonly and optmethodbool==True:
                    method=method.replace('D','-D')
                if not (self.use_gaus) and optmethodbool==False:
                    method=method.replace('D','-D')

        return method
 

    def WriteToLog(self,string):
        now = time.strftime("%c",time.localtime())
        self.logfh.write(now+' '+string+'\n')
        self.logfh.flush()
        os.fsync(self.logfh.fileno())

        
    def SanitizeMMExecutables(self):
        self.peditexe=self.SanitizeMMExecutable(self.peditexe)
        self.potentialexe=self.SanitizeMMExecutable(self.potentialexe)
        self.minimizeexe=self.SanitizeMMExecutable(self.minimizeexe)
        self.analyzeexe=self.SanitizeMMExecutable(self.analyzeexe)
        self.superposeexe=self.SanitizeMMExecutable(self.superposeexe)

    def SanitizeMMExecutable(self, executable):
        # Try to find Tinker executable with/without suffix
        if self.tinkerdir is None:
            self.tinkerdir = os.getenv("TINKERDIR", default="")
        exe = os.path.join(self.tinkerdir, executable)
        if self.which(exe) is None:
            exe = exe[:-2] if exe.endswith('.x') else exe + '.x'
            if self.which(exe) is None:
                print("ERROR: Cannot find Tinker {} executable".format(executable))
                sys.exit(2)
        return exe

    def which(self,program):
        def is_exe(fpath):
            try:
                 return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
            except:
                 return None
    
        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file
    
        return None

    def initialize(self):
        """
        Intent: Initialize all paths to needed executables
        Input:
        Output:
        Referenced By: main
        Description: -
        """
        self.foundgauss=False
        if self.gausdir is None:
            self.gausdir = ""
        if self.gausexe is None:
            self.gausexe = ""

        if self.which(os.path.join(self.gausdir, self.gausexe)) is None:
            for g in ["g16", "g09", "g03"]:
                gausexe = self.which(os.path.join(self.gausdir, g))
                if gausexe is not None:
                    self.gausexe = gausexe
                    self.gausdir = os.path.dirname(gausexe)
                    self.foundgauss=True
                    break

        if self.use_gaus or self.use_gausoptonly:
            if self.which(os.path.join(self.gausdir, self.gausexe)) is None:
                print("ERROR: Invalid Gaussian directory: ", self.gausdir)
                sys.exit(1)
            self.cubegenexe = os.path.join(self.gausdir,self.cubegenexe)
            self.formchkexe = os.path.join(self.gausdir,self.formchkexe)

        if self.which('obminimize') is not None:
            self.obminimizeexe = self.which('obminimize')

        cmdstr=self.analyzeexe+' '+os.path.abspath(os.path.join(self.poltypepath, os.pardir))+r'/VersionFiles/'+'water.xyz'+' '+'-k'+' '+os.path.abspath(os.path.join(self.poltypepath, os.pardir))+r'/VersionFiles/'+'water.key'+' '+'e'+'>'+' '+'version.out'
        try:
            print('Calling: '+cmdstr) 
            returned_value = subprocess.call(cmdstr, shell=True)
        except:
            raise ValueError("ERROR: " + cmdstr+' '+'path'+' = '+os.getcwd())      
        temp=open('version.out','r')
        results=temp.readlines()
        temp.close()
        latestversion = False
        for line in results:
            if "Version" in line:
                linesplit = line.split()
                self.versionnum = linesplit[2]
                if version.parse(self.versionnum) >= version.parse("8.8.3"):
                    latestversion = True
                    break

        if not latestversion:
            if self.forcefield.upper() != "AMOEBA+":  #allow old version for AMOEBA+
                raise ValueError("Notice: Not latest working version of tinker (8.8.3)"+' '+os.getcwd())
      
        if ("TINKERDIR" in os.environ):
            self.tinkerdir = os.environ["TINKERDIR"]
            self.peditexe = os.path.join(self.tinkerdir,self.peditexe)
            self.potentialexe = os.path.join(self.tinkerdir,self.potentialexe)
            self.minimizeexe = os.path.join(self.tinkerdir,self.minimizeexe)
            self.analyzeexe = os.path.join(self.tinkerdir,self.analyzeexe)
            self.superposeexe = os.path.join(self.tinkerdir,self.superposeexe)
    
        if (not self.which(self.analyzeexe)):
            print("ERROR: Cannot find TINKER analyze executable")
            sys.exit(2)
            
            
            

        if self.gdmadir is None:
            self.gdmadir = os.getenv("GDMADIR", default="")
        self.gdmaexe = os.path.join(self.gdmadir, self.gdmaexe) 
        if (not self.which(self.gdmaexe)):
            print("ERROR: Cannot find GDMA executable")
            sys.exit(2)


        if (not self.which('psi4')):
            print("ERROR: Cannot find PSI4 executable")
            sys.exit(2)
         

        if self.use_gaus or self.use_gausoptonly:
            if ("GAUSS_SCRDIR" in os.environ):
                self.scratchdir = os.environ["GAUSS_SCRDIR"]
                if not os.path.isdir(self.scratchdir):
                    os.mkdir(self.scratchdir)
    
    
    
    
    
    def init_filenames (self):
        """
        Intent: Initialize file names
        Input:
        Output:
        Referenced By: main
        Description: -
        """
    
    
        if ("GAUSS_SCRDIR" in os.environ):
            self.scratchdir = os.environ["GAUSS_SCRDIR"].rstrip('//')
            if not os.path.isdir(self.scratchdir):
                os.mkdir(self.scratchdir)

        else:
            if ("PSI_SCRATCH" in os.environ):
                self.scratchdir = os.environ["PSI_SCRATCH"]
                if not os.path.isdir(self.scratchdir):
                    os.mkdir(self.scratchdir)
    
        head, self.molstructfname = os.path.split(self.molstructfname)
        self.molecprefix =  os.path.splitext(self.molstructfname)[0]
        self.logfname = self.assign_filenames ( "logfname" , "-poltype.log")
        self.chkname = self.assign_filenames ( "chkname" , ".chk")
        self.fname = self.assign_filenames ( "fname" , ".fchk")
        self.gausfname = self.assign_filenames ( "gausfname" , ".log")
        self.firstgausoptfname = self.assign_filenames ( ".gausoptfname" , "-opt_1.log")
        self.secondgausoptfname = self.assign_filenames ( ".gausoptfname" , "-opt_2.log")
        self.gdmafname = self.assign_filenames ( "gdmafname" , ".gdmaout")
        self.keyfname = self.assign_filenames ( "keyfname" , ".key")
        self.xyzfname = self.assign_filenames ( "xyzfname" , ".xyz")
        self.peditinfile = self.assign_filenames ( "peditinfile" , "-peditin.txt")
        self.superposeinfile = self.assign_filenames ( "superposeinfile" , "-superin.txt")
        self.espgrdfname = self.assign_filenames ( "espgrdfname" , ".grid")
        self.qmespfname = self.assign_filenames ( "qmespfname" , ".cube")
        self.qmesp2fname = self.assign_filenames ( "qmesp2fname" , ".pot")
        self.grpfname = self.assign_filenames ( "grpfname" , "-groups.txt")
        self.key2fname = self.assign_filenames ( "key2fname" , ".key_2")
        self.key3fname = self.assign_filenames ( "key3fname" , ".key_3")
        self.key4fname = self.assign_filenames ( "key4fname" , ".key_4")
        self.key5fname = self.assign_filenames ( "key5fname" , ".key_5")
        self.key6fname= self.assign_filenames ( "key6fname" , ".key_6")
        self.xyzoutfile = self.assign_filenames ( "xyzoutfile" , ".xyz_2")
        self.scrtmpdirgau = self.scratchdir.rstrip('//') + '/Gau-' + self.molecprefix
        self.scrtmpdirpsi4 = self.scratchdir.rstrip('//') + '/Psi4-' + self.molecprefix

        self.tmpxyzfile = 'final.xyz'
        self.tmpkeyfile = 'final.key'
        self.comtmp = self.assign_filenames ( "comtmp" , "-tmp.com")
        self.firstcomoptfname = self.assign_filenames ( "comoptfname" , "-opt_1.com")
        self.firstchkoptfname = self.assign_filenames ( "chkoptfname" , "-opt_1.chk")
        self.firstfckoptfname = self.assign_filenames ( "fckoptfname" , "-opt_1.fchk")
        self.firstlogoptfname = self.assign_filenames ( "logoptfname" , "-opt_1.log")
        self.secondcomoptfname = self.assign_filenames ( "comoptfname" , "-opt_2.com")
        self.secondchkoptfname = self.assign_filenames ( "chkoptfname" , "-opt_2.chk")
        self.secondfckoptfname = self.assign_filenames ( "fckoptfname" , "-opt_2.fchk")
        self.secondlogoptfname = self.assign_filenames ( "logoptfname" , "-opt_2.log")

        self.compopfname = self.assign_filenames ( "compopfname" , "-pop.com")
        self.chkpopfname = self.assign_filenames ( "chkpopfname" , "-pop.chk")
        self.fckpopfname = self.assign_filenames ( "fckpopfname" , "-pop.fchk")
        self.logpopfname = self.assign_filenames ( "logpopfname" , "-pop.log")
        self.comdmafname = self.assign_filenames ( "comdmafname" , "-dma.com")
        self.chkdmafname = self.assign_filenames ( "chkdmafname" , "-dma.chk")
        self.fckdmafname = self.assign_filenames ( "fckdmafname" , "-dma.fchk")
        self.logdmafname = self.assign_filenames ( "logdmafname" , "-dma.log")
        self.comespfname = self.assign_filenames ( "comespfname" , "-esp.com")
        self.chkespfname = self.assign_filenames ( "chkespfname" , "-esp.chk")
        self.fckespfname = self.assign_filenames ( "fckespfname" , "-esp.fchk")
        self.logespfname = self.assign_filenames ( "logespfname" , "-esp.log")


    def assign_filenames (self,filename,suffix):
        if filename in globals():
            return eval(filename)
        else:
            return self.molecprefix + suffix
    
    def printfile(self,filename):
        with open(os.path.abspath(os.path.join(self.poltypepath, os.pardir))+r'/'+filename,'r') as f:
            print(f.read(), end='')
    
    def copyright(self):
        self.printfile(self.versionfile)
    
    def usage(self):
        self.printfile(self.helpfile)
    
    def FindAddedHydrogenIndexes(self,mols):
        hydindexes=[]
        hydratedmol=mols[1]
        originalmol=mols[0]
        smarts=rdmolfiles.MolToSmarts(originalmol)
        matches = hydratedmol.GetSubstructMatches(Chem.MolFromSmarts(smarts))
        firstmatch=matches[0]
        for atom in hydratedmol.GetAtoms():
            atomidx=atom.GetIdx()
            if atomidx not in firstmatch: # if its an H
                hydindexes.append(atomidx)
        return hydindexes
    
    def CheckIsInput2D(self,mol,obConversion,rdkitmol):
        is2d=True
        for atom in openbabel.OBMolAtomIter(mol):
            zcoord=atom.GetZ()
            if zcoord!=0:
                is2d=False
        newmol=mol 
        if is2d==True: 
            molprefix=self.molstructfname.split('.')[0]
            newname=molprefix+'_3D'+'.mol'
            self.molstructfname=newname

            rdmolfiles.MolToMolFile(rdkitmol,'test.mol',kekulize=True)
            AllChem.EmbedMolecule(rdkitmol)
            rdmolfiles.MolToMolFile(rdkitmol,newname,kekulize=True)
            newmol = openbabel.OBMol()
            inFormat = obConversion.FormatFromExt(newname)
            obConversion.SetInFormat(inFormat)
            obConversion.ReadFile(newmol,newname)
    
        return newmol,rdkitmol
    
    def CallJobsSeriallyLocalHost(self,fulljobtooutputlog,skiperrors):
       for job in fulljobtooutputlog.keys():
           temp={}
           self.call_subsystem(job,True,skiperrors)
           temp[job]=fulljobtooutputlog[job]
           finishedjob,errorjob=self.WaitForTermination(temp)
       finishedjobs,errorjobs=self.WaitForTermination(fulljobtooutputlog)
       return finishedjobs,errorjobs

    def CallJobsLocalHost(self,fulljobtooutputlog,skiperrors):
       for job in fulljobtooutputlog.keys():
           self.call_subsystem(job,True,skiperrors)
       finishedjobs,errorjobs=self.WaitForTermination(fulljobtooutputlog)
       return finishedjobs,errorjobs


    def WaitForTermination(self,jobtooutputlog):
        finishedjobs=[]
        errorjobs=[]
        errormessages=[]
        outputStatusDict = copy.deepcopy(jobtooutputlog)
        while len(finishedjobs)!=len(jobtooutputlog.keys()):
            for job in jobtooutputlog.keys():
                outputlog=jobtooutputlog[job]
                if os.path.isfile(outputlog):
                    statinfo=os.stat(outputlog)
                    size=statinfo.st_size
                    if size==0:
                        continue
                finished,error,errormessages=self.CheckNormalTermination(outputlog,errormessages)
                if finished==True and error==False: # then check if SP has been submitted or not
                    if outputlog not in finishedjobs:
                        self.NormalTerm(outputlog)
                        finishedjobs.append(outputlog)
                elif finished==False and error==True:
                    if outputlog not in finishedjobs:
                        self.ErrorTerm(outputlog)
                        finishedjobs.append(outputlog)
                        errorjobs.append(outputlog)
                elif finished==False and error==False:
                    if not os.path.isfile(outputlog):
                        self.WriteToLog('Waiting on '+outputlog+' '+'to begin')
                    else:
                        printStr = 'Waiting on '+outputlog+' '+'for termination '
                        if (printStr != outputStatusDict[job]):
                          self.WriteToLog(printStr)
                          outputStatusDict[job] = printStr
                else: # this case is finshed=True and error=True because there stupid quotes sometimes have word error in it                  
                    if outputlog not in finishedjobs:
                        error=False
                        self.NormalTerm(outputlog)
                        finishedjobs.append(outputlog)
    
            time.sleep(self.sleeptime) # how often to check logs (default every 30 s)
            #self.WriteToLog('**********************************************')
        self.WriteToLog('All jobs have terminated ')
        return finishedjobs,errorjobs

    def CycleCount(self,logname):
        temp=open(logname,'r')
        results=temp.readlines()
        temp.close()
        count=0
        for line in results:
            if 'Converged' in line or 'Convergence Check' in line:
                count+=1
        return count


    def CheckNormalTermination(self,logfname,errormessages=None): # needs to handle error checking now
        """
        Intent: Checks the *.log file for normal termination
        """
        error=False
        term=False
        if os.path.isfile(logfname):
            head,tail=os.path.split(logfname)
            Ftime=os.path.getmtime(logfname)
            reltime=time.time()-Ftime
            htime=reltime*0.000277778
            updatetime=2 # hours
            for line in open(logfname):
                if 'poltype' in tail:
                    if 'Poltype Job Finished' in line:
                        term=True
                else:
                    if "Final optimized geometry" in line or "Electrostatic potential computed" in line or 'Psi4 exiting successfully' in line or "LBFGS  --  Normal Termination due to SmallGrad" in line or "Normal termination" in line:
                        term=True
                    if ('error' in line or 'Error' in line or 'ERROR' in line or 'impossible' in line or 'software termination' in line or 'segmentation violation, address not mapped to object' in line or 'galloc:  could not allocate memory' in line or 'Erroneous write.' in line) and 'DIIS' not in line and 'mpi' not in line and 'except' not in line:
                        error=True
                    if 'segmentation violation' in line and 'address not mapped to object' not in line or 'Waiting' in line:
                        error=False
                        continue
                    if ('Error termination request processed by link 9999' in line or 'Error termination via Lnk1e in' in line) or ('OptimizationConvergenceError' in line) and 'opt' in logfname:
                        if self.CycleCount(logfname)>=poltype.optmaxcycle:
                            term=True
                            error=False


            if error==True:
                message='Error '+line+ 'logpath='+logfname
   
            if error==False and term==False and htime>=updatetime:
                error=True
                message='Error '+'Job died and has not been updated in '+str(updatetime)+' hours'+' last update time = '+str(htime)+' hours'+' logname='+logfname
            if error==True and term==False:
                if errormessages!=None:
                    if message not in errormessages:
                        self.WriteToLog(message) 
                        errormessages.append(message)
                else:
                    self.WriteToLog(message) 


        if errormessages!=None:
            return term,error,errormessages
        else:
            return term,error        


    
        
    def NormalTerm(self,logfname):
        self.WriteToLog("Normal termination: logfile=%s path=%s" % (logfname,os.getcwd()))
    
    
    def ErrorTerm(self,logfname):
        self.WriteToLog("ERROR termination: logfile=%s path=%s" % (logfname,os.getcwd()))


    def call_subsystem(self,cmdstr,wait=False,skiperrors=False):
        if self.printoutput==True:
            print("Calling: " + cmdstr+' '+'path'+' = '+os.getcwd())
        self.WriteToLog(" Calling: " + cmdstr+' '+'path'+' = '+os.getcwd())
        p = subprocess.Popen(cmdstr, shell=True,stdout=self.logfh, stderr=self.logfh)
        if wait==True:
            p.wait()
            if skiperrors==False:
                if p.returncode != 0:
                    self.WriteToLog("ERROR: " + cmdstr+' '+'path'+' = '+os.getcwd())
                    raise ValueError("ERROR: " + cmdstr+' '+'path'+' = '+os.getcwd())

    def WriteOutLiteratureReferences(self, keyfilename): # to use ParmEd on key file need Literature References delimited for parsing
        with open(keyfilename, "r") as temp:
            results = temp.readlines()
        tempname = keyfilename.replace('.key','_temp.key')
        with open(tempname, "w") as temp:
            foundatomblock = False
            for line in results:
                if 'atom' in line and not foundatomblock:
                    foundatomblock=True
                    temp.write('#############################'+'\n')
                    temp.write('##                         ##'+'\n')
                    temp.write('##  Literature References  ##'+'\n')
                    temp.write('##                         ##'+'\n')
                    temp.write('#############################'+'\n')
                    temp.write('\n')
                    temp.write('Wu, J.C.; Chattree, G.; Ren, P.Y.; Automation of AMOEBA polarizable force field'+'\n')
                    temp.write('parameterization for small molecules. Theor Chem Acc.'+'\n')
                    temp.write('\n')
                    temp.write(line)
                else:
                    temp.write(line)
        os.remove(keyfilename)
        os.replace(tempname, keyfilename)

    def RaiseOutputFileError(self, logname):
        raise ValueError(f"An error occured for {logname}") 

    def WritePoltypeInitializationFile(self, poltypeinput):
        inifilepath = os.path.abspath("poltype.ini")
        with open(inifilepath, "w") as temp:
            for key, value in poltypeinput.items():
                line = f"{key}={value}\n"
                temp.write(line)
        return inifilepath

    def CheckTorsionParameters(self, keyfilename, torsionsmissing, hydtorsions):
        """
        don't check torsions skipped due to rule that if a-b-c-d,
        # a or d is hydrogen and not all possible a and d around b-c is hydrogen
        then torsion is skipped, if database transfers all zeros do not check
        """
        with open(keyfilename, 'r') as temp:
            results = temp.readlines()
        for line in results:
            if 'torsion' in line and '#' not in line:
                linesplit = line.split()
                ls = [int(l) for l in linesplit[1:5]]
                revls = ls[::-1]
                if (ls in torsionsmissing or revls in torsionsmissing) and (ls not in hydtorsions or revls not in hydtorsions):
                    prms = [float(i) for i in linesplit[5::3]]
                    if not any(prms):
                        raise ValueError(f"Torsion parameters are all zero {line} path = {os.getcwd()}")

    def main(self):
         
        if self.amoebabioprmpath!=None and (self.modifiedproteinpdbname!=None or self.unmodifiedproteinpdbname!=None):
            knownresiduesymbs,modproidxs,proboundidxs,boundaryatomidxs,proOBmol,molname,modresiduelabel,proidxtoligidx,ligidxtoproidx,modmol,smarts,check,connectedatomidx,backboneindexesreference,modligidxs=modres.GenerateModifiedProteinPoltypeInput(self)
            self.molstructfname=molname
            head, self.molstructfname = os.path.split(self.molstructfname)
            self.molecprefix =  os.path.splitext(self.molstructfname)[0]

        if self.amoebabioprmpath!=None and (self.modifiedproteinpdbname!=None or self.unmodifiedproteinpdbname!=None): # if already have core parameters in modified prm database then dont regenerate parameters
            if check==False:
                self.GenerateParameters()
        else:
           params= self.GenerateParameters()
           return params

    
        if self.amoebabioprmpath!=None and (self.modifiedproteinpdbname!=None or self.unmodifiedproteinpdbname!=None):
            modres.GenerateModifiedProteinXYZAndKey(self,knownresiduesymbs,modproidxs,proboundidxs,boundaryatomidxs,proOBmol,molname,modresiduelabel,proidxtoligidx,ligidxtoproidx,modmol,smarts,check,connectedatomidx,backboneindexesreference,modligidxs)
    
    
    def GrabIndexToCoordinates(self,mol):
        indextocoordinates={}
        iteratom = openbabel.OBMolAtomIter(mol)
        for atom in iteratom:
            atomidx=atom.GetIdx()
            rdkitindex=atomidx-1
            coords=[atom.GetX(),atom.GetY(),atom.GetZ()]
            indextocoordinates[rdkitindex]=coords
        return indextocoordinates

    def AddInputCoordinatesAsDefaultConformer(self,m,indextocoordinates):
        conf = m.GetConformer()
        for i in range(m.GetNumAtoms()):
            x,y,z = indextocoordinates[i]
            conf.SetAtomPosition(i,Point3D(x,y,z))

        return m 

    def NumberOfChargedAtoms(self,mol):
        atomitermol=openbabel.OBMolAtomIter(mol)
        chgcount=0
        for atm in atomitermol:
            chg=atm.GetFormalCharge()
            if chg!=0:
                chgcount+=1
        return chgcount

           

    def CheckIfCartesianXYZ(self,f):
        check=True
        temp=open(f,'r')
        results=temp.readlines()
        temp.close()
        for line in results:
            linesplit=line.split()
            if len(linesplit)>4:
                check=False
        return check

    def RemoveCartesianXYZFiles(self):
        files=os.listdir()
        for f in files:
            filename, file_extension = os.path.splitext(f)
            if file_extension=='.xyz' and 'opt' not in filename:
                check=self.CheckIfCartesianXYZ(f)
                if check==True:
                    os.remove(f)

    def CheckMemorySettings(self):
        proc = int(self.numproc)
        if proc > 8:
            raise ValueError('Too many input processors, lower the numproc value to 8 or less')
        maxmem_value, maxdisk_value = self.GenerateMemoryValues()
        if (maxmem_value < 50) and (maxdisk_value < 2*maxmem_value):
            raise ValueError('Increase maxdisk value to twice maxmem value')

    def GenerateMemoryValues(self):
        if 'MB' in self.maxmem:
            maxmem_value = float(self.maxmem[:-2])*.001 # convert to GB
        elif 'GB' in self.maxmem:
            maxmem_value = float(self.maxmem[:-2])
        else:
            raise ValueError("maxmem must have units of MB or GB attached (e.g. \"700MB\")")
        if 'MB' in self.maxdisk:
            maxdisk_value=float(self.maxdisk[:-2])*.001 # convert to GB
        elif 'GB' in self.maxdisk:
            maxdisk_value=float(self.maxdisk[:-2])
        else:
            raise ValueError("maxmem must have units of MB or GB attached (e.g. \"100GB\")")
        return maxmem_value, maxdisk_value


    def CheckInputCharge(self,molecule):
        atomicnumtoformalchg={1:{2:1},5:{4:1},6:{3:-1},7:{2:-1,4:1},8:{1:-1,3:1},15:{4:1},16:{1:-1,3:1,5:-1},17:{0:-1,4:3},9:{0:-1},35:{0:-1},53:{0:-1}}
        for atom in molecule.GetAtoms():
            atomidx=atom.GetIdx()
            atomnum=atom.GetAtomicNum()
            val=atom.GetExplicitValence()
            valtochg=atomicnumtoformalchg[atomnum]
            if val not in valtochg.keys(): # then assume chg=0
                chg=0
            else:
                chg=valtochg[val]
    
            polneighb=False
            if atomnum==6:
                for natom in atom.GetNeighbors():
                    natomicnum=natom.GetAtomicNum()
                    if natomicnum==7 or natomicnum==8 or natomicnum==16:
                        polneighb=True
                if polneighb and val==3:
                    chg=1

            userformalcharge=atom.GetFormalCharge()
            
            if userformalcharge!=chg:
                raise ValueError('Valence is not consistent with user input charge ,atomindex='+str(atomidx+1)+' , atomnumber= '+str(atomnum)+' user input charge is '+str(userformalcharge)+' but expected charge from valence is '+str(chg)) 
        return molecule



 
    def GenerateParameters(self):
        self.CheckMemorySettings()        

        obConversion = openbabel.OBConversion()
        mol = openbabel.OBMol()
        inFormat = obConversion.FormatFromExt(self.molstructfname)
        obConversion.SetInFormat(inFormat)
        obConversion.ReadFile(mol, self.molstructfname)
        
        self.atomnum=mol.NumAtoms() 
        self.totalcharge=mol.GetTotalCharge()
        # Begin log. *-poltype.log
        self.logfh = open(self.logfname,"a",buffering=1)
        if not os.path.exists(self.scrtmpdirpsi4):
            mkdirstr='mkdir '+self.scrtmpdirpsi4
            self.call_subsystem(mkdirstr,True)
        if not os.path.exists(self.scrtmpdirgau):
            mkdirstr='mkdir '+self.scrtmpdirgau
            self.call_subsystem(mkdirstr,True)

        obConversion.SetOutFormat('mol')
        self.molstructfnamemol=self.molstructfname.replace('.sdf','.mol')
        obConversion.WriteFile(mol,self.molstructfnamemol)
        indextocoordinates=self.GrabIndexToCoordinates(mol)
        m=Chem.MolFromMolFile(self.molstructfnamemol,removeHs=False,sanitize=False)
        self.CheckInputCharge(m)
        m=Chem.MolFromMolFile(self.molstructfnamemol,removeHs=False)
        m=self.AddInputCoordinatesAsDefaultConformer(m,indextocoordinates)
        mol,m=self.CheckIsInput2D(mol,obConversion,m)
        self.mol=mol
        self.rdkitmol=m
        if self.keyfiletoaddtodatabase!=None:
            databaseparser.AddKeyFileParametersToParameterFile(self,m)   
            sys.exit()
       
        if ('I ' in self.mol.GetSpacedFormula()):
            if self.foundgauss==True:
                self.use_gaus=True


        chgcount=self.NumberOfChargedAtoms(mol)
        if self.totalcharge==0 and chgcount>1:
            if self.foundgauss==True:
                self.use_gauPCM=True
                self.SanitizeAllQMMethods()

            self.toroptpcm=True
            self.optpcm=True
            self.torsppcm=True

        if self.use_gauPCM==True:
            self.use_gausoptonly=False
            self.use_gaus=True
            self.SanitizeAllQMMethods()

        atomiter=openbabel.OBMolAtomIter(self.mol)
        atomnum=0
        for atom in atomiter:
            atomnum+=1


        #if atomnum<25: TEMP FOR TESTING TORTOR
        #    self.dontfrag=True 
        self.RemoveCartesianXYZFiles()
 
        self.WriteToLog("Running on host: " + gethostname())
        # Initializing arrays
        
        self.canonicallabel = [ 0 ] * mol.NumAtoms()
        self.localframe1 = [ 0 ] * mol.NumAtoms()
        self.localframe2 = [ 0 ] * mol.NumAtoms()
        self.idxtosymclass,self.symmetryclass=symm.gen_canonicallabels(self,mol) 

 
        # QM calculations are done here
        # First the molecule is optimized. (-opt) 
        # This optimized molecule is stored in the structure optmol
        # Then the electron density matrix is found (-dma)
        # This is used by GDMA to find multipoles
        # Then information for generating the electrostatic potential grid is found (-esp)
        # This information is used by cubegen
        self.comoptfname=self.firstcomoptfname 
        self.chkoptfname=self.firstchkoptfname 
        self.fckoptfname=self.firstfckoptfname
        self.logoptfname=self.firstlogoptfname 
        self.gausoptfname=self.firstgausoptfname 

        if self.use_gausgeomoptonly==True:
            self.use_gausoptonly=True

        optmol = opt.GeometryOptimization(self,mol)
        if self.skipsecondopt==False:
            self.optmaxcycle=5
            self.optmethod='MP2' 
            self.comoptfname=self.secondcomoptfname 
            self.chkoptfname=self.secondchkoptfname 
            self.fckoptfname=self.secondfckoptfname
            self.logoptfname=self.secondlogoptfname 
            self.gausoptfname=self.secondgausoptfname 
            optmol.SetTotalCharge(mol.GetTotalCharge())
            optmol.SetTotalSpinMultiplicity(mol.GetTotalSpinMultiplicity())
            optmol = opt.GeometryOptimization(self,optmol)
        if self.use_gausgeomoptonly==True:
            self.use_gausoptonly=False
            self.use_gaus=False


        torgen.FindPartialDoubleBonds(self,m)
        if not os.path.isfile(self.key4fname) or not os.path.isfile(self.torsionsmissingfilename) or not os.path.isfile(self.torsionprmguessfilename):
            bondprmstotransferinfo,angleprmstotransferinfo,torsionprmstotransferinfo,strbndprmstotransferinfo,opbendprmstotransferinfo,vdwprmstotransferinfo,torsionsmissing,classkeytotorsionparametersguess,missingvdwatomindextoneighbors=databaseparser.GrabSmallMoleculeAMOEBAParameters(self,optmol,mol,m)
       
        if os.path.isfile(self.torsionsmissingfilename):
            torsionsmissing=databaseparser.ReadTorsionList(self,self.torsionsmissingfilename)
        if os.path.isfile(self.torsionprmguessfilename):
            classkeytotorsionparametersguess=databaseparser.ReadDictionaryFromFile(self,self.torsionprmguessfilename)
        if os.path.isfile(self.vdwmissingfilename):
            missingvdwatomindices=databaseparser.ReadVdwList(self,self.vdwmissingfilename)

        esp.SPForDMA(self,optmol,mol)
        # Obtain multipoles from Gaussian fchk file using GDMA
    
        if not os.path.isfile(self.gdmafname):
            mpole.run_gdma(self)
    
        # Set up input file for poledit
        # find multipole local frame definitions

        lfzerox,atomindextoremovedipquad,atomtypetospecialtrace,atomindextoremovedipquadcross = mpole.gen_peditinfile(self,mol)
        

        
        
        if (not os.path.isfile(self.xyzfname) or not os.path.isfile(self.keyfname)):
            # Run poledit
            cmdstr = self.peditexe + " 1 " + self.gdmafname +' '+self.paramhead+ " < " + self.peditinfile
            self.call_subsystem(cmdstr,True)
            # Add header to the key file output by poledit
            while not os.path.isfile(self.keyfname):
                time.sleep(1)
                self.WriteToLog('Waiting for '+self.keyfname)
            mpole.prepend_keyfile(self,self.keyfname,optmol)
            mpole.SanitizeMultipoleFrames(self,self.keyfname)
        # post process local frames written out by poledit
        mpole.post_proc_localframes(self,self.keyfname, lfzerox,atomindextoremovedipquad,atomindextoremovedipquadcross)
        if self.atomnum!=1: 
             esp.SPForESP(self,optmol,mol) 
        # End here if qm calculations were all that needed to be done 
        if self.qmonly:
            self.WriteToLog("poltype QM-only complete.")
            sys.exit(0)
    
               
        # scaling of multipole values for certain atom types
        # checks if the molecule contains any atoms that should have their multipole values scaled
        scalelist = mpole.process_types(self,mol)
        
        
        # generate the electrostatic potential grid used for multipole fitting
        if self.atomnum!=1: 
            esp.gen_esp_grid(self,optmol)
    
        # Average multipoles based on molecular symmetry
        # Does this using the script avgmpoles.pl which is found in the poltype directory
        # Atoms that belong to the same symm class will now have only one common multipole definition
        if not os.path.isfile(self.key2fname):
            mpole.AverageMultipoles(self,optmol)

        if self.espfit and not os.path.isfile(self.key3fname) and self.atomnum!=1:
            # Optimize multipole parameters to QM ESP Grid (*.cube_2)
            # tinker's potential utility is called, with option 6.
            # option 6 reads: 'Fit Electrostatic Parameters to a Target Grid'
            
            esp.ElectrostaticPotentialFitting(self) 
        else:
            shutil.copy(self.key2fname, self.key3fname)
        # Remove header terms from the keyfile
        mpole.rm_esp_terms_keyfile(self,self.key3fname)
        if self.atomnum!=1 and not os.path.isfile('RMSPD.txt'): 
            esp.ElectrostaticPotentialComparison(self)  
        
        # Multipoles are scaled if needed using the scale found in process_types
        mpole.post_process_mpoles(self,self.key3fname, scalelist)
        
        # Now that multipoles have been found
        # Other parameters such as opbend, vdw, etc. are found here using a look up table
        # Part of the look up table is here in poltype.py 
        # Most of it is in the file databaseparser.py found in the poltype directory
    
        # Finds aromatic carbons and associated hydrogens and corrects polarizability
        # Find opbend values using a look up table
        # Outputs a list of rotatable bonds (found in get_torlist) in a form usable by databaseparser.py
    
        # Map from idx to symm class is made for databaseparser.py
        # databaseparser.py method is called to find parameters and append them to the keyfile
        if not os.path.exists(self.key4fname):
            databaseparser.appendtofile(self,self.key3fname,self.key4fname, bondprmstotransferinfo,angleprmstotransferinfo,torsionprmstotransferinfo,strbndprmstotransferinfo,opbendprmstotransferinfo,vdwprmstotransferinfo)
        if self.torsppcm:
            torgen.PrependStringToKeyfile(self,self.key4fname,'solvate GK')
        # Find rotatable bonds for future torsion scans
        (self.torlist, self.rotbndlist,hydtorsions,nonaroringtorlist) = torgen.get_torlist(self,mol,torsionsmissing)
        torgen.get_all_torsions(self,mol)
        self.torlist,self.rotbndlist=torgen.RemoveDuplicateRotatableBondTypes(self) # this only happens in very symmetrical molecules
        self.torlist=[tuple(i) for i in self.torlist]
        self.torlist=[tuple([i]) for i in self.torlist]
        self.torsettovariabletorlist={}
        for torset in self.torlist:
            self.torsettovariabletorlist[tuple(torset)]=[]
        nonaroringtorlist=[tuple(i) for i in nonaroringtorlist]
        nonaroringtorlist=[tuple([i]) for i in nonaroringtorlist]
        self.rotbndtoanginc=torgen.DetermineAngleIncrementAndPointsNeededForEachTorsionSet(self,mol,self.rotbndlist)
        torgen.DefaultMaxRange(self,self.torlist)
        if self.dontdotor==True:
            self.torlist=[]
        # add missingvdwindices to torlist (for fragmenter input)
        missingvdwatomsets=[]
        if self.isfragjob==False and self.dontfrag==False and self.dontdovdwscan==False:
            for vdwatomindex in missingvdwatomindices:
                ls=tuple([tuple([vdwatomindex])])
                missingvdwatomsets.append(ls)
                self.torlist.append(ls)
        if self.dontdotor==True and self.dontdovdwscan==True:
            shutil.copy(self.key4fname,self.key5fname)
        self.torsettofilenametorset={}
        self.torsettotortorindex={}
        self.torsettotortorphaseindicestokeep={}
        self.nonaroringtors=[]
        self.nonaroringtorsets=[]
        self.classkeytoinitialprmguess={}
        if self.dontfrag==False and self.tortor==True and self.dontdotor==False:
            torgen.PrepareTorsionTorsion(poltype,optmol,mol)
 
        if self.refinenonaroringtors==True and self.dontfrag==False:
            rings.RefineNonAromaticRingTorsions(self,mol,optmol,classkeytotorsionparametersguess)
        if self.isfragjob==False and not os.path.isfile(self.key5fname) and self.dontfrag==False and (self.dontdotor==False or self.dontdovdwscan==False):
            

            WBOmatrix,outputname,error=frag.GenerateWBOMatrix(self,self.rdkitmol,self.mol,self.logoptfname.replace('.log','.xyz'))
            highlightbonds=[]
            for torset in self.torlist:
                for tor in torset:
                    if len(tor)>1:
                        rotbnd=[tor[1]-1,tor[2]-1]
                        highlightbonds.append(rotbnd)
            frag.Draw2DMoleculeWithWBO(self,WBOmatrix,self.molstructfname.replace('.sdf',''),self.rdkitmol,bondindexlist=highlightbonds,imgsize=1500)        
            rotbndindextoparentindextofragindex,rotbndindextofragment,rotbndindextofragmentfilepath,equivalentrotbndindexarrays,rotbndindextoringtor,equivalentrotbndindexmaps=frag.GenerateFragments(self,self.mol,self.torlist,WBOmatrix,missingvdwatomsets,nonaroringtorlist) # returns list of bond indexes that need parent molecule to do torsion scan for (fragment generated was same as the parent0
            equivalentrotbndindexarrays,rotbndindextoringtor=frag.SpawnPoltypeJobsForFragments(self,rotbndindextoparentindextofragindex,rotbndindextofragment,rotbndindextofragmentfilepath,equivalentrotbndindexarrays,rotbndindextoringtor,equivalentrotbndindexmaps)

        if self.dontfrag==False and self.isfragjob==False and not os.path.isfile(self.key5fname) and (self.dontdotor==False or self.dontdovdwscan==False):
            frag.GrabVdwAndTorsionParametersFromFragments(self,rotbndindextofragmentfilepath,equivalentrotbndindexarrays,rotbndindextoringtor) # just dump to key_5 since does not exist for parent molecule
        else:          
            # Torsion scanning then fitting. *.key_5 will contain updated torsions
            if not os.path.isfile(self.key5fname):
                if len(self.torlist)!=0:
                    # torsion scanning
                    torgen.gen_torsion(self,optmol,self.torsionrestraint,mol)
                    # torsion fitting
                    if self.dontdotorfit==True:
                        shutil.copy(self.key4fname,self.key5fname)
                        sys.exit()
                    torfit.process_rot_bond_tors(self,optmol)
                else:
                    shutil.copy(self.key4fname,self.key5fname)

        if self.dontdovdwscan==False and self.isfragjob==True:
            vdwfit.VanDerWaalsOptimization(self,missingvdwatomindices)       
        if self.isfragjob==False and self.dontdotor==False:
            self.CheckTorsionParameters(self.key5fname,torsionsmissing,hydtorsions)

        self.WriteOutLiteratureReferences(self.key5fname) 
        # A series of tests are done so you one can see whether or not the parameterization values
        # found are acceptable and to what degree
        opt.StructureMinimization(self)
        if self.atomnum != 1:
            opt.gen_superposeinfile(self)
            opt.CheckRMSD(self)
        if self.torsppcm:
            torgen.RemoveStringFromKeyfile(self,self.key5fname,'solvate GK')
        if self.atomnum!=1: 
             esp.CheckDipoleMoments(self,optmol)
        self.WriteToLog('Poltype Job Finished'+'\n')
        keyfilecopyname=self.key5fname.replace('.key','_copy.key')
        shutil.copy(self.key5fname,keyfilecopyname)
        torgen.RemoveStringFromKeyfile(self,keyfilecopyname,'SOLUTE')
        torgen.RemoveStringFromKeyfile(self,keyfilecopyname,'TARGET-DIPOLE')
        torgen.RemoveCommentsFromKeyFile(self,keyfilecopyname)
        if os.path.exists(self.scrtmpdirgau):
            shutil.rmtree(self.scrtmpdirgau)
        if os.path.exists(self.scrtmpdirpsi4):
            shutil.rmtree(self.scrtmpdirpsi4)

        #return param



if __name__ == '__main__':
    poltype=PolarizableTyper() 
    #params=poltype.main()
    poltype.main()
