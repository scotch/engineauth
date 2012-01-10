
section.span8
  % include "partials/messages.html"
  form action="" method="POST"
    = bootstrap_form_field(form.current)
    hr /
    = bootstrap_form_field(form.password)
    = bootstrap_form_field(form.confirm)
    .actions
      input.btn.primary type="submit" value="Save Changes" /
