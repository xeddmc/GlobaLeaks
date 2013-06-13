GLClient.controller('SubmissionCtrl', ['$scope', '$rootScope', '$location', 'Node',
    'Submission', 'Receivers', 'WhistleblowerTip', function($scope, $rootScope,
      $location, Node, Submission, Receivers, WhistleblowerTip) {

  var checkReceiverSelected = function() {
    $scope.receiver_selected = false;
    // Check if there is at least one selected receiver
    angular.forEach($scope.submission.receivers_selected, function(receiver) {
      $scope.receiver_selected = $scope.receiver_selected | receiver;
    });
  }

  Node.get(function(node_info){
    $scope.node_info = node_info;
  });

  new Submission(function(submission){
    $scope.submission = submission;
    $scope.maximumFilesize = submission.maximum_filesize;

    $scope.current_context = submission.current_context;

    $scope.submit = $scope.submission.submit;
    checkReceiverSelected();

  });

  $scope.view_tip = function(receipt) {
    WhistleblowerTip(receipt, function(tip_id){
      $location.path('/status/' + tip_id);
    });
  };

  $rootScope.uploadedFiles = [];
  $rootScope.uploadingFiles = [];
  $scope.uploading = false;

  $scope.disclaimer = {accepted: false};
  $scope.steps = [
    '1 Receiver selection',
    '2 Fill out your submission',
    '3 Final Step'
  ];

  // Watch for changes in certain variables
  $scope.$watch('submission.current_context', function(){
    if ($scope.current_context) {
      $scope.submission.create();
      checkReceiverSelected();
    }
  }, false);

  $scope.$watch('receivers_selected', function() {
    if ($scope.receivers_selected) {
      checkReceiverSelected();
    }
  }, true);

  $scope.$watch('uploadingFiles', function(){

    if ($scope.uploadingFiles.length === 0)
      $scope.uploading = false;
    else
      $scope.uploading = true;

  }, true);

}]);