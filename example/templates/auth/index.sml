nav.breadcrumb
  li | Account Settings
  span.divider | /

.row
  nav.span3
    % include "accounts/shared/menu.html"
  section.span13
    % include "partials/messages.html"
    h4 | {{ user.displayName }}
    p > a href="/profiles/{{ user.user_id }}/edit" | Edit Profile
    h3 | Email address
    p
      {{ user.email }}
      span > a href="/settings/email" | Edit
    
    h3 | Notifications
