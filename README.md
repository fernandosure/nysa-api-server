-Nysa api-server
----------

This is a project that listen commands from the nysa-slackbot and keeps the desired state configuration synced in AWS S3 files.
For each ECS Cluster a new s3 file is created with the desired state configuration in JSON format.

This project only handles the desired state for the clusters and when required the api-server will send a SQS message to nysa-scheduler
that has the responsibility of retrieving the existing ECS configuration and make the necessary changes to match the desired state with the configuration already deployed on AWS.


Usage
-----

The nysa-api-server has the following components
- API
- Control plane UI

The API component is responsible of managing the desired state of the cluster(s) and exposes the following endpoints.

- GET {{base_url}}/api/v1/clusters: Returns the available clusters that nysa is currently managing
- GET {{base_url}}/api/v1/clusters/{{cluster}}/config: Returns the actual cluster desired state and this is the actual configuration that is being updated either using nysa-slack bot and/or nysa-control-plane
- POST {{base_url}}/api/v1/clusters: Creates a new cluster managed by Nysa. The requirement is only one: an existing provisioned ECS cluster with worker nodes attached to it
- PUT {{base_url}}/api/v1/clusters/{{cluster}}/config: If you need to add a NEW service that isn't currently being managed by nysa this endpoint will let you update the cluster desired state to include this new service and with its specifications
- GET {{base_url}}/api/v1/clusters/{{cluster}}/services: Returns the cluster existing/deployed services and its associated image tag and desired count instances
- GET {{base_url}}/api/v1/clusters/{{cluster}}/services/{{service}}/tags: Returns the 10th most recent image tags for a given service.
- PUT {{base_url}}/api/v1/clusters/{{cluster}}/services/{{service}}: Updates the service image tag and/or service desired count instances.
- DELETE {{base_url}}/api/v1/clusters/{{cluster}}/services/{{service}}: Updates the service image tag and/or service desired count instances.

You can get more information about the api and its exposed endpoints along with the required parameters by clicking [here](https://documenter.getpostman.com/view/172769/nysa/RWEgryg4)

YAML Configuration
-----------

You can form as well a YAML configuration file for use it when creating or updating a cluster definition (eg. POST / PUT /api/clusters).
Basically the YAML stackfile is similar in form to a docker-compose yaml file with the following structure

```
vpc:
  id: vpc-xxx
  subnets:
    public: ["subnet-xxx", "subnet-xxx"]
    private: ["subnet-xxx", "subnet-xxx"]

  security_groups:
    public: ["sg-xxx"]
    private: ["sg-xxx"]

logging:
  log_driver: awslogs
  options:
    awslogs-group: /ecs/staging
    awslogs-region: us-east-1
    awslogs-stream-prefix: svc

service_discovery:
  namespace: example.sd

defaults:
  memory: 930
  environment:
    - JAVA_OPTS: -Duser.timezone="UTC" -Xms256m -Xmx640m -XX:MaxMetaspaceSize=256m
    - SPRING_PROFILES_ACTIVE: staging
    - LOGGING_LEVEL_ROOT: INFO
    - SERVER_PORT: 80

services:
  - routing-service:
      image: xxx.dkr.ecr.us-east-1.amazonaws.com/routing-service:latest
      ports:
        - "8080:8080"
      environment:
        - SERVER_PORT: 8080
      desired_count: 1
      elb:
        type: public
        protocol: HTTPS
        ports:
          public: 443
          container: 8080
        certificates:
          - arn:aws:acm:us-east-1:xxx:certificate/xxx-xxx-xxx-xxx-xxx
        dns:
          hosted_zone_id: xxxx
          record_name: staging.example.com
        healthcheck:
          protocol: HTTP
          port: 8080
          path: /health


  - user-service:
      image: xxx.dkr.ecr.us-east-1.amazonaws.com/user-service:latest
      ports:
        - "80:80"
      desired_count: 1
      dns_discovery:
        name: user.staging

 # WORKERS NO PORTS EXPOSED
  - email-worker:
      image: xxx.dkr.ecr.us-east-1.amazonaws.com/email-worker:xxx

```

-----------

# VPC Section
```
vpc:
  id: vpc-xxx
  subnets:
    public: ["subnet-xxx", "subnet-xxx"]
    private: ["subnet-xxx", "subnet-xxx"]

  security_groups:
    public: ["sg-xxx"]
    private: ["sg-xxx"]
```
vpc
- id: the VPC id where the ECS cluster is located

vpc.subnets
- public: subnet-id where the public load balancers (if any) will be placed on
- private: subnet.id where the private load balancers (if any) will be placed on

vpc.security_groups
- public: the security group that will be attached to a public load balancer
- private: the security group that will be attached to private load balancer o service discovery service


# Logging Section
```
logging:
  log_driver: awslogs
  options:
    awslogs-group: /ecs/staging
    awslogs-region: us-east-1
    awslogs-stream-prefix: svc
```
In this section you specify the logging driver and (optional) the parameters to that specific driver. You can use gelf, awslogs, syslog, etc.


# Service Discovery Section
```
service_discovery:
  namespace: example.sd
```

In this section you specify the desired private namespace for registering the services using AWS built-in service discovery based on dns. You cant assing multilevel domains here, only first level domain e.g. example.com

# Defaults Section
```
defaults:
  memory: 930
  environment:
    - JAVA_OPTS: -Duser.timezone="UTC" -Xms256m -Xmx640m -XX:MaxMetaspaceSize=256m
    - SPRING_PROFILES_ACTIVE: staging
    - LOGGING_LEVEL_ROOT: INFO
    - SERVER_PORT: 80
```
In this section you need to specify the hard limit (in MiB) of memory to present to the container and the default environment variables that will be applied to all services within the stackfile. The reason behind the global environment section is for preventing copy and paste all over the place instead if you need to overwrite a specific envvar you can declare that within the service definition and that envvar will have greater precedence over the global one.



# Service Section
## When a service needs to be publicly exposed in a public subnet.
```
services:
  - routing-service:
      image: xxx.dkr.ecr.us-east-1.amazonaws.com/routing-service:latest
      ports:
        - "8080:8080"
      environment:
        - SERVER_PORT: 8080
      desired_count: 1
      elb:
        type: public
        protocol: HTTPS
        ports:
          public: 443
          container: 8080
        certificates:
          - arn:aws:acm:us-east-1:xxx:certificate/xxx-xxx-xxx-xxx-xxx
        dns:
          hosted_zone_id: xxxx
          record_name: staging.example.com
        healthcheck:
          protocol: HTTP
          port: 8080
          path: /health
```
In this section you define an array of services that will be deployed in the cluster.
Each array item corresponds to a different service and you will need to specify the name of the service and then its properties.

- image: Specify the image to start the container from
- ports: if the service will expose ports to the outside then you need to specify those in short syntax (HOST:CONTAINER).
- environment: the environment variable declared in this section have greater precedence over the global definition and will overwrite the global one.
- desired_count: the number of desired instances for the service
- elb: the application load balancer definition.
  - type: whether if the load balancer will be public (will be placed in the public subnet and a public security group assigned) or private (will be place in the private subnet and a private security group assigned)
  - protocol: The protocol for connections from clients to the load balancer (HTTP/HTTPS)
  - ports:
    - public: The port on which the load balancer is listening
    - container: The port on which the target container will receive traffic (this will need to match the public exposed port of the container)
  - certificates: a single item array of the AWS ACM (certificate manager) arn of the certificate to be applied to the ALB
  - dns:
    - hosted_zone_id: route53 hosted_zone_id for updating the CNAME record that the load balancer will listen requests from.
    - record_name: the route53 recordset of from which the ALB will listen requests from (if isnt already created it will create it automatically otherwise will update the recordset)
  - healthcheck: the configurations the load balancer uses when performing health checks on targets.
    - protocol: The protocol the load balancer uses when performing health checks on the container target.
    - port: The port the load balancer uses when performing health checks on the container target.
    - path: The ping path that is the destination on the targets for health checks. The default is /.

## When a service only needs to be reachable by other services that are part of the same cluster.
```
services:
  - user-service:
      image: xxx.dkr.ecr.us-east-1.amazonaws.com/user-service:latest
      ports:
        - "80:80"
      desired_count: 1
      dns_discovery:
        name: user.staging
```


- dns_discovery: When using this feature make sure that you already declared the service discovery namespace that will be used to register the services.
  - name: the name of the route53 recordset to be used by other services to reach this service (it will create an 'A' record) if you want to use the same namespace for different clusters make sure to split the name of the service into a multilevel domain (e.g. `<service_name>.<cluster_name/environment>.<namespace>`)  

## When a service doesn't need to be exposed (worker services)
```
 - email-worker:
     image: xxx.dkr.ecr.us-east-1.amazonaws.com/email-worker:xxx
```
There aren't any exposed ports and no load balancer / service discovery configuration. Only the container image definition and if required (desired_count)

Installation
------------

The project is available as a docker image simply run::

    $ docker run -e PROFILE=prod -e AWS_DEFAULT_REGION=us-east-1 xxx.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server


Configuration
-------------
nysa-api-server its integrated with AWS Secret Manager for managing the secrets used during the application life cycle.
The only configuration that nysa expects as a environment variable is the PROFILE variable that indicates the desired configuration that will get from AWS Secret Manager

- SLACK_NOTIFICATIONS_WEBHOOK_URL: The slack incoming webhook url that the scheduler uses to post back information to the user
- AWS_S3_BUCKET: The bucket name for storing the desired state configuration of the clusters
- AWS_SQS_NOTIFICATION_QUEUE: The SQS queue name for sending deployment jobs to the scheduler

Deploy new changes
------------

If you want to make some changes and then distribute the application you can build a docker image

    $ docker build -t xxx.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server .

and then in the destination server you just need to pull this new image created

    $ docker pull xxx.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server
