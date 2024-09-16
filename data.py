from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import time
import pandas as pd
import numpy as np

# Set up the Chrome WebDriver
driver = webdriver.Chrome()

WEBSITE = "https://www.tnpds.gov.in/pages/reports/pds-nfsa-offtake-report-state.xhtml"
START_YEAR = 2022
END_YEAR = 2024
END_MONTH = "July"
CARD_TYPES = ["AAY", "PHH", "NPHH"]

# Month list to map text with the dropdown
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Open the webpage
driver.get(WEBSITE)
driver.get(WEBSITE)
time.sleep(3)

# Select the language (English)
english_label = driver.find_element(By.CSS_SELECTOR, "label[for='masterForm:languageSelectMenu:1']")
english_label.click()
time.sleep(3)

# Function to fetch data for a specific month, year, and card type
def fetch_data(month, year, card_type):
    # Select the month
    month_dropdown = driver.find_element(By.ID, "form:month")
    select_month = Select(month_dropdown)
    select_month.select_by_visible_text(month)

    # Select the year
    year_dropdown = driver.find_element(By.ID, "form:year")
    select_year = Select(year_dropdown)
    select_year.select_by_visible_text(str(year))

    # Select the card type
    card_dropdown = driver.find_element(By.ID, "form:request")
    select_card = Select(card_dropdown)
    select_card.select_by_visible_text(card_type)
    time.sleep(1)

    # Click the search button
    search_button = driver.find_element(By.NAME, "form:j_idt112")
    search_button.click()

    time.sleep(3)

    # Extract the table data
    table = driver.find_element(By.ID, "form:j_idt114")
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Extract headers
    headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, "th")]
    headers.insert(0, "NFSA Card Type")
    headers.insert(0, "Year")
    headers.insert(0, "Month")

    # Create a list to store data
    data_rows = []
    for row in rows[1:]:  # Skip header
        cols = row.find_elements(By.TAG_NAME, "td")
        data = [col.text for col in cols]
        data.insert(0, card_type)  
        data.insert(0, year)      
        data.insert(0, month)      
        data_rows.append(data)

    return headers, data_rows

# Initialize an empty DataFrame to store combined data
df_combined = pd.DataFrame()

# Loop through each year, month, and card type, and save data in a combined CSV file
for year in range(START_YEAR, END_YEAR + 1):
    for month in MONTHS:
        if year == END_YEAR and MONTHS.index(month) > MONTHS.index(END_MONTH):
            break
        for card_type in CARD_TYPES:
            fetched_headers, data = fetch_data(month, year, card_type)
            df_fetched = pd.DataFrame(data, columns=fetched_headers)

            # If df_combined is empty, initialize it with the first fetched dataframe
            if df_combined.empty:
                df_combined = df_fetched
            else:
                # Check if headers are the same as combined DataFrame headers
                if set(df_fetched.columns) != set(df_combined.columns):

                    # Add missing columns to df_fetched with NaN values
                    for col in df_combined.columns:
                        if col not in df_fetched.columns:
                            df_fetched[col] = np.nan  # Add missing columns to fetched data with NaN

                    # Add new columns in df_combined for extra headers in df_fetched
                    for col in df_fetched.columns:
                        if col not in df_combined.columns:
                            df_combined[col] = np.nan  # Add new columns to df_combined with NaN

                # Append the fetched data to the combined DataFrame
                df_combined = pd.concat([df_combined, df_fetched], ignore_index=True)

# # Print column names for debugging
# print("Columns before merging:", df_combined.columns)

# Merge 'AAY RICE(KG)' and 'RICE(KG)' columns
if 'AAY RICE(KG)' in df_combined.columns and 'RICE(KG)' in df_combined.columns:
    # Combine the columns, prioritizing non-NaN values
    df_combined['RICE(KG)'] = df_combined['AAY RICE(KG)'].combine_first(df_combined['RICE(KG)'])
    df_combined.drop(columns=['AAY RICE(KG)'], inplace=True)  # Drop the 'AAY RICE(Kg)' column

# # Print column names after merging for debugging
# print("Columns after merging:", df_combined.columns)

# Save the combined data to a single CSV file
df_combined.to_csv("combined_data.csv", index=False, encoding='utf-8')
print(f"Data saved in combined_data.csv")

# Close the driver after all data is collected
driver.quit()
