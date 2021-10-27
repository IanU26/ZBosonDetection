import ROOT # imports the ROOT analysis framework
from DataFormats.FWLite import Events, Handle #Imports handing of CMS events from python
ROOT.AutoLibraryLoader.enable()
import math

def deltaR(eta1,phi1,eta2,phi2):
    deltaPhi = phi1-phi2
    if deltaPhi<-2*math.pi:
        deltaPhi = deltaPhi+2*math.pi
    if deltaPhi>2*math.pi:
        deltaPhi = deltaPhi-2*math.pi
    deltaEta=eta1-eta2
    return math.sqrt(deltaPhi*deltaPhi+deltaEta*deltaEta)


#pick some files
files = [
'root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2010/Summer12/DYToEE_M-20_TuneZ2star_HFshowerLibrary_7TeV_pythia6/AODSIM/LowPU2010_DR42_PU_S0_START42_V17B-v1/00000/085D5D1E-AB30-E211-B266-E61F13191A8B.root',
'root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2010/Summer12/DYToEE_M-20_TuneZ2star_HFshowerLibrary_7TeV_pythia6/AODSIM/LowPU2010_DR42_PU_S0_START42_V17B-v1/00000/12ED08DF-AE30-E211-898C-00215E2222CE.root',
'root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2010/Summer12/DYToEE_M-20_TuneZ2star_HFshowerLibrary_7TeV_pythia6/AODSIM/LowPU2010_DR42_PU_S0_START42_V17B-v1/00000/1661DCAE-A730-E211-BD58-E41F13181B0C.root'


]


#declare an event object
events=Events(files)

#define a Handle. A handle is a pointer to an object stored into the collission event. In this case I define a handle to a collection of electrons:

electronHandle  = Handle  ('vector<reco::GsfElectron>')
genHandle  = Handle('vector<reco::GenParticle>')


#Create an event counter
N=0


##Declare a ROOT histogram of the Pt of the genElectron before and after matching
genPtAll = ROOT.TH1D("genPt","",20,0,100)
genPtSelectedMatched = ROOT.TH1D("genPtSelMatch","",20,0,100)
electronPtAll = ROOT.TH1D("electronPt","",20,0,100)
electronPtSelected = ROOT.TH1D("electronPtSelectedMatched","",20,0,100)



#loop through the events:
for event in events:
    #enable this to process small number of events (for tests)
    if N==5000:
       break;
    # print the event number every 500 events
    if N % 500==0:
        print N
    N=N+1    

    #pull the electron Handle from the event 
    event.getByLabel('gsfElectrons',electronHandle)
    electrons = electronHandle.product()

    #pull the gen electrons from the event
    event.getByLabel('genParticles','','SIM',genHandle)
    genParticles = genHandle.product()
    #filter electrons that come from Z with |eta|<2.5
    genElectrons = filter(lambda x: abs(x.pdgId())==11 and abs(x.eta())<2.5 and x.status()==1,genParticles)



    #apply a selection! (Your code will go here I apply as example H/E <0.1)
    selectedElectrons=[]
    for e in electrons:
        if e.hcalOverEcal()<0.1:
            selectedElectrons.append(e)



    #loop on true electrons
    for g in genElectrons:
        print g.pt(),g.eta(),g.phi(),g.status()
        #fill the true pt
        genPtAll.Fill(g.pt())
        #see if this electron is matched to a real one
        for e in selectedElectrons:
            if deltaR(g.eta(),g.phi(),e.eta(),e.phi())<0.3:
                genPtSelectedMatched.Fill(g.pt())
                break #if it finds a match it stops
            
        
    #loop on all and add code here to calculate the misID probability

        






#open a file to save the plot
#see ROOT class TFile
f=ROOT.TFile("plots.root","RECREATE")
f.cd() # go to the file
genPtAll.Write()
genPtSelectedMatched.Write()
efficiency = ROOT.TGraphAsymmErrors(genPtSelectedMatched,genPtAll)
efficiency.Write()
efficiency.Draw("AP")
f.Close() #close the file


