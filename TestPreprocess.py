import os
import openpyxl
import pandas as pd
from openpyxl.styles import PatternFill

if __name__ == '__main__':
    '''Test of preprocess'''
    file_path = 'resources/QualityTest2.xlsx'
    file_dir = 'temp_files'
    df = pd.read_excel(file_path, sheet_name=0)
    num_rows = len(df)
    # Output file
    excel_output = 'result.xlsx'

    # Create a Pandas ExcelWriter using openpyxl
    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='result', index=False)
        workbook = writer.book
        sheet = writer.sheets['result']

        # Create fill styles for coloring rows
        yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')

        for i in range(1, num_rows + 1):
            filename = f'{i}.csv'
            file_path = os.path.join(file_dir, filename)

            if os.path.exists(file_path):
                if os.path.getsize(file_path) == 0:
                    print(f'{filename} is empty. Coloring row red.')
                    for cell in sheet[i + 1]:
                        cell.fill = red_fill  # Color the entire row red
            else:
                print(f'{filename} does not exist')
                # Perform actions for missing files here, if needed

        workbook.save(excel_output)
