import numpy as np
from scipy.optimize import minimize
import scipy as sp
import os,sys
import time
import re
from statistics import mean
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from sklearn import *
import optimization as opt
import openbabel
import itertools
import symmetry as symm
from socket import gethostname
import shlex
from scipy.optimize import fmin
from scipy import optimize
import shutil
import copy
import traceback

def CheckAllVdwTypesExist(poltype,keyfilename):
    temp=open(keyfilename,'r')
    results=temp.readlines()
    temp.close()
    vdwtypes=[]
    for line in results:
        if 'vdw' in line and '#' not in line:
            linesplit=line.split()
            atomtype=int(linesplit[1])
            vdwtypes.append(atomtype)
    alltypes=[]
    for atom in poltype.rdkitmol.GetAtoms():
        atomidx=atom.GetIdx()+1
        symtype=poltype.idxtosymclass[atomidx]
        alltypes.append(symtype)
    for atomtype in alltypes:
        if atomtype not in vdwtypes:
            raise ValueError('Missing vdwtype in keyfile '+str(atomtype)) 

def best_fit_slope_and_intercept(xs,ys):
    xs=np.array(xs)
    ys=np.array(ys)
    m = (((mean(xs)*mean(ys)) - mean(xs*ys)) /
         ((mean(xs)*mean(xs)) - mean(xs*xs)))
    b = mean(ys) - m*mean(xs)
    return m, b

def squared_error(ys_orig,ys_line):
    ys_orig=np.array(ys_orig)
    ys_line=np.array(ys_line)
    return sum((ys_line - ys_orig) * (ys_line - ys_orig))

def coefficient_of_determination(ys_orig,ys_line):
    y_mean_line = [mean(ys_orig) for y in ys_orig]
    squared_error_regr = squared_error(ys_orig, ys_line)
    squared_error_y_mean = squared_error(ys_orig, y_mean_line)
    try:
        value=1 - (squared_error_regr/squared_error_y_mean)

    except:
        value=1 # incase division by 0

    return value 

def MeanError(data,pred):
    Sum=0
    for i in range(len(data)):
        true=data[i]
        predv=pred[i]
        diff=true-predv
        Sum+=diff
    Sum=Sum/len(data)
    return Sum
    


def writePRM(poltype,params,vdwtypes,idxtotype):
    vdwradius=None
    vdwdepth=None
    vdwred=None
    vdwtypesalreadyfit=[]
    vdwtypetonewline={}
    for i in range(len(params)):
        oFile = open("temp.key", 'w')
        rFile=open(poltype.key5fname,'r')
        vdwtype=vdwtypes[i]
        vartype=idxtotype[i]
        if vartype=='rad':
            vdwradius=params[i]

        elif vartype=='depth':
            vdwdepth=params[i]
            if (i+1) in idxtotype.keys():
                nexttype=idxtotype[i+1]

                if nexttype!='red':
                    vdwred=1
            else:
                vdwred=1


        elif vartype=='red':
            vdwred=params[i]
        if vdwradius!=None and vdwdepth!=None and vdwred!=None:
            for line in rFile.readlines():
                linesplit=line.split()
                if 'vdw' in line:
                    if linesplit[1]==vdwtype:
                        newline="vdw %s %s %s %s \n"%(vdwtype,vdwradius, vdwdepth,vdwred)
                        vdwtypetonewline[vdwtype]=newline
                        oFile.write(newline)
                    else:
                        notinline=True
                        for othertype in vdwtypesalreadyfit:
                            if linesplit[1]==othertype:
                                notinline=False
                                break
                        if notinline==True:
                            oFile.write(line)
                        else:
                            newline=vdwtypetonewline[othertype]
                            oFile.write(newline)

                else:
                    oFile.write(line)

            vdwtypesalreadyfit.append(vdwtype)
            vdwradius=None
            vdwdepth=None
            vdwred=None
    oFile.flush()
    os.fsync(oFile.fileno())
    oFile.close()
    rFile.close()
    os.remove(poltype.key5fname)
    os.rename("temp.key",poltype.key5fname)
    CheckAllVdwTypesExist(poltype,poltype.key5fname)
    return

def readOneColumn(filename,columnnumber,prefix=None):
    temp=open(filename,'r')
    results=temp.readlines()
    temp.close()
    array=[]
    for line in results:
        if prefix!=None:
            if prefix not in line:
                continue
        linesplit=line.split()
        value=linesplit[columnnumber]
        array.append(value)
    return array
     
def NormalizeTarget(poltype,filename,aprefix=None):
    prefixarray=readOneColumn(filename,0)
    energyarray=readOneColumn(filename,1)
    energyarray=[float(i) for i in energyarray]
    prefixtoenergyarray={}
    for prefixidx in range(len(prefixarray)):
        prefix=prefixarray[prefixidx]
        if aprefix!=None:
            if aprefix not in prefix:
                continue
        energy=energyarray[prefixidx]
        prefixsplit=prefix.split('_')
        prefixsplit=prefixsplit[:-1] 
        prefix=''.join(prefixsplit)
        if prefix not in prefixtoenergyarray.keys():
            prefixtoenergyarray[prefix]=[]
        prefixtoenergyarray[prefix].append(energy)
    for prefix,energyarray in prefixtoenergyarray.items():
        normenergyarray=[i-min(energyarray) for i in energyarray]
        prefixtoenergyarray[prefix]=normenergyarray
    totalenergyarray=[]
    for prefix,energyarray in prefixtoenergyarray.items():
        for e in energyarray:
            totalenergyarray.append(e)
    
    return np.array(totalenergyarray)


def myFUNC(params,poltype,vdwtypes,idxtotype,count):
    params=list(params)
    writePRM(poltype,params,vdwtypes,idxtotype)
    target = NormalizeTarget(poltype,'QM_DATA')

    temp=open('QM_DATA','r')
    cmdarray=[] 
    filenamearray=[]
    for line in temp.readlines():
        xyzname=line.split()[0]
        filename=xyzname.replace('.xyz','.alz')
        cmdstr=poltype.analyzeexe+' '+xyzname+' '+'-k '+poltype.key5fname +' e '+'> '+filename
        cmdarray.append(cmdstr)
        filenamearray.append(filename)

    temp.close()
    for cmd in cmdarray:
        poltype.call_subsystem(cmd,True)

    ReadAnalyzeEnergiesWriteOut(poltype,filenamearray)
    current = NormalizeTarget(poltype,'SP.dat')
    current,target,distarray=ScreenHighEnergyPoints(poltype,current,target)
    if count>1:
        weightlist=np.exp(-np.array(target)/poltype.boltzmantemp)

    else:
        weightlist=np.ones(len(target))
    return weightlist*(current-target)

def ScreenHighEnergyPoints(poltype,current,target,distarray=None):
    tol=15
    newcurrent=[]
    newtarget=[]
    newdistarray=[]
    for i in range(len(current)):
        cur=current[i]
        tar=target[i]
        try:
            if distarray==None:
                pass
        except:
            dist=distarray[i]
        if cur>=tol or tar>=tol:
            pass
        else:
            newcurrent.append(cur)
            newtarget.append(tar)
            try:
                if distarray==None:
                    pass
            except:
                newdistarray.append(dist)
    return np.array(newcurrent),np.array(newtarget),np.array(newdistarray)


def PlotQMVsMMEnergy(poltype,vdwtypesarray,prefix,count,allprefix=False):
    if allprefix==False:
        target= NormalizeTarget(poltype,'QM_DATA',prefix)
        current=NormalizeTarget(poltype,'SP.dat',prefix)

    else:
        target=[]
        current=[]
        for ls in prefix:
            target.extend(NormalizeTarget(poltype,'QM_DATA',ls))
            current.extend(NormalizeTarget(poltype,'SP.dat',ls))
    current,target,distarray=ScreenHighEnergyPoints(poltype,current,target)
    vdwtypes=[str(i) for i in vdwtypesarray]
    vdwtypestring=','.join(vdwtypes)
    MSE=MeanError(current,target)
    MAE=metrics.mean_absolute_error(current,target)
    m, b = best_fit_slope_and_intercept(current,target)
    regression_line = [(m*x)+b for x in current]
    weightlist=np.exp(-np.array(target)/poltype.boltzmantemp)

    energy_list=target-current
    if count>1:
        energy_list=np.multiply(weightlist,energy_list)
    shifted_target=np.add(1,target)
    shifted_current=np.add(1,current)
    relative_energy_list=shifted_target-shifted_current
    if count>1:
        relative_energy_list=np.multiply(weightlist,relative_energy_list)

    def FirstRMSD(c):
        return np.sqrt(np.mean(np.square(np.add(target-current,c))))
    result=fmin(FirstRMSD,.5)
    first_new_rmse=FirstRMSD(0)


    def RMSD(c):
        return np.sqrt(np.mean(np.square(np.add(energy_list,c))))
    result=fmin(RMSD,.5)
    new_rmse=RMSD(0)

    def RMSDRel(c):
        return np.sqrt(np.mean(np.square(np.add(np.divide(relative_energy_list,shifted_target),c))))
    resultRel=fmin(RMSDRel,.5)
    new_rmse_rel=RMSDRel(0)
    r_squared = coefficient_of_determination(current,target)
    fig = plt.figure()
    plt.plot(current,target,'.',label='R^2=%s MAE=%s RMSE=%s RelRMSE=%s MSE=%s'%(round(r_squared,2),round(MAE,2),round(new_rmse,2),round(new_rmse_rel,2),round(MSE,2)))
    plt.plot(current,regression_line,label='Linear Regression line')
    plt.ylabel('QM BSSE Corrected (kcal/mol)')
    plt.xlabel('AMOEBA (kcal/mol)')
    plt.legend(loc='best')
    plt.title('QM vs AMOEBA , '+vdwtypestring)
    if count>1:
        suffix='_boltzman.png'
    else:
        suffix='.png'
    if allprefix==False:
        fig.savefig('QMvsAMOEBA-'+prefix+'_'+vdwtypestring+suffix)
    else:
        prefstring=','.join(prefix)
        fig.savefig('QMvsAMOEBA-'+prefstring+'_'+vdwtypestring+suffix)
        prefix=prefstring
    rmsetol=1.6
    relrmsetol=.2
    goodfit=True
    if new_rmse>rmsetol and new_rmse_rel>relrmsetol:
        goodfit=False
        if allprefix==True and count>1:
            raise ValueError('RMSE is too high! RMSE='+str(new_rmse)+' tol='+str(rmsetol)+' '+'RelRMSE='+str(new_rmse_rel)+' tol='+str(relrmsetol)+' '+prefix)
        elif allprefix==True and count<=1:
            mes='RMSE is too high! RMSE='+str(new_rmse)+' tol='+str(rmsetol)+' '+'RelRMSE='+str(new_rmse_rel)+' tol='+str(relrmsetol)+' '+prefix
            print(mes,flush=True)

    return goodfit

def VDWOptimizer(poltype,count,fitredboolarray):
    x0 = []

    curvdwtypes=readOneColumn("INITIAL.PRM", 1)
    vdwtypes=[]
    temp=open("INITIAL.PRM",'r')
    lines = temp.readlines()
    idxtotype={}
    count=0
    for lineidx in range(len(lines)):
        fitredbool=fitredboolarray[lineidx]
        line=lines[lineidx]
        x0.append(float(line.split()[2]))
        idxtotype[count]='rad'
        count+=1
        x0.append(float(line.split()[3]))
        idxtotype[count]='depth'
        count+=1

        if fitredbool==True:
            x0.append(float(line.split()[4]))
            idxtotype[count]='red'
            count+=1

        vdwtype=curvdwtypes[lineidx]
        vdwtypes.append(vdwtype)
        vdwtypes.append(vdwtype)
        if fitredbool==True:
            vdwtypes.append(vdwtype)

    x0 = np.array(x0)
    rmax=readOneColumn("INITIAL.PRM", 6)
    rmax=[float(i) for i in rmax]
    rmin=readOneColumn("INITIAL.PRM", 5)
    rmin=[float(i) for i in rmin]
    depthmax=readOneColumn("INITIAL.PRM", 8)
    depthmax=[float(i) for i in depthmax]
    depthmin=readOneColumn("INITIAL.PRM", 7)
    depthmin=[float(i) for i in depthmin]
    redmax=readOneColumn("INITIAL.PRM", 10)
    redmax=[float(i) for i in redmax]
    redmin=readOneColumn("INITIAL.PRM", 9)
    redmin=[float(i) for i in redmin]
    l1=list(zip(rmin, rmax))
    l2=list(zip(depthmin, depthmax))
    l3=list(zip(redmin, redmax))
    lower=[]
    upper=[]
    for i in range(len(l1)):
        fitredbool=fitredboolarray[i]
        l1bound=l1[i]
        l2bound=l2[i]
        l3bound=l3[i]
        l1lower=l1bound[0] 
        l1upper=l1bound[1] 
        l2lower=l2bound[0] 
        l2upper=l2bound[1] 
        l3lower=l3bound[0] 
        l3upper=l3bound[1] 
        lower.append(l1lower)
        lower.append(l2lower)
        if fitredbool==True:
            lower.append(l3lower)
        upper.append(l1upper)
        upper.append(l2upper)
        if fitredbool==True:
            upper.append(l3upper)
    MyBounds=[lower,upper]
    MyBounds=tuple(MyBounds)
    ''' local optimization method can be BFGS, CG, Newton-CG, L-BFGS-B,etc.., see here\
    https://docs.scipy.org/doc/scipy-0.19.1/reference/generated/scipy.optimize.minimize.html'''
    errorfunc= lambda p, poltype, vdwtypes,idxtotype,count: (myFUNC(p,poltype,vdwtypes,idxtotype,count))
    fail=False
    try: 
        ret = optimize.least_squares(errorfunc, x0, jac='2-point', bounds=MyBounds, diff_step=1e-4,args=(poltype,vdwtypes,idxtotype,count))
    except:
        fail=True
    vdwradii=[]
    vdwdepths=[] 
    vdwreds=[]
    ofile = open("RESULTS.OPT", "a")
    if fail==False:
        for i in range(len(ret.x)):
            vartype=idxtotype[i]
            if vartype=='rad':
                vdwradius=round(ret.x[i],3)
                vdwradii.append(vdwradius)

            elif vartype=='depth':
                vdwdepth=round(ret.x[i],3)
                vdwdepths.append(vdwdepth)
                if (i+1) in idxtotype.keys():
                    nexttype=idxtotype[i+1]
                    if nexttype!='red':
                        vdwred=1
                        vdwreds.append(vdwred)
                else:
                    vdwred=1
                    vdwreds.append(vdwred)


            elif vartype=='red':
                vdwred=round(ret.x[i],3)
                vdwreds.append(vdwred)
                
        ofile.write("%s\n"%(ret.message))
        ofile.write("\n")
    ofile.close()
    return vdwradii,vdwdepths,vdwreds,fail 


def MoveDimerAboutMinima(poltype,txyzFile,outputprefixname,nAtomsFirst,atomidx1,atomidx2,equildistance,array):
    fnamearray=[]
    for i in range(len(array)):
        frac=array[i]
        fname=outputprefixname+'_%s.xyz' %(str(frac))
        fnamearray.append(fname)
        with open(fname,'w') as f:
            twoDots = [atomidx1,atomidx2] #two atoms selected to vary; the atom number exactly in TINKER file
            temp=open(txyzFile,'r')
            lines=temp.readlines()
            temp.close()
            coordSecondMol = [] #Coordinates of the second molecule
            data = lines[twoDots[0]].split()
            coordFirstAtm = [float(data[2]), float(data[3]), float(data[4])] 
            data = lines[twoDots[1]].split()
            coordSecondAtm = [float(data[2]), float(data[3]), float(data[4])] 
            varyVector = []
            norm = 0.0
            for i in range(3):
                varyVector.append(coordSecondAtm[i] - coordFirstAtm[i])
                norm += (coordSecondAtm[i]-coordFirstAtm[i])**2.0
            norm = norm**0.5 # initial distance between the two atoms
            distance=norm*frac
            for i in range(3):
                varyVector[i] = (distance - norm) * varyVector[i]/norm # scaling the x,y,z coordinates of displacement vector to new distance
            stringsList = [] 
            for i in range(nAtomsFirst+1, len(lines), 1):
                data = lines[i].split()
                coordSecondMol.append( [float(data[2]), float(data[3]), float(data[4]),] )
                headString = ' '.join(lines[i].split()[0:2]) 
                tailString = ' '.join(lines[i].split()[5:])
                stringsList.append([headString, tailString])
            for i in range(0, nAtomsFirst+1, 1):
                f.write(lines[i])
    
            for i in range(len(coordSecondMol)):
                for j in range(3):
                    coordSecondMol[i][j] = coordSecondMol[i][j]+varyVector[j]
    
            for i in range(len(coordSecondMol)):
                f.write("%s %s %s %s %s"%(stringsList[i][0], coordSecondMol[i][0], coordSecondMol[i][1], coordSecondMol[i][2], stringsList[i][1])+'\n')
            f.flush()
            os.fsync(f.fileno())
    return fnamearray


def ConvertProbeDimerXYZToTinkerXYZ(poltype,inputxyz,tttxyz,outputxyz,waterbool,probeatoms):
    temp=open(inputxyz,'r')
    resultsinputxyz=temp.readlines()
    temp.close()
    todelete=[]
    for lineidx in range(len(resultsinputxyz)):
        line=resultsinputxyz[lineidx]
        linesplit=line.split()
        if len(linesplit)==0:
            todelete.append(lineidx)
    for index in todelete:
        del resultsinputxyz[index]
 
    temp=open(tttxyz,'r')
    resultstttxyz=temp.readlines()
    temp.close()
    outfile=open(outputxyz,'w')
    outarray=[]
    for lineidx in range(len(resultstttxyz)):
        inputxyzline=resultsinputxyz[lineidx]
        tttxyzline=resultstttxyz[lineidx]
        if lineidx==0:
            totatoms=inputxyzline
        if lineidx!=0:
    
            linesplitinput=inputxyzline.split()
            linesplittttxyz=tttxyzline.split()
            output=''
            output+=' '.join(linesplittttxyz[0:2])+' '
            output+=' '.join(linesplitinput[1:])+' '
            output+=' '.join(linesplittttxyz[5:])
            outarray.append(output)
    
    outfile.write(totatoms)
    for out in outarray:
        outfile.write(out+'\n')
    
    
    totalatomnum=int(totatoms.strip().replace('\n',''))

    if waterbool==True:
        for lineidx in range(len(resultsinputxyz)):
            inputxyzline=resultsinputxyz[lineidx]
            if lineidx==totalatomnum-2:
                outline = str(totalatomnum-2)+ ' ' +inputxyzline.split()[0]+ " " + ' '.join(inputxyzline.split()[1:5]) + " 349 " + str(totalatomnum-1) + " " + str(totalatomnum) + "" 
                outfile.write(outline+'\n')
            elif lineidx==totalatomnum-1:
                outline = str(totalatomnum-1) + ' ' +inputxyzline.split()[0]+ " " + ' '.join(inputxyzline.split()[1:5]) + " 350 " + str(totalatomnum-2)+ ""
                outfile.write(outline+'\n')
            elif lineidx==totalatomnum:
                outline = str(totalatomnum) + ' ' +inputxyzline.split()[0]+ " " + ' '.join(inputxyzline.split()[1:5]) + " 350 " + str(totalatomnum-2)+ ""
                outfile.write(outline+'\n')
    else:
        count=0
        newoutarray=[]
        for lineidx in range(len(resultsinputxyz)):
            inputxyzline=resultsinputxyz[lineidx]
            if lineidx>probeatoms:
                tttindex=lineidx-probeatoms
            else:
                tttindex=lineidx        
            tttxyzline=resultstttxyz[tttindex]
            if lineidx!=0:
                count+=1 
                if count>probeatoms:
                    linesplitinput=inputxyzline.split()
                    linesplittttxyz=tttxyzline.split()
                    output=''
                    atomindex=int(linesplittttxyz[0])
                    linesplittttxyz[0]=str(atomindex+probeatoms)
                    output+=' '.join(linesplittttxyz[0:2])+' '
                    output+=' '.join(linesplitinput[1:])+' '
                    for i in range(6,len(linesplittttxyz)):
                        currentindex=str(int(linesplittttxyz[i])+probeatoms)
                        linesplittttxyz[i]=currentindex
                    output+=' '.join(linesplittttxyz[5:])
                    newoutarray.append(output)
    
        for out in newoutarray:
            outfile.write(out+'\n')

    outfile.close()


def GrabMonomerEnergy(poltype,line):
    linesplit=line.split()
    energy=float(linesplit[4]) 
    monomerenergy=(energy)*poltype.Hartree2kcal_mol
    return monomerenergy



def ReadCounterPoiseAndWriteQMData(poltype,logfilelist):
    temp=open('QM_DATA','w')
    for f in logfilelist:
        tmpfh=open(f,'r')
        if poltype.use_gaus==True:
            frag1calc=False
            frag2calc=False
            for line in tmpfh:
                if 'Counterpoise: corrected energy =' in line:
                    dimerenergy=float(line.split()[4])*poltype.Hartree2kcal_mol
                elif 'Counterpoise: doing DCBS calculation for fragment   1' in line:
                    frag1calc=True
                    frag2calc=False
                elif 'Counterpoise: doing DCBS calculation for fragment   2' in line:
                    frag1calc=False
                    frag2calc=True
                elif 'SCF Done' in line:
                    if frag1calc:
                        frag1energy=GrabMonomerEnergy(poltype,line)
                    elif frag2calc:
                        frag2energy=GrabMonomerEnergy(poltype,line)
            interenergy=dimerenergy-(frag1energy+frag2energy)
        else:
            for line in tmpfh:
                if 'CP Energy =' in line and 'print' not in line:
                    linesplit=line.split()
                    interenergy=float(linesplit[3])*poltype.Hartree2kcal_mol

        tmpfh.close()
        try:
            temp.write(f.replace('_sp.log','.xyz')+' '+str(interenergy)+'\n')
        except:
            temp.write(f.replace('_sp.log','.xyz')+' '+str(interenergy)+'\n')

    temp.close()




def PlotEnergyVsDistance(poltype,distarray,prefix,radii,depths,reds,vdwtypesarray,count):
    vdwtypes=[str(i) for i in vdwtypesarray]
    vdwtypestring=','.join(vdwtypes)
    qmenergyarray = NormalizeTarget(poltype,'QM_DATA',prefix)
    energyarray = NormalizeTarget(poltype,'SP.dat',prefix)

    energyarray,qmenergyarray,distarray=ScreenHighEnergyPoints(poltype,energyarray,qmenergyarray,distarray)

    def RMSD(c):
        return np.sqrt(np.mean(np.square(np.add(np.subtract(np.array(energyarray),np.array(qmenergyarray)),c))))


    r_squared = round(coefficient_of_determination(energyarray,qmenergyarray),2)
    result=fmin(RMSD,.5)
    minRMSD=round(RMSD(result[0]),2)
    if count>1:
        suffix='_boltzman.png'
    else:
        suffix='.png'
    plotname='EnergyVsDistance-'+prefix+'_'+vdwtypestring+suffix
    fig = plt.figure()
    title=prefix+' VdwTypes = '+vdwtypestring
    plt.title(title)
    string=''
    for i in range(len(radii)):
        rad=radii[i]
        depth=depths[i]
        red=reds[i]
        cur='Radius=%s, Depth=%s ,Red=%s'%(round(rad,2),round(depth,2),round(red,2))
        string+=cur
    plt.plot(distarray,energyarray,'--bo',label='MM ,'+string)
    plt.plot(distarray,qmenergyarray,'--ro',label='QM')
    plt.plot()
    plt.ylabel('Energy (kcal/mol)')
    plt.xlabel('Distance Angstrom '+'RMSD=%s, R^2=%s'%(minRMSD,r_squared))
    plt.legend(loc='best')
    fig.savefig(plotname)


def ReadIntermolecularEnergyMM(poltype,filename):
    with open(filename,'r') as f:
        results=f.readlines()
        for line in results:
            if "Intermolecular Energy :" in line:
                linesplit=line.split()
                energy=linesplit[3]
    return energy

def ReadAnalyzeEnergiesWriteOut(poltype,filenamelist):
    temp=open('SP.dat','w')
    for filename in filenamelist:
        energy=ReadIntermolecularEnergyMM(poltype,filename)
        temp.write(filename+' '+str(energy)+'\n')
    temp.close() 


def WriteInitialPrmFile(poltype,vdwtypesarray,initialradii,initialdepths,minradii,maxradii,mindepths,maxdepths,initialreds,minreds,maxreds):

    temp=open('INITIAL.PRM','w')
    for i in range(len(vdwtypesarray)):
        vdwtype=str(vdwtypesarray[i])
        initialradius=str(initialradii[i])
        initialdepth=str(initialdepths[i])
        initialred=str(initialreds[i])
        minradius=str(minradii[i])
        maxradius=str(maxradii[i])
        mindepth=str(mindepths[i])
        maxdepth=str(maxdepths[i])
        minred=str(minreds[i])
        maxred=str(maxreds[i])
        line='vdw '+vdwtype+' '+initialradius+' '+initialdepth+' '+initialred+' '+minradius+' '+maxradius+' '+mindepth+' '+maxdepth+' '+minred+' '+maxred+'\n'
        temp.write(line)

    temp.close()

def readTXYZ(poltype,TXYZ):
    temp=open(TXYZ,'r')
    lines = temp.readlines()[1:] #TINKER coordinate starts from second line
    atoms=[];coord=[]
    order=[];types=[];connections=[]
    for line in lines:
        data=line.split()
        order.append(data[0])
        types.append(data[5])
        connections.append(data[6:])
        atoms.append(data[1])
        coord.append([float(data[2]), float(data[3]), float(data[4])])
    return atoms,coord,order, types, connections

def TXYZ2COM(poltype,TXYZ,comfname,chkname,maxdisk,maxmem,numproc,mol,probeatoms):
    data = readTXYZ(poltype,TXYZ)
    atoms = data[0];coord = data[1]
    opt.write_com_header(poltype,comfname,chkname,maxdisk,maxmem,numproc)
    tmpfh = open(comfname, "a")
    if ('I ' in poltype.mol.GetSpacedFormula()):
        poltype.espbasisset='gen'
        iodinebasissetfile=poltype.iodineespbasissetfile 
        basissetfile=poltype.espbasissetfile 
    
    opstr="#P %s/%s Sp Counterpoise=2" % (poltype.espmethod,poltype.espbasisset)

    if ('I ' in poltype.mol.GetSpacedFormula()):
        opstr+=' pseudo=read'
    string=' MaxDisk=%s \n'%(maxdisk)
    opstr+=string
    mul=mol.GetTotalSpinMultiplicity()
    chg=mol.GetTotalCharge()
    tmpfh.write(opstr)
    commentstr = poltype.molecprefix + " Gaussian SP Calculation on " + gethostname()
    tmpfh.write('\n%s\n\n' % commentstr)
    tmpfh.write('%d %d %d %d %d %d\n' % (chg,mul,chg,mul,0,1))

    for n in range(len(atoms)):
        if n>=len(atoms)-probeatoms:
            tmpfh.write("%3s%s             %14.7f%14.7f%14.7f\n"%(atoms[n],'(Fragment=2)',float(coord[n][0]),float(coord[n][1]),float(coord[n][2]))) 
        else:
            tmpfh.write("%3s%s             %14.7f%14.7f%14.7f\n"%(atoms[n],'(Fragment=1)',float(coord[n][0]),float(coord[n][1]),float(coord[n][2])))    
    
    if ('I ' in poltype.mol.GetSpacedFormula()):
        formulalist=poltype.mol.GetSpacedFormula().lstrip().rstrip().split()
        temp=open(poltype.basissetpath+basissetfile,'r')
        results=temp.readlines()
        temp.close()
        for line in results:
            if '!' not in line:
                tmpfh.write(line)

        temp=open(poltype.basissetpath+iodinebasissetfile,'r')
        results=temp.readlines()
        temp.close()
        for line in results:
            if '!' not in line:
                tmpfh.write(line)


        temp=open(poltype.basissetpath+iodinebasissetfile,'r')
        results=temp.readlines()
        temp.close()
        for line in results:
            if '!' not in line:
                tmpfh.write(line)


    tmpfh.write("\n")
    tmpfh.close()

def ReadInBasisSet(poltype,tmpfh,normalelementbasissetfile,otherelementbasissetfile,space):
    newtemp=open(poltype.basissetpath+normalelementbasissetfile,'r')
    results=newtemp.readlines()
    newtemp.close()
    for line in results:
        if '!' not in line:
            tmpfh.write(space+line)


    newtemp=open(poltype.basissetpath+otherelementbasissetfile,'r')
    results=newtemp.readlines()
    newtemp.close()
    for line in results:
        if '!' not in line:
            tmpfh.write(space+line)
    return tmpfh




def CreatePsi4SPInputFile(poltype,TXYZ,mol,maxdisk,maxmem,numproc,probeatoms):
    data = readTXYZ(poltype,TXYZ)
    atoms = data[0];coord = data[1]
    mul=mol.GetTotalSpinMultiplicity()
    chg=mol.GetTotalCharge()
    inputname=TXYZ.replace('.xyz','_sp.psi4')

    temp=open(inputname,'w')
    temp.write('molecule { '+'\n')
    temp.write('%d %d\n' % (chg, mul))
    for n in range(len(atoms)):
        if n==len(atoms)-probeatoms:
            temp.write('--'+'\n')
            temp.write('%d %d\n' % (0, 1))
        if n>=len(atoms)-probeatoms:
            temp.write("%3s             %14.7f%14.7f%14.7f\n"%(atoms[n],float(coord[n][0]),float(coord[n][1]),float(coord[n][2]))) 
        else:
            temp.write("%3s             %14.7f%14.7f%14.7f\n"%(atoms[n],float(coord[n][0]),float(coord[n][1]),float(coord[n][2])))    

    temp.write('}'+'\n')
    temp.write('memory '+maxmem+'\n')
    temp.write('set_num_threads(%s)'%(numproc)+'\n')
    temp.write('psi4_io.set_default_path("%s")'%(poltype.scrtmpdirpsi4)+'\n')
    temp.write('set maxiter '+str(poltype.scfmaxiter)+'\n')
    temp.write('set freeze_core True'+'\n')
    temp.write('set PROPERTIES_ORIGIN ["COM"]'+'\n')
    spacedformulastr=mol.GetSpacedFormula()
    if ('I ' in spacedformulastr):
        temp.write('basis {'+'\n')
        temp.write('['+' '+poltype.espbasissetfile+' '+poltype.iodineespbasissetfile +' '+ ']'+'\n')
        temp=ReadInBasisSet(poltype,temp,poltype.espbasissetfile,poltype.iodineespbasissetfile,'')
        temp.write('}'+'\n')
        temp.write("e_dim= energy('%s',bsse_type='cp')" % (poltype.espmethod.lower())+'\n')
    else:
        temp.write("e_dim= energy('%s/%s',bsse_type='cp')" % (poltype.espmethod.lower(),poltype.espbasisset)+'\n')
    temp.write('\n')
    temp.write("psi4.print_out('CP Energy = %10.6f' % (e_dim))"+'\n')
    temp.write('clean()'+'\n')
    temp.close()
    temp=open(inputname,'r')
    results=temp.readlines()
    temp.close()
    outputname=os.path.splitext(inputname)[0] + '.log'
    return inputname,outputname



def WriteOutCartesianXYZ(poltype,mol,filename):
    output=open(filename,'w')
    atomcounter=0
    coordarray=[]
    atomiter=openbabel.OBMolAtomIter(mol)
    etab = openbabel.OBElementTable()
    for atom in atomiter:
        atomcounter+=1
        atomsymb=etab.GetSymbol(atom.GetAtomicNum())
        x=str(atom.GetX())
        y=str(atom.GetY())
        z=str(atom.GetZ())
        xyzline=atomsymb+' '+x+' '+y+' '+z
        coordarray.append(xyzline)
            
    output.write(str(atomcounter)+'\n')
    for coord in coordarray:
        output.write(coord+'\n')
    output.close()


def GenerateSPInputFiles(poltype,filenamearray,mol,probeatoms):
    qmfilenamearray=[]
    for filename in filenamearray:
        if poltype.use_gaus==True:
            qmfilename=filename.replace('.xyz','_sp.com')
            chkfilename=filename.replace('.xyz','_sp.chk')
            TXYZ2COM(poltype,filename,qmfilename,chkfilename,poltype.maxdisk,poltype.maxmem,poltype.numproc,mol,probeatoms)
        else:
            qmfilename,outputname=CreatePsi4SPInputFile(poltype,filename,mol,poltype.maxdisk,poltype.maxmem,poltype.numproc,probeatoms)
        qmfilenamearray.append(qmfilename)
    return qmfilenamearray


def ExecuteSPJobs(poltype,qmfilenamearray,prefix):
    jobtooutputlog={}
    listofjobs=[]
    fulljobtooutputlog={}
    outputfilenames=[]
    for i in range(len(qmfilenamearray)):
        filename=qmfilenamearray[i]
        if poltype.use_gaus==True:
            cmdstr = 'cd '+shlex.quote(os.getcwd())+' && '+'GAUSS_SCRDIR='+poltype.scrtmpdirgau+' '+poltype.gausexe+' '+filename
        
            outputname=filename.replace('.com','.log')
        else:
            outputname=filename.replace('.psi4','.log')
            cmdstr='cd '+shlex.quote(os.getcwd())+' && '+'psi4 '+filename+' '+outputname


        
        finished,error=poltype.CheckNormalTermination(outputname)
        if finished==True and error==False:
            pass
        else:
            if os.path.isfile(outputname):
                statinfo=os.stat(outputname)
                size=statinfo.st_size
                if size!=0:
                    os.remove(outputname)
                    listofjobs.append(cmdstr)
                    jobtooutputlog[cmdstr]=os.getcwd()+r'/'+outputname
            else:
                listofjobs.append(cmdstr)
                jobtooutputlog[cmdstr]=os.getcwd()+r'/'+outputname
        outputfilenames.append(outputname)
    lognames=[]
    for job in listofjobs:
        log=jobtooutputlog[job]
        lognames.append(os.path.abspath(poltype.logfname))
    fulljobtolog=dict(zip(listofjobs, lognames)) 
    fulljobtooutputlog.update(jobtooutputlog)

    scratchdir=poltype.scrtmpdirgau
    jobtologlistfilenameprefix=os.getcwd()+r'/'+'QMSPJobToLog'+'_'+prefix
    if poltype.externalapi!=None:
        if len(listofjobs)!=0:
            call.CallExternalAPI(poltype,fulljobtolog,jobtologlistfilenameprefix,scratchdir)
        finshedjobs,errorjobs=poltype.WaitForTermination(fulljobtooutputlog)
    else:
        finishedjobs,errorjobs=poltype.CallJobsSeriallyLocalHost(fulljobtooutputlog,True)

    return outputfilenames


def GrabVdwParameters(poltype,vdwtype):
    CheckAllVdwTypesExist(poltype,poltype.key5fname)
    temp=open(poltype.key5fname,'r')
    results=temp.readlines()
    temp.close()
    vdwdepthlimit=.4 # may need to change this to handle ions case
    for line in results:
        if 'vdw' in line:
            if str(vdwtype) in line:
                linesplit=line.split()
                radius=float(linesplit[2])
                minvdwradius=radius-.1*radius
                maxvdwradius=radius+.1*radius
                depth=float(linesplit[3])
                minvdwdepth=depth-.1*depth
                maxvdwdepth=depth+.1*depth
                if maxvdwdepth>vdwdepthlimit:
                    maxvdwdepth=vdwdepthlimit
                if depth>maxvdwdepth:
                    depth=maxvdwdepth-.001
                if len(linesplit)==5:
                    red=float(linesplit[4])
                else:
                    red=1
                minred=red-.1*red
                maxred=1
                return radius,depth,minvdwradius,maxvdwradius,minvdwdepth,maxvdwdepth,red,minred,maxred


def GenerateCoordinateGuesses(indextoreferencecoordinate):
    coordinatesguess=[]
    for i in range(len(indextoreferencecoordinate.keys())):
        coordinate=indextoreferencecoordinate[i]
        x,y,z=coordinate[:]
        coordinatesguess.append(x)
        coordinatesguess.append(y)
        coordinatesguess.append(z)
    return coordinatesguess

def UpdateCoordinates(coords,indextoreferencecoordinate):
    for i in range(len(indextoreferencecoordinate.keys())):
        startindex=3*i
        coordinate=np.array([coords[startindex],coords[startindex+1],coords[startindex+2]])
        indextoreferencecoordinate[i]=coordinate
    return indextoreferencecoordinate

def GenerateReferenceDistances(indextoreferencecoordinate,indextomolecule,indextotargetatom,indextoreferenceelement,vdwradius):
    indexpairtoreferencedistance={}
    indexpairtobounds={}
    indices=list(indextoreferencecoordinate.keys())
    allpairs=list(itertools.combinations(indices, 2)) 
    for pair in allpairs:
        index1=pair[0]
        index2=pair[1]
        molecule1=indextomolecule[index1]
        molecule2=indextomolecule[index2]
        coord1=indextoreferencecoordinate[index1]
        coord2=indextoreferencecoordinate[index2]
        target1=indextotargetatom[index1]
        target2=indextotargetatom[index2]
        element1=indextoreferenceelement[index1]
        element2=indextoreferenceelement[index2]
        vdwradius1=vdwradius[element1]
        vdwradius2=vdwradius[element2]
        if molecule1==molecule2:
            targetdistance=np.linalg.norm(coord1-coord2)
            bound=[targetdistance,targetdistance]
        else:
            if target1=='target' and target2=='target': # then use vdw distances
                targetdistance=(vdwradius1**3+vdwradius2**3)/(vdwradius1**2+vdwradius2**2)
                if targetdistance<2:
                    targetdistance=2
                bound=[targetdistance,targetdistance]

        indexpairtoreferencedistance[tuple(pair)]=targetdistance 
        indexpairtobounds[tuple(pair)]=bound

    for pair in allpairs:
        index1=pair[0]
        index2=pair[1]
        molecule1=indextomolecule[index1]
        molecule2=indextomolecule[index2]
        coord1=indextoreferencecoordinate[index1]
        coord2=indextoreferencecoordinate[index2]
        target1=indextotargetatom[index1]
        target2=indextotargetatom[index2]
        element1=indextoreferenceelement[index1]
        element2=indextoreferenceelement[index2]
        vdwradius1=vdwradius[element1]
        vdwradius2=vdwradius[element2]
        if molecule1==molecule2:
            targetdistance=np.linalg.norm(coord1-coord2)
            bound=[targetdistance,targetdistance]
        else:
            if target1=='target' and target2=='target': # then use vdw distances
                targetdistance=(vdwradius1**3+vdwradius2**3)/(vdwradius1**2+vdwradius2**2)
                if targetdistance<2:
                    targetdistance=2

                bound=[targetdistance,targetdistance]
            else:
                bound=[targetdistance,100] # high upper bound, large range to not add cost in cost function                

        indexpairtoreferencedistance[tuple(pair)]=targetdistance 
        indexpairtobounds[tuple(pair)]=bound

 
    return indexpairtoreferencedistance,indexpairtobounds


def GenerateReferenceAngles(poltype,p2,atoms2,p1,atoms1,mol,probemol,indextoreferencecoordinate):
    indicestoreferenceangleprobe={}
    indicestoreferenceanglemoleculeneighb={}
    indicestoreferenceanglemoleculeneighbneighb={}
    acceptorindex=p1
    shiftedp2=len(atoms1)+p2
    donorindex=shiftedp2
    donorneighbs=[]
    probeidxtosymclass,symmetryclass=symm.gen_canonicallabels(poltype,probemol) 
    acceptoratom=mol.GetAtom(p1+1)
    acceptorhyb=acceptoratom.GetHyb()
    donoratom=probemol.GetAtom(p2+1)
    probeneighbs=[]
    atomatomiter=openbabel.OBAtomAtomIter(donoratom)
    for atom in atomatomiter:
        probeneighbs.append(atom.GetIdx())
    acceptorneighbs=[]
    atomatomiter=openbabel.OBAtomAtomIter(acceptoratom)
    for atom in atomatomiter:
        acceptorneighbs.append(atom.GetIdx())

    probeneighbsymclasses=[probeidxtosymclass[i] for i in probeneighbs] 
    probeneighbsymclassesset=list(set(probeneighbsymclasses))
    probeneighbatoms=[probemol.GetAtom(i) for i in probeneighbs]
    acceptorneighbatoms=[mol.GetAtom(i) for i in acceptorneighbs]
    probeneighbs=[i-1+len(atoms1) for i in probeneighbs] # shift to 0 index, shift passed first molecule
    acceptorneighbs=[i-1 for i in acceptorneighbs]
    donorcoordinate=indextoreferencecoordinate[donorindex]
    acceptorcoordinate=indextoreferencecoordinate[acceptorindex]
    for donorneighbindex in probeneighbs:
        if len(probeneighbs)==2 and len(probeneighbsymclassesset)==1:
            angleatoms=[probeneighbatoms[0],donoratom,probeneighbatoms[1]]
            bisectangle=probemol.GetAngle(angleatoms[0],angleatoms[1],angleatoms[2])
            angle=180-.5*bisectangle 

        elif len(probeneighbs)==1:
            angle=180
        else:

            donorneighbcoordinate=indextoreferencecoordinate[donorneighbindex]
            donortoacceptor=acceptorcoordinate-donorcoordinate
            donortodonorneighb=donorneighbcoordinate-donorcoordinate
            donortoacceptornormed=donortoacceptor/np.linalg.norm(donortoacceptor)
            donortodonorneighbnormed=donortodonorneighb/np.linalg.norm(donortodonorneighb) 
            angle=np.arccos(np.dot(donortoacceptornormed,donortodonorneighbnormed))


        angleindices=tuple([donorneighbindex,donorindex,acceptorindex])
        indicestoreferenceangleprobe[angleindices]=angle
    if len(acceptorneighbs)!=1 and acceptorhyb==2:
        angle=90
        for acceptorneighbindex in acceptorneighbs:
            angleindices=tuple([donorindex,acceptorneighbindex,acceptorindex])
            indicestoreferenceanglemoleculeneighb[angleindices]=angle

    elif len(acceptorneighbs)==1:
        neighb=acceptorneighbatoms[0]
        atomatomiter=openbabel.OBAtomAtomIter(neighb)
        neighbofneighbsatoms=[]
        for atom in atomatomiter:
            neighbofneighbsatoms.append(atom)
        for atom in neighbofneighbsatoms:
            atomidx=atom.GetIdx()
            if (atomidx-1)!=acceptorindex:
                angleatoms=[atom,neighb,acceptoratom] 
                angle=mol.GetAngle(angleatoms[0],angleatoms[1],angleatoms[2])
                angleindices=tuple([atomidx-1,neighb.GetIdx()-1,acceptorindex,donorindex]) # acceptorindex and donorindex colinear here, but need both to get correct distance information for law of cosines
                indicestoreferenceanglemoleculeneighbneighb[angleindices]=angle
    
    return indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb


def ConvertAngleRestraintToDistanceRestraint(indexpairtoreferencedistance,indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb,indexpairtobounds,indextoreferencecoordinate):
    for indices,targetangle in indicestoreferenceangleprobe.items(): 
        donorneighbindex=indices[0]
        acceptorindex=indices[2]
        donorindex=indices[1]
        inputpair=tuple([donorneighbindex,donorindex])
        inputdistance=GrabPairwiseDistance(inputpair,indexpairtoreferencedistance)
        targetpair=tuple([donorindex,acceptorindex])
        targetdistance=GrabPairwiseDistance(targetpair,indexpairtoreferencedistance)
        angledist=LawOfCosines(inputdistance,targetdistance,targetangle)    
        anglepair=tuple([donorneighbindex,acceptorindex])
        indexpairtoreferencedistance[anglepair]=angledist
        indexpairtobounds[anglepair]=[angledist,angledist]

    for indices,targetangle in indicestoreferenceanglemoleculeneighb.items(): 
        acceptorneighbindex=indices[1]
        acceptorindex=indices[2]
        donorindex=indices[0]
        inputpair=tuple([acceptorneighbindex,acceptorindex])
        inputdistance=GrabPairwiseDistance(inputpair,indexpairtoreferencedistance)
        targetpair=tuple([donorindex,acceptorindex])
        targetdistance=GrabPairwiseDistance(targetpair,indexpairtoreferencedistance)
        acceptorcoordinate=indextoreferencecoordinate[acceptorindex]
        acceptorneighbcoordinate=indextoreferencecoordinate[acceptorneighbindex]
        donorcoordinate=indextoreferencecoordinate[donorindex]
        donoracceptorvector=acceptorcoordinate-donorcoordinate
        donoracceptorneighbvector=acceptorneighbcoordinate-donorcoordinate
        donoracceptorvectornormed=donoracceptorvector/np.linalg.norm(donoracceptorvector)
        donoracceptorneighbvectornormed=donoracceptorneighbvector/np.linalg.norm(donoracceptorneighbvector)
        currentangle=np.arccos(np.dot(donoracceptorvectornormed,donoracceptorneighbvectornormed))
        angle=180-currentangle-targetangle
        angledist=LawOfCosines(inputdistance,targetdistance,angle)    
        anglepair=tuple([acceptorneighbindex,donorindex])
        indexpairtoreferencedistance[anglepair]=angledist
        indexpairtobounds[anglepair]=[angledist,angledist]

    for indices,targetangle in indicestoreferenceanglemoleculeneighbneighb.items(): 
        acceptorneighbneighbindex=indices[0]
        acceptorneighbindex=indices[1]
        acceptorindex=indices[2]
        donorindex=indices[3] 
        inputpair=tuple([acceptorneighbneighbindex,acceptorneighbindex])
        inputdistance=GrabPairwiseDistance(inputpair,indexpairtoreferencedistance)
        targetpair=tuple([donorindex,acceptorindex])
        targetdistance=GrabPairwiseDistance(targetpair,indexpairtoreferencedistance)
        anotherinputpair=tuple([acceptorneighbindex,acceptorindex])
        anotherinputdistance=GrabPairwiseDistance(anotherinputpair,indexpairtoreferencedistance)
        firstdistance=inputdistance
        seconddistance=targetdistance+anotherinputdistance
        angledist=LawOfCosines(firstdistance,seconddistance,targetangle)    
        anglepair=tuple([acceptorneighbneighbindex,donorindex])
        indexpairtoreferencedistance[anglepair]=angledist
        indexpairtobounds[anglepair]=[angledist,angledist]


           
    return indexpairtoreferencedistance,indexpairtobounds



def GrabPairwiseDistance(pair,indexpairtoreferencedistance):
    if pair in indexpairtoreferencedistance.keys():
        distance=indexpairtoreferencedistance[pair]
    elif pair[::-1] in indexpairtoreferencedistance.keys():
        distance=indexpairtoreferencedistance[pair[::-1]]
    return distance


def LawOfCosines(a,b,angleC):
    return np.sqrt(a**2+b**2-2*a*b*np.cos(np.radians(angleC)))

def GenerateInitialDictionaries(coords1,coords2,atoms1,atoms2,p1,p2):
    indextoreferencecoordinate={}
    indextoreferenceelement={}
    indextomolecule={}
    indextotargetatom={}
    count=0
    for i in range(len(coords1)):
        coords=np.array(coords1[i])
        element=atoms1[i]

        indextoreferencecoordinate[count]=coords
        indextoreferenceelement[count]=element
        indextomolecule[count]='molecule1'
        if count==p1:
            string='target'
        else:
            string='steric'
        indextotargetatom[count]=string
        count+=1     
    p2=p2+len(coords1)
    for i in range(len(coords2)):
        coords=np.array(coords2[i])
        element=atoms2[i]
        indextoreferencecoordinate[count]=coords
        indextoreferenceelement[count]=element
        indextomolecule[count]='molecule2'
        if count==p2:
            string='target'
        else:
            string='steric'
        indextotargetatom[count]=string

        count+=1     
    return indextoreferencecoordinate,indextoreferenceelement,indextomolecule,indextotargetatom


def optimizedimer(poltype,atoms1, atoms2, coords1, coords2, p1, p2, dimer,vdwradius,mol,probemol,probeidxtosymclass):
    indextoreferencecoordinate,indextoreferenceelement,indextomolecule,indextotargetatom=GenerateInitialDictionaries(coords1,coords2,atoms1,atoms2,p1,p2) 
    indexpairtoreferencedistance,indexpairtobounds=GenerateReferenceDistances(indextoreferencecoordinate,indextomolecule,indextotargetatom,indextoreferenceelement,vdwradius)
    indexpairtoreferencedistanceoriginal=indexpairtoreferencedistance.copy()
    indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb=GenerateReferenceAngles(poltype,p2,atoms2,p1,atoms1,mol,probemol,indextoreferencecoordinate)
    indexpairtoreferencedistance,indexpairtobounds=ConvertAngleRestraintToDistanceRestraint(indexpairtoreferencedistance,indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb,indexpairtobounds,indextoreferencecoordinate) 
    
    shiftedp2=p2+len(atoms1)
    coordinatesguess=GenerateCoordinateGuesses(indextoreferencecoordinate)
    def PairwiseCostFunction(x):
        func=0
        for indexpair,bounds in indexpairtobounds.items():
            firstindex=indexpair[0]
            secondindex=indexpair[1]
            startfirstindex=3*firstindex
            startsecondindex=3*secondindex     
            firstcoordinate=np.array([x[startfirstindex],x[startfirstindex+1],x[startfirstindex+2]])
            secondcoordinate=np.array([x[startsecondindex],x[startsecondindex+1],x[startsecondindex+2]])       
            distance=np.linalg.norm(firstcoordinate-secondcoordinate)
            referencedistance=indexpairtoreferencedistance[indexpair]
            difference=np.abs(distance-referencedistance)
            lowerbound=bounds[0]
            upperbound=bounds[1]
            if distance<lowerbound or distance>upperbound:
                func+=difference**2


        return func


    sol = minimize(PairwiseCostFunction, coordinatesguess, method='SLSQP',options={'disp':False, 'maxiter': 1000, 'ftol': 1e-6})
    coords=sol.x
    indextoreferencecoordinate=UpdateCoordinates(coords,indextoreferencecoordinate)

    with open(dimer, "w") as f:
      f.write(str(len(indextoreferencecoordinate.keys()))+"\n")
      f.write("\n")
      for index,coordinate in indextoreferencecoordinate.items():
          element=indextoreferenceelement[index]
          f.write("%3s %12.5f%12.5f%12.5f\n"%(element, coordinate[0], coordinate[1], coordinate[2]))
    if 'water' in dimer:
        waterbool=True
    else:
        waterbool=False
    outputxyz=dimer.replace('.xyz','-tinkermin.xyz')
    probeatoms=len(atoms2)
    ConvertProbeDimerXYZToTinkerXYZ(poltype,dimer,poltype.xyzoutfile,outputxyz,waterbool,probeatoms)
    outputxyz,restraints=MinimizeDimer(poltype,outputxyz,poltype.key5fname,indexpairtoreferencedistanceoriginal,indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb,p1,p2,atoms1,probeidxtosymclass)
    return outputxyz,restraints

def MinimizeDimer(poltype,inputxyz,keyfile,indexpairtoreferencedistanceoriginal,indicestoreferenceangleprobe,indicestoreferenceanglemoleculeneighb,indicestoreferenceanglemoleculeneighbneighb,p1,p2,atoms1,probeidxtosymclass):
    p2shifted=p2+len(atoms1)
    inputpair=tuple([p1,p2shifted])
    distanceguess=GrabPairwiseDistance(inputpair,indexpairtoreferencedistanceoriginal)
    distanceratio=.1
    distanceforceconstant=5 # kcal/mol/ang^2
    angleforceconstant=.1 # kcal/mol/deg^2
    lower,upper=GrabUpperLowerBounds(poltype,distanceguess,distanceratio)
    lower=0 # only for distance since want flat-bottom
    p1babel=p1+1
    p2babel=p2+1+len(atoms1)
    restraints=[[p1babel,p2babel]]
    resstring='RESTRAIN-DISTANCE '+str(p1babel)+' '+str(p2babel)+' '+str(distanceforceconstant)+' '+str(lower)+' '+str(upper)+'\n'
    reslist=[resstring]
    angleratio=.03
    anglereslist=[]
    anglereslist,restraints=GrabAngleRestraints(poltype,indicestoreferenceangleprobe,p1,p2shifted,p1babel,p2babel,probeidxtosymclass,angleratio,angleforceconstant,anglereslist,atoms1,restraints)
    anglereslist,restraints=GrabAngleRestraints(poltype,indicestoreferenceanglemoleculeneighb,p1,p2shifted,p1babel,p2babel,probeidxtosymclass,angleratio,angleforceconstant,anglereslist,atoms1,restraints)
    anglereslist,restraints=GrabAngleRestraints(poltype,indicestoreferenceanglemoleculeneighbneighb,p1,p2shifted,p1babel,p2babel,probeidxtosymclass,angleratio,angleforceconstant,anglereslist,atoms1,restraints)
    reslist.extend(anglereslist)
    tempkeyfilename=inputxyz.replace('.xyz','.key')
    shutil.copyfile(keyfile,tempkeyfilename)
    temp=open(tempkeyfilename,'a')
    for line in reslist:
        temp.write(line)
    temp.close()
    torminlogfname=inputxyz.replace('.xyz','.out')
    mincmdstr = poltype.minimizeexe+' '+inputxyz+' -k '+tempkeyfilename+' 0.1'+' '+'>'+torminlogfname
    term,error=poltype.CheckNormalTermination(torminlogfname)
    if term==True and error==False:
        pass
    else:
        poltype.call_subsystem(mincmdstr,True)

    finaloutputxyz=inputxyz+'_2'
    newfilename=inputxyz.replace('.xyz','cart.xyz')
    ConvertTinktoXYZ(poltype,finaloutputxyz,newfilename)
    maxresidx=3-1
    newrestraints=[]
    for residx in range(len(restraints)):
        res=restraints[residx]
        if residx<=maxresidx:
            newrestraints.append(res)
    return newfilename,newrestraints

def ConvertTinktoXYZ(poltype,filename,newfilename):
    temp=open(os.getcwd()+r'/'+filename,'r')
    tempwrite=open(os.getcwd()+r'/'+newfilename,'w')
    results=temp.readlines()
    for lineidx in range(len(results)):
        line=results[lineidx]
        if lineidx==0:
            linesplit=line.split()
            tempwrite.write(linesplit[0]+'\n')
            tempwrite.write('\n')
            tempwrite.flush()
            os.fsync(tempwrite.fileno())
        else:
            linesplit=line.split()
            newline=linesplit[1]+' '+linesplit[2]+' '+linesplit[3]+' '+linesplit[4]+'\n'
            tempwrite.write(newline)
            tempwrite.flush()
            os.fsync(tempwrite.fileno())
    temp.close()
    tempwrite.close()


def GrabAngleRestraints(poltype,indicestoangle,p1,p2shifted,p1babel,p2babel,probeidxtosymclass,angleratio,angleforceconstant,anglereslist,atoms1,restraints):
    inputpair=tuple([p1,p2shifted])
    indices,angleguesses=GrabAngle(inputpair,indicestoangle)
    for i in range(len(indices)):
        tup=indices[i]
        angle=angleguesses[i]
        babelindices=[j+1 for j in tup]
        classes=[]
        lower,upper=GrabUpperLowerBounds(poltype,angle,angleratio,angle=True)
        resstring='RESTRAIN-ANGLE '+str(babelindices[0])+' '+str(babelindices[1])+' '+str(babelindices[2])+' '+str(angleforceconstant)+' '+str(lower)+' '+str(upper)+'\n'
        anglereslist.append(resstring)
        restraints.append(babelindices)
         

    return anglereslist,restraints

def GrabAngle(inputpair,indicestoangle):
    indices=[]
    angleguesses=[]
    for tupindices,angle in indicestoangle.items():
        a=inputpair[0]
        b=inputpair[1]
        if a in tupindices and b in tupindices:
            indices.append(tupindices[:2+1])
            angleguesses.append(angle)

 
    return indices,angleguesses


def GrabUpperLowerBounds(poltype,guess,ratio,angle=False):
    if angle==False:
        lower=guess-guess*ratio
        upper=guess+guess*ratio
    else:
        lower=guess-360*ratio
        upper=guess+360*ratio

    return lower,upper

def GenerateProbePathNames(poltype,vdwprobenames,moleculexyz):
    probepaths=[]
    if 'water' in vdwprobenames:
        path=poltype.vdwprobepathname+'water.xyz'
        probepaths.append(path)
    if poltype.homodimers==True:
        probepaths.append(moleculexyz)
    return probepaths


def readXYZ(poltype,xyz):
  atoms  = np.loadtxt(xyz, usecols=(0,), dtype='str', unpack=True, skiprows=2)
  coords = np.loadtxt(xyz, usecols=(1,2,3), dtype='float', unpack=False, skiprows=2)
  return atoms,coords


def CheckBuriedAtoms(poltype,indexarray,molecule,zeroindex=False):
    indicestodelete=[]
    for i in range(len(indexarray)):
        index=indexarray[i]
        if zeroindex==False:
            idx=index
        else:
            idx=index+1
        atom=molecule.GetAtom(idx)
        valence=atom.GetValence()
        hyb=atom.GetHyb() 
        if valence==4 and hyb==3:
            indicestodelete.append(i)
    for index in indicestodelete:
        del indexarray[index]

    return indexarray


def GrabWaterTypes(poltype):
    probeidxtosymclass={1:349,2:350,3:350}
    return probeidxtosymclass

def GenerateInitialProbeStructure(poltype,missingvdwatomindices):
    molecules = [poltype.xyzfname]
    probes = GenerateProbePathNames(poltype,poltype.vdwprobenames,poltype.xyzfname)
    vdwradius = {"H" : 1.20, "Li": 1.82, "Na": 2.27, "K": 2.75, "Rb": 3.03, "Cs": 3.43, \
                 "Be": 1.53, "Mg": 1.73, "Ca": 2.31, "B": 1.92, "C": 1.70, "N": 1.55, "O":1.52, \
                 "P" : 1.80, "S" : 1.80, "F" : 1.47, "Cl":1.75, "Br":1.85, "Zn":1.39,'I':4.61}           
    dimernames=[]
    probeindices=[]
    moleculeindices=[]
    numberprobeatoms=[]
    for mol in molecules:
        atoms1,coords1,order1, types1, connections1=readTXYZ(poltype,mol)
        mol_spots = missingvdwatomindices.copy()
        mol_spots = [i-1 for i in mol_spots]
        moldimernames=[]
        atomrestraintslist=[]
        for prob in probes:
            probename=os.path.basename(prob)
            prefix=poltype.molstructfname.split('.')[0]
            if prefix in prob:
                probemol=poltype.mol
                atoms2=atoms1.copy()
                coords2=coords1.copy()
            else:
                atoms2,coords2=readXYZ(poltype,prob)
                probemol=opt.load_structfile(poltype,prob)
            probeidxtosymclass,symmetryclass=symm.gen_canonicallabels(poltype,probemol) 
            prob_spots=[]

            for symclass in list(probeidxtosymclass.values()): 
                keys= GrabKeysFromValue(poltype,probeidxtosymclass,symclass)       
                probeidx=keys[0]-1 # shift to 0 index
                if probeidx not in prob_spots:
                    prob_spots.append(probeidx)
            if 'water' in prob:
                probeidxtosymclass=GrabWaterTypes(poltype)
            prob_spots = CheckBuriedAtoms(poltype,prob_spots,probemol,zeroindex=True)
            if 'water' not in prob:
                mol_spots = CheckBuriedAtoms(poltype,mol_spots,poltype.mol,zeroindex=True) 

            for p1 in mol_spots:
                probelist=[]
                probeindiceslist=[]
                moleculeindiceslist=[]
                reslist=[]
                for p2 in prob_spots:
                    e1=atoms1[p1]
                    e2=atoms2[p2]
                    if e1=='H' and e2=='H':
                        continue
                    dimer = mol[:-4] + "-" + probename[:-4] + "_" + str("%d_%d"%(p1+1,len(atoms1)+p2+1)) + ".xyz"
                    outputxyz,restraints=optimizedimer(poltype,atoms1, atoms2, coords1, coords2, p1, p2, dimer,vdwradius,poltype.mol,probemol,probeidxtosymclass)
                    probelist.append(outputxyz)
                    probeindiceslist.append(p2+1+len(atoms1))
                    moleculeindiceslist.append(p1+1)
                    reslist.append(restraints)
                moleculeindices.append(moleculeindiceslist)
                probeindices.append(probeindiceslist)
                moldimernames.append(probelist)
                atomrestraintslist.append(reslist)
                numberprobeatoms.append(probemol.NumAtoms())
    
    return moldimernames,probeindices,moleculeindices,numberprobeatoms,atomrestraintslist

def GrabKeysFromValue(poltype,dic,thevalue):
    keylist=[]
    for key,value in dic.items():
        if value==thevalue:
            keylist.append(key)
    return keylist


def ReplaceParameterFileHeader(poltype,paramhead,keyfile):
    tempname='temp.key'
    temp=open(keyfile,'r')
    results=temp.readlines()
    temp.close() 
    temp=open(tempname,'w')
    for line in results:
        if 'parameter' in line and '#' not in line:
            newline='parameters '+paramhead+'\n'
        else:
            newline=line
        temp.write(newline)
    temp.close() 
    os.remove(keyfile)
    os.rename(tempname,keyfile)
  
def CheckIfFittingCompleted(poltype,prefix):
    check=False
    files=os.listdir()
    for f in files:
        if prefix in f and '.png' in f:
            check=True
            break
    return check

def CombineProbesThatNeedToBeFitTogether(poltype,probeindices,moleculeindices,fullprefixarrays,fulldistarrays,alloutputfilenames):

    newprobeindices=[]
    newmoleculeindices=[]
    newprefixarrays=[]
    newdistarrays=[]
    newoutputfilenames=[]
    indextoindexlist={}
    for i in range(len(moleculeindices)):
        moleculelist=moleculeindices[i]
        firstindex=moleculelist[0]
        if i not in indextoindexlist.keys():
            indextoindexlist[i]=[i]
        for j in range(len(moleculeindices)):
            othermoleculelist=moleculeindices[j]
            otherfirstindex=othermoleculelist[0]
            if j not in indextoindexlist.keys():
                indextoindexlist[j]=[j]
            if firstindex==otherfirstindex and i!=j:
                groupedindices=[i,j]
                for idx in groupedindices:
                    if idx not in indextoindexlist[i]:
                        indextoindexlist[i].append(idx)
                    if idx not in indextoindexlist[j]:
                        indextoindexlist[j].append(idx)
    indicesalreadydone=[]
    for index,indexlist in indextoindexlist.items():
        if index not in indicesalreadydone:
            tempmoleculeindices=[]
            tempprobeindices=[]
            tempprefixes=[]
            tempdistarrays=[]
            tempfilenames=[]
            for idx in indexlist:
                indicesalreadydone.append(idx)  
                moleculelist=moleculeindices[idx]
                probelist=probeindices[idx]
                prefixes=fullprefixarrays[idx]
                distarrays=fulldistarrays[idx]
                filenames=alloutputfilenames[idx]
                tempmoleculeindices.append(moleculelist)
                tempprobeindices.append(probelist)
                tempprefixes.append(prefixes)
                tempdistarrays.append(distarrays)     
                tempfilenames.append(filenames)
            
            newprobeindices.append(tempprobeindices)
            newmoleculeindices.append(tempmoleculeindices)
            newprefixarrays.append(tempprefixes)
            newdistarrays.append(tempdistarrays)
            newoutputfilenames.append(tempfilenames)  

    return newprobeindices,newmoleculeindices,newprefixarrays,newdistarrays,newoutputfilenames
 

def RemoveIgnoredIndices(poltype,probeindices,moleculeindices,moleculeprobeindicestoignore):
    finalprobeindices=[]
    finalmoleculeindices=[]
    for i in range(len(probeindices)):
        probeindexlist=probeindices[i]
        moleculeindexlist=moleculeindices[i]
        newprobeindexlist=[]
        newmoleculeindexlist=[]
        for j in range(len(probeindexlist)):
            probeindex=probeindexlist[j]
            moleculeindex=moleculeindexlist[j]
            ls=[moleculeindex,probeindex]
            if ls in moleculeprobeindicestoignore:
                pass
            else:
                newmoleculeindexlist.append(moleculeindex)
                newprobeindexlist.append(probeindex)
        if len(newprobeindexlist)!=0:
            finalprobeindices.append(newprobeindexlist)
        if len(newmoleculeindexlist)!=0:
            finalmoleculeindices.append(newmoleculeindexlist)


    return finalprobeindices,finalmoleculeindices

def VanDerWaalsOptimization(poltype,missingvdwatomindices):
    poltype.parentdir=os.getcwd()+r'/'
    vdwfoldername='vdw'
    if not os.path.isdir(vdwfoldername):
        os.mkdir(vdwfoldername)
    shutil.copy(poltype.key5fname,vdwfoldername+r'/'+poltype.key5fname)
    CheckAllVdwTypesExist(poltype,poltype.key5fname)
    shutil.copy(poltype.xyzoutfile,vdwfoldername+r'/'+poltype.xyzoutfile)
    shutil.copy(poltype.xyzfname,vdwfoldername+r'/'+poltype.xyzfname)
    os.chdir(vdwfoldername) 
    poltype.optmaxcycle=400
    poltype.optmethod='wB97X-D'
    poltype.espmethod='wB97X-D'
    poltype.espbasisset="aug-cc-pVDZ"
    tempuse_gaus=poltype.use_gaus
    tempuse_gausoptonly=poltype.use_gausoptonly
    #if ('I ' in poltype.mol.GetSpacedFormula()):
    #    pass
    #else:
    #    poltype.use_gaus=False
    #    poltype.use_gausoptonly=False
    poltype.SanitizeAllQMMethods()
    paramhead=os.path.abspath(os.path.join(os.path.split(__file__)[0] , os.pardir))+ "/ParameterFiles/amoebabio18.prm"
    ReplaceParameterFileHeader(poltype,paramhead,poltype.key5fname)
    array=[.8,.9,1,1.1,1.2]
    dimerfiles,probeindices,moleculeindices,numberprobeatoms,atomrestraintslist=GenerateInitialProbeStructure(poltype,missingvdwatomindices)
    obConversion = openbabel.OBConversion()
    checkarray=[]
    fullprefixarrays=[]
    fulldistarrays=[]
    alloutputfilenames=[]
    originalcharge=poltype.mol.GetTotalCharge()
    originalmul=poltype.mol.GetTotalSpinMultiplicity()
    moleculeprobeindicestoignore=[] # if opt fails

    for i in range(len(probeindices)):
        filenameslist=dimerfiles[i]
        restraintslist=atomrestraintslist[i]
        probeindexlist=probeindices[i]
        moleculeindexlist=moleculeindices[i]
        probeatoms=numberprobeatoms[i]
        distancearrays=[]
        prefixarrays=[]
        filenamesarray=[] 
        for probeidx in range(len(probeindexlist)):
            filename=filenameslist[probeidx]
            restraints=restraintslist[probeidx]
            mol = openbabel.OBMol()
            if 'water' in filename:
                totchg=originalcharge
                totmul=originalmul
            else: # homodimer
                totchg=2*originalcharge
                totmul=originalmul# assume is always 1
            mol.SetTotalCharge(totchg)
            mol.SetTotalSpinMultiplicity(totmul)
            chk=mol.GetTotalCharge()
            probeindex=probeindexlist[probeidx]
            moleculeindex=moleculeindexlist[probeidx]
            inFormat = obConversion.FormatFromExt(filename)
            obConversion.SetInFormat(inFormat)
            obConversion.ReadFile(mol, filename)
            prefix=filename.replace('.xyz','')
            check=CheckIfFittingCompleted(poltype,prefix)
            checkarray.append(check)
            poltype.comoptfname=prefix+'-opt.com'
            poltype.chkoptfname=prefix+'-opt.chk'
            poltype.fckoptfname=prefix+'-opt.fchk'
            poltype.logoptfname=prefix+'-opt.log'
            poltype.gausoptfname=prefix+'-opt.log'
            optmol,error = opt.GeometryOptimization(poltype,mol,checkbonds=False,modred=False,bondanglerestraints=restraints,skipscferror=False,charge=totchg,skiperrors=True)
            if error==True:
                moleculeprobeindicestoignore.append([moleculeindex,probeindex])
                continue
            prefixarrays.append(prefix)
            dimeratoms=mol.NumAtoms()
            moleculeatoms=dimeratoms-probeatoms
            moleculeatom=optmol.GetAtom(moleculeindex)
            probeatom=optmol.GetAtom(probeindex)
            try:
                moleculeatomcoords=np.array([moleculeatom.GetX(),moleculeatom.GetY(),moleculeatom.GetZ()])
                probeatomcoords=np.array([probeatom.GetX(),probeatom.GetY(),probeatom.GetZ()])
            except:
                moleculeprobeindicestoignore.append([moleculeindex,probeindex])
                continue
            moleculeatomcoords=np.array([moleculeatom.GetX(),moleculeatom.GetY(),moleculeatom.GetZ()])
            probeatomcoords=np.array([probeatom.GetX(),probeatom.GetY(),probeatom.GetZ()])
            equildistance=np.linalg.norm(probeatomcoords-moleculeatomcoords)
            distarray=np.multiply(equildistance,np.array(array))
            distancearrays.append(distarray)
            outputprefixname=filename.split('.')[0]
            outputxyz=outputprefixname+'_tinker.xyz'
            inputxyz=outputprefixname+'_cartesian.xyz'
            WriteOutCartesianXYZ(poltype,optmol,inputxyz)
            if 'water' in outputxyz:
                waterbool=True
            else:
                waterbool=False
            ConvertProbeDimerXYZToTinkerXYZ(poltype,inputxyz,poltype.xyzoutfile,outputxyz,waterbool,probeatoms)
            filenamearray=MoveDimerAboutMinima(poltype,outputxyz,outputprefixname,moleculeatoms,moleculeindex,probeindex,equildistance,array)
            qmfilenamearray=GenerateSPInputFiles(poltype,filenamearray,poltype.mol,probeatoms)
            outputfilenames=ExecuteSPJobs(poltype,qmfilenamearray,prefix)
            filenamesarray.append(outputfilenames)
        fullprefixarrays.append(prefixarrays)
        fulldistarrays.append(distancearrays)
        alloutputfilenames.append(filenamesarray)
    dothefit=False
    for check in checkarray:
        if check==False:
            dothefit=True
    if dothefit==True:
        probeindices,moleculeindices=RemoveIgnoredIndices(poltype,probeindices,moleculeindices,moleculeprobeindicestoignore)
        newprobeindices,newmoleculeindices,newprefixarrays,newdistarrays,newoutputfilenames=CombineProbesThatNeedToBeFitTogether(poltype,probeindices,moleculeindices,fullprefixarrays,fulldistarrays,alloutputfilenames)

        for k in range(len(newprobeindices)):
            goodfit=False
            count=1
            subprobeindices=newprobeindices[k]
            submoleculeindices=newmoleculeindices[k]
            subprefixarrays=newprefixarrays[k]
            subdistarrays=newdistarrays[k]
            subfilenames=newoutputfilenames[k]
            flat_probeindices = [item for sublist in subprobeindices for item in sublist]
            flat_moleculeindices = [item for sublist in submoleculeindices for item in sublist]
            flat_prefixarrays = [item for sublist in subprefixarrays for item in sublist]
            flat_distarrays = [item for sublist in subdistarrays for item in sublist]
            flat_filenames = [item for sublist in subfilenames for item in sublist]
            flat_filenames = [item for sublist in flat_filenames for item in sublist]

            while goodfit==False:
                if count>2:
                    break
                vdwtypesarray=[]
                initialradii=[]
                initialdepths=[]
                initialreds=[]
                minradii=[]
                maxradii=[]
                mindepths=[]
                maxdepths=[]
                minreds=[]
                maxreds=[]
                fitredboolarray=[]
                ReadCounterPoiseAndWriteQMData(poltype,flat_filenames)
                for probeidx in range(len(flat_probeindices)):
                    prefix=flat_prefixarrays[probeidx]
                    probeindex=flat_probeindices[probeidx]
                    moleculeindex=flat_moleculeindices[probeidx]
                    vdwtype=poltype.idxtosymclass[moleculeindex]
                    atom=poltype.mol.GetAtom(moleculeindex)
                    valence=atom.GetValence()
                    if valence==1:
                       fitred=True
                    else:
                       fitred=False
                    if vdwtype not in vdwtypesarray:
                        vdwtypesarray.append(vdwtype)
                        fitredboolarray.append(fitred)
                        initialvdwradius,initialvdwdepth,minvdwradius,maxvdwradius,minvdwdepth,maxvdwdepth,red,minred,maxred=GrabVdwParameters(poltype,vdwtype)
                        initialradii.append(initialvdwradius)
                        initialdepths.append(initialvdwdepth)
                        minradii.append(minvdwradius)
                        maxradii.append(maxvdwradius)
                        mindepths.append(minvdwdepth)
                        maxdepths.append(maxvdwdepth)
                        initialreds.append(red)
                        minreds.append(minred)
                        maxreds.append(maxred)
                    if 'water' not in prefix:
                        adjustedprobeindex=probeindex-len(poltype.idxtosymclass.keys())
                        vdwtype=poltype.idxtosymclass[adjustedprobeindex]
                        atom=poltype.mol.GetAtom(adjustedprobeindex)
                        valence=atom.GetValence()
                        if valence==1:
                           fitred=True
                        else:
                           fitred=False

                        if vdwtype not in vdwtypesarray:
                            vdwtypesarray.append(vdwtype)
                            fitredboolarray.append(fitred)
                            initialvdwradius,initialvdwdepth,minvdwradius,maxvdwradius,minvdwdepth,maxvdwdepth,red,minred,maxred=GrabVdwParameters(poltype,vdwtype)
                            initialradii.append(initialvdwradius)
                            initialdepths.append(initialvdwdepth)
                            minradii.append(minvdwradius)
                            maxradii.append(maxvdwradius)
                            mindepths.append(minvdwdepth)
                            maxdepths.append(maxvdwdepth)
                            initialreds.append(red)
                            minreds.append(minred)
                            maxreds.append(maxred)
                WriteInitialPrmFile(poltype,vdwtypesarray,initialradii,initialdepths,minradii,maxradii,mindepths,maxdepths,initialreds,minreds,maxreds)
                vdwradii,vdwdepths,vdwreds,fail=VDWOptimizer(poltype,count,fitredboolarray)
                if fail==True: # rare case failure not due to inputs but something intenral to optimizer?
                    goodfit=True
                if fail==False:
                    for k in range(len(flat_prefixarrays)):
                        prefix=flat_prefixarrays[k]
                        distarray=flat_distarrays[k]
                        PlotEnergyVsDistance(poltype,distarray,prefix,vdwradii,vdwdepths,vdwreds,vdwtypesarray,count)
                        othergoodfit=PlotQMVsMMEnergy(poltype,vdwtypesarray,prefix,count)
                    goodfit=PlotQMVsMMEnergy(poltype,vdwtypesarray,flat_prefixarrays,count,allprefix=True)
                    count+=1

    shutil.copy(poltype.key5fname,'../'+poltype.key5fname)
    os.chdir(poltype.parentdir)
    poltype.use_gaus=tempuse_gaus
    poltype.use_gausoptonly=tempuse_gausoptonly

