from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from csv import writer
import argparse


def append_list_as_row(file_name, list_of_elem):
   with open(file_name,'w') as file:

       for line in list_of_elem:
           file.write(line)
           file.write('\n')

# pour exécuter ce script, il faut un fichier .fdf généré grâce à l'outil Acrobat
def main(argv):

    fdf_file = open(argv+".fdf", 'rb')
    parser = PDFParser(fdf_file)
    doc = PDFDocument(parser)

    fields = resolve1(doc.catalog['FDF'])['Annots']
    row_contents=[]
    for i in fields:
        field = resolve1(i)
        page, b_contents = field.get('Page'), field.get('Contents')
        if b_contents is not None:
            try:
                contents = b_contents.decode("latin1")
                row_contents.append(contents)
                
            except Exception as e:
                pass
    append_list_as_row(argv+'.csv', row_contents)    

    fdf_file.close()
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('src', help='FDF source')
    args = parser.parse_args()
    main(args.src)