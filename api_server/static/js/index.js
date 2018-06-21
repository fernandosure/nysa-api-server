angular.module('myApp', ['ui.router', 'ui.ace', 'ui.bootstrap'])

.config(['$urlRouterProvider', '$locationProvider', '$stateProvider', function ($urlRouterProvider, $locationProvider, $stateProvider) {

    $urlRouterProvider
    .when('', '/clusters')
    .when('/', '/clusters');


    $stateProvider
    .state('cluster', {
        url:'/clusters',
        abstract: true,
        template: '<ui-view />',
    })

    .state('cluster.list', {
        url: '',
        templateUrl: '/static/js/views/clusters_list.html',
        controller: 'clusterListController',
        resolve: {
            clusters: ['apiService', function (apiService) { return apiService.getClusterList() }]
        }
    })

    .state('cluster.services', {
        url: '/:clusterId/services',
        templateUrl: '/static/js/views/services_list.html',
        controller: 'serviceListController',
        resolve: {
            services: ['apiService', '$stateParams', function (apiService, $stateParams) { return apiService.getServiceList($stateParams.clusterId) }]
        }
    })


    .state('cluster.config', {
        url: '/:clusterId/config',
        templateUrl: '/static/js/views/cluster_config.html',
        controller: 'clusterConfigController',
        resolve: {
            config: ['apiService', '$stateParams', function (apiService, $stateParams) { return apiService.getClusterConfig($stateParams.clusterId) }]
        }
    })

}])

.service('apiService', ['$http', function ($http) {
    this.getClusterList = function () { return $http.get(baseUrl +'/api/v1/clusters')}
    this.getClusterConfig = function (clusterId) { return $http.get(baseUrl +'/api/v1/clusters/' + clusterId + '/config')}
    this.getServiceList = function (clusterId) { return $http.get(baseUrl +'/api/v1/clusters/' + clusterId + '/services')}
    this.updateClusterConfig = function (clusterId, data) { return $http.put(baseUrl +'/api/v1/clusters/' + clusterId + '/config', data)}
    this.updateService = function (clusterId, service, data) { return $http.put(baseUrl +'/api/v1/clusters/' + clusterId + '/services/' + service, data)}
}])

.controller('clusterListController', ['$scope', 'apiService', 'clusters', function ($scope, apiService, clusters) {
    $scope.clusters = clusters.data.content;
}])

.controller('serviceListController', ['$scope', 'apiService', 'services', '$stateParams', function ($scope, apiService, services, $stateParams) {

    $scope.alerts = [];
    $scope.services = services.data.content.map(function(obj){
       obj['image_tag'] = obj.image.split(':')[1];
       obj['editing'] = false;
       return obj
    })

    $scope.updateService = function(service) {
        service.editing = false;
        var data = {
            image_tag: service.image_tag,
            desired_count: service.desired_count
        }

        var promise = apiService.updateService($stateParams.clusterId, service.name, data);
        promise.then(function(){
             $scope.alerts = [{ type: 'success', msg: 'Success!!!'}];
        }), function(){
             $scope.alerts = [{ type: 'danger', msg: 'Oh snap! An error has occurred try submitting again.' }];
        }
    }

    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    }
}])

.controller('clusterConfigController', ['$scope', 'apiService', 'config', '$stateParams', function ($scope, apiService, config, $stateParams) {
    $scope.clusterConfig = YAML.stringify(config.data, 10);
    $scope.alerts = [];

    $scope.saveChanges = function() {
        var promise = apiService.updateClusterConfig($stateParams.clusterId, YAML.parse($scope.clusterConfig));
        promise.then(function(){
             $scope.alerts = [{ type: 'success', msg: 'Success!!!'}];
        }), function(){
             $scope.alerts = [{ type: 'danger', msg: 'Oh snap! An error has occurred try submitting again.' }];
        }
    }

    $scope.closeAlert = function(index) {
        $scope.alerts.splice(index, 1);
    }
}])
