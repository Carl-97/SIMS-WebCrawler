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

    # TODO : fix so that it takes multiple integers and add them do a list?
    @staticmethod
    def _identify_rsk(s):
        pattern = re.compile(r'\b\d{7}\b')
        matches = pattern.findall(s)
        modified_str = pattern.sub('', s).strip()
        return modified_str, matches if matches else None

    def pre_process(self):
        df = pd.read_excel(self.data_file, engine='openpyxl', header=0, dtype=str)
        dict_data = []

        for _, row in df.iterrows():
            row_items = list(map(str, row))
            processed_row = ";".join(filter(lambda item: item != "nan", row_items))

            modified_str_rsk, extracted_value_rsk = self._identify_rsk(processed_row)
            modified_str_brands, extracted_value_brands = self._identify_brands(modified_str_rsk)  # Added this line

            remaining_items = modified_str_brands.split(';')

            dictionary = {
                'id': extracted_value_rsk[0] if extracted_value_rsk else None,
                'brand': extracted_value_brands,
                **{f'attribute_{i}': item for i, item in enumerate(remaining_items)}
            }

            dict_data.append(dictionary)

        return dict_data


if __name__ == "__main__":
    manipulator = ExcelManip('../WebCrawler/resources/quality_secured_articles.xlsx')
    result = manipulator.pre_process()

    # print all data in dictionary
    for dictionary in result:
        print(dictionary)

    '''for dictionary in result:
        if 'rsk' in dictionary:
            if 'brand' in dictionary:
                print("This row has both RSK and Brand.")
                print(f"RSK: {dictionary['rsk']}, Brand: {dictionary['brand']}")
            else:
                print("This row has RSK only.")
                print(f"RSK: {dictionary['rsk']}")
        print("------")'''
