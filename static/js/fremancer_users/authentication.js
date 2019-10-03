/* Authentication form validation and submission.*/
requirejs.config({
  'paths': {
    'additional_methods': '//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.11.0/additional-methods.min',
    'jquery_validate': '//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.11.0/jquery.validate.min',
  },
  'shim': {
    'jquery_validate': {
      deps: ['jquery']
    },
    'additional_methods': {
      deps: ['jquery', 'jquery_validate']
    }
  }
})
define(['jquery', 'bootstrap', 'jquery_validate', 'additional_methods'], function ($) {
  /**
   * Validate the login form.
   * On success. Go to daily sales.
   * @export
   */
  function validateLoginForm() {
    var loginFormSpinner = $('button i.fa-spinner');
    loginFormSpinner.hide();
    var showLoginError = function (errors) {
      loginValidator.showErrors(errors);
    };
    var loginValidator = $('#loginForm').validate({
      errorClass: 'validation-error',
      validClass: 'validation-valid',
      rules: {
        email: {
          required: true,
          email: true
        },
        password: {
          required: true,
          minlength: 8
        }
      },
      submitHandler: function (form) {
        loginFormSpinner.show();
        var serializedForm = $('#loginForm').serialize();
        $.post('/users/login/', serializedForm, function (data) {
          if (data['success']) {
            window.location.href = '/';
          }
        }, 'json').always(function (data) {
          loginFormSpinner.hide();
          showLoginError(data['errors']);
          $('#msgLogin').html(data['msg']);
        });
      }
    });
  }

  /**
   * Validate the Signup form.
   * On success. Go to daily sales.
   * @export
   */
  function validateSignupForm() {
    var signupFormSpinner = $('#signupForm :button .fa-spinner');
    signupFormSpinner.hide();
    var signupValidator = $('#signupForm').validate({
      errorClass: 'validation-error',
      validClass: 'validation-valid',
      rules: {
        first_name: {
          required: true,
          minlength: 2
        },
        last_name: {
          required: true,
          minlength: 3
        },
        email: {
          required: true,
          email: true
        },
        password: {
          required: true,
          minlength: 8
        },
        re_password: {
          required: true,
          equalTo: '#signupForm #id_password'
        },
        phone_number: {
          required: true,
          phoneUS: true
        },
        larec_license: {
          required: false,
          minlength: 8
        }
      },
      submitHandler: function (form) {
        signupFormSpinner.show();
        $.post('/users/signup/', $('#signupForm').serialize(), function (data) {
          if (data['success']) {
            window.location.href = '/';
          }
        }, 'json').always(function (data) {
          signupFormSpinner.hide();
          showSignupError(data['errors']);
          $('#msgSignup').html(data['msg']);
        });
      }
    });

    function showSignupError(errors) {
      signupValidator.showErrors(errors);
    }
  }

  return {
    validateLoginForm: validateLoginForm,
    validateSignupForm: validateSignupForm
  };
});
