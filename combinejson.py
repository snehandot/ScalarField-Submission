import json
import os

def combine_json_files():
    file_names = [
        '8-K.json',
        'Form3.json',
        'Form4.json',
        'Form5.json',
        "10-K.json",
        "10-Q.json"
    ]
    
    combined_data = {}
    
    try:
        for file_name in file_names:
            # Read and parse each JSON file
            with open(file_name, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            
            # Use filename (without extension) as the key
            key = file_name.replace('.json', '')
            combined_data[key] = json_data
        with open('combined_data.json', 'w', encoding='utf-8') as output_file:
            json.dump(combined_data, output_file, indent=2, ensure_ascii=False)
        print('Combined JSON data saved to combined_data.json')

        
        #print('Combined JSON data:', combined_data)
        return combined_data
    
    except FileNotFoundError as e:
        print(f'Error: File not found - {e}')
        return None
    except json.JSONDecodeError as e:
        print(f'Error: Invalid JSON format - {e}')
        return None
    except Exception as e:
        print(f'Error reading files: {e}')
        return None
    # Save the combined data as a JSON file

    

combine_json_files()