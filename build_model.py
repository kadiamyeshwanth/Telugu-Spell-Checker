import re
from collections import Counter
import json
import xml.etree.ElementTree as ET
import sys

def tokenize(text):
    """Extracts Telugu words from a given text (Unicode range \u0C00-\u0C7F)."""
    if not text:
        return []
    return re.findall(r'[\u0C00-\u0C7F]+', text, re.UNICODE)


def build_model(xml_path, output_path='telugu_word_model.json'):
    """
    Parses a Wikipedia XML dump using a memory-efficient iterative parser,
    tokenizes the text, counts word frequencies, and saves the model.
    """
    word_counts = Counter()
    print(f"Parsing XML file from: {xml_path} using an iterative parser.")

    try:
        context = ET.iterparse(xml_path, events=("start", "end"))

        event, root = next(context)

        namespace = root.tag.split('}')[0].strip('{')
        text_path = f'./{{{namespace}}}revision/{{{namespace}}}text' 

        page_count = 0
        for event, elem in context:
            if event == 'end' and elem.tag == f'{{{namespace}}}page':
                text_element = elem.find(text_path)
                if text_element is not None and text_element.text:
                    words = tokenize(text_element.text)
                    word_counts.update(words)

                page_count += 1
                if page_count % 5000 == 0:
                    print(f"Processed {page_count} pages...")

                root.clear()

        print(f"\nProcessing complete. Processed a total of {page_count} pages.")
        print(f"Model created with {len(word_counts)} unique words.")

        print(f"Saving model to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dict(word_counts), f, ensure_ascii=False, indent=4)
            
    except FileNotFoundError:
        print(f"Error: XML file not found at {xml_path}. Please check the path.")
    except Exception as e:
        print(f"An error occurred during parsing: {e}")

if __name__ == "__main__":
    WIKI_XML_PATH = 'tewiki-latest-pages-articles.xml' 
    build_model(WIKI_XML_PATH)