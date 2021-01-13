from regex_filter import RegexFilter
from pos_filter_flair import POSFilter
from ner_filter_flair import NERFilter
import pandas as pd

class AnonymizeResume:

    filtre1 = RegexFilter()
    filtre2 = POSFilter()
    filtre3 = NERFilter()

        
    def anonymize_resume(self,df):
        list_Anonym = list()

     

        for i in df['value']:
            list_Anonym.append(self.filtre3.extract_ner(self.filtre2.extract_pos(self.filtre1.extract_regex(str(i)))))
        return list_Anonym