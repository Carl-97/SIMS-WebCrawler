import os
import pandas as pd
from openpyxl.styles import PatternFill


def check_file_for_data(file_name):
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                elements = line.strip().split("||")
                if elements[-1].endswith('.pdf'):
                    return True  # Return True if the last element ends with '.pdf'
        return False  # Return False if no line ends with '.pdf' in the file
    except Exception as e:
        print(f"Error reading file {file_name}: {str(e)}")
        return False


if __name__ == '__main__':
    '''Test of preprocess'''
    file_path = 'resources/QualityTest2.xlsx'
    file_dir = 'temp_files'
    excel_output = 'result.xlsx'
    df = pd.read_excel(file_path, sheet_name=0)
    num_rows = len(df)

    # Create a Pandas ExcelWriter using openpyxl
    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='result', index=False)
        workbook = writer.book
        sheet = writer.sheets['result']

        # Create fill styles for coloring rows
        yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
        red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
        green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
        blue_fill = PatternFill(start_color='0000FF', end_color='0000FF', fill_type='solid')

        for i in range(1, num_rows + 1):
            filename = f'{i}.csv'
            file_path = os.path.join(file_dir, filename)

            if os.path.exists(file_path):
                if os.path.getsize(file_path) == 0:
                    for cell in sheet[i + 1]:
                        cell.fill = red_fill
                else:
                    is_pdf = check_file_for_data(file_path)
                    if is_pdf:
                        for cell in sheet[i + 1]:
                            cell.fill = yellow_fill
            else:
                print(f'error {filename} does not exist')
                # Perform actions for missing files here, if needed

        workbook.save(excel_output)
