from PyPDF2 import PdfFileReader, PdfFileWriter


def pdf2text(file):
    #file_path = 'files/test.pdf'
    pdf = PdfFileReader(file)

    text = ''

    for page_num in range(pdf.numPages):
        # print('Page: {0}'.format(page_num))
        pageObj = pdf.getPage(page_num)

        try:
            txt = pageObj.extractText()
            # print(''.center(100, '-'))
        except:
            pass
        else:
            text += str(txt.encode("utf-8"))

    return text
