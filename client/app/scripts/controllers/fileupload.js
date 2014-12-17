GLClient.
controller('WBFileUploadCtrlSingle', ['$scope', 'Authentication', function($scope, Authentication) {
  $scope.options = {
    url: $scope.fileupload_url,
    multipart: false,
    headers: Authentication.headers(),
    autoUpload: true,
    maxNumberOfFiles: 1,
    maxFileSize: $scope.node.maximum_filesize * 1024 * 1024
  };
}]).
controller('WBFileUploadCtrlMultiple', ['$scope', 'Authentication', function($scope, Authentication) {
  $scope.options = {
    url: $scope.fileupload_url,
    multipart: false,
    headers: Authentication.headers(),
    autoUpload: true,
    maxFileSize: $scope.node.maximum_filesize * 1024 * 1024
  };
}]).
controller('FileUploadEditFileController', ['$scope', 'Authentication', function($scope, Authentication) {
  $scope.empty_d = true;
  $scope.empty_t = true;
  $scope.file_desc;
  $scope.file_title;
  $scope.edit = function() {
    if ($scope.file_desc) {
      $scope.empty_d = false; 
    }
    if ($scope.file_title) {
      $scope.empty_t = false; 
    }
  };
}]).
controller('FileDestroyController', ['$scope', 'Authentication', function($scope, Authentication) {
}]);
