% if messages
  div data-alert="alert" class="alert-message block-message {{ messages[0][1] }}"
    a.close href="#" | &times;
    ul
      % for message in messages
        li | {{ message[0]|safe }}


