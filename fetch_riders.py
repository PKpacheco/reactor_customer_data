import os
import requests
import csv 
import logging
from datetime import datetime
from dotenv import load_dotenv


#load env variables 
load_dotenv()

# logging
log_filename = "fetch_riders_log.log"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_filename), logging.StreamHandler()])

def fetch_riders_data():
    """
    Fetch rider data from the Spare API and return as a list of dict.
    """
    token = os.getenv('SPARELABS_API_TOKEN')
    if not token:
        raise ValueError("API token is missing, set the token in the .env file.")

    # run local for token
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # token_file_path = os.path.join(script_dir, 'token.txt')
    
    # with open(token_file_path, 'r') as f:
    #     token = f.read().strip() 

    url = "https://api.sparelabs.com/v1/riders"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    all_data = []

    # Fetch data page by page until all data is retrieved
    page = 1
    while True:
        params = {'limit': 50, 'skip': (page - 1) * 50}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            logging.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        data = response.json()
        if not data or 'data' not in data:
            break
        
        all_data.extend(data['data'])

        # Log progress fetch riders
        logging.info(f"Fetched {len(all_data)} riders so far...")


        # If there are less than 50 records in the response, it means all data is fetched
        if len(data['data']) < 50:
            break

        page += 1

    logging.info(f"Fetched {len(all_data)} riders.")
    return {'data': all_data}


def save_to_csv(data, filename):
    """
    Save the Spare rider data to a CSV file.
    """
    columns = [
        "Registration Number", 
        "First Name", 
        "Last Name", 
        "Telephone", 
        "Telephone Ext", 
        "Email", 
        "Mailing Address", 
        "City/Town", 
        "Province/State", 
        "Postal/Zip Code"
    ]

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        
        for rider in data["data"]:
            mailing_address_unit = rider['metadata'].get('mailingAddressUnit', '') if rider.get("metadata") else ""
            mailing_address = rider['metadata'].get('mailingAddress', '') if rider.get("metadata") else ""
            full_mailing_address = f"{mailing_address_unit}-{mailing_address}" if mailing_address_unit else mailing_address

            row = [
                rider.get("externalNumericId", ""),
                rider.get("firstName", ""),
                rider.get("lastName", ""),
                rider.get("phoneNumber", ""),
                "",  # Telephone Ext (empty column)
                rider.get("email", ""),
                full_mailing_address,
                # f"{rider['metadata'].get('mailingAddressUnit', '')}-{rider['metadata'].get('mailingAddress', '')}" if rider.get("metadata") else "",
                rider['metadata'].get("mailingCity", "") if rider.get("metadata") else "",
                rider['metadata'].get("provinceState", "") if rider.get("metadata") else "",
                rider['metadata'].get("postalZipCode", "") if rider.get("metadata") else ""
            ]
            writer.writerow(row)
    logging.info(f"Data successfully saved to {filename}")

def main():
    try:
        logging.info("Starting to fetch rider data...")
        riders_data = fetch_riders_data()
        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"riders_{current_date}.csv"
        save_to_csv(riders_data, filename)
        print(f"Data successfully saved to {filename}")


    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching riders data: {e}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
