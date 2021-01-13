import re
from flair.data import Sentence
from flair.models import SequenceTagger,  MultiTagger

class POSFilter:
    tagger = MultiTagger.load(['pos-multi'])

    def add_inclusive(self,str1,str2):
        if str1.endswith(str2):
            return str1[:-len(str2)]+"("+str2+")"
        else :
            return str1+"("+str2+")"
   
    def add_inclusive_adj(self,str1,str2,str3):
        if str1.endswith(str2):
            return str1+"("+str3+")"
        elif str1.endswith(str3):
            return str1[:-len(str3)]+str2+"("+str3+")"
    
    def merging_inclusive(self,sentence):
        strr=""
        for entity in sentence.get_spans('pos-multi'):
            
            for data in entity.labels:
                
                if re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'VERB' and len(entity.text)>2 :
                    #[TO DO] Tester avec l'auxiliare qui précède le verbe: si avoir, pas de changement, sinon:
                    if entity.text.endswith("é") or entity.text.endswith("ée"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    elif entity.text.endswith("i") or entity.text.endswith("ie"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    elif entity.text.endswith("is") or entity.text.endswith("ise"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    elif entity.text.endswith("t") or entity.text.endswith("te"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    elif entity.text.endswith("us") or entity.text.endswith("use"): #inclus(e)
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    elif entity.text.endswith("u") or entity.text.endswith("ue"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    else :
                        strr= strr+entity.text+" "
    
                elif re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'VERB' and len(entity.text)<2 :
                    strr= strr+entity.text+" "
            
            
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'ADJ'  :
                    if entity.text.endswith("ien") or entity.text.endswith("ienne"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"ien","ienne")
                    elif  entity.text.endswith("if") or entity.text.endswith("ive"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"if","ive")
                    elif  entity.text.endswith("er") or entity.text.endswith("ère"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"er","ère")
                    elif  entity.text.endswith("ier") or entity.text.endswith("ière"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"ier","ière")
                    elif  entity.text.endswith("on") or entity.text.endswith("onne"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"on","ne")
                    elif  entity.text.endswith("eur") or entity.text.endswith("euse"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"eur","euse")
                    elif  entity.text.endswith("leur") or entity.text.endswith("leure"): #meilleur(e)
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"eur","eure")
                    elif entity.text.endswith("é") or entity.text.endswith("ée"):
                        strr= strr+self.add_inclusive(entity.text,"e")+" "
                    else :
                        strr= strr+entity.text+" "
            
            
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'NOUN'  :                       
                    if entity.text.endswith("teur") or entity.text.endswith("trice"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"teur","trice")
                    elif entity.text.endswith("ieur") or entity.text.endswith("ieure"):
                        strr= strr+" "+self.add_inclusive_adj(entity.text,"eur","eure")
                    elif entity.text.endswith("peur") or entity.text.endswith("peuse"): #développeur(euse)
                        strr= strr+self.add_inclusive_adj(entity.text,"eur","euse")+" "
                    else :
                        strr= strr+" "+entity.text+" "
                                        
                        
                    
                #elif  entity.text == 'la' or entity.text == 'le' or entity.text == 'La' or entity.text == 'Le'  :                    
                    #strr= strr+"le/la"+" "
                elif  entity.text == 'il' or entity.text == 'elle' or entity.text == 'Il' or entity.text == 'Elle'   :                    
                    strr= strr+"il/elle"   +" "             
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'ADP'  :
                    strr= strr+" "+entity.text+" "
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'AUX'  :
                    strr= strr+" "+entity.text+" "
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'DET'  :
                    strr= strr+entity.text  +" "  
                elif  re.sub(r'\([^)]*\)', '', str(data))[:-1] == 'CCONJ'  :
                    strr= strr+" " +entity.text+" "     
                elif  entity.text == '.' or entity.text == ',' :
                    strr= strr+" " +entity.text+" "    
                                                        
                                
                else :
                    strr= strr+" "+entity.text+" "
        
        return self.format_line(self.clean_output(strr))

    def format_line(self,line):
        line=line.replace("_ ", "_")
        line=line.replace("'", " ' ")
        line=line.replace("]", "] ")
        return line


    def clean_output(self,line):
        input_string =line
        output_string = []
        space_flag = False 
        for index in range(len(input_string)):
            if input_string[index] != ' ':
                if space_flag == True:
                    if (input_string[index] == '.'
                            or input_string[index] == '?'
                            or input_string[index] == ','
                            or input_string[index] == '_'
                            or input_string[index] == ']'):
                        pass
                    else:
                        output_string.append(' ')
                    space_flag = False
                output_string.append(input_string[index])
            elif input_string[index - 1] != ' ':
                space_flag = True
        return (''.join(output_string))

    def extract_pos(self,line):
        sentence = Sentence(self.format_line(line))
        self.tagger.predict(sentence)
        return self.merging_inclusive(sentence)