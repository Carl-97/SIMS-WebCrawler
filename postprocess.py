import os
import csv
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill

class ExcelProcessor:
    def __init__(self, input_file, output_file, csv_directory):
        self.input_file = input_file
        self.output_file = output_file
        self.csv_directory = csv_directory

    def _has_only_pdf_urls(self, csv_file):
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                # Skip the row if it's just a separator, remove this if necessary
                if row and '||' in row[0]:
                    continue
                pdf_url = row[0]
                if not pdf_url.endswith('.pdf'):
                    return False
            return True

    def _find_all_pdf_urls(self, csv_file):
        pdf_urls = []
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row_number, row in enumerate(reader, start=1):
                # Skip the row if it's just a separator, remove this if necessary
                if row and '||' in row[0]:
                    continue
                pdf_url = row[0]
                if pdf_url.endswith('.pdf'):
                    pdf_urls.append(pdf_url)
        return pdf_urls

    def _add_to_row(self, sheet, row_index, num_cols, found_pdfs):
        for i, data_value in enumerate(found_pdfs, start=2):
            cell = sheet.cell(row=row_index + 1, column=num_cols + i)
            cell.value = data_value

    def _fill_row(self, row, fill_color):
        for cell in row:
            cell.fill = fill_color

    def process_excel(self):
        df = pd.read_excel(self.input_file, sheet_name=0)
        num_rows, num_cols = df.shape

        green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
        yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'result'

        # Copy headers and data from the original DataFrame to the new sheet
        for r_idx, row in enumerate(df.itertuples(index=False), start=1):
            for c_idx, value in enumerate(row, start=1):
                if r_idx == 1:  # If it's the first row, copy headers
                    sheet.cell(row=1, column=c_idx, value=df.columns[c_idx - 1])
                sheet.cell(row=r_idx + 1, column=c_idx, value=value)

        for index, row in enumerate(sheet.iter_rows(min_row=2, max_row=num_rows + 1, max_col=num_cols), start=1):
            csv_file_path = os.path.join(self.csv_directory, f"{index}.csv")

            if os.path.exists(csv_file_path):
                if os.path.getsize(csv_file_path) == 0:
                    self._fill_row(row, red_fill)
                elif self._has_only_pdf_urls(csv_file_path):
                    found_pdfs = self._find_all_pdf_urls(csv_file_path)
                    self._add_to_row(sheet, index, num_cols, found_pdfs)
                    self._fill_row(row, yellow_fill)
                else:
                    # This is for the cleaned data
                    # Recommendation: Format the cleaned data in a csv file and use that to add each piece of information
                    self._fill_row(row, green_fill)
            else:
                self._fill_row(row, red_fill)

        workbook.save(self.output_file)


if __name__ == '__main__':
    excel_processor = ExcelProcessor(
        input_file='resources/QualityTest2.xlsx',
        output_file='result.xlsx',
        csv_directory='temp_files'
    )
    excel_processor.process_excel()
