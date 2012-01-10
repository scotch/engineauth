ul.breadcrumb
  li | Account Settings
  span.divider | /

.row
  nav.span3.columns
    % include "accounts/shared/menu.html"
  section.span8.columns
    h3 | Email
    % include "partials/messages.html"
    form action="" method="POST"
      .clearfix
        label for=email | Email
        .input
          input.span4 value="{{ user.email }}" type="text" name=email /
      .actions
        input.btn.primary type="submit" value="Save Changes" /
