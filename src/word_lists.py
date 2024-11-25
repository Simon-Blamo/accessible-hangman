from word_grade_classifier import WordGradeClassifier
import json

class WordLists:
    def __init__(self):
        self.classifier = WordGradeClassifier()
        self.custom_words = set()
        # Initialize grade levels from the classifier's loaded data
        self.grade_levels = {}
        self.load_or_create_word_lists()

    def load_or_create_word_lists(self):
        """Initialize or load existing word lists"""
        # Load the grade-level words from the classifier
        self.grade_levels = self.classifier.load_grade_levels()
        
        # Convert lists to sets for faster lookup
        for grade in self.grade_levels:
            self.grade_levels[grade] = set(word.upper() for word in self.grade_levels[grade])
        
        # Load custom words
        try:
            self.custom_words = self.load_custom_words()
            # Add custom words to appropriate grade levels
            for word in self.custom_words:
                grade = self.classifier.assign_grade_level(word)
                if grade in self.grade_levels:
                    self.grade_levels[grade].add(word.upper())
        except (FileNotFoundError, json.JSONDecodeError):
            self.save_custom_words()

        # Print debug information
        for grade, words in self.grade_levels.items():
            print(f"Grade {grade}: {len(words)} words loaded")

    def get_words_by_grade(self, grade):
        """Get all words for a specific grade level."""
        words = self.grade_levels.get(str(grade), set())
        if not words:
            # If no words are found, try to reload from classifier
            self.grade_levels = self.classifier.load_grade_levels()
            words = set(word.upper() for word in self.grade_levels.get(str(grade), []))
            print(f"Reloaded words for grade {grade}: {len(words)} words found")
        return words

    def load_custom_words(self):
        """Load custom words from JSON file with error handling"""
        try:
            with open('custom_words.json', 'r') as f:
                content = f.read().strip()
                if not content:  # If file is empty
                    return set()
                return set(json.loads(content))
        except FileNotFoundError:
            return set()
        except json.JSONDecodeError:
            print("Warning: Custom words file is corrupted. Creating new file.")
            return set()

    def save_custom_words(self):
        """Save custom words to JSON file"""
        with open('custom_words.json', 'w') as f:
            json.dump(list(self.custom_words), f)

    def add_custom_word(self, word):
        """Add a new custom word"""
        word = word.strip().upper()
        if word:
            self.custom_words.add(word)
            self.save_custom_words()
            # Update grade levels
            grade = self.classifier.assign_grade_level(word)
            if grade in self.grade_levels:
                self.grade_levels[grade].add(word)

    def remove_custom_word(self, word):
        """Remove a custom word"""
        word = word.strip().upper()
        if word in self.custom_words:
            self.custom_words.remove(word)
            self.save_custom_words()
            # Update grade levels
            for grade_words in self.grade_levels.values():
                grade_words.discard(word)