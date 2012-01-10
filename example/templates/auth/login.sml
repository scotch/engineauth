% from "macros/form_macros.html" import bootstrap_form_field

nav.breadcrumb
  li | Account Settings
  span.divider | /

.row
  nav.span3.columns
    % include "accounts/shared/menu.html"
  section.span8.columns
    % include "partials/messages.html"
    form action="", method="POST"
      = bootstrap_form_field(form.current)
      hr /
      = bootstrap_form_field(form.password)
      = bootstrap_form_field(form.confirm)
      .actions
        input.btn.primary type="submit" value="Save Changes" /
