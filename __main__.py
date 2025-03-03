"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as aws

# Define the shell script as user_data
user_data_script = """#!/bin/bash
sudo apt update -y
sudo apt install net-tools -y
sudo apt install -y docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo docker network create --subnet 172.18.0.0/16 vxlan-net
sudo docker network ls
ip a
"""

# Create a VPC
vpc = aws.ec2.Vpc("my-vpc",
   cidr_block="10.0.0.0/16",
   tags={"Name": "my-vpc"}
)

# Create a public subnet
public_subnet = aws.ec2.Subnet("my-subnet",
   vpc_id=vpc.id,
   cidr_block="10.0.0.0/24",
   availability_zone="ap-southeast-1a",
   map_public_ip_on_launch=True,
   tags={"Name": "my-subnet"}
)

# Create an Internet Gateway
igw = aws.ec2.InternetGateway("my-internet-gateway",
   vpc_id=vpc.id,
   tags={"Name": "my-internet-gateway"}
)

# Create a route table
public_route_table = aws.ec2.RouteTable("my-route-table",
   vpc_id=vpc.id,
   tags={"Name": "my-route-table"}
)

# Create a route for the Internet Gateway
route = aws.ec2.Route("igw-route",
   route_table_id=public_route_table.id,
   destination_cidr_block="0.0.0.0/0",
   gateway_id=igw.id
)

# Associate the route table with the public subnet
route_table_association = aws.ec2.RouteTableAssociation("public-route-table-association",
   subnet_id=public_subnet.id,
   route_table_id=public_route_table.id
)

# Create a security group for the public instances
public_security_group = aws.ec2.SecurityGroup("public-secgrp",
   vpc_id=vpc.id,
   description="Enable HTTP and SSH access for public instance",
   ingress=[
       {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},  # Allow SSH
       {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},  # Allow HTTP
   ],
   egress=[
       {"protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]},
   ]
)

# Use the specified Ubuntu 24.04 LTS AMI
ami_id = "ami-01811d4912b4ccb26"

# Create EC2 instances with the script execution
instance1 = aws.ec2.Instance("my-instance-1",
   instance_type="t2.micro",
   vpc_security_group_ids=[public_security_group.id],
   ami=ami_id,
   subnet_id=public_subnet.id,
   key_name="my-key",
   associate_public_ip_address=True,
   user_data=user_data_script,  # Inject script here
   tags={"Name": "my-instance-1"}
)

instance2 = aws.ec2.Instance("my-instance-2",
   instance_type="t2.micro",
   vpc_security_group_ids=[public_security_group.id],
   ami=ami_id,
   subnet_id=public_subnet.id,
   key_name="my-key",
   associate_public_ip_address=True,
   user_data=user_data_script,  # Inject script here
   tags={"Name": "my-instance-2"}
)

# Pulumi exports
pulumi.export("vpcId", vpc.id)
pulumi.export("publicSubnetId", public_subnet.id)
pulumi.export("igwId", igw.id)
pulumi.export("publicRouteTableId", public_route_table.id)
pulumi.export("publicSecurityGroupId", public_security_group.id)
pulumi.export("instance1Id", instance1.id)
pulumi.export("instance1PublicIp", instance1.public_ip)
pulumi.export("instance1PrivateIp", instance1.private_ip)  # ✅ Add private IP
pulumi.export("instance2Id", instance2.id)
pulumi.export("instance2PublicIp", instance2.public_ip)
pulumi.export("instance2PrivateIp", instance2.private_ip)  # ✅ Add private IP
