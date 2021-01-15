import re

class RegexFilter:

    def patterns(self):
        pattern_list = [r'[\w\.-]+@[\w\.-]+',   #extract_email
                        r'(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d',   #extract_date
                        r'\d\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{3}\s*\d{3}',  #extract_num_so_sec
                        r' ([0-9][0-9][0-9][0-9] )|(\s*\d{4}-\d{4}\s*)',    #extract_single_date
                        r'\s*[0-99\s-]*?\s+(ans|mois)', #extract_time_period
                        r'\s*([0-99\s]*?)\s*enfants',   #extract_enfants
                        r'[Mm]arié(e?)|[Pp]acsé(e?)|[Dd]ivorcé(e?)|[Ss]éparé(e?)|[Cc]élibataire',   #extract_sit_fam
                        r'((\s)(\()*(Féminin)(\))*(\s))|((\s)(\()*(Masculin)(\))*(\s))', #extract_sexe
                        r'((\s)(\()*(F)(\))*(\s))|((\s)(\()*(M)(\))*(\s))', #extract_sexe_abrev                       
                        r'\+*\(\+*\s*\d{3}\s*\)\s*\d{2,5}[-\.\s]??\d{2,4}[-\.\s]??\d{3,4}', #extract_tel
                        r'^\d*[.]\d*[.]?\d*[.]?\d*[.]?\d*',  #extract_tel
                        r'\+*\d{2}[\s]??\d{1}[\s]??\d{2}[\s]??\d{2}[\s]??\d{2}[\s]??\d{2}',  #extract_tel
                        r'^\(\+\d*\)\s\d*[.,]\d*[.,]?\d*[.,]?\d*[.,]?\d*',   #extract_tel
                        r'(?P<url>https?://[^\s]+)',    #extract_url
                        r'Mandarin|MANDARIN|Hindi|HINDI|Espagnol|ESPAGNOL|Arabe|ARABE|Bengali|BENGALI|Russe|RUSSE|Portugais|PORTUGAIS|Indonésien|INDONESIEN|Urdu|URDU|Allemand|ALLEMAND|Japonais|JAPONAIS|Swahili|SWAHILI|Marathi|MARATHI|Télougou|TELOUGOU|Punjabi|PUNJABI|Chinois Wu|CHINOIS WU|Tamoul|TAMOUL|Turc|TURC|Roumain|ROUMAIN|Italien|ITALIEN|Chinois|CHINOIS|Kabyle|KABYLE'    #xtract_language
                        ]
        return pattern_list