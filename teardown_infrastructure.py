import boto3

# AWS Configuration
AWS_REGION = 'ap-south-1'
BUCKET_NAME = 'ankitas3bucket8012025'
ALB_NAME = 'my-app-alb'
TARGET_GROUP_NAME = 'my-target-group'
AUTO_SCALING_GROUP_NAME = 'my-auto-scaling-group'
LAUNCH_TEMPLATE_NAME = 'my-launch-template'

# Initialize AWS clients
ec2 = boto3.resource('ec2', region_name=AWS_REGION)
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
elbv2 = boto3.client('elbv2', region_name=AWS_REGION)
autoscaling = boto3.client('autoscaling', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)

# Delete S3 Bucket
def delete_bucket(bucket_name):
    print(f"Deleting S3 bucket '{bucket_name}'...")
    try:
        # Delete all objects in the bucket
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            for obj in response['Contents']:
                s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                print(f"Deleted object: {obj['Key']}")
        # Delete the bucket itself
        s3.delete_bucket(Bucket=bucket_name)
        print(f"S3 bucket '{bucket_name}' deleted.")
    except Exception as e:
        print(f"Error deleting S3 bucket: {e}")

# Terminate EC2 Instances
def terminate_instances():
    print("Terminating EC2 instances...")
    try:
        instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'pending']}])
        for instance in instances:
            instance_id = instance.id
            instance.terminate()
            print(f"Terminating instance: {instance_id}")
            instance.wait_until_terminated()
            print(f"Instance '{instance_id}' terminated.")
    except Exception as e:
        print(f"Error terminating EC2 instances: {e}")

# Delete Load Balancer and Target Group
def delete_load_balancer_and_target_group():
    print("Deleting Application Load Balancer and Target Group...")
    try:
        load_balancers = elbv2.describe_load_balancers(Names=[ALB_NAME])
        for lb in load_balancers['LoadBalancers']:
            alb_arn = lb['LoadBalancerArn']
            elbv2.delete_load_balancer(LoadBalancerArn=alb_arn)
            print(f"Deleting ALB: {alb_arn}")

        waiter = elbv2.get_waiter('load_balancers_deleted')
        waiter.wait(LoadBalancerArns=[alb_arn])
        print("ALB deleted.")

        target_groups = elbv2.describe_target_groups(Names=[TARGET_GROUP_NAME])
        for tg in target_groups['TargetGroups']:
            target_group_arn = tg['TargetGroupArn']
            elbv2.delete_target_group(TargetGroupArn=target_group_arn)
            print(f"Target group '{TARGET_GROUP_NAME}' deleted.")
    except Exception as e:
        print(f"Error deleting ALB or Target Group: {e}")

# Delete Auto Scaling Group
def delete_auto_scaling_group():
    print("Deleting Auto Scaling Group...")
    try:
        autoscaling.update_auto_scaling_group(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            MinSize=0,
            DesiredCapacity=0
        )
        autoscaling.delete_auto_scaling_group(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            ForceDelete=True
        )
        print(f"Auto Scaling Group '{AUTO_SCALING_GROUP_NAME}' deleted.")
    except Exception as e:
        print(f"Error deleting Auto Scaling Group: {e}")

# Delete Launch Template
def delete_launch_template():
    print("Deleting Launch Template...")
    try:
        ec2_client.delete_launch_template(LaunchTemplateName=LAUNCH_TEMPLATE_NAME)
        print(f"Launch Template '{LAUNCH_TEMPLATE_NAME}' deleted.")
    except Exception as e:
        print(f"Error deleting Launch Template: {e}")

# Teardown Infrastructure
def teardown_infrastructure():
    delete_bucket(BUCKET_NAME)
    terminate_instances()
    delete_load_balancer_and_target_group()
    delete_auto_scaling_group()
    delete_launch_template()
    print("Teardown completed.")

# Run the teardown
if __name__ == '__main__':
    teardown_infrastructure()
