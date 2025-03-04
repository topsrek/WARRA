import os
import tabula
import pandas as pd
import json
import re
import glob
from PyPDF2 import PdfReader
import pdfplumber


def process_beilage_1(tables, headers):
    """Special processing for Beilage_1 tables"""
    combined_table = pd.concat(tables, ignore_index=True)

    # Remove the first row (contains headers)
    combined_table = combined_table.iloc[1:]

    # Set proper column names
    combined_table.columns = ["LST", "Refundierungen", "Rechnungsbeträge"]

    # Convert numbers to float
    for col in ["Refundierungen", "Rechnungsbeträge"]:
        combined_table[col] = (
            combined_table[col].str.replace(".", "").str.replace(",", ".").astype(float)
        )

    return combined_table


def process_beilage_3(pdf_path):

    total_df = pd.DataFrame([])
    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:

            raw_table = page.extract_table(table_settings={"join_x_tolerance": 10})
            # print(raw_table)

            # Initialize lists for cleaned data
            cleaned_data = []

            # keep LS and month_year in this scope to save for last row
            month_year = None
            ls = None

            for index, row in enumerate(raw_table):

                # print(row, index)
                #if index in [0, 1, 2, 3, 4]:  # Skip header rows
                #    continue
                parts = row[0].split(" ")
                last_row = False
                if index == len(raw_table) - 1:
                    last_row = True
                    fg_code = None
                    title = "Gesamt"
                    # ls and month_year are carried over from the second to last row in this table

                print(parts)
                if not last_row:
                    ls = parts[0]
                    month_year = parts[1]
                    fg_code = int("".join(filter(str.isdigit, parts[2])))
                if str(
                    parts[-4].replace(".", "")
                ).isnumeric():  # some rows have different format from pdfplumber
                    # another test could probably be to check is len(parts[-2]) is 1
                    if not last_row:
                        title = " ".join(
                            [parts[2].split(str(fg_code))[1]] + parts[3:-4]
                        )
                    if parts[-4] == "-":
                        postal = None
                    else:
                        postal = int(parts[-4].replace(".", ""))
                    if parts[-3] == "-":
                        online = None
                    else:
                        online = int("".join(parts[-3:-1]).replace(".", ""))
                else:
                    if not last_row:
                        title = " ".join(
                            [parts[2].split(str(fg_code))[1]] + parts[3:-3]
                        )
                    if parts[-3] == "-":
                        postal = None
                    else:
                        postal = int(parts[-3].replace(".", ""))
                    if parts[-2] == "-":
                        online = None
                    else:
                        online = int(parts[-2].replace(".", ""))
                if parts[-1] == "-":
                    gesamt = None
                else:
                    gesamt = int(parts[-1].replace(".", ""))

                print(
                    {
                        "LS": ls,
                        "Month_Year": month_year,
                        "FG-Code": fg_code,
                        "Title": title,
                        "Postal": postal,
                        "Online": online,
                        "Gesamt": gesamt,
                    }
                )

                data_entry = {
                    "ÖGK-LS": ls,
                    "Monat.Jahr": month_year,
                    "FG-Code": fg_code,
                    "Fachrichtung": title.strip(),
                    "postal": postal,
                    "online": online,
                    "Gesamt": gesamt,
                }
                # print(data_entry)
                cleaned_data.append(data_entry)

            # Create DataFrame from cleaned data
            cleaned_df = pd.DataFrame(cleaned_data)

            # Sort by FG-Code, putting None values at the end
            cleaned_df = cleaned_df.sort_values(
                "FG-Code", na_position="last"
            ).reset_index(drop=True)

            total_df = pd.concat([total_df, cleaned_df])

        return total_df


def process_beilage_10(pdf_path):

    total_df = pd.DataFrame([])
    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            extracted_tables = list(map(lambda x: x.extract(), tables))
            if pdf_path.endswith("Beilage_10.pdf"):
                if page.page_number in [2, 10, 18, 26, 34, 42, 50, 58, 66, 74]:
                    relevant_table = extracted_tables[2]
                    relevant_table[4] = [relevant_table[4][0].split("\n")[0]]
                    extracted_tables = (
                        extracted_tables[:2]
                        + [relevant_table[:5]]
                        + [relevant_table[4:]]
                        + extracted_tables[3:]
                    )
                    # if table_index == 2:
                    #    print(raw_table)
                    #    raw_table[3] = [raw_table[3][0].split("\n")[0]]
                    #    #raw_table = raw_table[1:]
            for table_index, raw_table in enumerate(extracted_tables):
                print(f"processing table {table_index+1} on page {page.page_number}")

                # Initialize lists for cleaned data
                cleaned_data = []
                # print(raw_table)
                # raw_table = raw_table[1][0].split("\n")+[raw_table[2][0], raw_table[3][0]]
                raw_table = raw_table[1:]
                print(raw_table)
                month_year = None
                ls = None
                for index, row in enumerate(raw_table):

                    print(row, index)
                    # if index in [0, 1, 2, 3, 4]:  # Skip header rows
                    #    continue
                    parts = row[0].split(" ")
                    print(parts)
                    last_row = False
                    if index == len(raw_table) - 1:
                        last_row = True
                        fg_code = None
                        title = "Gesamt"
                        # ls and month_year are carried over from the second to last row in this table

                    # print(parts)
                    if not last_row:
                        ls = parts[0]
                        month_year = parts[1]
                        fg_code = int("".join(filter(str.isdigit, parts[2])))
                    if str(
                        parts[-4].replace(".", "")
                    ).isnumeric():  # some rows have different format from pdfplumber
                        # another test could probably be to check is len(parts[-2]) is 1
                        if not last_row:
                            title = " ".join(
                                [parts[2].split(str(fg_code))[1]] + parts[3:-4]
                            )
                        if parts[-4] == "-":
                            postal = None
                        else:
                            postal = int(parts[-4].replace(".", ""))
                        if parts[-3] == "-":
                            online = None
                        else:
                            online = int("".join(parts[-3:-1]).replace(".", ""))
                    else:
                        if not last_row:
                            title = " ".join(
                                [parts[2].split(str(fg_code))[1]] + parts[3:-3]
                            )
                        if parts[-3] == "-":
                            postal = None
                        else:
                            postal = int(parts[-3].replace(".", ""))
                        if parts[-2] == "-":
                            online = None
                        else:
                            online = int(parts[-2].replace(".", ""))
                    if parts[-1] == "-":
                        gesamt = None
                    else:
                        gesamt = int(parts[-1].replace(".", ""))

                    print(
                        {
                            "LS": ls,
                            "Month_Year": month_year,
                            "FG-Code": fg_code,
                            "Title": title,
                            "Postal": postal,
                            "Online": online,
                            "Gesamt": gesamt,
                        }
                    )

                    data_entry = {
                        "ÖGK-LS": ls,
                        "Monat.Jahr": month_year,
                        "FG-Code": fg_code,
                        "Fachrichtung": title.strip(),
                        "postal": postal,
                        "online": online,
                        "Gesamt": gesamt,
                    }
                    # print(data_entry)
                    cleaned_data.append(data_entry)

                # Create DataFrame from cleaned data
                cleaned_df = pd.DataFrame(cleaned_data)

                # Sort by FG-Code, putting None values at the end
                cleaned_df = cleaned_df.sort_values(
                    "FG-Code", na_position="last"
                ).reset_index(drop=True)

                total_df = pd.concat([total_df, cleaned_df])

        return total_df


def process_beilage_2(pdf_path):
    """Special processing for Beilage_2 tables"""

    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        raw_table = page.extract_table()
        # print(raw_table)

        # Initialize lists for cleaned data
        cleaned_data = []

        for index, row in enumerate(raw_table):

            # print(row)
            if index == 0:  # Skip header row
                continue

            parts = row[0].split("\n")
            if len(parts) != 1:
                # Case: Text is split across multiple lines with FG code in middle
                # Example: "FA für Intensivmedizin\n2\nFA für Augenheilkunde und"
                text = parts[0].strip()
                second_line = parts[2]

                numbers = parts[1]
                ref = numbers.split(" ")[-2]
                rech = numbers.split(" ")[-1]
                fg_code = int(numbers.split(" ")[0])

                title = parts[0] + " " + parts[2]
            else:
                if index == len(raw_table) - 1:
                    # last row
                    print(parts[0].split(" "))
                    fg_code = None
                    title = "Gesamt"
                    ref = "".join(parts[0].split(" ")[1:3])
                    rech = "".join(parts[0].split(" ")[3:5])
                else:
                    # Case: Single line
                    # Try to extract FG code from start of text
                    fg_code_match = re.match(r"^\s*(\d+)\s*", parts[0])
                    if fg_code_match:
                        fg_code = int(fg_code_match.group(1))
                        name_without_nmbrs = " ".join(parts[0].split(" ")[:-2])
                        title = name_without_nmbrs[fg_code_match.end() :].strip()
                    else:
                        fg_code = None
                        title = parts[0]
                    ref = parts[0].split(" ")[-2]
                    rech = parts[0].split(" ")[-1]

            ref_value = (
                float(str(ref).replace(".", "").replace(",", "."))
                if ref != "-"
                else None
            )
            rech_value = (
                float(str(rech).replace(".", "").replace(",", "."))
                if rech != "-"
                else None
            )
            data_entry = {
                "FG-Code": fg_code,
                "Fachrichtung": title.strip(),
                "Refundierungen": ref_value,
                "Rechnungsbeträge": rech_value,
            }
            # print(data_entry)
            cleaned_data.append(data_entry)

        # Create DataFrame from cleaned data
        cleaned_df = pd.DataFrame(cleaned_data)

        # Sort by FG-Code, putting None values at the end
        cleaned_df = cleaned_df.sort_values("FG-Code", na_position="last").reset_index(
            drop=True
        )

        return cleaned_df


def process_beilage_8(pdf_path):
    """Special processing for Beilage_8 and Beilage_9 tables"""
    total_df = pd.DataFrame([])
    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            for table_index, table in enumerate(tables):
                print(f"processing table {table_index+1} on page {page.page_number}")
                raw_table = table.extract()

                # Initialize lists for cleaned data
                cleaned_data = []
                # print(raw_table)
                raw_table = raw_table[1][0].split("\n") + [
                    raw_table[2][0],
                    raw_table[3][0],
                ]
                # print(raw_table)
                month_year = None
                ls = None
                for index, row in enumerate(raw_table):

                    # keep LS and month_year in this scope to save for last row

                    last_row = False
                    if index == len(raw_table) - 1:
                        last_row = True
                    parts = row.split("\n")
                    print(parts)

                    parts_parts = parts[0].split(" ")
                    if last_row:
                        month_year = "Durchschnitt " + month_year[-2:]
                        fg_code = None
                        title = "Gesamt"
                        ref = parts_parts[1]
                        if pdf_path.endswith("Beilage_9.pdf"):
                            rech = "".join(parts_parts[2:4])
                        else:
                            rech = parts_parts[2]
                    else:
                        ls = parts_parts[0]
                        month_year = parts_parts[1]
                        fg_code = int(parts_parts[2])
                        title = parts_parts[3]
                        unprofessional = False
                        if pdf_path.endswith("Beilage_9.pdf"):
                            if ls == "ÖGK-K" and index in [0, 2]:
                                unprofessional = True
                            if ls == "ÖGK-O" and table_index == 0 and index in [1]:
                                unprofessional = True
                            if ls == "ÖGK-S":
                                if table_index in [0, 1]:
                                    if index in [2]:
                                        unprofessional = True
                                if table_index == 2:
                                    if index in [1, 2]:
                                        unprofessional = True
                            if ls == "ÖGK-ST":
                                if table_index in [0, 1]:
                                    if index in [0, 1]:
                                        unprofessional = True
                                if table_index == 2:
                                    if index in [0, 1, 2]:
                                        unprofessional = True
                            if ls == "ÖGK-T":
                                if index in [1]:
                                    unprofessional = True

                        if unprofessional:
                            ref = parts_parts[-3]
                            rech = "".join(parts_parts[-2:])
                        else:
                            ref = parts_parts[-2]
                            rech = parts_parts[-1]

                    ref_value = (
                        float(str(ref).replace(".", "").replace(",", "."))
                        if ref != "-"
                        else None
                    )
                    rech_value = (
                        float(str(rech).replace(".", "").replace(",", "."))
                        if rech != "-"
                        else None
                    )
                    data_entry = {
                        "ÖGK-LS": ls,
                        "Monat.Jahr": month_year,
                        "FG-Code": fg_code,
                        "Fachrichtung": title.strip(),
                        "Refundierungen": ref_value,
                        "Rechnungsbeträge": rech_value,
                    }
                    # print(data_entry)
                    cleaned_data.append(data_entry)

                # Create DataFrame from cleaned data
                cleaned_df = pd.DataFrame(cleaned_data)

                # Sort by FG-Code, putting None values at the end
                cleaned_df = cleaned_df.sort_values(
                    "FG-Code", na_position="last"
                ).reset_index(drop=True)

                total_df = pd.concat([total_df, cleaned_df])

        return total_df


def process_beilage_7(pdf_path):
    total_df = pd.DataFrame([])
    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            raw_table = page.extract_table(table_settings={"join_x_tolerance": 10})
            # print(raw_table)

            # Initialize lists for cleaned data
            cleaned_data = []

            # keep LS and month_year in this scope to save for last row
            month_year = None
            ls = None

            for index, row in enumerate(raw_table):

                print(row, index)
                if index in [0, 1, len(raw_table) - 1]:  # Skip header and empty rows
                    continue
                # split by new line (needed for Vorarlberg)
                parts = row[0].split("\n")[-1].split(" ")
                print(parts)
                last_row = False
                shift = 0
                if index == len(raw_table) - 2:  # empty row after last row with content
                    last_row = True
                    month_year = "Durchschnitt"
                    shift = -1

                if not last_row:
                    ls = parts[0]
                    month_year = parts[1]

                # WAHonline data is not avilable for all
                WAHonline_available = False
                if ls in [
                    "ÖGK-B",
                    "ÖGK-K",
                    "ÖGK-N",
                    "ÖGK-O",
                    "ÖGK-S",
                    "ÖGK-ST",
                    "ÖGK-T",
                ]:
                    if month_year not in ["Jän.23", "Feb.23", "Mär.23", "Apr.23"]:
                        WAHonline_available = True
                elif ls in ["ÖGK-W"]:
                    if month_year not in [
                        "Jän.23",
                        "Feb.23",
                        "Mär.23",
                        "Apr.23",
                        "Mai.23",
                        "Jun.23",
                    ]:
                        WAHonline_available = True
                elif "ÖGK-V" in row[0]:
                    WAHonline_available = False  # no data available for ÖGK-V

                if WAHonline_available:
                    onlineWAH = int(parts[6 + shift].replace(".", ""))
                else:
                    onlineWAH = None

                if pdf_path.endswith("Beilage_12.pdf"):
                    if month_year not in ["Jän.23", "Feb.23", "Mär.23", "Apr.23"]:
                        # no data in any bundesland before Mai.23
                        postal = int(parts[2 + shift].replace(".", ""))
                        onlineMeine = int(parts[4 + shift].replace(".", ""))
                    else:
                        postal = None
                        onlineMeine = None
                else:
                    postal = int(parts[2 + shift].replace(".", ""))
                    onlineMeine = int(parts[4 + shift].replace(".", ""))

                print(
                    {
                        "LS": ls,
                        "Month_Year": month_year,
                        "Postal": postal,
                        "OnlineMeine": onlineMeine,
                        "OnlineWAH": onlineWAH,
                    }
                )

                data_entry = {
                    "ÖGK-LS": ls,
                    "Monat.Jahr": month_year,
                    "Postal": postal,
                    "OnlineMeine": onlineMeine,
                    "OnlineWAH": onlineWAH,
                }
                # print(data_entry)
                cleaned_data.append(data_entry)

            # Create DataFrame from cleaned data
            cleaned_df = pd.DataFrame(cleaned_data)

            # Sort by FG-Code, putting None values at the end
            cleaned_df = cleaned_df.reset_index(drop=True)

            total_df = pd.concat([total_df, cleaned_df])

        return total_df


def process_beilage_7a(pdf_path):
    total_df = pd.DataFrame([])
    # Read the PDF with pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            for table_index, table in enumerate(tables):
                print(f"processing table {table_index+1} on page {page.page_number}")
                raw_table = table.extract()

                # Initialize lists for cleaned data
                cleaned_data = []

                # keep LS and month_year in this scope to save for last row
                month_year = None
                ls = None

                # hidden row on some tables
                if table_index == 0:
                    last_row_index = len(raw_table) - 2
                elif table_index == 1:
                    last_row_index = len(raw_table) - 1
                elif table_index == 2:
                    last_row_index = len(raw_table) - 1

                # hidden table on first page
                if page.page_number == 1:
                    if table_index == 3:
                        continue

                for index, row in enumerate(raw_table):
                    print(row, index)
                    if table_index == 0:
                        wrong_row_indices = [0, 1, last_row_index + 1]
                    else:
                        wrong_row_indices = [0, last_row_index + 1]

                    if page.page_number in [3, 4]:
                        if table_index == 0:
                            odd_or_even = 1
                        elif table_index == 1:
                            odd_or_even = 0
                        elif table_index == 2:
                            if index == last_row_index:
                                odd_or_even = 1
                        if index in wrong_row_indices:  # Skip header and empty rows
                            continue
                        if index % 2 == odd_or_even:
                            row = [row[0] + " " + row[1]]
                    if index in wrong_row_indices:  # Skip header and empty rows
                        continue
                    parts = row[0].split(" ")
                    print(parts)
                    last_row = False
                    shift = 0
                    if index == last_row_index:
                        last_row = True
                        month_year = "Durchschnitt " + month_year[-2:]
                        shift = -1

                    if not last_row:
                        ls = parts[0]
                        month_year = parts[1]

                    postal = int(parts[2 + shift].replace(".", ""))
                    onlineMeine = int(parts[4 + shift].replace(".", ""))

                    print(
                        {
                            "LS": ls,
                            "Month_Year": month_year,
                            "Postal": postal,
                            "OnlineMeine": onlineMeine,
                        }
                    )

                    data_entry = {
                        "ÖGK-LS": ls,
                        "Monat.Jahr": month_year,
                        "Postal": postal,
                        "OnlineMeine": onlineMeine,
                    }
                    # print(data_entry)
                    cleaned_data.append(data_entry)

                # Create DataFrame from cleaned data
                cleaned_df = pd.DataFrame(cleaned_data)

                # Sort by FG-Code, putting None values at the end
                cleaned_df = cleaned_df.reset_index(drop=True)

                total_df = pd.concat([total_df, cleaned_df])

        return total_df


def extract_question_from_pdf(pdf_path):
    """Extract the question from a PDF"""
    with open(pdf_path, "rb") as file:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n"

    # Try different patterns to find the question
    patterns = [
        r"Wie hoch waren.*?\?.*?\).*?(?=\n\n|Antwort:|$)",  # Beilage_1 style
        r"Wie verteilen sich.*?\?.*?\).*?(?=\n\n|Antwort:|$)",  # Beilage_2 style
        r"Wie viele.*?\?.*?\).*?(?=\n\n|Antwort:|$)",  # Beilage_3 und _4 style
        r"Wie viele.*?.*?\).*?(?=\n\n|Antwort:|$)",  # Beilage_5 style
        r"Mit welcher.*?.\?*?\).*?(?=\n\n|Antwort:|$)",  # Beilage_7 style
        r"(?:Frage|Anfrage).*?(?:\d+/J):[\s\n]*(.*?)(?=\n\n|Antwort:|$)",  # Generic pattern
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            question = match.group(0)
            return " ".join(question.split())

    return "Question not found"


def check_and_convert_to_int(df, columns, filename=None):
    """
    Check if any values in the specified columns are floats and convert them to integers.
    Raises a warning if floating point values are found.
    
    Args:
        df (pandas.DataFrame): The dataframe to check and convert
        columns (list): List of column names to check and convert
        filename (str, optional): Name of the file being processed, for better warning messages
        
    Returns:
        pandas.DataFrame: The dataframe with converted columns
    """
    file_info = f" in {filename}" if filename else ""
    
    for col in columns:
        if col in df.columns:
            # Check if any non-null values have decimal parts
            non_null_values = df[col].dropna()
            if len(non_null_values) > 0:
                # Check if any values are not equal to their integer representation
                if any(non_null_values != non_null_values.astype(int)):
                    print(f"WARNING: Found floating point values in column {col}{file_info}!")
                    # Print the problematic values for debugging
                    problematic = non_null_values[non_null_values != non_null_values.astype(int)]
                    print(f"Problematic values: {problematic.tolist()}")
                
                # Convert to int regardless (will truncate any decimals)
                df[col] = df[col].apply(
                    lambda x: int(x) if pd.notnull(x) else None
                )
    
    return df


def ensure_integers_in_dict(data_dict):
    """
    Recursively check dictionaries and lists for float values that are actually integers
    and convert them to proper integers.
    
    Args:
        data_dict: Dictionary, list, or scalar value to process
        
    Returns:
        Processed data with floats converted to ints where appropriate
    """
    if isinstance(data_dict, dict):
        return {k: ensure_integers_in_dict(v) for k, v in data_dict.items()}
    elif isinstance(data_dict, list):
        return [ensure_integers_in_dict(item) for item in data_dict]
    elif isinstance(data_dict, float) and data_dict.is_integer():
        return int(data_dict)
    else:
        return data_dict


def process_beilage_tables(tables, pdf_path, save_dir):
    """Process tables from a Beilage PDF and save as both CSV and JSON"""

    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    if not tables:
        print(f"No tables found in: {pdf_path}")
        return

    # Store headers
    headers = tables[0].iloc[0] if tables else None

    # Process based on Beilage type
    if base_filename == "Beilage_1":
        combined_table = process_beilage_1(tables, headers)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {"Refundierungen": "EUR", "Rechnungsbeträge": "EUR"},
            "year": "2023",
            "original_headers": {
                "columns": [
                    "LST",
                    "Wahlarztkostenrefundierungen",
                    "Wahlarztkostenrechnungsbeträge",
                ]
            },
        }

    elif base_filename in ("Beilage_2"):
        combined_table = process_beilage_2(pdf_path)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {"Refundierungen": "EUR", "Rechnungsbeträge": "EUR"},
            "year": "2023",
            "description": {
                "Refundierungen": "Wahlarztkostenrefundierungen nach Fachrichtung",
                "Rechnungsbeträge": "Wahlarztkostenrechnungsbeträge nach Fachrichtung",
            },
        }

    elif base_filename in (
        "Beilage_3",
        "Beilage_4",
        "Beilage_5",
        "Beilage_5a",
        "Beilage_6",
        "Beilage_6a",
    ):
        combined_table = process_beilage_3(pdf_path)
        
        # For Beilage_3 and Beilage_4, check if any values are floats and convert to int
        if base_filename in ("Beilage_3", "Beilage_4"):
            combined_table = check_and_convert_to_int(combined_table, ["postal", "online", "Gesamt"], pdf_path)
        
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {"postal": "Anzahl", "online": "Anzahl", "Gesamt": "Anzahl"},
            "year": "2023",
            "description": {
                "postal": "postalische Anträge nach Monat und Fachrichtung",
                "online": "online Anträge nach Monat und Fachrichtung",
            },
        }

    elif base_filename in ("Beilage_7", "Beilage_12"):
        combined_table = process_beilage_7(pdf_path)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {
                "postal": "Kalendertage",
                "OnlineMeine": "Kalendertage",
                "OnlineWAH": "Kalendertage",
            },
            "year": "2023",
            "description": {
                "postal": "postalische Anträge nach Monat",
                "OnlineMeine": "online Anträge nach Monat",
                "OnlineWAH": "online Anträge nach Monat",
            },
        }
    elif base_filename in ("Beilage_7a"):
        combined_table = process_beilage_7a(pdf_path)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {
                "postal": "Kalendertage",
                "OnlineMeine": "Kalendertage",
            },
            "year": "2023",
            "description": {
                "postal": "postalische Anträge nach Monat",
                "OnlineMeine": "online Anträge nach Monat",
            },
        }
    elif base_filename in ("Beilage_8", "Beilage_9"):
        combined_table = process_beilage_8(pdf_path)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {"Refundierungen": "EUR", "Rechnungsbeträge": "EUR"},
            "year": "2023",
            "description": {
                "Refundierungen": "Wahlarztkostenrefundierungen nach Fachrichtung",
                "Rechnungsbeträge": "Wahlarztkostenrechnungsbeträge nach Fachrichtung",
            },
        }
    elif base_filename in ("Beilage_10", "Beilage_11"):
        combined_table = process_beilage_10(pdf_path)
        
        # Check if any numeric values are actually floats and convert to int
        combined_table = check_and_convert_to_int(combined_table, ["postal", "online", "Gesamt"], pdf_path)
        
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "units": {"postal": "Anzahl", "online": "Anzahl", "Gesamt": "Anzahl"},
            "year": "2023",
            "description": {
                "postal": "postalische Anträge nach Monat und Fachrichtung",
                "online": "online Anträge nach Monat und Fachrichtung",
            },
        }

    else:
        # Default processing for other Beilage files
        combined_table = pd.concat(tables, ignore_index=True)
        metadata = {
            "question": extract_question_from_pdf(pdf_path),
            "processed_date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        }

    # Convert all numeric columns to integers where appropriate
    for col in combined_table.columns:
        if combined_table[col].dtype == float:
            # Check if all non-null values are integers
            non_null = combined_table[col].dropna()
            if len(non_null) > 0 and all(non_null == non_null.astype(int)):
                # Convert to integer type for both CSV and JSON output
                combined_table[col] = combined_table[col].apply(
                    lambda x: int(x) if pd.notnull(x) else None
                )

    # Save as JSON with metadata
    data_dict = combined_table.to_dict(orient="records")
    
    # Ensure all integer values are properly represented in the data dictionary
    data_dict = ensure_integers_in_dict(data_dict)
    
    data_with_metadata = {
        "metadata": metadata,
        "data": data_dict,
    }
    save_json(save_dir, base_filename, data_with_metadata)
    save_csv(save_dir, base_filename, combined_table)


def verify_json_integers(json_path):
    """
    Verify that integer values are properly saved as integers in the JSON file.
    
    Args:
        json_path (str): Path to the JSON file to verify
        
    Returns:
        bool: True if all integer values are properly saved as integers, False otherwise
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    def check_for_integer_floats(obj, path=""):
        """Check if any floats should be integers in the JSON data"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                current_path = f"{path}.{k}" if path else k
                if not check_for_integer_floats(v, current_path):
                    return False
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                current_path = f"{path}[{i}]"
                if not check_for_integer_floats(item, current_path):
                    return False
        elif isinstance(obj, float) and obj.is_integer():
            print(f"WARNING: Found float with integer value at {path}: {obj}")
            return False
        return True
    
    return check_for_integer_floats(data)


def save_json(save_dir, base_filename, data_with_metadata):
    """
    Save data with metadata as JSON file.
    Ensures integer values are saved as integers, not floats.
    """
    # Custom JSON encoder to handle integer values
    class IntegerEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, pd.Series):
                return obj.tolist()
            if isinstance(obj, float) and obj.is_integer():
                return int(obj)
            return super().default(obj)
    
    # Apply the conversion to the entire data structure
    processed_data = ensure_integers_in_dict(data_with_metadata)

    json_dir = os.path.join(save_dir, "json_files")
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{base_filename}_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4, cls=IntegerEncoder)
    print(f"Saved JSON to: {json_path}")
    
    # Verify that integer values are properly saved
    if not verify_json_integers(json_path):
        print(f"WARNING: Some integer values may not be properly saved in {json_path}")
    else:
        print(f"Integer values verified in {json_path}")


def save_csv(save_dir, base_filename, combined_table):
    """
    Save combined table as CSV file.
    Ensures integer values are saved as integers, not floats.
    """
    # Convert float columns that contain only integers to integer type
    for col in combined_table.columns:
        if combined_table[col].dtype == float:
            # Check if all non-null values are integers
            non_null = combined_table[col].dropna()
            if len(non_null) > 0 and all(non_null == non_null.astype(int)):
                # Convert to integer type
                combined_table[col] = combined_table[col].astype('Int64')  # pandas nullable integer type
    
    csv_dir = os.path.join(save_dir, "csv_files")
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{base_filename}_combined_tables.csv")
    combined_table.to_csv(csv_path, index=False, quoting=1)
    print(f"Saved CSV to: {csv_path}")


def extract_tables_from_pdf(pdf_path, output_dir):
    """Extract tables from a PDF and process them"""
    if pdf_path.endswith("_1.pdf"):
        # beilage 1 used another package
        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)
        return tables

    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables from each page
            page_tables = page.extract_tables()
            if page_tables:
                # Convert to pandas DataFrames
                for table in page_tables:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    tables.append(df)
    return tables


def main():
    # Directory containing the PDFs
    pdf_directory = "./downloaded_files"

    # Directory for saving extracted data
    output_directory = "./extracted_data"

    # Create a log file for warnings
    log_file = os.path.join(output_directory, "processing_warnings.log")
    os.makedirs(output_directory, exist_ok=True)
    
    # Redirect stdout to both console and log file
    import sys
    original_stdout = sys.stdout
    log_f = open(log_file, 'w')
    
    class TeeOutput:
        def __init__(self, file1, file2):
            self.file1 = file1
            self.file2 = file2
        
        def write(self, data):
            self.file1.write(data)
            self.file2.write(data)
            self.file1.flush()
            self.file2.flush()
        
        def flush(self):
            self.file1.flush()
            self.file2.flush()
    
    sys.stdout = TeeOutput(original_stdout, log_f)
    
    try:
        # Process the following PDF files in the directory
        # only files ending with _1.pdf through _12.pdf and 5a, 6a and 7a.pdf
        # other files are handled manually (copy pasting etc)
        pdf_paths = (
            glob.glob(os.path.join(pdf_directory, "*_[1-9].pdf"))
            + glob.glob(os.path.join(pdf_directory, "*_1[0-2].pdf"))
            + glob.glob(os.path.join(pdf_directory, "*_[5-7]a.pdf"))
        )
        for pdf_path in pdf_paths:
            print(f"Processing: {pdf_path}")
            tables = extract_tables_from_pdf(pdf_path, output_directory)
            process_beilage_tables(tables, pdf_path, output_directory)

        print("Finished processing.")
        print("\nTo see warnings with context, run the following command:")
        print(f"grep -A 3 -B 3 WARNING {log_file}")
    finally:
        # Restore stdout
        sys.stdout = original_stdout
        log_f.close()


if __name__ == "__main__":
    main()
