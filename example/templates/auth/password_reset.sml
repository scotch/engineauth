.row
  header.span16.columns
    h1 | Forgot Password
  .span7.columns
    % include "partials/messages.html"
    form action="" method="POST"
      .clearfix
        label for=email | Email
        .input
          input.span4 type="text" name=email /
      .actions
        input.btn.primary type="submit" value="Send Rest Instructions" /
