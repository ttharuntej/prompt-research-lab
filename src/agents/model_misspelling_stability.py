from typing import Dict, List, Optional, Union, Tuple
from enum import Enum
import random
from config import settings

SEVERITY_MAPPING = {
    "light": 0.1,
    "medium": 0.2,
    "severe": 0.4
}

class MisspellingStrategy(Enum):
    RANDOM_CHAR = "random_char"
    COMMON_TYPOS = "common_typos"
    KEYBOARD_PROXIMITY = "keyboard_proximity"

class MisspellingGenerator:
    def __init__(self):
        # Common keyboard-proximity typos
        self.keyboard_proximity = {
            'a': 'qwsz', 'b': 'vghn', 'c': 'xdfv', 'd': 'srfce',
            'e': 'wrsdf', 'f': 'dcvgt', 'g': 'fvbht', 'h': 'gbnjy',
            'i': 'ujko', 'j': 'huknm', 'k': 'jilm', 'l': 'kop',
            'm': 'njk', 'n': 'bhjm', 'o': 'iklp', 'p': 'ol',
            'q': 'wa', 'r': 'edft', 's': 'awdzx', 't': 'rfgy',
            'u': 'yihj', 'v': 'cfgb', 'w': 'qase', 'x': 'zsdc',
            'y': 'tghu', 'z': 'asx'
        }
        
        # Common typos/misspellings
        self.common_typos = {
            'the': ['teh', 'hte', 'th'],
            'and': ['adn', 'nad', 'an'],
            'to': ['too', 'tp', 't'],
            'of': ['fo', 'ff', 'f'],
            'in': ['ni', 'inn', 'n'],
            'that': ['taht', 'tht', 'tha'],
            'is': ['si', 'iz', 'i'],
            'for': ['fro', 'fr', 'fo']
        }

        self.severity = SEVERITY_MAPPING.get(
            settings.MISSPELLING_SEVERITY.lower(), 
            0.2  # default to medium if unknown
        )

    def generate_variant(
        self, 
        text: str, 
        severity: Union[float, str] = None,
        strategy: MisspellingStrategy = MisspellingStrategy.RANDOM_CHAR,
        return_changes: bool = False
    ) -> Union[str, Tuple[str, int]]:
        """
        Generate a misspelled variant of the input text
        
        Args:
            text: Input text to modify
            severity: How severe the misspellings should be (0.0 to 1.0)
            strategy: Which misspelling strategy to use
            return_changes: Whether to return the count of changed characters
            
        Returns:
            If return_changes is False: misspelled text
            If return_changes is True: tuple of (misspelled text, number of changes)
        """
        # Use provided severity or instance default
        use_severity = (
            SEVERITY_MAPPING.get(severity.lower(), 0.2) 
            if isinstance(severity, str) 
            else severity if isinstance(severity, float)
            else self.severity
        )
        
        misspelled_text = ""
        char_changes = 0
        
        for char in text:
            if random.random() < use_severity and char.isalpha():
                misspelled_text += random.choice('abcdefghijklmnopqrstuvwxyz')
                char_changes += 1
            else:
                misspelled_text += char
                
        if return_changes:
            return misspelled_text, char_changes
        return misspelled_text
