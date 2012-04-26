% from "macros/quicklinks.html" import quicklinks

<!DOCTYPE HTML>
html
  head
    title | EngineAuth: Multi-Provider Authentication for App Engine
    meta charset="utf-8" /
    meta name="description"       content="" /
    meta name="author"            content="" /
    meta name="viewport"          content="width=device-width, initial-scale=1.0" /
    link rel="stylesheet"         href="/static/css/bootstrap.css?v=1" /
    link rel="stylesheet"         href="/static/css/application.css?v=1" /
    script src="http://cdnjs.cloudflare.com/ajax/libs/json2/20110223/json2.js" |
    script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js" |

    link href="/static/js/google-code-prettify/prettify.css" type="text/css" rel="stylesheet" /
    script type="text/javascript" src="/static/js/google-code-prettify/prettify.js" |
    script type="text/javascript" src="/static/js/bootstrap-alert.js" |
    script type="text/javascript" src="/static/js/bootstrap-tab.js" |
    script type="text/javascript" src="/static/js/bootstrap-collapse.js" |
    <!--[if lt IE 9]>
    <script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
    script type="text/javascript"
      | var _gaq = _gaq || [];
      | _gaq.push(["_setAccount", "UA-28149225-1"]);
      | _gaq.push(['_setDomainName', 'scotchmedia.com']);
      | _gaq.push(["_trackPageview"]);
      | (function() {
      |  var ga = document.createElement("script");
      |  ga.type = "text/javascript";
      |  ga.async = true;
      |  ga.src = ("https:" == document.location.protocol ? "https://ssl" : "http://www") + ".google-analytics.com/ga.js";
      |  var s = document.getElementsByTagName("script")[0];
      |  s.parentNode.insertBefore(ga, s);
      | })();

  body
    .navbar
      .navbar-inner.navbar-fixed
        .container
          a.brand href="/" | EngineAuth
          ul.nav
            li > a href="http://code.scotchmedia.com/engineauth/docs" | docs

    = quicklinks('scotch', 'engineauth', 'scotchmedia', 'EngineAuth', 'http://code.scotchmedia.com/engineauth')
    .container.main-content
      % block content
        .
    footer.footer
      .container
        p | Designed modified from <a href="http://twitter.github.com/bootstrap/" target="_blank">Twitters' Bootstrap</a> by <a href="http://www.scotchmedia.com" target="_blank">Scotch Media</a>.
        p | Code licensed under the <a href="http://www.apache.org/licenses/LICENSE-2.0" target="_blank">Apache License v2.0</a>. Design and Documentation licensed under <a href="http://creativecommons.org/licenses/by/3.0/">CC BY 3.0</a>.

    <!---
    #fb-root |

    script
      | $(function () {
      |   window.prettyPrint && prettyPrint();
      |   $('.tabs a:last').tab('show')
      | })
      |
      | window.fbAsyncInit = function() {
      |   FB.init({
      |     appId      : "169981169706769", // App ID
      |     channelURL : "//engineauth.scotchmedia.com/channel", // Channel File
      |     status     : true, // check login status
      |     cookie     : true, // enable cookies to allow the server to access the session
      |     oauth      : true, // enable OAuth 2.0
      |     xfbml      : true  // parse XFBML
      |   });
      |   // Additional initialization code here
      | };
      | // Load the SDK Asynchronously
      | (function(d){
      |    var js, id = "facebook-jssdk"; if (d.getElementById(id)) {return;}
      |    js = d.createElement("script"); js.id = id; js.async = true;
      |    js.src = "//connect.facebook.net/en_US/all.js";
      |    d.getElementsByTagName("head")[0].appendChild(js);
      |  }(document));
    --->