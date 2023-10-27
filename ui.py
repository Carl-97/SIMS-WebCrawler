from WebCrawler.crawler import WebCrawler
from urllib.parse import quote
import streamlit as st #for UI
import os #for UI
import shutil #for UI
import pandas as pd#for UI
import main as cape1903
from datetime import datetime

KEYS = ['brand', 'article_id', 'type_desc']
start_time = None
end_time = None
datetime1 = None
datetime2 = None


def updateNumbers():
    nummer_found.markdown(f'RSK or E-Nummer found: {countNummer} ({countNummer / i * 100:.2f}%)')
    search_performed.markdown(f'Google Searches performed: {countGoogleSearch} ({countGoogleSearch / i * 100:.2f}%)')


def crawl_with_id(id_val, web_crawler, index):
    websites = [
        f'https://www.e-nummersok.se/sok?Query={id_val}',
        f'https://www.rskdatabasen.se/sok?Query={id_val}'
    ]
    for url in websites:
        web_crawler.crawl_website_with_depth(str(index), 0, start_url=url)


def crawl_with_keys(data_dict, web_crawler, index):
    values_to_use = [data_dict[key] for key in KEYS if key in data_dict and data_dict[key] is not None]
    if values_to_use:
        print(f'Key Value: {values_to_use}')
        search_query = " ".join(values_to_use)
        search_query = quote(search_query)
        google_search_url = f'https://www.google.com/search?q={search_query}'
        print(f'{google_search_url}')
        web_crawler.crawl_website_with_depth(str(index), 1, start_url=google_search_url)
    else:
        print("Dictionary has no valid values to perform a search.")


if 'files_processed' not in st.session_state:
    st.session_state.files_processed = False

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
    st.markdown(f'<p class="text">Number of Lines (Items): {num_rows}</p>', unsafe_allow_html=True)
    processed_text = st.markdown(f'<p class="text">Items processed: not yet started</p>', unsafe_allow_html=True)
    my_expander = st.expander('Click to expand for more information', expanded=False)
    nummer_found = my_expander.markdown('RSK or E-Nummer found: ...')
    search_performed = my_expander.markdown('Google Searches performed: ...')

    print(f"Number of Lines (Items): {num_rows}")
    del df
    if st.button("Start processing File"):
        start_time = datetime.now().time()
        print(f"Start Time: {start_time.strftime('%H:%M:%S')}")
        datetime1 = datetime.combine(datetime.today(), start_time) #used to print time used in seconds
        progress_bar = st.progress(0)
        status_text = st.empty()
        processed_text.markdown(f'<p class="text">Items processed: 0</p>', unsafe_allow_html=True)
# following code section is mostly for Web Crawling
        cape1903.empty_folder('temp_files')
        data = cape1903.run_identify(upload_excel)
        wc = WebCrawler()

        i = 1
        for idx, dictionary in enumerate(data, start=1):
            if 'id' in dictionary and dictionary['id'] is not None:
                id_nr = dictionary['id']
                crawl_with_id(id_nr, wc, idx)
                crawl_with_keys(dictionary, wc, idx)
                countNummer += 1
                updateNumbers()
            else:
                crawl_with_keys(dictionary, wc, idx)
                countGoogleSearch += 1
                updateNumbers()

# next 4 code lines is for UI (update the progress bar, the number of processed Items, and the percentage number for the progress bar
            progress_percentage = (i/num_rows)*100
            progress_bar.progress(int(progress_percentage)) #update the progress bar once it is done with scraping
            processed_text.markdown(f'<p class="text">Items processed: {i}</p>', unsafe_allow_html=True) #update the number of items procesed
            status_text.markdown(f'<p class="text">Progress: {progress_percentage:.2f}%</p>', unsafe_allow_html=True) #update the percentage text
            i += 1
        wc.close()
        cape1903.run_postprocess(upload_excel)
        st.session_state.files_processed = True
        end_time = datetime.now().time()
        print(f"End Time: {end_time.strftime('%H:%M:%S')}")
        datetime2 = datetime.combine(datetime.today(), end_time)
        print("------Done------")

        #print time difference
        time_difference = datetime2 - datetime1
        total_seconds = time_difference.total_seconds()
        print(f"Total Time in Seconds: {total_seconds}")

        # here the Preprocess will happen

#code section below is for UI (Processing complete, prepare zip for download
        status_text.markdown("<p class='text'>Processing Complete!</p>", unsafe_allow_html=True)

    if st.session_state.files_processed:
        zip_name = "download.zip"
        if os.path.exists('temp_files'):
            shutil.make_archive(zip_name.replace('.zip', ''), 'zip', 'temp_files', )

        with open(zip_name, "rb") as file:
            st.download_button( label="Download Zipped CSV Files", data=file, file_name=f"Processed_{original_file_name}.zip", mime='application/zip', )
            # remove Files after Download
            # os.remove(zip_name)

        with open("result.xlsx", "rb") as file:
            btn = st.download_button(
                label="Download Result Excel",
                data=file,
                file_name=f"Processed_{original_file_name}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        if st.button("Clean and Restart"):
            # remove zipped File after Download
            os.remove(zip_name)
            cape1903.empty_folder('temp_files')
            '''# remove CSV Files in temp_files
            folder_path = 'temp_files'
            file_paths = [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path)]
            for file_path in file_paths:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error occurred while deleting file {file_path}: {str(e)}")'''

            #remove result.xlsx
            os.remove("result.xlsx")

            st.session_state.files_processed = False
            st.rerun()
