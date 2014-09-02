# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 14:16:25 2012

@author: proto

"""
import numpy as np
import libsbml2bngl
import libsbml
import analyzeRDF
import MySQLdb
from SOAPpy import WSDL,Types
import pickle
import re
from restful_lib import Connection
import urllib,urllib2
#from wordcloud import cloudText
import operator
from collections import Counter

import libsbml
import networkx as nx

from os import listdir
from os.path import isfile, join
import sys
sys.path.insert(0, '../utils/')
import pygraphviz as pgv
import bioservices
import pprint

def main():
    history = np.load('stats3b.npy')
    history2 = np.load('stats3.npy')
    dictionary = {}
    
    for index in range (0,len(history)):
        flag = False
        if history[index] == []:
            continue
        else:
            for index2 in range(0,len(history2)):
                element = history2[index2]
                
                if element[0] == index+1:
                    if element[2] == 0.0:
                        flag = True
                        break
                    else:
                        break
                elif element[0] > index+1:
                    continue
            if flag:
                continue
            for molecule in history[index]:
                if molecule == []:
                    continue
                
                for uniprot in molecule[1][1]:
                    
                    if uniprot not in dictionary:
                        dictionary[uniprot] = []
                    if index+1 not in [x[0] for x in dictionary[uniprot]]:
                        dictionary[uniprot].append([index+1,molecule[0]])
    
    np.save('statsFinal.npy',np.array(dictionary))
    for element in dictionary:
        if len(dictionary[element]) > 1:
            print element,dictionary[element]
            
def bagOfWords():
    with open('sortedC.dump','rb') as f:
        sortedFiles = pickle.load(f)
        
    with open('parsedAnnotations.dump','rb') as f:
        annotations = pickle.load(f)
    
    with open('classificationDict.dump','rb') as f:
        classifications = pickle.load(f)
        
    bins = np.digitize(sortedFiles,np.arange(0,1.1,0.1))
    annotationDict = {x:{} for x in range(1,12)}
    classDict = {x:{} for x in range(1,12)}
    
    problem = {}
    problem['empty'] = 0
    problem['none'] = 0
    problem['pheno'] = 0
    for idx,element in enumerate(classifications):
        if bins[idx] == 1:
            if element == {}:
                problem['empty'] += 1
            else:
                if 'None' in element:
                    problem['none'] += element['None']
                if 'Generation' in element:
                    problem['pheno'] += element['Generation']  
                if 'Decay' in element:
                    problem['pheno'] += element['Decay']
    
    print problem
    for idx,element in enumerate(annotations):
        if idx < len(bins):
            if len(element) > 0:
                for ann in element:
                    for word in ann[0].split(' '):
                        if word not in annotationDict[bins[idx]]:
                            annotationDict[bins[idx]][word] = 0
                        annotationDict[bins[idx]][word] += 1.0
    for element in annotationDict:
        annotationDict[element] = {x:annotationDict[element][x] for x in annotationDict[element] if annotationDict[element][x] > 3 and len(x) > 2}
    print annotationDict
    
    for element in annotationDict:
        stringA = ''
        for word in annotationDict[element]:
            tword = word.replace('/','')
            tword = word.replace('-','')
            stringA += ' ' + ' '.join([tword for x in range(0,int(annotationDict[element][word]))])
        cloudText(stringA,'cloud{0}.png'.format(element))
    
    stringA = ''
    for element in [9,10,11]:
        for word in annotationDict[element]:
            tword = word.replace('/','')
            tword = word.replace('-','')
            stringA += ' ' + ' '.join([tword for x in range(0,int(annotationDict[element][word]))])
    cloudText(stringA,'cloudMax.png')
        
import pyparsing as pyp
goGrammar = pyp.Suppress(pyp.Literal('<name>')) +  pyp.Word(pyp.alphanums + ' -_') + pyp.Suppress(pyp.Literal('</name>')) 

def resolveAnnotation(annotation):
    if not hasattr(resolveAnnotation, 'db'):
        resolveAnnotation.db = {}
        resolveAnnotation.ch = bioservices.ChEBI(verbose=False)
        resolveAnnotation.uni = bioservices.UniProt(verbose=False)
        resolveAnnotation.k = bioservices.kegg.KeggParser(verbose=False)
        resolveAnnotation.qg = bioservices.QuickGO(verbose=False)
        resolveAnnotation.db['http://identifiers.org/uniprot/P62988'] = 'http://identifiers.org/uniprot/P62988'
        resolveAnnotation.db['http://identifiers.org/uniprot/P06842'] = 'http://identifiers.org/uniprot/P06842'
        resolveAnnotation.db['http://identifiers.org/uniprot/P07006'] = 'http://identifiers.org/uniprot/P06842'
        
    if annotation in resolveAnnotation.db:
        return resolveAnnotation.db[annotation]
    
        
    tAnnotation = annotation.replace('%3A',':')
    tAnnotation = annotation.split('/')[-1]
    #tAnnotation = re.search(':([^:]+:[^:]+$)',tAnnotation).group(1)
    try:
        if 'obo.go' in annotation:

            res = resolveAnnotation.qg.Term(tAnnotation)
            tmp = res.findAll('name')
            finalArray = []
            for x in tmp:
                try:
                    tagString = str(goGrammar.parseString(str(x))[0])
                    if tagString not in ['Systematic synonym']:
                        finalArray.append(str(goGrammar.parseString(str(x))[0]))
                except pyp.ParseBaseException:
                    continue
                
            resolveAnnotation.db[annotation] = finalArray
            return resolveAnnotation.db[annotation]
    
        elif 'kegg' in annotation:
            
            data = resolveAnnotation.k.get(tAnnotation)
            dict_data =  resolveAnnotation.k.parse(data)
            resolveAnnotation.db[annotation] = dict_data['name']
            return resolveAnnotation.db[annotation]
            
        elif 'uniprot' in annotation:
            identifier = annotation.split('/')[-1]
            result = resolveAnnotation.uni.quick_search(identifier)
            resolveAnnotation.db[annotation] = result[result.keys()[0]]['Protein names']
            return resolveAnnotation.db[annotation]
            
        elif 'chebi' in annotation:
            tmp = annotation.split('/')[-1]
            
            entry = resolveAnnotation.ch.getLiteEntity(tmp)
            for element in entry:
                resolveAnnotation.db[annotation] = element['chebiAsciiName']
                return resolveAnnotation.db[annotation]
        elif 'cco' in annotation or 'pirsf' in annotation or 'pubchem' in annotation or 'omim' in annotation:
            return annotation
        #elif 'taxonomy' in annotation:
            #uniprot stuff for taxonomy
        #    pass
            '''
            url = 'http://www.uniprot.org/taxonomy/'
            params = {
            'from':'ACC',
            'to':'P_REFSEQ_AC',
            'format':'tab',
            'query':'P13368 P20806 Q9UM73 P97793 Q17192'
            }
            
            data = urllib.urlencode(params)
            request = urllib2.Request(url, data)
            contact = "" # Please set your email address here to help us debug in case of problems.
            request.add_header('User-Agent', 'Python contact')
            response = urllib2.urlopen(request)
            page = response.read(200000)
            '''
        else:
            print 'ERRROERROROERRRO'
            #assert(False)
            return annotation
    except:
        return annotation
    #finally:

#def extractAnnotations(xmlFiles):
    
def main2():
    #go database
    print '---'    
    annotationArray = []
    with open('annotations.dump','rb') as f:
        ar = pickle.load(f)
    modelAnnotations = Counter()

    for idx,element in enumerate(ar):
        print idx
        for index  in element:
            
            for annotation in element[index]:
                    bioArray = []
                    #tAnnotation = annotation.replace('%3A',':')
                    #tAnnotation = re.search(':([^:]+:[^:]+$)',tAnnotation).group(1)
                    resultArray = resolveAnnotation(annotation)
                    if type(resultArray) is list:
                        for result in resultArray:
                            modelAnnotations[result] += 1
                    elif 'http' not in resultArray:
                        modelAnnotations[resultArray] += 1
    
        #annotationArray.append(modelAnnotations)
    print modelAnnotations
    with open('parsedAnnotations.dump','wb') as f:
        pickle.dump(annotationArray,f)

def histogram():
    import matplotlib.pyplot as plt
    import numpy as np
    evaluationFile = open('sortedC.dump','rb')
    ev1 =     pickle.load(evaluationFile)
    number,rulesLength,evaluation,evaluation2 =  zip(*ev1)
    evaluation20 = []
    evaluationn20 = []
    trueEvaluation = []
    trueRatio = []
    ratio20 = []
    ration20 = []
    
    
    problemModels = []
    print 'syndec',len([x for x in rulesLength if x == -1])
    for x,y,z,w in zip(rulesLength,evaluation,number,evaluation2):
        if x>=10:
            if y <= 0.1:
                problemModels.append(z)
            evaluation20.append(y)
            ratio20.append(1-w)
        if x>=0:
            if x<10:
                evaluationn20.append(y)
                ration20.append(1-w)
            trueEvaluation.append(y)
            trueRatio.append(1-w)
            
            
    print '0 atom large models',problemModels
    plt.clf()
    plt.hist(rulesLength,bins=[10,30,50,70,90,110,140,180,250,400])
    plt.xlabel('Number of reactions',fontsize=18)
    plt.savefig('lengthDistro.png')
    plt.clf()
    plt.hist(trueEvaluation, bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                                0.8, 0.9, 1.0])

    
    plt.xlabel('Atomization Degree ({0} models)'.format(len(trueEvaluation)),fontsize=18)    
    plt.savefig('atomizationDistroHist.png')

    plt.clf()
    plt.hist(evaluation20, bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                                0.8, 0.9, 1.0])
    plt.xlabel('Atomization Degree >10 reactions ({0} models)'.format(len(evaluation20)), fontsize=18)
    plt.savefig('atomizationDistroHist10ormore.png')

    plt.clf()
    plt.hist(evaluationn20, bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7,
                                0.8, 0.9, 1.0])
    plt.xlabel('Atomization Degree <=10 reactions ({0} models)'.format(len(evaluationn20)), fontsize=18)
    plt.savefig('atomizationDistroHist10orless.png')

    strueEvaluation=np.sort( trueEvaluation )
    yvals=np.arange(len(strueEvaluation))/float(len(strueEvaluation))
    plt.clf()
    plt.plot( strueEvaluation, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Atomization Degree CDF', fontsize=18)
    plt.savefig('atomizationDistroCDF.png')

    strueRatio=np.sort( trueRatio )
    yvals=np.arange(len(trueRatio))/float(len(trueRatio))
    plt.clf()
    plt.plot( strueRatio, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Compression Degree CDF', fontsize=18)
    plt.savefig('compressionDistroCDF.png')

    s10ormore=np.sort( evaluation20 )
    yvals=np.arange(len(evaluation20))/float(len(evaluation20))
    plt.clf()
    plt.plot( s10ormore, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Atomization Degree CDF (>10 reactions)', fontsize=18)
    plt.savefig('atomizationDistroCDF10ormore.png')

    strueRatio=np.sort( ratio20 )
    yvals=np.arange(len(ratio20))/float(len(ratio20))
    plt.clf()
    plt.plot( strueRatio, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Compression Degree CDF (>10 reactions)', fontsize=18)
    plt.savefig('compressionDistro10orMoreCDF.png')

    s10orless=np.sort( evaluationn20 )
    yvals=np.arange(len(evaluationn20))/float(len(evaluationn20))
    plt.clf()
    plt.plot( s10orless, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Atomization Degree CDF (<= 10 reactions)', fontsize=18)
    plt.savefig('atomizationDistroCDF10orless.png')

    strueRatio=np.sort( ration20 )
    yvals=np.arange(len(ration20))/float(len(ration20))
    plt.clf()
    plt.plot( strueRatio, yvals )
    plt.axis([0, 1, 0, 1])
    plt.xlabel('Compression Degree CDF (<= 10 reactions)', fontsize=18)
    plt.savefig('compressionDistro10orlessCDF.png')

    ev = []
    idx = 1
    '''
    for x, y, z in zip(rulesLength, evaluation, compartmentLength):
        
        if idx in [18, 51, 353, 108, 109, 255, 268, 392]:
            idx+=1

        if x < 15 and y > 0.7 and z>1:
            print '---',idx,x,y
        idx+=1
    '''
    #plt.hist(ev,bins =[0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0])
    #plt.xlabel('Atomization Degree',fontsize=18)    
    #plt.savefig('ruleifyDistro3.png')


def rankingAnalysis():
    annotationFile = open('parsedAnnotations.dump','rb')
    evaluationFile = open('sortedC.dump','rb')
    
    annotations = pickle.load(annotationFile)
    pickle.load(evaluationFile)
    ev1 =     pickle.load(evaluationFile)
    totalAnnotations = {}
    totalAppereances = {}
    weightedTotalAppereances = {}
    for ann,evaluation in zip(annotations,ev1):
        total = sum(ann[x] for x in ann)
        for x in ann:
            if x not in totalAnnotations:
                totalAnnotations[x] = 0
                totalAppereances[x] = 0
                weightedTotalAppereances[x] = 0
            totalAnnotations[x] += ann[x]*evaluation/total
            totalAppereances[x] += ann[x]
            weightedTotalAppereances[x] += ann[x]*1.0/total
            
    sortedAnnotations = sorted(totalAnnotations.iteritems(), key=operator.itemgetter(1),reverse=True)
    sortedAppereances = sorted(totalAppereances.iteritems(), key=operator.itemgetter(1),reverse=True)
    sortedWeightedAppereances = sorted(weightedTotalAppereances.iteritems(), key=operator.itemgetter(1),reverse=True)
    print '--- top proteins weighted by the number of times they appear and how atomizable their model is'
    print sortedAnnotations[0:10]
    print '--- top protein by number of appereances in a model'
    print sortedAppereances[0:10]
    print '--- top proteins by number of weighted appeareances in a model'
    print sortedWeightedAppereances[0:10]
    #print sortedAnnotations
    
def inverseAnnotationClassification():
    annotationFile = open('annotations.dump','rb')
    annotations = pickle.load(annotationFile)    


bioqual = ['BQB_IS','BQB_HAS_PART','BQB_IS_PART_OF','BQB_IS_VERSION_OF',
          'BQB_HAS_VERSION','BQB_IS_HOMOLOG_TO',
'BQB_IS_DESCRIBED_BY','BQB_IS_ENCODED_BY','BQB_ENCODES','BQB_OCCURS_IN',
'BQB_HAS_PROPERTY','BQB_IS_PROPERTY_OF','BQB_UNKNOWN']

modqual = ['BQM_IS','BQM_IS_DESCRIBED_BY','BQM_IS_DERIVED_FROM','BQM_UNKNOWN']

qual = [modqual,bioqual]
def extractXMLInfo(fileName):
    #if not hasattr(extractXMLInfo, 'm'):
    #    extractXMLInfo.m = Miriam()
    
    reader = libsbml.SBMLReader()
    document = reader.readSBMLFromFile(fileName)
    model = document.getModel()
    from collections import defaultdict

    metaArray = defaultdict(list)   
    metaDict = {}
    metaDict2 = defaultdict(list)
    if model != None:
        #annotation = model.getAnnotation()
        #lista = libsbml.CVTermList()
        #libsbml.RDFAnnotationParser.parseRDFAnnotation(annotation,lista)
        #for idx in range(0,lista.getSize()):
        #  resource = lista.get(idx).getResources().getValue(0)
        #  metaArray.add(resource)
        
        for species in model.getListOfSpecies():
            name = species.getName()
            speciesId = species.getId()
            annotation = species.getAnnotation()
            lista = libsbml.CVTermList()
            libsbml.RDFAnnotationParser.parseRDFAnnotation(annotation,lista)
            for idx in range(0,lista.getSize()):
              for idx2 in range(0, lista.get(idx).getResources().getLength()):
                  resource = lista.get(idx).getResources().getValue(idx2)
                  qualifierType = lista.get(idx).getQualifierType()
                  qualifierDescription= bioqual[lista.get(idx).getBiologicalQualifierType()] if qualifierType \
                  else modqual[lista.get(idx).getModelQualifierType()]
                  #resource = resolveAnnotation(resource)
                  metaArray[qualifierDescription].append(resource)
                  metaDict[speciesId] = (name,resource,qualifierDescription)
                  metaDict2[resource].append([speciesId,name,qualifierDescription])

    return metaArray,metaDict,metaDict2
            

    
    
def biomodelsInteractome():
    directory = 'complex'
    onlyfiles = [ f for f in listdir('./' + directory) if isfile(join('./' + directory,f))]
    bnglFiles = [x for x in onlyfiles if 'bngl' in x and 'log' not in x]

    xmlFiles = [ f for f in listdir('./XMLExamples/curated') if isfile(join('./XMLExamples/curated',f)) and f.endswith('.xml')]
    xmlFiles = sorted(xmlFiles)
    xmlArray = []
    xmlExtendedArray = []
    xmlExtendedArray2 = {}
    for xml in xmlFiles:
        if '019.' in xml:
            pass
        metaArray,metaDict ,metaDict2= extractXMLInfo(join('./XMLExamples/curated',xml))
        xmlArray.append(metaArray)
        xmlExtendedArray.append(metaDict)
        xmlExtendedArray2[xml] = metaDict2
    with open('xmlAnnotationsExtended.dump','wb') as f:
        pickle.dump(xmlExtendedArray,f)
    with open('xmlAnnotations.dump','wb') as f:
        pickle.dump(xmlArray,f)
    with open('xmlAnnotationsExtended2.dump','wb') as f:
        pickle.dump(xmlExtendedArray2,f)

def reduceElements(element,linkArray):
    s = [len(set.intersection(element,x)) > 0 for x in linkArray]
    indexes = np.nonzero(s)
    s = [linkArray[x] for x in indexes[0]]
    if len(s) > 0:
        union = set.union(*s)
    else:
        union = set([])
    
    return set.union(union,element),[x for idx,x in enumerate(linkArray) if idx not in indexes[0]]


def basicReactome(relationshipMatrix):
    fileName = 'basicReactome2'
    graph = nx.Graph()
    for element in range(0,len(relationshipMatrix)):
        graph.add_node('Model {0}'.format(element+1),color='teal')
    edgeList = []
    for idx,row in enumerate(relationshipMatrix):
        for idx2,column in enumerate(row):
            if column != 0.0:
                edgeList.append(['Model {0}'.format(idx+1),'Model {0}'.format(idx2+1),int(column)])
    graph.add_weighted_edges_from(edgeList)
    nx.write_gml(graph,'%s.gml' % fileName)
    nx.write_graphml(graph,'%s.graphml'% fileName)
    #subprocess.call(['circo', '-Tpng', '{0}.dot'.format(fileName),'-o{0}.png'.format(fileName)])

def basicCSVReactome(relationshipMatrix):
    with open('basicReactome.csv','w') as f:
        for idx,row in enumerate(relationshipMatrix):
            for idx2,column in enumerate(row):
                if column > 0:
                    f.write('Model{0},Model{1},{2}\n'.format(idx+1,idx2+1,column))


def getLinkArray(relationshipMatrix):
    '''
    based on a relationship matrix get which models related to each other
    form a continuous group
    '''
    linkArray = []
    for idx,element in enumerate(relationshipMatrix):
        tmp = set([idx+1])
        s = np.nonzero(element)[0]+1
        print s
        for element in s:
            tmp.add(element)
        linkArray.append(tmp)

    idx=0
    while idx +1< len(linkArray):
        tmp,tmp2 = reduceElements(linkArray[idx],linkArray[idx+1:])
        if tmp == linkArray[idx]:
            idx+=1
        else:
            linkArray = linkArray[0:idx]
            linkArray.append(tmp)
            linkArray.extend(tmp2)

    return linkArray  


def getModelRelationshipMatrix(annotations,threshold=3):
    blacklist = ['http://identifiers.org/obo.chebi/CHEBI:33699','http://identifiers.org/kegg.compound/C00562',
                 'http://identifiers.org/obo.chebi/CHEBI:36080','http://identifiers.org/chebi/CHEBI:33699',
                 'http://identifiers.org/obo.chebi/CHEBI:15422','http://identifiers.org/obo.chebi/CHEBI:16761',
                 'http://identifiers.org/obo.go/GO:0043234','http://identifiers.org/chebi/CHEBI:15422',
                 'http://identifiers.org/chebi/CHEBI:16761'
                 ]
    relationshipMatrix = np.zeros((len(annotations),len(annotations)))
    negativeRelationshipMatrix = np.zeros((len(annotations),len(annotations)))
    for element in range(0,len(annotations)-1):
        for element2 in range(element+1,len(annotations)):
            totalList1 = set([y for x in annotations[element] for y in annotations[element][x]])
            totalList2 = set([y for x in annotations[element2] for y in annotations[element2][x]])
            score = len([x for x in totalList1 if x in totalList2 and x not in blacklist])
            nscore = len([x for x in  totalList1 if x not in totalList2 and x not in blacklist]) + len([x for x in  totalList2 if x not in totalList1 and x not in blacklist])
            if score > threshold:
                relationshipMatrix[element,element2] = score
            else:
                relationshipMatrix[element,element2] = 0
            negativeRelationshipMatrix[element,element2] = nscore
    return relationshipMatrix,negativeRelationshipMatrix

def biomodelsInteractomeAnalysis():
    with open('xmlAnnotations.dump','rb') as f:
        annotations = pickle.load(f)

    relationshipMatrix,negativeRelationshipMatrix = getModelRelationshipMatrix(annotations)
    basicReactome(relationshipMatrix)
    #basicCSVReactome(relationshipMatrix)
    #return
    counter = Counter()
    for annotation in annotations:
        counter.update(annotation)
    array = []
    '''
    for element in counter:
        print element
        print (resolveAnnotation(element),counter[element]) 
        array.append([element,str(resolveAnnotation(element)),counter[element]]) 

    with open('annotationIntersectionResolved2.txt','w') as f:
        
        pickle.dump(array,f)
    '''    
        
    linkArray = getLinkArray(relationshipMatrix)
    linkArray = sorted(linkArray, key =lambda x:len(x),reverse=True)
    
    degrees =  [len(x) for x in linkArray]
    print np.average(degrees),np.std(degrees),np.median(degrees)

    with open('xmlAnnotations.txt','w') as f:
        pprint.pprint([('biomodels {0}'.format(idx+1),x) for idx,x in enumerate(annotations)],f)
        pprint.pprint(linkArray,f)
        
    with open('linkArray.dump','wb') as f:
        pickle.dump(linkArray,f)
    print [len(x) for x in linkArray]
     
def annotationSharingFinder():
    with open('xmlAnnotations.dump','rb') as f:
        annotations = pickle.load(f)
    with open('evalResults.dump','rb') as f:
        ev = pickle.load(f)
        
    from operator import itemgetter
    relationshipTracker = []
    relationshipMatrix,negativeRelationshipMatrix = getModelRelationshipMatrix(annotations)
    for idx,_ in enumerate(relationshipMatrix):
        for idx2,_ in enumerate(relationshipMatrix[idx]):
            if relationshipMatrix[idx][idx2] > 10:
                nameStr = 'BIOMD0000000%03d.xml' % (idx+1)
                nameStr2 = 'BIOMD0000000%03d.xml' % (idx2+1)
                sc1 = ev[nameStr][2] if nameStr in ev else 0
                sc2 = ev[nameStr2][2] if nameStr2 in ev else 0
                
                if sc1*sc2 > 0 and (1-sc1)*(1-sc2) > 0:
                    relationshipTracker.append([idx+1,idx2+1,float((0.5*relationshipMatrix[idx][idx2])+ negativeRelationshipMatrix[idx][idx2])*(1-sc1)*(1-sc2)])
    relationshipTracker =  sorted(relationshipTracker,key=itemgetter(2),reverse=True)
    print relationshipTracker
    #print relationshipTracker
    

def standardizeName(name):
    '''
    Remove stuff not used by bngl
    '''
    name2 = name
    
    sbml2BnglTranslationDict = {"^":"",
                                "'":"",
                                "*":"m"," ":"_",
                                "#":"sh",
                                ":":"_",'α':'a',
                                'β':'b',
                                'γ':'g',"(":"__",
                                ")":"__",
                                " ":"","+":"pl",
                                "/":"_",":":"_",
                                "-":"_",
                                ".":"_",
                                '?':"unkn",
                                ',':'_',
                                '[':'__',
                                  ']':'__',
                                  '>':'_',
                                  '<':'_'}
                                
    for element in sbml2BnglTranslationDict:
        name = name.replace(element,sbml2BnglTranslationDict[element])
    if name[:1].isdigit():
        name = 's' + name
    
    return name


def compareConventions(name1,name2):
    nameStr = 'BIOMD0000000%03d.xml' % (name1)
    nameStr2 = 'BIOMD0000000%03d.xml' % (name2)
    import re
    with open('xmlAnnotationsExtended2.dump','rb') as f:
        ann = pickle.load(f)
    dic1 = ann[nameStr]
    dic2 = ann[nameStr2]
    #print dic1
    with open('complex/output{0}.bngl'.format(name2),'r') as f:
        bnglContent = f.read()
    #pp.pprint(dict(dic1))
    #pp.pprint(dict(dic2))
    #print dic2
    counter = 0
    for element in [x for x in dic1 if x in dic2]:
        counter += 1
        print '---',element,dic1[element],dic2[element]
        if standardizeName(dic2[element][0][1]) !=standardizeName(dic1[element][0][1]):
            while re.search(r'(\W|^)({0})(\W|$)'.format(standardizeName(dic2[element][0][1])),bnglContent): 
                bnglContent = re.sub(r'(\W|^)({0})(\W|$)'.format(standardizeName(dic2[element][0][1])),r'\g<1>{0}\g<3>'.format(standardizeName(dic1[element][0][1])),bnglContent)
    with open('complex/modified_output{0}_n{1}.bngl'.format(name2,name1),'w') as f:
        f.write(bnglContent)
    return counter

if __name__ == "__main__":
    #bagOfWords()
    #main2()
    histogram()
    #rankingAnalysis()
    #print resolveAnnotation('http://identifiers.org/reactome/REACT_9417.3')
    #biomodelsInteractome()
    #biomodelsInteractomeAnalysis()
    #biomodelsInteractome()
    #counter = []
    
    #array = [11,14,19,28,32,49,237,344,399]
    '''    
    array = [19,33,48,84,262,263,264,394,398,424,427]
    for idx in range(0,len(array)-1):
        for idx2 in range(idx+1,len(array)):
            score = compareConventions(array[idx],array[idx2])
            counter.append([array[idx],
                            array[idx2],score])
            if score > 0:
                print array[idx],array[idx2],score
    
    counter = sorted(counter,key=lambda x:x[2])
    print counter
    '''
    
    #print compareConventions(19,424)
    
    #equivalenceDictionary = {'Ras-GTP':'RasGTP','Ras-GDP':'RasGDP'}
    #biomodelsInteractomeAnalysis()
    #print compareConventions(32,49)
    #extractXMLInfo('XMLExamples/curated/BIOMD0000000019.xml')
    #annotationSharingFinder()