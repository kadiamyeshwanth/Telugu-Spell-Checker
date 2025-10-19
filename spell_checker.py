# spell_checker.py (Enhanced with CLI Menu)

import json
import re
from collections import Counter
from itertools import chain
import sys


TELUGU_ALPHABET = 'అఆఇఈఉఊఋౠఎఏఐఒఓఔంఃకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళక్షఱ'

def edits1(word):
    """Generates all possible corrections that are one edit away from the word."""
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    # Restrict generation to only use the Telugu alphabet
    replaces = [L + c + R[1:] for L, R in splits if R for c in TELUGU_ALPHABET]
    inserts = [L + c + R for L, R in splits for c in TELUGU_ALPHABET]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """Generates all possible corrections that are two edits away from the word."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


class SpellChecker:
    def __init__(self, model_path):
        """Loads the word frequency index (Language Model) from secondary memory (JSON file) into main memory."""
        self.model_path = model_path
        print(f"Loading word model from {model_path}...")
        try:
            with open(model_path, 'r', encoding='utf-8') as f:
                self.WORDS = Counter(json.load(f))
            self.TOTAL_WORDS = sum(self.WORDS.values())
            print(f"✅ Model loaded with {len(self.WORDS)} unique words.")
        except FileNotFoundError:
            print(f"❌ Error: Model file not found at {model_path}. Please run build_model.py first.")
            self.WORDS = Counter()
            self.TOTAL_WORDS = 0
            
        self.source_document = None 
        self.candidates_map = {} 

    def known(self, words):
        """Returns the subset of `words` that appear in the language model."""
        return set(w for w in words if w in self.WORDS)

    def get_candidates(self, word):
        """
        Generates and ranks probable candidates.
        Ranking is based on: 1) Minimal edit distance, 2) Word frequency (semantics).
        """
        
        candidates = self.known([word]) 
        
        candidates.update(self.known(edits1(word)))
        
        if not candidates and word not in self.WORDS: 
             candidates.update(self.known(set(edits2(word))))

        if not candidates:
            return [(word, 0)] 

        ranked_candidates = sorted(
            [(c, self.WORDS.get(c, 0)) for c in candidates],
            key=lambda item: item[1],
            reverse=True
        )

        return ranked_candidates
    
    def correct_word(self, word):
        """
        Selects the single best correction for a word.
        Returns the best correction word and the list of (candidate, frequency) tuples.
        """
        ranked_candidates = self.get_candidates(word)
        
        best_correction, _ = ranked_candidates[0]
        
        return best_correction, ranked_candidates
    
    def correct_text(self, text):
        """
        Processes a full text. Stores the source document and a map of candidates 
        for misspelled words in main memory.
        """
        self.source_document = text
        self.candidates_map = {} 

        parts = re.findall(r'([\u0C00-\u0C7F]+|\W+)', text, re.UNICODE) 
        
        corrected_parts = []
        
        for part in parts:
            if re.match(r'[\u0C00-\u0C7F]+', part, re.UNICODE): 
                word = part
                
                best_correction, candidates_with_freq = self.correct_word(word)
                
                if best_correction != word:
                    corrected_parts.append(best_correction)
                    self.candidates_map[word] = [c for c, f in candidates_with_freq]
                else:
                    corrected_parts.append(word)
            else:
                corrected_parts.append(part)

        corrected_sentence = "".join(corrected_parts)
        
        return corrected_sentence, self.candidates_map



def run_test_cases(checker):
    """Runs the 5 predefined test cases."""
    test_cases = [
        # 1. Misspelled: మహాన, దేసం, బాష
        ("భారత్ ఒక మహాన దేసం. ఇక్కడ తెలుగు బాష మాట్లాడతారు.", "మహాన, దేసం, బాష (Great country language)"), 
        # 2. Misspelled: సహాసయం
        ("రాముడు అతనికి సహాసయం చేసాడు.", "సహాసయం (Help/Assistance)"),
        # 3. Misspelled: చదువకునాడు
        ("పుస్తకం చదువకునాడు.", "చదువకునాడు (Studied/Read)"),
        # 4. Misspelled: అందగా
        ("ఆమె పాటలు అందగా పాడింది.", "అందగా (Beautifully)"),
        # 5. Misspelled: కంటెకన్నా, ముఖయం
        ("ప్రపంచంలో కంటెకన్నా కమ్యూనికేషన్ చాలా ముఖయం.", "కంటెకన్నా, ముఖయం (Than, Important)")
    ]
    
    print("\n" + "=" * 70)
    print("✨ Running Predefined Test Cases (5/5) ✨")
    print("=" * 70)

    for i, (text, note) in enumerate(test_cases, 1):
        corrected_text, candidates_map = checker.correct_text(text)

        print("\n" + "---" * 23)
        print(f"Test Case {i}: (Focus: {note})")
        print("---" * 23)
        print("👉 Original Text:  ", text)
        print("✅ Corrected Text: ", corrected_text)
        
        if candidates_map:
            print("\n🔍 Corrections/Candidates:")
            for misspelled, candidates in candidates_map.items():
                display_candidates = ", ".join(candidates[:3]) + ("..." if len(candidates) > 3 else "")
                print(f"  '{misspelled}' -> Best: '{candidates[0]}', Other Top Candidates: {display_candidates}")
        else:
            print("\n🎉 No corrections were needed for this text.")
        print("---" * 23)

def run_custom_check(checker):
    """Prompts user for custom text and runs the spell checker."""
    print("\n" + "#" * 70)
    print("✍️ Custom Text Spell Check")
    print("#" * 70)
    print("Enter the Telugu text you want to check (or type 'back' to return to menu):")
    
    custom_text = input("Text: ").strip()
    
    if not custom_text or custom_text.lower() == 'back':
        return

    print("\n🔎 Processing text...")
    corrected_text, candidates_map = checker.correct_text(custom_text)

    print("\n" + "-" * 70)
    print("   Spell Check Results")
    print("-" * 70)
    print("👉 Original Text:  ", custom_text)
    print("✅ Corrected Text: ", corrected_text)
    
    if candidates_map:
        print("\n🔍 Corrections/Candidates:")
        for misspelled, candidates in candidates_map.items():
            display_candidates = ", ".join(candidates[:3]) + ("..." if len(candidates) > 3 else "")
            print(f"  '{misspelled}' -> Best: '{candidates[0]}', Other Top Candidates: {display_candidates}")
    else:
        print("\n🎉 No corrections were needed or found.")
    print("-" * 70)
    input("\nPress Enter to continue...") # Pause for better user experience


def main_menu(checker):
    """Handles the main application loop and menu."""
    while True:
        print("\n" + "=" * 50)
        print("  📚 Telugu Spell Checker Main Menu")
        print("=" * 50)
        print("1. Run 5 Predefined Test Cases")
        print("2. Enter Custom Text for Spell Check")
        print("3. Exit Application")
        print("=" * 50)

        choice = input("Enter your choice (1, 2, or 3): ").strip()

        if choice == '1':
            run_test_cases(checker)
        elif choice == '2':
            run_custom_check(checker)
        elif choice == '3':
            print("\n👋 Thank you for using the Telugu Spell Checker. Exiting...")
            sys.exit(0)
        else:
            print("\n⚠️ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    MODEL_PATH = 'telugu_word_model.json'

    checker = SpellChecker(MODEL_PATH)
    
    if checker.TOTAL_WORDS > 0:
        main_menu(checker)