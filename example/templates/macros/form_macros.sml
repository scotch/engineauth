% macro form_field_label(field, class="")
  label class="{{ class }}" for="{{ field.id }}" 
    = field.label.text
    % if field.flags.required
      abbr title="This field is required." | *

% macro form_field_description(field)
  % if field.description
    span.help-inline
      = field.description

% macro form_field_errors(field)
  % if field.errors
    ul.errors
      % for error in field.errors
        li
          = error

% macro form_field_boolean(field)
  = field(**kwargs)
  = form_field_label(field, 'boolean')
  = form_field_description(field)
  = form_field_errors(field)

{# outputs twitter bootstrap compatible fields #}
% macro bootstrap_form_field(field)
  div class="clearfix{% if field.errors %} error{% endif %}"
    = form_field_label(field)
    .input
      % if field.type == 'RadioField'
        = field(class='radio-group', **kwargs)
      % else
        = field(**kwargs)
      % if field.description
        p.help-inline
          = field.description
      % if field.errors
        br /
        span.help-inline
          % for error in field.errors
            = error


% macro form_field(field)
  % if field.type == 'BooleanField'
    = form_field_boolean(field, **kwargs)
  % else
    = form_field_label(field)
    % if field.type == 'RadioField'
      = field(class='radio-group', **kwargs)
    % else
      = field(**kwargs)
    = form_field_description(field)
    = form_field_errors(field)


% macro form_field_td(field)
    % if field.type == 'BooleanField'
      td.label |
      td.field
        = form_field_boolean(field, **kwargs)
    % else
      td.label
        = form_field_label(field)
      td.field |
      % if field.type == 'RadioField'
        = field(class='radio-group', **kwargs)
      % else
        = field(**kwargs)
      = form_field_description(field)
      = form_field_errors(field)


% macro form_fields(fields, label_class='horiz', input_class='medium')
  % for field in fields
    % if field.type == 'HiddenField'
      = field()
  ol
    % for field in fields
      % if field.type != 'HiddenField'
        li class="{{ label_class }}"
          = form_field(field, class=input_class)

