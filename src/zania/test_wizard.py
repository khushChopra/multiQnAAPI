import unittest
import os
from .wizard import AnsweringWizard
OPEN_API_KEY = os.environ.get("OPEN_API_KEY")

class TestAnsweringWizard(unittest.TestCase):
    def test_allow_only_pdf_and_json_document(self):
        self.assertRaises(ValueError, lambda: AnsweringWizard("doc.docx", "questions.json", "openai_key"))

    def test_json_document(self):
        wizard = AnsweringWizard("../misc/doc.json", "../misc/que.json", OPEN_API_KEY)
        self.assertEqual(wizard.get_document_json()[0].page_content, "Webpack")

    def test_json_questions(self):
        wizard = AnsweringWizard("../misc/doc.json", "../misc/que.json", OPEN_API_KEY)
        ques = wizard.get_questions_json()
        self.assertEqual(ques[0].page_content, "What is the candidates name?")
        self.assertEqual(ques[1].page_content, "What is his experience with Python")

    def test_pdf_questions(self):
        wizard = AnsweringWizard("../misc/doc.json", "../misc/questions.pdf", OPEN_API_KEY)
        ques = wizard.questions
        self.assertEqual(len(ques), 5)

if __name__ == '__main__':
    unittest.main()
