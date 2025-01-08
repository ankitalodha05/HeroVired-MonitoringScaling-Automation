import boto3

# AWS Configuration
AWS_REGION = 'ap-south-1'
BUCKET_NAME = 'ankitas3bucket8012025'
LAUNCH_TEMPLATE_NAME = 'my-launch-template'
AUTO_SCALING_GROUP_NAME = 'my-auto-scaling-group'
SNS_TOPIC_NAME = 'my-infra-notifications'

# Initialize AWS clients
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)
elbv2 = boto3.client('elbv2', region_name=AWS_REGION)
autoscaling = boto3.client('autoscaling', region_name=AWS_REGION)
sns = boto3.client('sns', region_name=AWS_REGION)

# Delete S3 Bucket
def delete_bucket(bucket_name):
    print(f"Deleting S3 bucket '{bucket_name}'...")
    try:
        objects = s3.list_objects_v2(Bucket=bucket_name).get('Contents', [])
        for obj in objects:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
            print(f"Deleted object '{obj['Key']}' from bucket '{bucket_name}'.")

        s3.delete_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' deleted.")
    except Exception as e:
        print(f"Error deleting S3 bucket: {e}")

# Delete Auto Scaling Group
def delete_auto_scaling_group(asg_name):
    print(f"Deleting Auto Scaling Group '{asg_name}'...")
    try:
        autoscaling.update_auto_scaling_group(AutoScalingGroupName=asg_name, MinSize=0, DesiredCapacity=0)
        autoscaling.delete_auto_scaling_group(AutoScalingGroupName=asg_name, ForceDelete=True)
        print(f"Auto Scaling Group '{asg_name}' deleted.")
    except Exception as e:
        print(f"Error deleting Auto Scaling Group: {e}")

# Delete Launch Template
def delete_launch_template(template_name):
    print(f"Deleting Launch Template '{template_name}'...")
    try:
        ec2_client.delete_launch_template(LaunchTemplateName=template_name)
        print(f"Launch Template '{template_name}' deleted.")
    except Exception as e:
        print(f"Error deleting Launch Template: {e}")

# Delete Load Balancer
def delete_load_balancer(lb_name):
    print(f"Deleting Load Balancer '{lb_name}'...")
    try:
        load_balancers = elbv2.describe_load_balancers()['LoadBalancers']
        for lb in load_balancers:
            if lb['LoadBalancerName'] == lb_name:
                lb_arn = lb['LoadBalancerArn']
                listeners = elbv2.describe_listeners(LoadBalancerArn=lb_arn)['Listeners']
                for listener in listeners:
                    elbv2.delete_listener(ListenerArn=listener['ListenerArn'])
                    print(f"Deleted listener '{listener['ListenerArn']}'.")

                elbv2.delete_load_balancer(LoadBalancerArn=lb_arn)
                print(f"Load Balancer '{lb_name}' deleted.")
    except Exception as e:
        print(f"Error deleting Load Balancer: {e}")

# Delete Target Group
def delete_target_group(target_group_name):
    print(f"Deleting Target Group '{target_group_name}'...")
    try:
        target_groups = elbv2.describe_target_groups()['TargetGroups']
        for tg in target_groups:
            if tg['TargetGroupName'] == target_group_name:
                elbv2.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
                print(f"Target Group '{target_group_name}' deleted.")
    except Exception as e:
        print(f"Error deleting Target Group: {e}")

# Terminate EC2 Instances
def terminate_instances():
    print("Terminating EC2 instances...")
    try:
        instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}])['Reservations']
        for reservation in instances:
            for instance in reservation['Instances']:
                instance_id = instance['InstanceId']
                ec2_client.terminate_instances(InstanceIds=[instance_id])
                print(f"Terminating instance '{instance_id}'...")
    except Exception as e:
        print(f"Error terminating EC2 instances: {e}")

# Delete SNS Topic
def delete_sns_topic(topic_name):
    print(f"Deleting SNS topic '{topic_name}'...")
    try:
        topics = sns.list_topics()['Topics']
        for topic in topics:
            if topic_name in topic['TopicArn']:
                sns.delete_topic(TopicArn=topic['TopicArn'])
                print(f"SNS topic '{topic_name}' deleted.")
    except Exception as e:
        print(f"Error deleting SNS topic: {e}")

# Teardown all resources
def teardown_infrastructure():
    delete_auto_scaling_group(AUTO_SCALING_GROUP_NAME)
    delete_launch_template(LAUNCH_TEMPLATE_NAME)
    terminate_instances()
    delete_load_balancer('my-app-alb')
    delete_target_group('my-target-group')
    delete_bucket(BUCKET_NAME)
    delete_sns_topic(SNS_TOPIC_NAME)
    print("Teardown complete.")

if __name__ == '__main__':
    teardown_infrastructure()
