from ExcelManip import excelmanip as em
from WebCrawler.crawlerDemo4 import WebCrawler
from urllib.parse import quote
import streamlit as st #for UI
import os #for UI
import shutil #for UI
import pandas as pd#for UI

def updateNumbers():
    nummer_found.markdown(f'RSK or E-Nummer found: {countNummer} ({countNummer / i * 100:.2f}%)')
    search_performed.markdown(f'Google Searches performed: {countGoogleSearch} ({countGoogleSearch / i * 100:.2f}%)')
    no_value.markdown(f'No Values found: {countNoValue} ({countNoValue / i * 100:.2f}%)')

# Note: using unsafe_allow_html can cause security problems if application is deployed on the web.
# belows Code section is used for the streamlit UI
st.markdown("""
    <style>
     @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap');
        .center {
            display: block;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
            font-family: Poppins, sans-serif;
            font-size: 75px;
        }
        .subtitle{
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-bottom: 20px;
            text-align: center;
            font-family: Poppins, sans-serif;
            font-size: 40px;
        }
        .text{
            display: block;
            margin-left: auto;
            margin-right: auto;
            text-align: center;
            font-family: 'Poppins', sans-serif;
            font-size: 13px;
            font-weight: 100;
        }
    </style>
    """, unsafe_allow_html=True)
st.markdown("<h1 class='center'>SSG</h1>", unsafe_allow_html=True)
st.markdown("<h1 class='subtitle' 'center'>Data Enrichment Tool</h1>", unsafe_allow_html=True)

upload_excel = st.file_uploader("Choose an Excel file", type="xlsx")
if upload_excel:
    original_file_name = upload_excel.name.rsplit(".", 1)[0]
    df = pd.read_excel(upload_excel)
    num_rows = len(df)
    countNummer = 0
    countGoogleSearch = 0
    countNoValue = 0
    st.markdown(f'<p class="text">Number of Lines (Items): {num_rows}</p>', unsafe_allow_html=True)
    processed_text = st.markdown(f'<p class="text">Items processed: not yet started</p>', unsafe_allow_html=True)
    my_expander = st.expander('Click to expand for more information', expanded=False)
    nummer_found = my_expander.markdown('RSK or E-Nummer found: ...')
    search_performed = my_expander.markdown('Google Searches performed: ...')
    no_value = my_expander.markdown('No Values found: ...')

    print(f"Number of Lines (Items): {num_rows}")
    del df
    if st.button("Start processing File"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        processed_text.markdown(f'<p class="text">Items processed: 0</p>', unsafe_allow_html=True)
# following code section is mostly for Web Crawling
        manipulator = em.ExcelManip(upload_excel)
        data = manipulator.pre_process()
        wc = WebCrawler()
        i = 1

        for dictionary in data:
            if 'id' in dictionary and dictionary['id'] is not None:
                id_val = dictionary['id']
                e_nr_url = f'https://www.e-nummersok.se/sok?Query={id_val}'
                rsk_nr_url = f'https://www.rskdatabasen.se/sok?Query={id_val}'
                wc.crawl_website_with_depth(str(i), 0, start_url=e_nr_url)
                wc.crawl_website_with_depth(str(i), 0, start_url=rsk_nr_url)
                countNummer += 1
                updateNumbers()
            else:
                print("No 'id' found. Performing a Google search...")
                # Filter out None values from the dictionary's values
                filtered_values = [value for value in dictionary.values() if value is not None]
                if filtered_values:
                    # Construct a Google search query using the filtered values
                    search_query = " ".join(filtered_values)
                    search_query = quote(search_query)  # URL encode the search query
                    google_search_url = f'https://www.google.com/search?q={search_query}'
                    print(f'Search Query {i}: {google_search_url}')
                    wc.crawl_website_with_depth(str(i), 1, start_url=google_search_url)
                    countGoogleSearch += 1
                    updateNumbers()
                else:
                    print("Dictionary has no valid values to perform a search.")
                    countNoValue += 1
                    updateNumbers()
# next 4 code lines is for UI (update the progress bar, the number of processed Items, and the percentage number for the progress bar
            progress_percentage = (i/num_rows)*100
            progress_bar.progress(int(progress_percentage)) #update the progress bar once it is done with scraping
            processed_text.markdown(f'<p class="text">Items processed: {i}</p>', unsafe_allow_html=True) #update the number of items procesed
            status_text.markdown(f'<p class="text">Progress: {progress_percentage:.2f}%</p>', unsafe_allow_html=True) #update the percentage text
            i += 1

        print("------Done------")
        wc.close()
#code section below is for UI (Processing complete, prepare zip for download
        status_text.markdown("<p class='text'>Processing Complete!</p>", unsafe_allow_html=True)

        zip_name = "download.zip"
        if os.path.exists('temp_files'):
            shutil.make_archive(zip_name.replace('.zip', ''), 'zip', 'temp_files', )

        with open(zip_name, "rb") as file:
            st.download_button( label="Download Zip Folder", data=file, file_name=f"Processed_{original_file_name}.zip", mime='application/zip', )
            # remove Files after Download
            # os.remove(zip_name)

#Delete CSV Files
            # folder_path = 'temp_files'
            # file_paths = [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path)]
            # for file_path in file_paths:
            #     try:
            #         os.remove(file_path)
            #     except Exception as e:
            #         print(f"Error occurred while deleting file {file_path}: {str(e)}")


