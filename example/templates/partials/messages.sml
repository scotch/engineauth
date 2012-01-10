% if messages
  div data-dismiss="alert" class="alert-message block-message {{ messages[0]['level'] }}"
    a.close href="#" | &times;
    ul
      % for message in messages
        li | {{ message['message']|safe }}


