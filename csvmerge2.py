import pandas as pd
import re
import os

# List of files to process
files = [
    'extracted_data_225.csv', 'extracted_data_226.csv', 'extracted_data_227.csv',
    'extracted_data_228.csv', 'extracted_data_229.csv'
]

def clean_label(text, label):
    if pd.isna(text): return ""
    text = str(text)
    # This regex removes the label part like "Name :", "House Number :", etc.
    pattern = rf"^{label}\s*[:\+\?\!\-\=]*\s*"
    return re.sub(pattern, "", text, flags=re.IGNORECASE).strip()

def parse_line2(text):
    if pd.isna(text): return "", ""
    text = str(text)
    relations = ['Fathers Name', 'Husbands Name', 'Mothers Name', 'Others', 'Wife Name']
    for rel in relations:
        if rel.lower() in text.lower():
            name = clean_label(text, rel)
            return name, rel
    return text, ""

def parse_line4(text):
    if pd.isna(text): return None, ""
    text = str(text)
    # Extract age and gender using regex
    age_match = re.search(r'Age\s*[:\+\?\!\-\=]*\s*(\d+)', text, re.IGNORECASE)
    gender_match = re.search(r'Gender\s*[:\+\?\!\-\=]*\s*(\w+)', text, re.IGNORECASE)
    
    age = int(age_match.group(1)) if age_match else None
    gender_str = gender_match.group(1).strip() if gender_match else ""
    
    # Normalize gender
    if gender_str.lower().startswith('f'): gender = 'F'
    elif gender_str.lower().startswith('m'): gender = 'M'
    else: gender = 'Unknown'
    
    return age, gender

def process_voter_file(file_path):
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()

    # Filter rows that look like voter records (usually have "Name" in line1)
    df = df[df['line1'].astype(str).str.contains("Name", case=False, na=False)]
    
    processed_rows = []
    for _, row in df.iterrows():
        voter_name = clean_label(row['line1'], "Name")
        rel_name, rel_type = parse_line2(row['line2'])
        house_no = clean_label(row['line3'], "House Number")
        age, gender = parse_line4(row['line4'])
        
        # Extract EPIC No from top_right_text (often it's the last word or the whole string)
        epic_raw = str(row['top_right_text']).strip() if pd.notna(row['top_right_text']) else ""
        # Sometimes there's a comma at the end or extra text
        epic_no = epic_raw.split()[-1].replace(',', '') if epic_raw else ""
        
        processed_rows.append({
            'Voter Full Name': voter_name,
            'Relative\'s Name': rel_name,
            'Relation Type': rel_type,
            'Age': age,
            'Gender': gender,
            'House No': house_no,
            'EPIC No': epic_no
        })
    
    return pd.DataFrame(processed_rows)

# Merge all files
all_dfs = []
for f in files:
    processed_df = process_voter_file(f)
    if not processed_df.empty:
        all_dfs.append(processed_df)

if all_dfs:
    merged_voters = pd.concat(all_dfs, ignore_index=True)
    # Deduplicate by EPIC Number
    merged_voters = merged_voters.drop_duplicates(subset=['EPIC No'])
    
    # Write to CSV
    merged_voters.to_csv('voters_data_merged_new.csv', index=False)
    
    # Stats calculation
    total_voters = len(merged_voters)
    gender_counts = merged_voters['gender'].value_counts() if 'gender' in merged_voters.columns else merged_voters['Gender'].value_counts()
    
    # Age bins
    age_bins = [0, 18, 25, 35, 45, 60, 100, 150]
    age_labels = ['0-18', '19-25', '26-35', '36-45', '46-60', '61-100', '100+']
    merged_voters['Age Group'] = pd.cut(merged_voters['Age'], bins=age_bins, labels=age_labels)
    age_group_counts = merged_voters['Age Group'].value_counts().sort_index()
    
    relation_counts = merged_voters['Relation Type'].value_counts()
    unique_houses = merged_voters['House No'].nunique()
    
    print("--- Stats Summary ---")
    print(f"Total Voters: {total_voters}")
    print("\nGender Distribution:")
    print(gender_counts)
    print("\nAge Group Distribution:")
    print(age_group_counts)
    print("\nRelation Type Distribution:")
    print(relation_counts)
    print(f"\nUnique Households: {unique_houses}")
else:
    print("No data extracted.")