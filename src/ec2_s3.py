import requests
import json
import csv
import boto3
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


def get_uah_exchange_rate(date_str, currency_code):
    """
    Retrieves UAH exchange rate for a specific currency from the NBU API for a specific date.

    Args:
        date_str (str): The date in YYYYMMDD format.
        currency_code (str): The currency code (USD or EUR).

    Returns:
        JSON: A dictionary containing the exchange rate, or None if an error occurs.
    """
    url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?valcode={currency_code}&date={date_str}&json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data:
            return {
                data[0]["cc"]: {
                    "rate": data[0]["rate"],
                    "exchangedate": data[0]["exchangedate"]
                }
            }
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {currency_code} data: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding {currency_code} JSON: {e}")
        return None


def get_uah_exchange_combined_rates(str_dates, currency_codes):    
    combined_rates = []
    for date in str_dates:
        for currency in currency_codes:
            currency_rate = get_uah_exchange_rate(date, currency)
            if currency_rate:
                # Append each record as a dictionary to the list
                combined_rates.append({
                    "Currency": currency,
                    "Rate": currency_rate[currency]["rate"],
                    "Exchange Date": currency_rate[currency]["exchangedate"]
                })
    return combined_rates


def json_to_csv(data, filename):
    """
    Converts JSON exchange rate data to a CSV file.

    Args:
        data (dict): The JSON data containing exchange rates.
        filename (str): The name of the CSV file to create.
    """
    if not data:
        print("No data to convert to CSV.")
        return

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    try:
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Currency", "Rate", "Exchange Date"])
            writer.writeheader()  # Write the header row

            for row in data:
                writer.writerow(row)

        print(f"Data written to {file_path}")

    except Exception as e:
        print(f"Error writing to CSV: {e}")


def upload_file_to_s3(bucket_name, file_path, object_name=None):
    """
    Upload a file to an S3 bucket.

    Args:
        bucket_name (str): Name of the S3 bucket.
        file_path (str): Path to the file to upload.
        object_name (str): S3 object name. If not specified, the file name is used.
    """

    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        s3_client = boto3.client('s3')

        with open(file_path, "rb") as f:
            s3_client.upload_fileobj(f, bucket_name, object_name)

        print(f"File '{file_path}' uploaded to '{bucket_name}/{object_name}'")

    except Exception as e:
        print(f"Error uploading file: {e}")


def download_file_from_s3(bucket_name, object_name):
    """
    Downloads a file from an S3 bucket.

    Args:
        bucket_name (str): Name of the S3 bucket.
        object_name (str): S3 object name.
    """

    local_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "s3_exchange_rates.csv")

    try:
        s3_client = boto3.client('s3')

        s3_client.download_file(bucket_name, object_name, local_file_path)

        print(f"File '{object_name}' downloaded from '{bucket_name}' to '{local_file_path}'")

    except Exception as e:
        print(f"Error downloading file: {e}")


def plot_uah_exchange_rates(csv_file, specified_year):
    """Plots UAH exchange rates against USD and EUR for specified year with exact values near markers."""

    try:
        df = pd.read_csv(csv_file)
        df['Exchange Date'] = pd.to_datetime(df['Exchange Date'], format='%d.%m.%Y')
        df_specified_year = df[df['Exchange Date'].dt.year == specified_year]
        df_specified_year['Month'] = df_specified_year['Exchange Date'].dt.month
        pivot_df = df_specified_year.pivot_table(index='Month', columns='Currency', values='Rate')

        plt.figure(figsize=(12, 6))

        # Plot USD
        plt.plot(pivot_df.index, pivot_df['USD'], marker='o', label='USD/UAH')
        for x, y in zip(pivot_df.index, pivot_df['USD']):
            plt.text(x, y, f'{y:.2f}', ha='center', va='bottom')  # Display USD values

        # Plot EUR
        plt.plot(pivot_df.index, pivot_df['EUR'], marker='o', label='EUR/UAH')
        for x, y in zip(pivot_df.index, pivot_df['EUR']):
            plt.text(x, y, f'{y:.2f}', ha='center', va='top')  # Display EUR values

        plt.title(f'UAH Exchange Rates ({specified_year})')
        plt.xlabel('Month')
        plt.ylabel('Exchange Rate')
        plt.xticks(range(1, 13))
        plt.legend()
        plt.grid(False)
        plt.tight_layout() # Adjust plot to fit labels
        
        #plt.show()

        plt.savefig("2022_uah_exchange_rates.png") # Save the figure
        plt.close() # Close to prevent showing the plot
        print("Plot saved to 2022_uah_exchange_rates.png")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
    except KeyError as e:
        print(f"Error: Missing column in CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def plot_uah_current_exchange_rate(csv_file):
    """Plots current UAH exchange rate."""

    try:
        df = pd.read_csv(csv_file)
        df['Exchange Date'] = pd.to_datetime(df['Exchange Date'], format='%d.%m.%Y')
        df.plot(x='Currency', y='Rate', kind='bar', title=f"UAH Exchange Rates ({df['Exchange Date'].iloc[0].strftime('%d.%m.%Y')})")
        # Add values above the bars.
        for index, value in enumerate(df['Rate']):
            plt.text(index, value + 0.1, f'{value:.2f}', ha='center', va='bottom')

        plt.xticks(rotation=45, ha='right') # Rotate x axis labels for better readability
        plt.tight_layout() # Adjust plot to fit labels

        #plt.show()

        plt.savefig("current_exchange_rate.png") # Save the figure
        plt.close() # Close to prevent showing the plot
        print("Plot saved to current_exchange_rate.png")

    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found.")
    except KeyError as e:
        print(f"Error: Missing column in CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    dates_for_2022 = [(datetime(2022, month, 1)).strftime("%Y%m%d") for month in range(1, 13)]    
    current_date = [datetime.now().strftime("%Y%m%d")]
    
    uah_exchange_rates = get_uah_exchange_combined_rates(dates_for_2022, ["USD", "EUR"])

    if uah_exchange_rates:
        print(json.dumps(uah_exchange_rates, indent=4))
        # Convert JSON to CSV
        json_to_csv(uah_exchange_rates, "exchange_rates.csv")
        # Upload a file to an S3 bucket
        upload_file_to_s3("bucket-s3", "src/exchange_rates.csv")
        # Downloads a file from an S3 bucket
        download_file_from_s3("bucket-s3", "exchange_rates.csv")
        # Plots UAH exchange rates
        plot_uah_exchange_rates("src/s3_exchange_rates.csv", 2022)
        #plot_uah_current_exchange_rate("src/s3_exchange_rates.csv")
        # Upload generated plot to an S3 bucket
        upload_file_to_s3("bucket-s3", "2022_uah_exchange_rates.png")
    else:
        print("Failed to retrieve exchange rates.")
