import os
from pystardict import Dictionary
import glob

class StarDictManager:
    def __init__(self, dict_dir="backend/dictionaries"):
        self.dict_dir = dict_dir
        self.dictionaries = []
        self.load_dictionaries()

    def load_dictionaries(self):
        self.dictionaries = []
        if not os.path.exists(self.dict_dir):
            print(f"Dictionary directory not found: {self.dict_dir}")
            return

        # Find all .ifo files
        ifo_files = glob.glob(os.path.join(self.dict_dir, "*.ifo"))
        
        for ifo_path in ifo_files:
            try:
                # pystardict expects the path without extension
                dict_prefix = os.path.splitext(ifo_path)[0]
                dictionary = Dictionary(dict_prefix)
                self.dictionaries.append(dictionary)
                print(f"Loaded dictionary: {os.path.basename(dict_prefix)}")
            except Exception as e:
                print(f"Failed to load dictionary {ifo_path}: {e}")

    def lookup(self, word):
        """
        Look up a word in all loaded dictionaries.
        Returns the first definition found, or None.
        """
        for dictionary in self.dictionaries:
            try:
                if word in dictionary:
                    # Get the definition (it might be bytes or string depending on the file)
                    definition = dictionary[word]
                    
                    # pystardict usually returns the raw data. 
                    # If it's HTML/Text, we might need to clean it.
                    # For now, let's assume it's a string or decode it.
                    if isinstance(definition, bytes):
                        try:
                            definition = definition.decode('utf-8')
                        except:
                            pass
                            
                    return str(definition)
            except Exception as e:
                print(f"Error looking up '{word}': {e}")
                continue
                
        return None
