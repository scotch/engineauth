
h2 | Your Datastore Values

ul.tabs
  li > a href="#profile" data-toggle="tab" | Profiles
  li > a href="#user" data-toggle="tab" | User
  li > a href="#session" data-toggle="tab" | Session

.tab-content
  #profile.tab-pane
    % if profiles.__len__
      h2 | Profiles
      h5 | Connect additional accounts to view that data that EngineAuth collects.
    % else
      h2 | No Profiles
      h5 | Connect a providers account to view the information that EngineAuth collects.
    % for p in profiles
      h3 | {{ p.key.id() }}
      div id="{{ p.key.id() }}"
        pre.prettyprint
          = p.to_dict()|do_pprint()

  #user.tab-pane
    h2 | User
    pre.prettyprint
      = user.to_dict()|do_pprint()

  #session.tab-pane
    h2 | Session
    pre.prettyprint
      = session.to_dict()|do_pprint()

script
  | $(function () {
  |   window.prettyPrint && prettyPrint();
  |   $('.tabs a:first').tab('show')
  |   $('.pills a:first').tab('show')
  | })