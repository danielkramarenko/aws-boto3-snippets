import boto3
import csv
from tabulate import tabulate


def create_dynamodb_table():
    """Creates a DynamoDB table with the specified schema."""

    dynamodb = boto3.resource('dynamodb')

    table = dynamodb.create_table(
        TableName='boto3_sdk_exchange_rates',
        KeySchema=[
            {
                'AttributeName': 'Currency',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'Rate',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'Currency',
                'AttributeType': 'S'  # String
            },
            {
                'AttributeName': 'Rate',
                'AttributeType': 'S'  # String
            },
            {
                'AttributeName': 'ExchangeDate',
                'AttributeType': 'S'  # String
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        },
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'ExchangeDateIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'ExchangeDate',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'Currency',
                        'KeyType': 'RANGE'
                    }

                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                'ProvisionedThroughput': {
                    'ReadCapacityUnits': 10,
                    'WriteCapacityUnits': 10
                }
            },
        ]
    )

    print(f"Table status: {table.table_status}")
    table.wait_until_exists()
    print(f"Table {table.table_name} created successfully.")


def display_csv_with_header(csv_file_path):
    """Reads a CSV file and displays it in the console with a formatted header row."""
    try:
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            data = list(reader)  # Read all rows into a list
            if data:
                headers = data[0]  # First row is the header
                rows = data[1:]  # Remaining rows are data
                print(tabulate(rows, headers=headers, tablefmt="grid"))  # Use tabulate for formatted output
            else:
                print("CSV file is empty.")
    except FileNotFoundError:
        print(f"Error: File '{csv_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def load_items_from_csv_to_table(table_name, csv_file_path):
    """Loads items from a CSV file into the DynamoDB table."""
    display_csv_with_header(csv_file_path)
    print()
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            table.put_item(Item=row)
    print(f"Items loaded from {csv_file_path} to DynamoDB table '{table_name}'.")


def add_item(table_name, currency, rate, exchange_date):
    """Adds a new item to the DynamoDB table."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item={'Currency': currency, 'Rate': rate, 'ExchangeDate': exchange_date})
    print(f"Item added: Currency={currency}, Rate={rate}, ExchangeDate={exchange_date}")


def edit_item(table_name, currency, old_rate, new_rate, new_exchange_date=None):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    # Delete the old item
    table.delete_item(Key={'Currency': currency, 'Rate': old_rate})

    # Create a new item with the updated rate
    new_item = {'Currency': currency, 'Rate': new_rate}
    if new_exchange_date:
        new_item['ExchangeDate'] = new_exchange_date
    table.put_item(Item=new_item)

    print(f"Item updated: Currency={currency}, Rate={new_rate}, ExchangeDate={new_exchange_date}")


def delete_item(table_name, currency, rate):
    """Deletes an item from the DynamoDB table."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    table.delete_item(Key={'Currency': currency, 'Rate': rate})
    print(f"Item deleted: Currency={currency}, Rate={rate}")


def query_items(table_name, currency=None, exchange_date=None):
    """Queries items from the DynamoDB table."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    if currency and exchange_date:
        response = table.query(
            IndexName='ExchangeDateIndex',
            KeyConditionExpression='ExchangeDate = :ed and Currency = :c',
            ExpressionAttributeValues={':ed': exchange_date, ':c': currency}
        )

    elif currency:
        response = table.query(
            KeyConditionExpression='Currency = :c',
            ExpressionAttributeValues={':c': currency}
        )

    elif exchange_date:
        response = table.query(
            IndexName='ExchangeDateIndex',
            KeyConditionExpression='ExchangeDate = :ed',
            ExpressionAttributeValues={':ed': exchange_date}
        )
    else:
        response = table.scan()

    items = response.get('Items', [])
    return items


def search_items():
    response = query_items("boto3_sdk_exchange_rates", currency='EUR')
    print("EUR Rates:")
    for obj in response:
        print(obj)


if __name__ == "__main__":
    # create_dynamodb_table()
    # load_items_from_csv_to_table(table_name="boto3_sdk_exchange_rates", 
    #                             csv_file_path="src/dynamodb_exchange_rates.csv")
    # add_item("boto3_sdk_exchange_rates", 'GBP', '52.6101', '27.02.2025')
    # edit_item("boto3_sdk_exchange_rates", 'GBP', '52.6101', '60.0001', '01.01.2025')
    # delete_item("boto3_sdk_exchange_rates", 'GBP', '60.0001')
    search_items()
