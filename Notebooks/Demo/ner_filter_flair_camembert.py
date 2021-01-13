import re
import flair
from flair.data import Corpus, Sentence
from flair.embeddings import TokenEmbeddings, WordEmbeddings, StackedEmbeddings, TransformerWordEmbeddings, CamembertEmbeddings
from typing import List
from flair.models import SequenceTagger
from flair.trainers import ModelTrainer
from flair.training_utils import EvaluationMetric

class NERFilter:
    model = SequenceTagger.load('resources/taggers/example-ner-camembert/best-model.pt')

    entitiesListName = []
    def merging_entities(self,sentence):
        entitiesList = []

        
        for entity in sentence.get_spans('ner')  :
            
            for data in entity.labels:
                if re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'PER' and len(entity.text)>2 :
                    #strr= strr+"[REDACTEDPER]"
                    entitiesList.append(entity.text)
                    self.entitiesListName.append('[REDACTEDPER]')
                    
                if re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'LOC' and len(entity.text)>2 :
                    #strr= strr+"[REDACTEDLOC]"
                    entitiesList.append(entity.text)
                    self.entitiesListName.append('[REDACTEDLOC]')
                    
                #if re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'MISC' and len(entity.text)>2 :
                    #strr= strr+"[REDACTEDMISC]"
                    #entitiesList.append(entity.text)
                    #self.entitiesListName.append('[REDACTEDMISC]')
                    
                                                    
                if re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'ORG' and len(entity.text)>2 :
                # strr= strr+"[REDACTEDORG]"
                    entitiesList.append(entity.text)
                    self.entitiesListName.append('[REDACTEDORG]')
                    
            
        return entitiesList

    def extract_ner(self,line):
        
        i=0
        
        sentence = Sentence(line)
        self.model.predict(sentence)

        for ent in self.merging_entities(sentence) :
            if ent in line:
                line=line.replace(ent,self.entitiesListName[i])
            i=i+1 
        self.entitiesListName=[]

        return line
