import pandas as pd
import re


class ExcelManip:
    def __init__(self, data_file, brands_file='resources/Brands.xlsx'):
        self.data_file = data_file
        self.brands_file = brands_file
        self.brand_names = self._load_brands()

    def _load_brands(self):
        brands_df = pd.read_excel(self.brands_file, dtype=str)
        return brands_df['Brandnames'].str.lower().dropna().tolist()

    # TODO : fix so that it takes multiple integers and add them do a list?
    def _identify_rsk(self, s):
        pattern = r'\b\d{7}\b'
        matches = re.findall(pattern, s)
        modified_str = re.sub(pattern, '', s).strip()
        return modified_str, matches if matches else None

    def _identify_brands(self, input_string):
        for brand in self.brand_names:
            if brand in input_string.lower():
                modified_str = re.sub(brand, '', input_string, flags=re.IGNORECASE).strip()
                return modified_str, brand
        return input_string, None

    def pre_process(self):
        df = pd.read_excel(self.data_file, engine='openpyxl', header=None, dtype=str)
        dict_data = []

        for _, row in df.iterrows():
            row_items = list(map(str, row))
            processed_row = ";".join(filter(lambda item: item != "nan", row_items))

            dictionary = {}

            modified_str_rsk, extracted_value_rsk = self._identify_rsk(processed_row)
            if extracted_value_rsk:
                dictionary['rsk'] = extracted_value_rsk[0] if extracted_value_rsk else None

            modified_str_brands, extracted_value_brands = self._identify_brands(modified_str_rsk)
            if extracted_value_brands:
                dictionary['brand'] = extracted_value_brands

            remaining_items = modified_str_brands.split(';')
            for i, item in enumerate(remaining_items):
                dictionary[f'attribute_{i}'] = item

            dict_data.append(dictionary)

        return dict_data


if __name__ == "__main__":
    manipulator = ExcelManip('../WebCrawler/resources/quality_secured_articles.xlsx')
    result = manipulator.pre_process()

    for dictionary in result:
        if 'rsk' in dictionary:
            if 'brand' in dictionary:
                print("This row has both RSK and Brand.")
                print(f"RSK: {dictionary['rsk']}, Brand: {dictionary['brand']}")
            else:
                print("This row has RSK only.")
                print(f"RSK: {dictionary['rsk']}")
        print("------")