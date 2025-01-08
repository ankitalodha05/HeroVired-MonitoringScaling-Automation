# AWS Infrastructure Deployment and Management Assignment

## **Assignment Description**

### **Overview**
Develop a system that automatically manages the lifecycle of a web application hosted on EC2 instances, monitors its health, and reacts to changes in traffic by scaling resources. Additionally, administrators should receive notifications regarding the infrastructure's health and scaling events.

---

## **Assignment Requirements**

### **1. Web Application Deployment**
- **Objective**: Deploy a web application on EC2 and store static files in an S3 bucket.
- **Tasks**:
  - Use `boto3` to create an S3 bucket for storing web application’s static files.
  - Launch an EC2 instance and configure it as a web server using Apache or Nginx.
  - Deploy the web application code onto the EC2 instance.

### **2. Load Balancing with ELB**
- **Objective**: Distribute traffic to multiple EC2 instances for improved availability and scalability.
- **Tasks**:
  - Use `boto3` to create an Application Load Balancer (ALB).
  - Register the EC2 instances with the ALB.

### **3. Auto Scaling Group (ASG) Configuration**
- **Objective**: Ensure the infrastructure can handle traffic spikes or reduce resources during low traffic.
- **Tasks**:
  - Use `boto3` to create an Auto Scaling Group (ASG).
  - Configure the ASG with the EC2 instance as a launch template.
  - Define scaling policies based on metrics like CPU utilization or network traffic.

### **4. SNS Notifications**
- **Objective**: Notify administrators about infrastructure events.
- **Tasks**:
  - Create different SNS topics for various alerts such as health issues, scaling events, or high traffic.
  - Integrate SNS with Lambda to trigger notifications to email or SMS when events occur.

### **5. Infrastructure Automation**
- **Objective**: Automate the deployment, updating, and teardown of the infrastructure.
- **Tasks**:
  - Write a Python script using `boto3` to:
    - Deploy the complete infrastructure.
    - Update individual components as required.
    - Tear down all resources when no longer needed.

---

## **Detailed Components**

### **1. S3 Bucket**
- Stores static files for the web application.
- Used as part of the web server configuration.

### **2. EC2 Instance**
- Hosts the web application.
- Configured with a web server (Apache or Nginx) to serve application traffic.
- Runs user-defined startup scripts for automatic setup during deployment.

### **3. Application Load Balancer (ALB)**
- Distributes incoming traffic across multiple EC2 instances.
- Ensures high availability and fault tolerance.
- Configured with a listener and a target group to route traffic to the EC2 instances.

### **4. Auto Scaling Group (ASG)**
- Automatically adjusts the number of EC2 instances based on traffic.
- Ensures the application can handle load spikes and minimizes cost during low traffic periods.
- Configured with scaling policies triggered by metrics like CPU utilization.

### **5. SNS Notifications**
- Sends alerts for:
  - **Health issues**: EC2 or ALB failures.
  - **Scaling events**: Addition or removal of EC2 instances.
  - **High traffic**: Alerts when traffic surpasses thresholds.
- Notifications sent to email or SMS subscribers.

### **6. Automation Script**
- Single Python script using `boto3` to:
  - Deploy the entire infrastructure.
  - Update any individual components as needed (e.g., EC2 configurations or scaling policies).
  - Tear down all infrastructure components, including S3, EC2, ALB, ASG, and SNS, when no longer required.

---

## **Workflow Summary**

1. **Setup**:
   - Create an S3 bucket for static files.
   - Launch and configure EC2 instances.
   - Deploy the web application.

2. **Load Balancer**:
   - Set up an ALB to distribute traffic across EC2 instances.
   - Register EC2 instances with the ALB target group.

3. **Auto Scaling**:
   - Create an Auto Scaling Group with a launch template.
   - Configure scaling policies for dynamic resource adjustments.

4. **Notifications**:
   - Set up SNS topics and integrate with Lambda for alerting.

5. **Automation**:
   - Deploy, update, and teardown infrastructure using a single Python script.

---

## **Expected Outcomes**

- A fully deployed web application hosted on AWS.
- Automatic scaling and load balancing based on traffic patterns.
- Real-time notifications for health and scaling events.
- Infrastructure lifecycle managed via an automation script.

---

## **Testing Checklist**

- **Web Application Deployment**:
  - Verify the web application is accessible.
  - Confirm the S3 bucket stores static files.

- **Load Balancer**:
  - Test ALB’s ability to distribute traffic to EC2 instances.

- **Auto Scaling**:
  - Simulate traffic to trigger scaling policies.
  - Ensure new instances are added or removed automatically.

- **Notifications**:
  - Test SNS topics by generating events.
  - Confirm notifications are sent to the subscribed email or phone number.

- **Teardown**:
  - Verify that all resources (S3, EC2, ALB, ASG, SNS) are deleted after teardown.

---

## **Documentation Notes**

- Follow best practices for IAM roles and policies.
- Ensure all components are created in the same AWS region for simplicity.
- Use AWS CloudWatch for monitoring application and infrastructure performance.

---

This document provides a detailed roadmap for completing the assignment, focusing on the requirements and expected outcomes without diving into the implementation code. For code-based implementation, refer to the deployment and teardown scripts provided separately.


