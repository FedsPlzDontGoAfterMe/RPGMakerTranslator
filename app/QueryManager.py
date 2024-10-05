#data: 
# [{
#     'json_file': json_file, # File path
#     'num_texts': len(texts_to_translate), # Number of texts to translate
#     'texts': [{'id': index,'orig': text,'trans': ''}] for index, text in enumerate(texts_to_translate)), # List of texts to translate
#     'data': data  # Original Json
# }]

class QueryManager:
    def load_dataset(self, texts:list, ignore_translated, search_text: str, red_flag: bool, yellow_flag: bool, green_flag: bool):
        """Load the dataset and filter the texts based on the search criteria. Basically query the dataset."""
        filtered_texts = []
        allowed_colors = ["red" if red_flag else "", "yellow" if yellow_flag else "", "green" if green_flag else ""]
        for text in texts:
            if ignore_translated and text['trans']:
                continue 
            # check if the search text is in the original text, translated text, or id
            # and if the color is in the allowed colors
            if (search_text.lower() in text['orig'].lower() or search_text.lower() in text['trans'].lower() or search_text.lower() in text['key'].lower()
                or search_text in str(text['id']) and 'color' in text and text['color'] in allowed_colors):
                filtered_texts.append(text)
        self.texts = filtered_texts
            
    def get_texts(self, start_index, num_texts):
        """Get texts from the query result."""
        if start_index < 0:
            start_index = 0
        end_index = len(self.texts) if start_index + num_texts > len(self.texts) else start_index + num_texts
        # Input validation then return the texts and the start and end index
        # I know that the input validation is not necessary, i dont care.
        return self.texts[start_index:end_index], start_index, end_index
    
    def update_texts(self, start_index, end_index, translation):
        """Update the translation of the texts in the query result"""
        for i in range(start_index, end_index):
            self.texts[i]['trans'] = translation[i - start_index]
        