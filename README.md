# aws-boto3-snippets
AWS Python Boto3 SDK

AWS EC2 Instances Computing Automation
    create_key_pair()
    create_instance()
    get_running_instances()
    stop_instance()
    get_stopped_instances()
    terminate_instance()

AWS S3 Buckets Automation
    create_s3_bucket(bucket_name)
    get_existing_s3_buckets()
    upload_file_to_s3(bucket_name, file_path, object_name=None)
    download_file_from_s3(bucket_name, object_name)
    display_csv_with_header(csv_file_path)
    delete_all_objects_in_s3_bucket(bucket_name)
    destroy_s3_bucket(bucket_name)

AWS DynamoDB Automation
    create_dynamodb_table()
    display_csv_with_header(csv_file_path)
    load_items_from_csv_to_table(table_name, csv_file_path)
    add_item(table_name, currency, rate, exchange_date)
    edit_item(table_name, currency, old_rate, new_rate, new_exchange_date=None)
    delete_item(table_name, currency, rate)
    query_items(table_name, currency=None, exchange_date=None)
    search_items()

EC2 S3 Amazon Web Services
    get_uah_exchange_rate(date_str, currency_code)
    get_uah_exchange_combined_rates(str_dates, currency_codes)
    json_to_csv(data, filename)
    upload_file_to_s3(bucket_name, file_path, object_name=None)
    download_file_from_s3(bucket_name, object_name)
    plot_uah_exchange_rates(csv_file, specified_year)
    plot_uah_current_exchange_rate(csv_file)
