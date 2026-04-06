#!/usr/bin/env python3
"""
Diigo Rescue - Convert Diigo HTML bookmarks to CSV
Copyright (c) 2026 Leandro Pérez
License: MIT
https://github.com/leandroprz/diigo-rescue
"""

import sys
import csv
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10MB

def parse_date_to_timestamp(date_str):
    """Convert date string like 'Jan 30, 2026' to Unix timestamp."""
    try:
        dt = datetime.strptime(date_str.strip(), '%b %d, %Y')
        return int(dt.timestamp())
    except:
        return ''

def extract_bookmarks(html_file):
    """Extract bookmarks from a Diigo HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    
    bookmarks = []
    items = soup.find_all('div', class_='ListItem')
    
    for item in items:
        # Skip empty divs
        if item.get('style') and 'display:none' in item.get('style'):
            continue
            
        bookmark = {'url': '', 'title': '', 'note': '', 'tags': '', 'created': ''}
        
        # Extract URL and title
        title_elem = item.find('h3', class_='titleInner')
        if title_elem:
            link = title_elem.find('a')
            if link:
                bookmark['url'] = link.get('href', '')
                bookmark['title'] = link.get_text(strip=True)
        
        # Extract date
        date_elem = item.find('div', class_='date')
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            bookmark['created'] = parse_date_to_timestamp(date_text)
        
        # Extract description
        desc_elem = item.find('div', class_='description')
        if desc_elem:
            bookmark['note'] = desc_elem.get_text(strip=True)
        
        # Extract tags
        tags_div = item.find('div', class_='tags')
        if tags_div:
            tag_spans = tags_div.find_all('span', class_='wrapper')
            tags = [span.get('title', '') for span in tag_spans if span.get('title')]
            if tags:
                bookmark['tags'] = ', '.join(tags)
        
        # Only add if we have at least a URL
        if bookmark['url']:
            bookmarks.append(bookmark)
    
    return bookmarks

def find_duplicates(bookmarks):
    """Find duplicate URLs in bookmarks."""
    url_map = {}
    duplicates = []
    
    for i, bookmark in enumerate(bookmarks):
        url = bookmark['url']
        if url in url_map:
            duplicates.append({
                'url': url,
                'first_index': url_map[url],
                'duplicate_index': i,
                'first': bookmarks[url_map[url]],
                'duplicate': bookmark
            })
        else:
            url_map[url] = i
    
    return duplicates

def remove_duplicates(bookmarks):
    """Remove duplicate URLs, keeping only the first occurrence."""
    seen_urls = set()
    unique_bookmarks = []
    
    for bookmark in bookmarks:
        url = bookmark['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_bookmarks.append(bookmark)
    
    return unique_bookmarks

def write_csv_files(bookmarks, output_dir):
    """Write bookmarks to CSV files, splitting when file size exceeds limit."""
    output_dir.mkdir(exist_ok=True)
    
    file_num = 1
    current_file = output_dir / f'bookmarks_{file_num:02d}.csv'
    current_size = 0
    total_written = 0
    files_created = []
    
    csv_file = open(current_file, 'w', newline='', encoding='utf-8')
    writer = csv.DictWriter(csv_file, fieldnames=['url', 'title', 'note', 'tags', 'created'])
    writer.writeheader()
    files_created.append(current_file)
    
    for bookmark in bookmarks:
        writer.writerow(bookmark)
        total_written += 1
        
        # Check file size
        csv_file.flush()
        current_size = current_file.stat().st_size
        
        if current_size >= MAX_FILE_SIZE:
            csv_file.close()
            file_num += 1
            current_file = output_dir / f'bookmarks_{file_num:02d}.csv'
            csv_file = open(current_file, 'w', newline='', encoding='utf-8')
            writer = csv.DictWriter(csv_file, fieldnames=['url', 'title', 'note', 'tags', 'created'])
            writer.writeheader()
            files_created.append(current_file)
            current_size = 0
    
    csv_file.close()
    return files_created, total_written

def validate_csv(csv_file, expected_count):
    """Validate CSV file has correct structure and row count."""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Check all rows have URL
            for i, row in enumerate(rows):
                if not row.get('url'):
                    return False, f"Row {i+1} missing URL"
            
            return True, len(rows)
    except Exception as e:
        return False, str(e)

def main():
    print("\nDiigo Rescue - Bookmark converter")
    print("-"*40+"\n")
    
    if len(sys.argv) != 2:
        print("Usage: python diigo_rescue.py <path_to_folder>")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    
    if not input_dir.is_dir():
        print(f"Error: {input_dir} is not a valid directory")
        sys.exit(1)
    
    # Find HTML files
    html_files = list(input_dir.glob('*.html')) + list(input_dir.glob('*.htm'))
    
    if not html_files:
        print("No HTML files found in the directory")
        sys.exit(1)
    
    print(f"Found {len(html_files)} HTML file(s):")
    
    # Extract bookmarks
    all_bookmarks = []
    failed = []
    
    for html_file in html_files:
        try:
            bookmarks = extract_bookmarks(html_file)
            all_bookmarks.extend(bookmarks)
            print(f"    {html_file.name}: {len(bookmarks)} bookmark(s)")
        except Exception as e:
            failed.append((html_file.name, str(e)))
            print(f"    {html_file.name}: Failed - {e}")
    
    if not all_bookmarks:
        print("\nNo bookmarks extracted")
        sys.exit(1)
    
    # Track original count
    original_count = len(all_bookmarks)
    
    # Check for duplicates
    duplicates = find_duplicates(all_bookmarks)
    
    if duplicates:
        print(f"\n{'-'*40}")
        print(f"Duplicate URLs found: {len(duplicates)}")
        print('-'*40)
        
        for i, dup in enumerate(duplicates[:10], 1):  # Show max 10 examples
            print(f"\n{i}. URL: {dup['url']}")
            print(f"   First occurrence:")
            print(f"     Title: {dup['first']['title']}")
            print(f"     Tags: {dup['first']['tags']}")
            print(f"   Duplicate:")
            print(f"     Title: {dup['duplicate']['title']}")
            print(f"     Tags: {dup['duplicate']['tags']}")
        
        if len(duplicates) > 10:
            print(f"\n   ... and {len(duplicates) - 10} more duplicate(s)")
        
        print("\nDo you want to remove duplicates? (keep only first occurrence)")
        choice = input("Enter 'y' to remove duplicates, or 'n' to keep all: ").lower().strip()
        
        if choice == 'y':
            all_bookmarks = remove_duplicates(all_bookmarks)
            print(f"\nRemoved {len(duplicates)} duplicate(s). Proceeding with {len(all_bookmarks)} unique bookmarks.")
        else:
            print("\nKeeping all bookmarks including duplicates.")
    
    # Write CSV files
    output_dir = input_dir / 'CSV_Export'
    print(f"\nWriting to {output_dir}/")
    
    csv_files, written_count = write_csv_files(all_bookmarks, output_dir)
    
    # Validate
    print("\nValidating CSV files...")
    total_validated = 0
    validation_failed = []
    
    for csv_file in csv_files:
        valid, result = validate_csv(csv_file, written_count)
        if valid:
            print(f"    {csv_file.name}: {result} row(s)")
            total_validated += result
        else:
            validation_failed.append((csv_file.name, result))
            print(f"    {csv_file.name}: {result}")
    
    # Summary
    print("\nSummary")
    print("-"*40)
    print(f"HTML files processed: {len(html_files)}")
    print(f"Total bookmarks extracted: {original_count}")
    if duplicates:
        print(f"Duplicate URLs found: {len(duplicates)}")
        print(f"Unique bookmarks exported: {len(all_bookmarks)}")
    else:
        print(f"Bookmarks exported: {len(all_bookmarks)}")
    print(f"Successfully written: {written_count}")
    print(f"Validated: {total_validated}")
    print(f"CSV files created: {len(csv_files)}")
    
    if failed:
        print(f"\nFailed HTML files: {len(failed)}")
        for filename, error in failed:
            print(f"  - {filename}: {error}")
    
    if validation_failed:
        print(f"\nValidation failures: {len(validation_failed)}")
        for filename, error in validation_failed:
            print(f"  - {filename}: {error}")
    
    if total_validated == len(all_bookmarks):
        print("\nAll bookmarks successfully exported and validated!")
    else:
        print(f"\nWarning: Validated count ({total_validated}) doesn't match extracted count ({len(all_bookmarks)})")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == '__main__':
    main()