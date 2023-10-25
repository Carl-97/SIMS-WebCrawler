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

    def _identify_brands(self, input_string):
        for brand in self.brand_names:
            if brand in input_string.lower():
                modified_str = re.sub(brand, '', input_string, flags=re.IGNORECASE).strip()
                return modified_str, brand
        return input_string, None

    @staticmethod
    def _identify_rsk(s):
        pattern = re.compile(r'\b\d{7}\b')
        matches = pattern.findall(s)
        modified_str = pattern.sub('', s).strip()
        return modified_str, matches if matches else None

    @staticmethod
    def _identify_column(row, column_name):
        if column_name in row.index:
            value = row[column_name]
            if not pd.isna(value):
                modified_row = row.copy()
                modified_row[column_name] = None  # Remove value from the copied row
                return modified_row, value
        return row, None

    @staticmethod
    def clean_row(row):
        cleaned_items = [str(item) if not pd.isna(item) else '' for item in row]
        return ";".join(cleaned_items)

    def pre_process(self):
        df = pd.read_excel(self.data_file, engine='openpyxl', header=0, dtype=str)
        dict_data = []

        for _, row in df.iterrows():
            modified_row, extracted_article_nr = self._identify_column(row, 'Artikelnummer')
            modified_row, extracted_type_desc = self._identify_column(modified_row, 'Typbeteckning')
            modified_row = self.clean_row(modified_row)

            modified_row, extracted_value_rsk = self._identify_rsk(modified_row)
            modified_row, extracted_value_brands = self._identify_brands(modified_row)

            remaining_items = modified_row.split(';')
            remaining_attributes = {f'attribute_{i}': item for i, item in enumerate(remaining_items)}

            dictionary = {
                'id': extracted_value_rsk[0] if extracted_value_rsk else None,
                'brand': extracted_value_brands if extracted_value_brands else None,
                'article_id': extracted_article_nr if extracted_article_nr else None,
                'type_desc': extracted_type_desc if extracted_type_desc else None
            }

            # Merge the dictionaries
            dictionary.update(remaining_attributes)

            dict_data.append(dictionary)

        return dict_data


if __name__ == "__main__":
    manipulator = ExcelManip('../resources/ifm_10.xlsx')
    result = manipulator.pre_process()

    # print all data in dictionary
    for dictionary in result:
        print(dictionary)
