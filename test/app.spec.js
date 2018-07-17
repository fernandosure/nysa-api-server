///var baseUrl = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port : '');

describe('ApiService Service', function() {
 var backend;

  // Before each test load our module
  beforeEach(angular.mock.module('myApp'));

  // Before each test set our injected apiService to our local backend variable
  beforeEach(inject(function(apiService) {
    backend = apiService;
  }));

  it('service should exist', function() {
    expect(backend).toBeDefined();
  });

  it('getClusterList should exist', function() {
    expect(backend.getClusterList).toBeDefined();
  });

  it('getClusterConfig should exist', function() {
    expect(backend.getClusterConfig).toBeDefined();
  });

  it('getServiceTags should exist', function() {
    expect(backend.getServiceTags).toBeDefined();
  });

  it('getServiceTags should exist', function() {
    expect(backend.getServiceTags).toBeDefined();
  });

  it('updateClusterConfig should exist', function() {
    expect(backend.updateClusterConfig).toBeDefined();
  });

  it('updateService should exist', function() {
    expect(backend.updateService).toBeDefined();
  });

  it('createCluster should exist', function() {
    expect(backend.createCluster).toBeDefined();
  });

});

describe('Controller tests', function(){

    beforeEach(module('myApp'));

    describe('clusterListController',function(){
        var clusterListController;
        var scope;
        var clusters = {
            data: {
                content: []
            }
        };

        beforeEach(inject(function($controller,  $rootScope, apiService, ){
            scope = $rootScope.$new();
            clusterListController = $controller('clusterListController', {
                $scope: scope,
                clusters: clusters
            });
        }));

        it('It should exists', function(){
            expect(clusterListController).toBeDefined();
        });

        it('Cluster list should have an empty list', function(){
            expect(scope.clusters).toEqual([]);
        });

    });


    describe('clusterCreateController',function(){
        var controller;
        var scope;


        beforeEach(inject(function($controller,  $rootScope, apiService, ){
            scope = $rootScope.$new();
            controller = $controller('clusterCreateController', {
                $scope: scope
            });
        }));

        it('It should exists', function(){
            expect(controller).toBeDefined();
        });


    });

});