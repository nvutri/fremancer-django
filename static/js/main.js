/**
 * JS for Landing Page.
 */
window.GoogleAnalyticsObject = "__ga__";
window.__ga__ = {
  q: [["create", "UA-73850436-1", "auto"]],
  l: Date.now()
};
requirejs.config({
  'baseUrl': '/static/js/',
  'paths': {
    'jquery': '//ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min',
    'jquery_validate_additional': '//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.11.0/additional-methods.min',
    'jquery_validate': '//cdnjs.cloudflare.com/ajax/libs/jquery-validate/1.11.0/jquery.validate.min',
    'bootstrap': '//netdna.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min',
    'jquery_placeholder': '//cdnjs.cloudflare.com/ajax/libs/jquery-placeholder/2.0.7/jquery.placeholder.min',
    'cayman_parallax': '/static/assets/js/parallax',
    'cayman_countto': '/static/assets/js/countto',
    'cayman_scripts': '/static/assets/js/theme_scripts',
    'ga': '//www.google-analytics.com/analytics'
  },
  'shim': {
    'bootstrap': {
      deps: ['jquery']
    },
    'jquery_placeholder': {
      deps: ['jquery']
    },
    'cayman_countto': {
      deps: ['jquery', 'cayman_scripts']
    },
    'cayman_parallax': {
      deps: ['jquery']
    },
    'cayman_scripts': {
      deps: ['jquery', 'cayman_parallax']
    },
    'ga': {
      exports: '__ga__'
    },
    'main': {
      deps: ['jquery', 'cayman_scripts']
    }
  }
});

define(['jquery', 'bootstrap', 'jquery_placeholder', 'cayman_scripts'], function ($) {
  // Display placeholder for I.E browsers.
  $('input, textarea').placeholder();

  require(['fremancer_users/authentication'], function (authentication) {
    // Activate validations on authentication forms.
    authentication.validateLoginForm();
    authentication.validateSignupForm();
  });

  // Send stats to Google Analytics.
  require(['ga'], function (ga) {
    ga('send', 'pageview');
  });
});
