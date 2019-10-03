/* Change password js. */
requirejs.config({
  'baseUrl' : '/static/js/fremancer_users',
  'paths' : {
    'jquery' : '//ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min',
    'bootstrap' : '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min',
    'jquery_validate' : '//ajax.aspnetcdn.com/ajax/jquery.validate/1.11.1/jquery.validate.min',
    'jquery_validate_additional' : '//ajax.aspnetcdn.com/ajax/jquery.validate/1.11.1/additional-methods.min',
    'theme_scripts': '/static/assets/js/theme_scripts'
  },
  'shim' : {
    'bootstrap' : {
      deps : ['jquery'],
    },
    'jquery_validate' : {
      deps : ['jquery'],
    },
    'validate_additional' : {
      deps : ['jquery', 'jquery_validate'],
    }
  }
});

define(['jquery', 'bootstrap'], function($) {
  require(['jquery_validate', 'validate_additional'], function(){
    $('#resetPasswordForm').validate({
      errorClass : "validation-error",
      validClass : "validation-valid"
    });
    $( "#id_password1" ).rules( "add", {
      required: true,
      minlength: 8
    });
    $( "#id_password2" ).rules( "add", {
      required: true,
      equalTo : '#id_password1'
    });
  });

  // Theme scripts.
  require(['theme_scripts'], function () {
  });
});
