import boto3
import base64
from botocore.exceptions import NoCredentialsError

# Global Variables
AWS_REGION = "us-east-1"
KEY_NAME = "2025"  # Replace with your key pair name
SECURITY_GROUP_ID = "sg-00254169f81cec7df"  # Replace with your security group ID
SUBNET_IDS = ["subnet-044e72c086482387d", "subnet-004a47b3f20739b81"]  # Replace with your subnet IDs
VPC_ID = "vpc-0719c24f48530d957"  # Replace with your VPC ID
AMI_ID = "ami-0e2c8caa4b6378d8c"  # Replace with an Ubuntu AMI ID in your region
BUCKET_NAME = "my-web-app-bucket"
TOPIC_NAME = "my-infra-alerts"

# Initialize AWS Clients
ec2 = boto3.resource('ec2', region_name=AWS_REGION)
ec2_client = boto3.client('ec2', region_name=AWS_REGION)
s3_client = boto3.client('s3', region_name=AWS_REGION)
elb_client = boto3.client('elbv2', region_name=AWS_REGION)
autoscaling_client = boto3.client('autoscaling', region_name=AWS_REGION)
sns_client = boto3.client('sns', region_name=AWS_REGION)


def create_s3_bucket():
    """Create an S3 bucket for storing static files."""
    try:
        if AWS_REGION == "us-east-1":
            # For us-east-1, no LocationConstraint
            s3_client.create_bucket(Bucket=BUCKET_NAME)
        else:
            # For other regions, specify LocationConstraint
            s3_client.create_bucket(
                Bucket=BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
            )
        print(f"S3 bucket '{BUCKET_NAME}' created successfully.")
    except s3_client.exceptions.BucketAlreadyExists as e:
        print(f"Bucket already exists: {e}")
    except s3_client.exceptions.BucketAlreadyOwnedByYou as e:
        print(f"Bucket already owned by you: {e}")
    except Exception as e:
        print(f"Error creating S3 bucket: {e}")


def launch_ec2_instance():
    """Launch an EC2 instance and configure it as a web server."""
    try:
        instance = ec2.create_instances(
            ImageId=AMI_ID,
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName=KEY_NAME,
            SecurityGroupIds=[SECURITY_GROUP_ID],
            SubnetId=SUBNET_IDS[0],
            UserData="""#!/bin/bash
            sudo apt update
            sudo apt install -y apache2
            echo "Hello World from EC2" | sudo tee /var/www/html/index.html
            sudo systemctl start apache2
            """,
        )[0]
        print(f"EC2 instance '{instance.id}' launched successfully.")
        return instance.id
    except Exception as e:
        print(f"Error launching EC2 instance: {e}")


def wait_for_instance_running(instance_id):
    """Wait until the EC2 instance is in the 'running' state."""
    print(f"Waiting for EC2 instance '{instance_id}' to reach 'running' state...")
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])
    print(f"EC2 instance '{instance_id}' is now running.")


def create_load_balancer():
    """Create an Application Load Balancer and Target Group."""
    try:
        lb = elb_client.create_load_balancer(
            Name='my-load-balancer',
            Subnets=SUBNET_IDS,
            SecurityGroups=[SECURITY_GROUP_ID],
            Scheme='internet-facing'
        )
        lb_arn = lb['LoadBalancers'][0]['LoadBalancerArn']
        print(f"Load Balancer created: {lb_arn}")

        target_group = elb_client.create_target_group(
            Name='my-target-group',
            Protocol='HTTP',
            Port=80,
            VpcId=VPC_ID
        )
        tg_arn = target_group['TargetGroups'][0]['TargetGroupArn']
        print(f"Target Group created: {tg_arn}")

        return lb_arn, tg_arn
    except Exception as e:
        print(f"Error creating Load Balancer: {e}")


def configure_auto_scaling(tg_arn):
    """Create Auto Scaling Group and Policies."""
    try:
        user_data = """#!/bin/bash
        sudo apt update
        sudo apt install -y apache2
        echo "Hello World from EC2" | sudo tee /var/www/html/index.html
        sudo systemctl start apache2
        """
        user_data_encoded = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")

        # Create Launch Template
        launch_template = ec2_client.create_launch_template(
            LaunchTemplateName='my-launch-template',
            LaunchTemplateData={
                'ImageId': AMI_ID,
                'InstanceType': 't2.micro',
                'KeyName': KEY_NAME,
                'SecurityGroupIds': [SECURITY_GROUP_ID],
                'UserData': user_data_encoded
            }
        )
        template_id = launch_template['LaunchTemplate']['LaunchTemplateId']
        print(f"Launch Template created: {template_id}")

        # Create Auto Scaling Group
        autoscaling_client.create_auto_scaling_group(
            AutoScalingGroupName='my-auto-scaling-group',
            LaunchTemplate={
                'LaunchTemplateId': template_id,
                'Version': '$Latest'
            },
            MinSize=1,
            MaxSize=3,
            DesiredCapacity=1,
            TargetGroupARNs=[tg_arn],
            VPCZoneIdentifier=",".join(SUBNET_IDS)
        )
        print("Auto Scaling Group created.")

        # Configure Scaling Policies
        autoscaling_client.put_scaling_policy(
            AutoScalingGroupName='my-auto-scaling-group',
            PolicyName='scale-out',
            AdjustmentType='ChangeInCapacity',
            ScalingAdjustment=1,
            Cooldown=300
        )
        print("Scaling policy configured.")
    except Exception as e:
        print(f"Error configuring Auto Scaling: {e}")


def setup_sns_notifications():
    """Set up SNS notifications for infrastructure events."""
    try:
        topic = sns_client.create_topic(Name=TOPIC_NAME)
        topic_arn = topic['TopicArn']
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint='your-email@example.com'  # Replace with your valid email
        )
        print(f"SNS topic created and email subscription added: {topic_arn}")
    except Exception as e:
        print(f"Error setting up SNS: {e}")


def deploy_infrastructure():
    """Automate the deployment of the web application infrastructure."""
    print("Starting infrastructure deployment...")
    create_s3_bucket()
    instance_id = launch_ec2_instance()
    wait_for_instance_running(instance_id)  # Ensure instance is running before proceeding
    lb_arn, tg_arn = create_load_balancer()
    elb_client.register_targets(
        TargetGroupArn=tg_arn,
        Targets=[{'Id': instance_id}]
    )
    print("EC2 instance registered with Load Balancer.")
    configure_auto_scaling(tg_arn)
    setup_sns_notifications()
    print("Infrastructure deployed successfully.")


if __name__ == "__main__":
    deploy_infrastructure()
