Nysa api-server
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



Installation
------------

The project is available as a docker image simply run::

    $ docker run -e PROFILE=prod -e AWS_DEFAULT_REGION=us-east-1 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server


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

    $ docker build -t 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server .

and then in the destination server you just need to pull this new image created

    $ docker pull 111633362669.dkr.ecr.us-east-1.amazonaws.com/nysa-api-server
