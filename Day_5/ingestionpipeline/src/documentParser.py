from langchain_core.documents import Document
from pypdf import PdfReader
import io

class DocumentParser:
    def __init__(self, fileName, fileContent, department):
        self.fileName: str = fileName
        self.fileContent = fileContent
        self.documents = []
        self.department = department

    def _text_parser(self):
        fileData = self.fileContent.decode('utf-8')
        doc = Document(
            page_content=fileData,
            metadata = {'source':self.fileName, 'department': self.department}
        )
        self.documents.append(doc)

    def _pdf_parser(self):
        file_stream = io.BytesIO(self.fileContent)
        fileData = PdfReader(file_stream)

        for page, content in enumerate(fileData.pages,1):
            pageData = content.extract_text()
            if pageData:
                doc = Document(
                    page_content=pageData,
                    metadata = {'source':self.fileName, 'page':page,'department':self.department}
                )
                self.documents.append(doc)
    
    def parse_document(self):
        if self.fileName.endswith('.pdf'):
            self._pdf_parser()
        elif self.fileName.endswith('.txt'):
            self._text_parser()
        return self.documents
