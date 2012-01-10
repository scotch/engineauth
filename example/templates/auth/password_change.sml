% from "macros/form_macros.html" import form_field_tb

nav.breadcrumb
  li | Account Settings
  span.divider | /

.row
  nav.span3.columns
    % include "accounts/shared/menu.html"
  section.span8.columns
    % include "partials/messages.html"
    form action="" method="POST"
      = form_field_tb(form.current)
      hr /
      = form_field_tb(form.password)
      = form_field_tb(form.confirm)
      .actions
        input.btn.primary type="submit" value="Save Changes" /
