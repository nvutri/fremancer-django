define([], function () {
  var done = false;
  var script = document.createElement('script');
  script.async = true;
  script.type = 'text/javascript';
  script.src = 'https://app.purechat.com/VisitorWidget/WidgetScript';
  document.getElementsByTagName('HEAD').item(0).appendChild(script);
  script.onreadystatechange = script.onload = function (e) {
    if (!done && (!this.readyState || this.readyState == 'loaded' || this.readyState == 'complete')) {
      var w = new PCWidget({c: '5e870754-81a5-47e5-a227-c6335d78feee', f: true});
      done = true;
    }
  };
});
