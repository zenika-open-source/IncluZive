from regex_filter import RegexFilter
from pos_filter_flair import POSFilter
from ner_filter_flair_camembert import NERFilter
import pandas as pd

class AnonymizeResume:

    def anonymize_resume(self,df):
        list_Anonym = list()

        filtre1 = RegexFilter()
        filtre2 = POSFilter()
        filtre3 = NERFilter()

        

        for i in df['value']:
            list_Anonym.append(filtre3.extract_ner(filtre2.extract_pos(filtre1.extract_regex(str(i)))))
        return list_Anonym