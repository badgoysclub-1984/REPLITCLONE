"""Code editor component"""

class CodeEditor:
    def __init__(self):
        self.content = ""
    
    def save_file(self, filename, content):
        with open(filename, 'w') as f:
            f.write(content)
    
    def load_file(self, filename):
        with open(filename, 'r') as f:
            return f.read()
