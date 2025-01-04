import boto3

# Global Variables
AWS_REGION = "us-east-1"
BUCKET_NAME = "my-web-app-bucket"
AUTO_SCALING_GROUP_NAME = "my-auto-scaling-group"
LAUNCH_TEMPLATE_NAME = "my-launch-template"
LOAD_BALANCER_NAME = "my-load-balancer"
TARGET_GROUP_NAME = "my-target-group"
TOPIC_NAME = "my-infra-alerts"

# Initialize AWS Clients
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
elb_client = boto3.client('elbv2', region_name=AWS_REGION)
autoscaling_client = boto3.client('autoscaling', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)

def delete_s3_bucket():
    """Delete the S3 bucket and all objects inside it."""
    try:
        # List and delete all objects in the bucket
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
                print(f"Deleted object: {obj['Key']}")

        # Delete the bucket
        s3_client.delete_bucket(Bucket=BUCKET_NAME)
        print(f"S3 bucket '{BUCKET_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting S3 bucket: {e}")

def terminate_ec2_instances():
    """Terminate all running EC2 instances."""
    try:
        response = ec2_client.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running', 'pending']}
        ])
        instance_ids = [instance['InstanceId'] for reservation in response['Reservations'] for instance in reservation['Instances']]
        if instance_ids:
            ec2_client.terminate_instances(InstanceIds=instance_ids)
            print(f"Terminating EC2 instances: {instance_ids}")
            ec2_client.get_waiter('instance_terminated').wait(InstanceIds=instance_ids)
            print("EC2 instances terminated successfully.")
        else:
            print("No EC2 instances to terminate.")
    except Exception as e:
        print(f"Error terminating EC2 instances: {e}")

def delete_load_balancer_and_target_group():
    """Delete the load balancer and its target group."""
    try:
        # Get the load balancer ARN
        lbs = elb_client.describe_load_balancers(Names=[LOAD_BALANCER_NAME])
        lb_arn = lbs['LoadBalancers'][0]['LoadBalancerArn']

        # Get the target group ARN
        tgs = elb_client.describe_target_groups(Names=[TARGET_GROUP_NAME])
        tg_arn = tgs['TargetGroups'][0]['TargetGroupArn']

        # Delete the load balancer
        elb_client.delete_load_balancer(LoadBalancerArn=lb_arn)
        print(f"Deleting load balancer: {LOAD_BALANCER_NAME}")
        elb_client.get_waiter('load_balancers_deleted').wait(LoadBalancerArns=[lb_arn])
        print("Load balancer deleted successfully.")

        # Delete the target group
        elb_client.delete_target_group(TargetGroupArn=tg_arn)
        print(f"Target group '{TARGET_GROUP_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting load balancer or target group: {e}")

def delete_auto_scaling_group():
    """Delete the auto-scaling group."""
    try:
        autoscaling_client.update_auto_scaling_group(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            MinSize=0,
            DesiredCapacity=0
        )
        autoscaling_client.delete_auto_scaling_group(AutoScalingGroupName=AUTO_SCALING_GROUP_NAME, ForceDelete=True)
        print(f"Auto-scaling group '{AUTO_SCALING_GROUP_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting auto-scaling group: {e}")

def delete_launch_template():
    """Delete the launch template."""
    try:
        ec2_client.delete_launch_template(LaunchTemplateName=LAUNCH_TEMPLATE_NAME)
        print(f"Launch template '{LAUNCH_TEMPLATE_NAME}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting launch template: {e}")

def delete_sns_topic():
    """Delete the SNS topic."""
    try:
        response = sns_client.list_topics()
        for topic in response['Topics']:
            if TOPIC_NAME in topic['TopicArn']:
                sns_client.delete_topic(TopicArn=topic['TopicArn'])
                print(f"SNS topic '{TOPIC_NAME}' deleted successfully.")
                break
    except Exception as e:
        print(f"Error deleting SNS topic: {e}")

def teardown_infrastructure():
    """Teardown all deployed infrastructure."""
    print("Starting infrastructure teardown...")
    delete_s3_bucket()
    terminate_ec2_instances()
    delete_load_balancer_and_target_group()
    delete_auto_scaling_group()
    delete_launch_template()
    delete_sns_topic()
    print("Infrastructure teardown completed.")

if __name__ == "__main__":
    teardown_infrastructure()
