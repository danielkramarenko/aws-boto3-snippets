import os
import boto3
import csv
from tabulate import tabulate


### EC2 Instances BEGIN ###
def create_key_pair(): 
    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        key_pair = ec2_client.create_key_pair(KeyName="ec2-key-pair-2")
        private_key = key_pair["KeyMaterial"]
        with os.fdopen(os.open("aws_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
            handle.write(private_key)

    except Exception as e:
        print(f"Error creating key pair: {e}")

def create_instance(): 
    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        instances = ec2_client.run_instances(ImageId="ami-05b10e08d247fb927", MinCount=1, 
                                            MaxCount=1, InstanceType="t2.micro", KeyName="ec2-key-pair")
        print(instances["Instances"][0]["InstanceId"])

    except Exception as e:
        print(f"Error running instances: {e}")

def get_running_instances():
    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        reservations = ec2_client.describe_instances(Filters=[
            {"Name": "instance-state-name", "Values": ["running"]}, 
            {"Name": "instance-type", "Values": ["t2.micro"]}
        ]).get("Reservations")
        instances_id = []
        for reservation in reservations:
            for instance in reservation["Instances"]:
                instance_id = instance["InstanceId"]
                instance_type = instance["InstanceType"]
                public_ip = instance["PublicIpAddress"]
                private_ip = instance["PrivateIpAddress"]
                print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")
                instances_id.append(instance_id)
        return instances_id

    except Exception as e:
        print(f"Error describing running instances: {e}")
        return []

def stop_instance():
    try:
        instance_id = get_running_instances()[0]
        ec2_client = boto3.client("ec2", region_name="us-east-1") 
        response = ec2_client.stop_instances(InstanceIds=[instance_id])
        print(response)

    except IndexError:
        print("All instances are stopped")
    except Exception as e:
        print(f"Error stopping instances: {e}")

def get_stopped_instances():
    try:
        ec2_client = boto3.client("ec2", region_name="us-east-1")
        reservations = ec2_client.describe_instances(Filters=[
            {"Name": "instance-state-name", "Values": ["stopped"]}, 
            {"Name": "instance-type", "Values": ["t2.micro"]}
        ]).get("Reservations")
        instances_id = []
        for reservation in reservations:
            for instance in reservation["Instances"]:
                instances_id.append(instance["InstanceId"])
        return instances_id

    except Exception as e:
        print(f"Error describing stopped instances: {e}")
        return []

def terminate_instance(): 
    try:
        instance_id = get_stopped_instances()[0]
        ec2_client = boto3.client("ec2", region_name="us-east-1") 
        response = ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(response)
    
    except Exception as e:
        print(f"Error terminating instances: {e}")
### EC2 Instances END ###


### S3 Buckets BEGIN ###
def create_s3_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3', region_name="us-east-1")
        location = {'LocationConstraint': "us-west-2"}
        response = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        print(response)

    except Exception as e:
        print(f"Error creating bucket: {e}")

def get_existing_s3_buckets():
    try:
        s3 = boto3.client('s3')
        response = s3.list_buckets()
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f' S3 bucket: {bucket["Name"]}')

    except Exception as e:
        print(f"Error getting bucket list: {e}")

def upload_file_to_s3(bucket_name, file_path, object_name=None):
    if object_name is None:
        object_name = os.path.basename(file_path)

    try:
        s3_client = boto3.client('s3')
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"File {object_name} has been uploaded to S3")

    except Exception as e:
        print(f"Error uploading file: {e}")

def download_file_from_s3(bucket_name, object_name):
    local_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), object_name)

    try:
        s3_client = boto3.client('s3')
        s3_client.download_file(bucket_name, object_name, local_file_path)
        print(f"File {object_name} has been downloaded from S3")

    except Exception as e:
        print(f"Error downloading file: {e}")

def display_csv_with_header(csv_file_path):
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

def delete_all_objects_in_s3_bucket(bucket_name):
    try:
        s3_client = boto3.client('s3')
        objects_list = s3_client.list_objects(Bucket=bucket_name)
        if 'Contents' in objects_list:
            objects_to_delete = [{'Key': obj['Key']} for obj in objects_list['Contents']]

            while objects_to_delete:
                batch = objects_to_delete[:1000] # get a batch of up to 1000
                del objects_to_delete[:1000]  # remove the processed batch

                s3_client.delete_objects(
                    Bucket=bucket_name,
                    Delete={'Objects': batch, 'Quiet': True}
                )
                print(f"Deleted {len(batch)} objects from S3 bucket...")

    except Exception as e:
        print(f"Error deleting objects in S3 bucket: {e}")

def destroy_s3_bucket(bucket_name):
    try:
        delete_all_objects_in_s3_bucket(bucket_name)
        s3_client = boto3.client('s3')
        response = s3_client.delete_bucket(Bucket=bucket_name)
        print(response)

    except Exception as e:
        print(f"Error destroying bucket: {e}")
### S3 Buckets END ###


if __name__ == "__main__":
    # EC2 Instances
    #create_key_pair()
    create_instance()
    #get_running_instances()
    #stop_instance()
    #terminate_instance()
    
    # S3 Buckets
    #create_s3_bucket('new-bucket-s3')
    #get_existing_s3_buckets()
    #upload_file_to_s3('new-bucket-s3', 'src/dynamodb_exchange_rates.csv', 's3-data.csv')
    #download_file_from_s3('new-bucket-s3', 's3-data.csv')
    #display_csv_with_header('src/s3-data.csv')
    #destroy_s3_bucket('new-bucket-s3')
