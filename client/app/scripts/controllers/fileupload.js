GLClient.controller('WBFileUploadCtrlSingle', ['$scope', 'Authentication', function($scope, Authentication) {
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
}]).
controller('FileUploadControllerMock', ['$scope', 'Authentication', function($scope, Authentication) {
  $scope.uploading = true;
  $scope.uploading_files = [
    {
      "name": "FileA",
      "size": 1000,
      "type": "image"
    },
    {
      "name": "FileB.png",
      "size": 100,
      "type": "document"
    },
    {
      "name": "Antani fuffa.png",
      "size": 100,
      "type": "image"
    },
    {
      "name": "FileB.png",
      "size": 1020,
      "type": "video"
    },
    {
      "name": "The file name.png",
      "size": 1020,
      "type": "document"
    } 
  ];
}]);
