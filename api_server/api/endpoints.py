import json
from flask import jsonify, request
from api_server import jsonschema
from api_server.api import api
from api_server.logger import log
from api_server.sqs_event import ClusterDeployNotification, ServiceDestroyNotification
from api_server.s3_utils import s3_get_object_contents, s3_get_list_of_objects, s3_object
from nysa_aws.stack_definition import StackDefinition
from nysa_aws.ecr import EcrClient


#############################
# CREATE A NEW CLUSTER
#############################
@api.route('/v1/clusters', methods=['POST'])
@jsonschema.validate('clusters', 'create')
def new_cluster():
    log.info('new_cluster')

    cluster_contents = s3_get_object_contents(request.json.get(u'name'))
    if cluster_contents:
        return jsonify({'message': 'cluster already exists'}), 422
    else:
        s3_object(request.json.get(u'name')).put(Body=json.dumps(request.json.get(u'config')))
        ClusterDeployNotification(request.json.get(u'name'), request.json.get(u'config')).notify()
        return jsonify({"message": "deploying..."}), 201


#############################
# GET A LIST OF CLUSTERS
#############################
@api.route('/v1/clusters', methods=['GET'])
def get_clusters():
    log.info('get_clusters')

    return jsonify({
        'content': [obj.key for obj in s3_get_list_of_objects()]
    })


#############################
# GET CLUSTER CONFIG
#############################
@api.route('/v1/clusters/<string:cluster>/config', methods=['GET'])
def get_cluster_config(cluster):
    log.info('get_cluster_config')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    return jsonify(config)


#############################
# DEPLOY CHANGES IN CLUSTER CONFIG
#############################
@api.route('/v1/clusters/<string:cluster>/deploy', methods=['POST'])
def deploy_cluster_config(cluster):
    log.info('deploy_cluster')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    ClusterDeployNotification(cluster, config).notify()
    return jsonify({'message': 'deploying...'}), 202


#############################
# UPDATE CLUSTER
#############################
@api.route('/v1/clusters/<string:cluster>/config', methods=['PUT'])
def update_cluster(cluster):
    log.info('update_cluster')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404
    else:
        s3_object(cluster).put(Body=json.dumps(request.json))
        ClusterDeployNotification(cluster, request.json).notify()
        return jsonify({"message": "deploying..."}), 202


#############################
# GET CLUSTER SERVICES
#############################
@api.route('/v1/clusters/<string:cluster>/services', methods=['GET'])
def get_services(cluster):
    log.info('get_services')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    stack = StackDefinition(config)
    return jsonify({'content': [{
                                    'name': svc.name,
                                    'image': svc.image,
                                    'desired_count': svc.desired_count
                                 } for svc in stack.services]
                    })


#############################
# GET SERVICE TAGS
#############################
@api.route('/v1/clusters/<string:cluster>/services/<string:service>/tags', methods=['GET'])
def get_service_tags(cluster, service):
    log.info('get_service_tags')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    stack = StackDefinition(config)

    svc = next((x for x in stack.services if x.name == service), None)
    if svc is None:
        return jsonify({'message': 'service does not exists'}), 404

    ecr = EcrClient()
    ecr_repo = svc.image.rsplit(u':', 1)[0].split(u'/')[1]
    repository = ecr.get_single_repository(ecr_repo)
    images = [img for img in sorted(repository.images, key=lambda k: k.pushed_at, reverse=True)]

    return jsonify({'content': [{
                                    "tag": None if img.tags is None else img.tags[0],
                                    "pushed_at": img.pushed_at
                                } for img in images]
                    })


#############################
# UPDATE SERVICE
#############################
@api.route('/v1/clusters/<string:cluster>/services/<string:service>', methods=['PUT'])
def update_service(cluster, service):
    log.info('update_service')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    svc = next((x for x in config.get('services') if x.keys()[0] == service), None)
    if svc is None:
        return jsonify({'message': 'service does not exists'}), 404

    svc = svc[svc.keys()[0]]
    if request.json.get('image_tag'):
        svc[u'image'] = "{}:{}".format(svc[u'image'].rsplit(u':', 1)[0], request.json.get('image_tag'))

    if request.json.get('desired_count'):
        svc[u'desired_count'] = request.json.get('desired_count')

    s3_object(cluster).put(Body=json.dumps(config))

    if request.json.get('deploy', True):
        ClusterDeployNotification(cluster, config).notify()
        return jsonify({'message': 'deploying...'}), 202
    else:
        return jsonify({}), 202


#############################
# DELETE SERVICE
#############################
@api.route('/v1/clusters/<string:cluster>/services/<string:service>', methods=['DELETE'])
def delete_service(cluster, service):
    log.info('delete_service')

    cluster_contents = s3_get_object_contents(cluster)
    if cluster_contents is None:
        return jsonify({'message': 'cluster does not exists'}), 404

    config = json.loads(cluster_contents[u'Body'].read())
    idx = next((i for i, item in enumerate(config.get('services'))
                if item.keys()[0] == service), -1)

    if idx == -1:
        return jsonify({'message': 'service does not exists'}), 404

    del config[u'services'][idx]
    s3_object(cluster).put(Body=json.dumps(config))
    ServiceDestroyNotification(cluster, service).notify()
    return jsonify({'message': 'deploying...'}), 202
