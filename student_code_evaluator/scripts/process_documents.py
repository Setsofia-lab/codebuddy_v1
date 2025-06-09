import os
import fitz  # PyMuPDF
import nbformat

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
    return text

def extract_code_from_ipynb(ipynb_path):
    """Extracts code from code cells in an iPython Notebook."""
    code = ""
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                code += cell.source + "\n"
    except Exception as e:
        print(f"Error reading iPython Notebook {ipynb_path}: {e}")
    return code

def read_text_file(file_path):
    """Reads text from a plain text file."""
    text = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading text file {file_path}: {e}")
    return text

def process_documents_in_directory(directory_path):
    """Processes all supported document types in a directory and returns their content."""
    documents = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.pdf'):
                text = extract_text_from_pdf(file_path)
                if text:
                    documents.append({'filename': file, 'content': text, 'type': 'pdf'})
            elif file.endswith('.py') or file.endswith('.txt'):
                text = read_text_file(file_path)
                if text:
                    documents.append({'filename': file, 'content': text, 'type': 'text'})
            elif file.endswith('.ipynb'):
                code = extract_code_from_ipynb(file_path)
                if code:
                    documents.append({'filename': file, 'content': code, 'type': 'ipynb'})
    return documents

if __name__ == '__main__':
    # Example usage:
    # Create a dummy data directory and files for testing
    if not os.path.exists('test_data'):
        os.makedirs('test_data')
    with open('test_data/sample.txt', 'w') as f:
        f.write("This is a sample text file.")
    with open('test_data/sample.py', 'w') as f:
        f.write("print('Hello, world!')")
    # Create a dummy ipynb file (minimal structure)
    ipynb_content = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": "a = 1\nb = 2\nprint(a + b)"
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": "# This is a markdown cell"
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    with open('test_data/sample.ipynb', 'w') as f:
        nbformat.write(ipynb_content, f)

    # Note: To test PDF reading, you would need a sample.pdf file in test_data

    print("Processing documents in 'test_data':")
    processed_docs = process_documents_in_directory('test_data')
    for doc in processed_docs:
        print(f"--- {doc['filename']} ({doc['type']}) ---")
        print(doc['content'])
        print("-" * 20)

    # Clean up dummy files
    os.remove('test_data/sample.txt')
    os.remove('test_data/sample.py')
    os.remove('test_data/sample.ipynb')
    os.rmdir('test_data')
