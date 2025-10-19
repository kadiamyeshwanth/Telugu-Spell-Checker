# Telugu Spell Checker - README

## Project Overview
A Telugu language spell checker that identifies misspelled words and provides ranked correction suggestions based on edit distance and word frequency.

---

## Dataset
**Source:** Telugu Wikipedia XML Dump  
**Download:** https://dumps.wikimedia.org/tewiki/latest/tewiki-latest-pages-articles.xml.bz2

---

## Requirements
- Python 3.7 or higher
- Standard Python libraries only (no external packages needed)
- 4GB RAM minimum
- 2-5GB disk space

---

## How to Run

### Step 1: Build the Language Model
```bash
python build_model.py
```
This creates `telugu_word_model.json` from the Wikipedia XML dump (takes 10-30 minutes).

### Step 2: Run Spell Checker
```bash
python spell_checker.py
```

### Menu Options:
1. **Run 5 Predefined Test Cases** - Automatically tests with sample Telugu text
2. **Enter Custom Text** - Check your own Telugu text for spelling errors
3. **Exit** - Close the application

---

## Module Descriptions

### 1. build_model.py
**Purpose:** Builds word frequency model from Wikipedia data

**Key Functions:**
- `tokenize(text)` - Extracts Telugu words using Unicode range [\u0C00-\u0C7F]
- `build_model(xml_path, output_path)` - Parses XML, counts word frequencies, saves to JSON

**Process:**
- Uses iterative XML parsing for memory efficiency
- Counts Telugu word frequencies
- Stores language model in JSON format on hard drive (secondary memory)

### 2. spell_checker.py
**Purpose:** Performs spell checking and correction

**Key Components:**

**Error Model:**
- `edits1(word)` - Generates words with 1 edit distance (deletion, transposition, replacement, insertion)
- `edits2(word)` - Generates words with 2 edit distance

**SpellChecker Class:**
- `__init__(model_path)` - Loads word frequency index from secondary memory (JSON) to main memory
- `known(words)` - Filters words that exist in vocabulary
- `get_candidates(word)` - Generates and ranks corrections by edit distance and frequency
- `correct_word(word)` - Returns best correction for a single word
- `correct_text(text)` - Corrects full text, stores source document and candidates map in main memory

---

## Algorithm

Uses **Noisy Channel Model** approach:
1. Check if word exists (edit distance = 0)
2. Generate candidates with edit distance = 1
3. If no candidates, generate edit distance = 2
4. Filter candidates that exist in vocabulary
5. Rank by word frequency (higher frequency = more likely correct)
6. Return best candidate

**Edit Operations:** Deletion, Insertion, Substitution, Transposition

---

## Test Cases & Results

### Test Case 1: Multiple Misspellings
**Original:** భారత్ ఒక మహాన దేసం. ఇక్కడ తెలుగు బాష మాట్లాడతారు.  
**Corrected:** భారత్ ఒక మహాన దేశం. ఇక్కడ తెలుగు భాష మాట్లాడతారు.  
**Corrections:** దేసం→దేశం, బాష→భాష

### Test Case 2: Single Word Error
**Original:** రాముడు అతనికి సహాసయం చేసాడు.  
**Corrected:** రాముడు అతనికి సహాయం చేసాడు.  
**Corrections:** సహాసయం→సహాయం

### Test Case 3: Verb Misspelling
**Original:** పుస్తకం చదువకునాడు.  
**Corrected:** పుస్తకం చదువుకున్నాడు.  
**Corrections:** చదువకునాడు→చదువుకున్నాడు

### Test Case 4: Adverb Correction
**Original:** ఆమె పాటలు అందగా పాడింది.  
**Corrected:** ఆమె పాటలు అందంగా పాడింది.  
**Corrections:** అందగా→అందంగా

### Test Case 5: Multiple Errors
**Original:** ప్రపంచంలో కంటెకన్నా కమ్యూనికేషన్ చాలా ముఖయం.  
**Corrected:** ప్రపంచంలో కంటే కమ్యూనికేషన్ చాలా ముఖ్యం.  
**Corrections:** కంటెకన్నా→కంటే, ముఖయం→ముఖ్యం

---

## Memory Management

**Secondary Memory (Hard Drive):**
- `telugu_word_model.json` - Complete word frequency index stored as JSON file

**Main Memory (RAM):**
- `self.WORDS` - Word frequency dictionary loaded from JSON
- `self.source_document` - Original text being checked
- `self.candidates_map` - Dictionary of misspelled words → candidate corrections

**Efficiency:**
- Model built using streaming XML parser (iterparse) to avoid loading entire file
- Language model loaded once and reused for all corrections
- Candidates generated on-demand

---

## File Structure
```
project/
├── build_model.py          # Model building script
├── spell_checker.py        # Spell checking script
├── telugu_word_model.json  # Generated language model
└── tewiki-latest-pages-articles.xml  # Wikipedia dump (download separately)
```

---

## References
- Peter Norvig's Spelling Corrector: http://norvig.com/spell-correct.html
- Telugu Wikipedia: https://dumps.wikimedia.org/tewiki/
- Telugu Unicode: U+0C00 to U+0C7F

---

## Project Information
**Course:** Information Retrieval (M2025)  
**Assignment:** A1 - Spell Checker  
**Author:** Yeshwanth Kadiam  
**Roll Number:** S20230010111  

---

**Declaration:** This is my original work. All sources have been properly acknowledged.
