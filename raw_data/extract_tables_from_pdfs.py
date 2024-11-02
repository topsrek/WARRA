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
                if index in [0, 1, 2, 3, 4]:  # Skip header rows
                    continue
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

    # Save as JSON with metadata
    data_with_metadata = {
        "metadata": metadata,
        "data": combined_table.to_dict(orient="records"),
    }
    save_json(save_dir, base_filename, data_with_metadata)
    save_csv(save_dir, base_filename, combined_table)


def save_json(save_dir, base_filename, data_with_metadata):

    json_dir = os.path.join(save_dir, "json_files")
    os.makedirs(json_dir, exist_ok=True)
    json_path = os.path.join(json_dir, f"{base_filename}_data.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_with_metadata, f, ensure_ascii=False, indent=4)
    print(f"Saved JSON to: {json_path}")


def save_csv(save_dir, base_filename, combined_table):
    csv_dir = os.path.join(save_dir, "csv_files")
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, f"{base_filename}_combined_tables.csv")
    combined_table.to_csv(csv_path, index=False, quoting=1)
    print(f"Saved CSV to: {csv_path}")


def extract_tables_from_pdf(pdf_path, output_dir):
    """Extract tables from a PDF and process them"""
    if 0:
        # Extract all tables from the PDF
        tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)

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

    process_beilage_tables(tables, pdf_path, output_dir)


def main():
    # Directory containing the PDFs
    pdf_directory = "downloaded_files"

    # Directory for saving extracted data
    output_directory = "extracted_data"

    # Process all PDF files in the directory
    for pdf_path in glob.glob(os.path.join(pdf_directory, "*_12.pdf")):
        print(f"Processing: {pdf_path}")
        tables = extract_tables_from_pdf(pdf_path, output_directory)
        process_beilage_tables(tables, pdf_path, output_directory)

    print("Finished processing.")


if __name__ == "__main__":
    main()
