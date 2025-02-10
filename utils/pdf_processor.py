import PyPDF2
import spacy

class PDFProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
    
    def extract_text(self, pdf_file):
        text = ""
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def process_text(self, text):
        doc = self.nlp(text)
        return " ".join([token.lemma_.lower() for token in doc 
                        if token.is_alpha and not token.is_stop])
