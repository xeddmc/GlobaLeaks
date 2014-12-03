GLClient.controller('SubmissionCtrl',
    ['$scope', '$rootScope', '$location', '$modal', 'Authentication', 'Node', 'Submission', 'Receivers', 'WhistleblowerTip',
      function ($scope, $rootScope, $location, $modal, Authentication, Node, Submission, Receivers, WhistleblowerTip) {
  
  $scope.fake_submission = {
    completed: false,
    receipt: '3583104390243402'
  }
  $scope.fake_submit = function() {
    $scope.fake_submission.completed = true; 
  }

  $rootScope.invalidForm = true;

  $scope.receiptConfimation = "";
  var context_id = $location.search().context;
  var receivers = $location.search().receivers;
  if (receivers) {
    receivers = JSON.parse(receivers);
  }

  Node.get(function (node) {
    $scope.node = node;

    new Submission(function (submission) {
      $scope.submission = submission;

      $scope.maximumFilesize = submission.maximum_filesize;
      
      $scope.current_context = submission.current_context;

      $scope.fields = submission.fields;
      $scope.indexed_fields = submission.indexed_fields;

      $scope.submission = submission;

      if ($scope.submission.contexts.length == 1 && !$scope.submission.current_context.show_receivers) {
        $scope.skip_first_step = true;
        $scope.selection = 1;
      } else {
        $scope.skip_first_step = false;
        $scope.selection = 0;
      }

      $scope.submit = $scope.submission.submit;

      checkReceiverSelected();
    }, context_id, receivers);

  });

  var checkReceiverSelected = function () {
    $scope.receiver_selected = false;
    // Check if there is at least one selected receiver
    angular.forEach($scope.submission.receivers_selected, function (receiver) {
      $scope.receiver_selected = $scope.receiver_selected | receiver;
    });

  };

  $scope.selected_receivers_count = function () {
    var count = 0;

    if ($scope.submission) {
      angular.forEach($scope.submission.receivers_selected, function (selected) {
        if (selected) {
          count += 1;
        }
      });
    }

    return count;
  };

  $scope.selectable = function () {

    if ($scope.submission.current_context.maximum_selectable_receivers == 0) {
      return true;
    }

    return $scope.selected_receivers_count() < $scope.submission.current_context.maximum_selectable_receivers;
  };

  $scope.switch_selection = function (receiver) {
    if (receiver.disabled)
      return;
    if ($scope.submission.receivers_selected[receiver.id] || $scope.selectable()) {
      $scope.submission.receivers_selected[receiver.id] = !$scope.submission.receivers_selected[receiver.id];
    }
  };

  $scope.view_tip = function (receipt) {
    WhistleblowerTip(receipt, function () {
      $location.path('/status/');
    });
  };

  $scope.uploading = false;

  $scope.disclaimer = {accepted: false};
  
  // Watch for changes in certain variables
  $scope.$watch('submission.current_context', function () {
    if ($scope.current_context) {
      $scope.submission.create(function () {
        $scope.fileupload_url = '/submission/' + $scope.submission.current_submission.id + '/file';
      });
      checkReceiverSelected();
     }
  }, false);

  $scope.$watch('submission.receivers_selected', function () {
    if ($scope.submission) {
      checkReceiverSelected();
    }
  }, true);

  $rootScope.$watch('anonymous', function (newVal, oldVal) {
    if ($scope.node) {
      if (newVal == false && !$scope.node.tor2web_submission) {
        $location.path("/");
      }
    }
  });

  var open_steps_intro = function () {
    var modalInstance = $modal.open({
      templateUrl: 'views/partials/steps_intro.html',
      controller: 'StepsIntroCtrl',
      size: 'lg',
      scope: $scope
    });

  };

  open_steps_intro();
}]).
controller('StepsIntroCtrl', ['$scope', '$rootScope', '$modalInstance', function ($scope, $rootScope, $modalInstance) {

  steps = 3;

  $scope.proceed = function () {
    if ($scope.step < steps) {
      $scope.step += 1;
    }
  }

  $scope.back = function () {
    if ($scope.step > 0) {
      $scope.step -= 1;
    }
  }

  $scope.cancel = function () {
    $modalInstance.close();
  };

  $scope.step = 0;
}]).
controller('SubmissionFieldCtrl', ['$scope', '$rootScope', function ($scope, $rootScope) {
  $scope.queue = [];
  $scope.$watch('queue', function () {
    $scope.$parent.uploading = false;
    if ($scope.queue) {
      $scope.queue.forEach(function (k) {
        if (!k.id) {
          $scope.$parent.uploading = true;
        } else {
          $scope.submission.current_submission.files.push(k.id);
          if ($scope.submission.current_submission.wb_steps[$scope.field] == undefined) {
            $scope.submission.current_submission.wb_steps[$scope.field] = {};
          }
          $scope.submission.current_submission.wb_steps[$scope.field].value = k.id;
        }
      });
    }
  }, true);
}]).
controller('SubmissionFormController', ['$scope', '$rootScope', function ($scope, $rootScope) {
  $scope.$watch('submissionForm.$valid', function () {
    $rootScope.invalidForm = $scope.submissionForm.$invalid;
  }, true);
}]).
controller('SubmissionStepsCtrl', ['$scope', function($scope) {

  $scope.getCurrentStepIndex = function(){
    return $scope.selection;
  };

  // Go to a defined step index
  $scope.goToStep = function(index) {
    if ( $scope.uploading ) {
      return;
    }

    $scope.selection = index;
  };

  $scope.hasNextStep = function(){
    if ( $scope.current_context == undefined )
      return false;

    return $scope.selection < $scope.current_context.steps.length;
  };

  $scope.hasPreviousStep = function(){
    if ( $scope.current_context == undefined )
      return false;

    return $scope.selection > 0;
  };

  $scope.incrementStep = function() {
    if ( $scope.uploading )
      return;

    if ( $scope.hasNextStep() )
    {
      $scope.selection = $scope.selection + 1;
    }
  };

  $scope.decrementStep = function() {
    if ( $scope.uploading )
      return;

    if ( $scope.hasPreviousStep() )
    {
      $scope.selection = $scope.selection - 1;
    }
  };

}]).
controller('SubmissionFormControllerMock', ['$scope', '$rootScope', function ($scope, $rootScope) {
  $scope.steps = [
    [
      {
        "label": "File upload",
        "hint": "Hint are",
        "type": "fileupload"
      }
    ],
    [
      {
        "label": "Text Area",
        "hint": "Hint are",
        "type": "textarea"
      },
   
    ]
  ];
  $scope.selected_file = undefined;
  $scope.upload_in_progress = false;
  $scope.uploading_files = [];

  $scope.upload_file = function() {
    $scope.upload_in_progress = true;
    var name = "file_";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        name += possible.charAt(Math.floor(Math.random() * possible.length));
    $scope.uploading_files.push({
      "name": name,
      "size": Math.floor(Math.random() * 1000),
      "type": "image"
    });
  };


}]).
controller('HideExpandController', ['$scope', '$rootScope', function($scope, $rootScope) {
  $scope.expanded = false;
}]);

