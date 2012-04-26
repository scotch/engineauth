| {% set providers = [
|   ('google', '/auth/google'),
|   ('facebook', '/auth/facebook'),
|   ('twitter', '/auth/twitter'),
|   ('yahoo', '/auth/appengine_openid?provider=yahoo.com'),
|   ('linkedin', '/auth/linkedin'),
|   ('aol', '/auth/appengine_openid?provider=aol.com'),
|   ('myopenid', '/auth/appengine_openid?provider=myopenid.com'),
|   ('myspace', '/auth/appengine_openid?provider=myspace.com'),
|   ('github', '/auth/github'),
| ] -%}

.ea-form.row.well
  % include "partials/messages.html"
  .span6
    h4 | To get started, login with one of your existing accounts.
    ul
      % for p, u in providers
        li.provider-btn > a.btn href="{{ u }}" > img src="/static/img/{{ p }}.png" /
  .span5
    h4 | Or create a new one.
    .password-form
      form.horizontal-form method="POST" action="/auth/password"
        fieldset.control-group
          label.control-label for="email" | Email
          .controls > input.input-medium type="text" name="email" /
        fieldset.control-group
          label.control-label for="password" | Password
          .controls > input.input-medium type="password" name="password" /
        fieldset.form-actions
          button.btn type="submit" | Login
