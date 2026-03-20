"""Tests for code editor"""
import unittest
from src.editor.editor import CodeEditor

class TestCodeEditor(unittest.TestCase):
    def setUp(self):
        self.editor = CodeEditor()
    
    def test_save_file(self):
        self.editor.save_file('test.py', 'print("hello")')
        content = self.editor.load_file('test.py')
        self.assertEqual(content, 'print("hello")')

if __name__ == '__main__':
    unittest.main()