% extends "base.html"

% block content
  h1 | EngineAuth: Test Site
  h3 | This is a test site to demonstrate the EngineAuth authentication flow.
  p
    a href="http://code.scotchmedia.com/engineauth" | EngineAuth Documentation
    - Read the full documentation.

  .alert-message.block-message.info
    To protect your privacy all data is deleted every 60 minutes.

  % include "auth/engineauth_form.html"

  % include "auth/datastore_display.html"