/* Change password js. */
define(['jquery', 'bootstrap', 'validate_additional'], function($) {
  return {
    initialize : function(){
      // Hide the spinning in the submit buttons.
      $('#pwdForm :button .fa-spinner').hide();

      // Validate the password form.
      var pwdValidator = $("#pwdForm").validate({
        errorClass : "validation-error",
        validClass : "validation-valid",
        rules : {
          old_password : "required",
          new_password : {
            required: true,
            minlength: 8
          },
          retype_new_password : {
            required : true,
            equalTo : '#new_password'
          }
        },
        submitHandler : function(form) {
          $('#pwdForm :button .fa-spinner').show();
          var serializedForm = $('#pwdForm').serialize();
          var jqxhr = $.post('/users/change_pwd/', serializedForm, function(data) {
            if (data['success']) {
              window.location.href = '/';
            }
          }, 'json').always(function(data) {
            $('#pwdForm :button .fa-spinner').hide();
            showChangePwdError(data['errors']);
          });
        }
      });
      var showChangePwdError = function(errors) {
        pwdValidator.showErrors(errors);
      };
    }
  }
});
