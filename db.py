import json
from datetime import datetime
from typing import List, Dict, Any, Union
from api import order
def SEARCH(combined_json: Dict[str, Any], 
                           form_types: List[str] = None,
                           tickers: List[str] = None,
                           years: Union[List[Union[int, str]], int, str] = None,form_sec=None):
    """
    Filter JSON form data by multiple criteria.
    Structure: Forms -> Tickers -> Form Numbers -> Data (with filingDate)
    
    Args:
        combined_json: JSON data with structure {form_type: {ticker: {form_no: {filingDate: "YYYY-MM-DD", ...}}}}
        form_types: List of form types to include (None = return all form types)
        tickers: List of tickers to include (None = return all tickers)
        years: Year(s) to filter by (None = return all years, e.g., [2022, 2023] or 2022)
    
    Returns:
        List of filtered form entries
    """
    json_file_path = "combined_data.json"
    combined_json = load_json_data(json_file_path)
    filtered_forms = []
    
    # Convert years to list of strings
    # years_str = [str(year) for year in years]

    
    # Determine which form types to iterate through
    if form_types:
        # Iterate only through specified form types
        form_types_to_check = [ft for ft in form_types if ft in combined_json]
    else:
        # Iterate through all form types
        form_types_to_check = list(combined_json.keys())
    
    for form_type in form_types_to_check:
        # print("Hi11")
        form_type_data = combined_json[form_type]
        if not isinstance(form_type_data, dict):
            continue
        
        # Determine which tickers to iterate through
        if tickers:
            # Direct matching - names must match exactly
            tickers_to_check = [ticker for ticker in form_type_data.keys() 
                               if ticker in tickers]
        else:
            # Iterate through all tickers
            tickers_to_check = list(form_type_data.keys())
        
        # print("Hi22")

        for ticker in tickers_to_check:
            ticker_data = form_type_data[ticker]

            # print("Hi33")

            # Iterate through form numbers (third level)
            for form_data in ticker_data:
    
                #print(form_data)
                # Check filing date (skip entries without filing date)
                filing_date = form_data['filingDate']

                
                    
                # print("Hi44")

                # Apply year filter (None means include all years)
                if years:
                    if int(filing_date[:4]) in years:
                        # print("In")
                        pass
                    else:
                        continue
                
                if form_type=="10-K" or form_type=="10-Q":
                    # print("Here1")
                    url=form_data['url']
                    # print("Here2")
                    form_data=order(url,form_sec)
                    # print("Here3")
                    print(type(form_data))
                filtered_entry = {
                    'formType': form_type,
                    'ticker': ticker,
                    'data': form_data
                }
                
                # print(filtered_entry,"joke")
                filtered_forms.append(filtered_entry)
    print(len(filtered_forms),"final")
    return filtered_forms

def load_json_data(file_path: str) -> Dict[str, Any]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Loaded JSON data as dictionary
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        raise
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        raise
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        raise
# Example usage
if __name__ == "__main__":
    # Load JSON data from file
    try:
        json_file_path = "combined_data.json"  # Replace with your JSON file path
        combined_json = load_json_data(json_file_path)
        
        # Example: Filter by years [2022, 2023]
        # results_years = filter_forms_by_criteria(combined_json, years=[2022, 2023])
        
        # Example: Get all forms (no filters)
        # all_results = filter_forms_by_criteria(combined_json)
        
        # Example: Filter by multiple criteria
        filtered_results = SEARCH(
            combined_json, 
            form_types=['Form3'], 
            tickers=['NVDA'], 
            years=[]
        )
        # print(filtered_results,"lol")
        
        # Use the results as needed in your application
        # The function returns a list of dictionaries with the filtered data
            
    except Exception as e:
        print(f"Failed to process JSON file: {e}")
        print("Please ensure your JSON file exists and has the correct structure:")
        print('{"FormType": {"Ticker": {"FormNo": {"filingDate": "YYYY-MM-DD", ...}}}}')
            
    except Exception as e:
        print(f"Failed to process JSON file: {e}")
        print("Please ensure your JSON file exists and has the correct structure:")
        print('{"FormType": {"Ticker": {"FormNo": {"filingDate": "YYYY-MM-DD", ...}}}}')