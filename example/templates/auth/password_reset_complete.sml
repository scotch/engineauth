% from "macros/form_macros.html" import form_field_tb

section.span8.columns.offset4
  h1 | Enter a new password
  % include "partials/messages.html"
  form action="" method="POST"
    = form_field_tb(form.password)
    = form_field_tb(form.confirm)
    .actions
      input.btn.primary type="submit" value="Save" /
