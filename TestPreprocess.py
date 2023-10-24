import os
import csv
import pandas as pd
from openpyxl.styles import PatternFill


def has_only_pdf_urls(csv_file):
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


def find_all_pdf_urls(csv_file):
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


def add_to_row(sheet, row_index, num_cols, found_pdfs):
    for i, data_value in enumerate(found_pdfs, start=2):
        cell = sheet.cell(row=row_index+1, column=num_cols + i)
        cell.value = data_value


def fill_row(row, fill_color):
    for cell in row:
        cell.fill = fill_color


if __name__ == '__main__':
    file_path = 'resources/QualityTest2.xlsx'
    file_dir = 'temp_files'
    excel_output = 'result.xlsx'
    df = pd.read_excel(file_path, sheet_name=0)
    num_rows, num_cols = df.shape

    green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
    blue_fill = PatternFill(start_color='0000FF', end_color='0000FF', fill_type='solid')

    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='result', index=False)
        workbook = writer.book
        sheet = writer.sheets['result']

        index = 1
        for index, row in enumerate(sheet.iter_rows(min_row=2, max_row=num_rows + 1, max_col=num_cols), start=1):
            csv_file_path = os.path.join(file_dir, f"{index}.csv")
            if os.path.exists(csv_file_path):
                if os.path.getsize(csv_file_path) == 0:
                    fill_row(row, red_fill)
                elif has_only_pdf_urls(csv_file_path):
                    found_pdfs = find_all_pdf_urls(csv_file_path)
                    add_to_row(sheet, index, num_cols, found_pdfs)
                    fill_row(row, yellow_fill)
                else:
                    '''This is for the cleaned data
                    recommendation would be that the cleaned data is formatted in a csv file and use that to add each 
                    piece of information to a new cell by calling a method'''
                    fill_row(row, green_fill)
            else:
                fill_row(row, red_fill)
            index += 1

        workbook.save(excel_output)
