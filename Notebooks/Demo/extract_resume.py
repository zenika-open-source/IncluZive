import pdfminer
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams
from pdfminer.converter import PDFPageAggregator
import pandas as pd 
import numpy as np

class ExtractResume:

    def parse_obj(self,lt_objs,df):

        # loop over the object list
        for obj in lt_objs:

            # if it's a textbox, print text and location
            if isinstance(obj, pdfminer.layout.LTTextBoxHorizontal):
                #print ("%6d, %6d, %s" % (obj.bbox[0], obj.bbox[1], obj.get_text().replace('\n', '_')))
                #new_row = {'x':obj.bbox[0], 'y':obj.bbox[1], 'value':obj.get_text().replace('\n', '_')}
                new_row = {'x':obj.bbox[0], 'y':obj.bbox[1], 'value':obj.get_text()}
                df = df.append(new_row, ignore_index=True)

            # if it's a container, recurse
            elif isinstance(obj, pdfminer.layout.LTFigure):
                self.parse_obj(obj._objs,df)
                
        return df  

    def extract_resume(self,resume_name):
        fp = open(resume_name, 'rb')

        parser = PDFParser(fp)

        # Create a PDF document object that stores the document structure.
        # Password for initialization as 2nd parameter
        document = PDFDocument(parser)

        # Check if the document allows text extraction. If not, abort.
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        # Create a PDF resource manager object that stores shared resources.
        rsrcmgr = PDFResourceManager()

        # Create a PDF device object.
        device = PDFDevice(rsrcmgr)

        # BEGIN LAYOUT ANALYSIS
        # Set parameters for analysis.
        laparams = LAParams()

        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)

        # Create a PDF interpreter object.
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        df = pd.DataFrame( columns = ['x', 'y','value']) 

        # loop over all pages in the document
        for page in PDFPage.create_pages(document):

            # read the page into a layout object
            interpreter.process_page(page)
            layout = device.get_result()

            # extract text from this object
            df=self.parse_obj(layout._objs,df)

        df['bloc']=''
        df['bloc'] = np.where(df['x'].between(0,100), 'L', df['bloc'])

        df['bloc'] = np.where(df['x'].between(101,500), 'R', df['bloc'])

        df_left = df[df['bloc'] == 'L']
        df_right = df[df['bloc'] == 'R']

        df_left=df_left.sort_values("y", ascending=False)
        df_right=df_right.sort_values("y", ascending=False)

        df_left['value'] = df_left['value'].map(lambda x: x.rstrip('\n'))

        df_right['value'] = df_right['value'].map(lambda x: ' '+x)

        df_right = df_right.append(df_right).reset_index().drop_duplicates(subset='index').drop(columns='index')

        df_left = df_left.append(df_left).reset_index().drop_duplicates(subset='index').drop(columns='index')

        return pd.concat([df_right, df_left], ignore_index=True)