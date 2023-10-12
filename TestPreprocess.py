import os
import openpyxl
from openpyxl.styles import PatternFill

if __name__ == '__main__':
    '''Test of preprocess'''

    # Define the Excel file path
    excel_file_path = 'resources/QualityTest.xlsx'
    workbook = openpyxl.load_workbook(excel_file_path)

    # Get the default (first) sheet
    sheet = workbook.active

    # Define the directory containing your files
    file_directory = 'temp_files'

    # Create fill styles for coloring rows
    yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
    red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

    # Initialize num_rows to 0
    num_rows = 0

    # Create a list to track rows that need to be colored
    rows_to_color = []

    # Iterate through rows in the Excel sheet based on the number of rows with data
    for row in sheet.iter_rows(values_only=True):
        num_rows += 1
        expected_filename = f'{num_rows}.csv'
        csv_file_path = os.path.join(file_directory, expected_filename)

        if os.path.exists(csv_file_path):
            print(f'Read file {expected_filename}')
        else:
            print(f'{expected_filename} does not exist')
            # Add the row index to the list of rows to color
            rows_to_color.append(num_rows)

    # Apply the fill styles to the rows that need to be colored
    for row_index in rows_to_color:
        for cell in sheet[row_index]:
            cell.fill = red_fill  # Color rows with missing files red

    # Save the modified Excel workbook
    workbook.save(excel_file_path)
