import boto3
import base64

# AWS Configuration
AWS_REGION = 'ap-south-1'
AMI_ID = 'ami-053b12d3152c0cc71'
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'key001'
SECURITY_GROUP_ID = 'sg-018020d70c7709677'  # Default Security Group ID
SUBNET_IDS = ['subnet-0c6019b285b2f90dd', 'subnet-0de147b2255f5b6ea']  # Subnet IDs
VPC_ID = 'vpc-086967ca84428fabe'
BUCKET_NAME = 'ankitas3bucket8012025'
LAUNCH_TEMPLATE_NAME = 'my-launch-template'
AUTO_SCALING_GROUP_NAME = 'my-auto-scaling-group'

# Initialize AWS clients
ec2 = boto3.resource('ec2', region_name=AWS_REGION)
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
s3 = boto3.client('s3', region_name=AWS_REGION)
elbv2 = boto3.client('elbv2', region_name=AWS_REGION)
autoscaling = boto3.client('autoscaling', region_name=AWS_REGION)

# Create S3 Bucket
def create_bucket(bucket_name):
    print(f"Creating S3 bucket '{bucket_name}'...")
    try:
        s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': AWS_REGION})
        print(f"S3 bucket '{bucket_name}' created.")
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")

# Launch EC2 Instance
def create_instance():
    print("Launching EC2 instance using default Security Group...")
    try:
        user_data = """#!/bin/bash
        sudo yum update -y
        sudo yum install -y git python3 python3-pip nginx
        sudo pip3 install flask gunicorn boto3
        sudo git clone https://github.com/your-repo/flask-app.git /home/flask_app
        cd /home/flask_app
        gunicorn --bind 0.0.0.0:5000 app:app --daemon
        """
        instance = ec2.create_instances(
            ImageId=AMI_ID,
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            SubnetId=SUBNET_IDS[0],
            SecurityGroupIds=[SECURITY_GROUP_ID],
            MinCount=1,
            MaxCount=1,
            UserData=base64.b64encode(user_data.encode('utf-8')).decode('utf-8')
        )
        instance[0].wait_until_running()
        instance_id = instance[0].id
        print(f"EC2 instance '{instance_id}' launched successfully.")
        return instance_id
    except Exception as e:
        print(f"Error launching EC2 instance: {e}")
        return None

# Create Launch Template
def create_launch_template():
    print("Creating Launch Template...")
    try:
        user_data = """#!/bin/bash
        sudo yum update -y
        sudo yum install -y git python3 python3-pip nginx
        sudo pip3 install flask gunicorn boto3
        sudo git clone https://github.com/your-repo/flask-app.git /home/flask_app
        cd /home/flask_app
        gunicorn --bind 0.0.0.0:5000 app:app --daemon
        """
        response = ec2_client.create_launch_template(
            LaunchTemplateName=LAUNCH_TEMPLATE_NAME,
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': INSTANCE_TYPE,
                'KeyName': KEY_NAME,
                'SecurityGroupIds': [SECURITY_GROUP_ID],
                'UserData': base64.b64encode(user_data.encode('utf-8')).decode('utf-8')
            }
        )
        print(f"Launch Template '{LAUNCH_TEMPLATE_NAME}' created successfully.")
        return response['LaunchTemplate']['LaunchTemplateId']
    except Exception as e:
        print(f"Error creating Launch Template: {e}")
        raise

# Create Load Balancer
def create_load_balancer(instance_id):
    print("Creating Application Load Balancer...")
    try:
        alb = elbv2.create_load_balancer(
            Name='my-app-alb',
            Subnets=SUBNET_IDS,
            SecurityGroups=[SECURITY_GROUP_ID],
            Scheme='internet-facing',
            Type='application'
        )
        alb_arn = alb['LoadBalancers'][0]['LoadBalancerArn']
        print(f"ALB '{alb_arn}' created.")

        target_group = elbv2.create_target_group(
            Name='my-target-group',
            Protocol='HTTP',
            Port=5000,
            VpcId=VPC_ID
        )
        target_group_arn = target_group['TargetGroups'][0]['TargetGroupArn']
        print(f"Target group '{target_group_arn}' created.")

        elbv2.register_targets(
            TargetGroupArn=target_group_arn,
            Targets=[{'Id': instance_id}]
        )
        print(f"EC2 instance '{instance_id}' registered to target group.")

        elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[{'Type': 'forward', 'TargetGroupArn': target_group_arn}]
        )
        print("Listener created for the ALB.")

        return alb_arn, target_group_arn
    except Exception as e:
        print(f"Error creating Load Balancer: {e}")
        raise

# Create Auto Scaling Group
def create_auto_scaling_group(target_group_arn):
    print("Creating Auto Scaling Group...")
    try:
        create_launch_template()  # Ensure Launch Template is created
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=AUTO_SCALING_GROUP_NAME,
            LaunchTemplate={
                'LaunchTemplateName': LAUNCH_TEMPLATE_NAME,
                'Version': '$Latest'
            },
            MinSize=1,
            MaxSize=5,
            DesiredCapacity=2,
            TargetGroupARNs=[target_group_arn],
            VPCZoneIdentifier=','.join(SUBNET_IDS)
        )
        print("Auto Scaling Group created successfully.")
    except Exception as e:
        print(f"Error creating Auto Scaling Group: {e}")

# Deploy Infrastructure
def deploy_infrastructure():
    create_bucket(BUCKET_NAME)
    instance_id = create_instance()
    if not instance_id:
        print("Failed to launch EC2 instance. Aborting deployment.")
        return

    alb_arn, target_group_arn = create_load_balancer(instance_id)
    create_auto_scaling_group(target_group_arn)

if __name__ == '__main__':
    deploy_infrastructure()
