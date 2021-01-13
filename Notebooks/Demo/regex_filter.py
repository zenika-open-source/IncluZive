import re

class RegexFilter:

    def extract_email(self, line) :
        line = re.sub(r'[\w\.-]+@[\w\.-]+', " [redacted_email] ", line)
        return line 

    def extract_date(self, line) :
        line = re.sub('(0[1-9]|[12][0-9]|3[01])[- /.](0[1-9]|1[012])[- /.](19|20)\d\d', " [redacted_date] ", line)
        return line 

    def extract_num_so_sec(self, line) :
        line = re.sub(r'\d\s*\d{2}\s*\d{2}\s*\d{2}\s*\d{3}\s*\d{3}', " [redacted_num_sec_so] ", line)
        return line

    def extract_single_date(self, line) :
        line = re.sub(r' ([0-9][0-9][0-9][0-9] )|(\s*\d{4}-\d{4}\s*)', " [redacted_s_date] ", line)
        return line

    def extract_time_period(self, line) :
        line = re.sub(r'\s*[0-99\s-]*?\s+(ans|mois)', " [redacted_time_period] ", line)
        return line

    def extract_enfants(self, line) :
        line = re.sub(r'\s*([0-99\s]*?)\s*enfants', " [redacted_enfants] ", line)
        return line

    def extract_sit_fam(self, line) :
        line = re.sub(r'mariée|marié|pacsée|pacsé|divorcée|divorcé|séparée|séparé|célibataire|Mariée|Marié|Pacsée|Pacsé|Divorcée|Divorcé|Séparée|Séparé|Célibataire', " [redacted_sit_fam] ", line)
        return line

    def extract_sexe(self, line) :
        line = re.sub(r'((\s)(\()*(Féminin)(\))*(\s))|((\s)(\()*(Masculin)(\))*(\s))', " [redacted_sexe] ", line)
        return line

    def extract_sexe_abrev(self, line) :
        line = re.sub(r'((\s)(\()*(F)(\))*(\s))|((\s)(\()*(M)(\))*(\s))', " [redacted_sexe_abrev] ", line)
        return line

    def extract_tel(self, line) :
        line = re.sub(r'\+*\(\+*\s*\d{3}\s*\)\s*\d{2,5}[-\.\s]??\d{2,4}[-\.\s]??\d{3,4}', " [redacted_tel] ", line)
        return line

    def extract_url(self, line) :
        line = re.sub(r'(?P<url>https?://[^\s]+)', " [redacted_url] ", line)
        return line

    def extract_language(self, line) :
        line = re.sub(r'Mandarin|MANDARIN|Hindi|HINDI|Espagnol|ESPAGNOL|Arabe|ARABE|Bengali|BENGALI|Russe|RUSSE|Portugais|PORTUGAIS|Indonésien|INDONESIEN|Urdu|URDU|Allemand|ALLEMAND|Japonais|JAPONAIS|Swahili|SWAHILI|Marathi|MARATHI|Télougou|TELOUGOU|Punjabi|PUNJABI|Chinois Wu|CHINOIS WU|Tamoul|TAMOUL|Turc|TURC|Roumain|ROUMAIN|Italien|ITALIEN|Chinois|CHINOIS', " [redacted_language] ", line)
        return line

    def extract_regex(self,line) :
        return self.extract_language(self.extract_email(self.extract_date(self.extract_num_so_sec(self.extract_single_date(self.extract_time_period(self.extract_enfants(self.extract_sit_fam(self.extract_sexe(self.extract_sexe_abrev(self.extract_url(self.extract_tel(line))))))))))))

