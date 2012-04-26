
h2 | Your Datastore Values (Only visiable to you)

ul.tabs
  li > a href="#profile" data-toggle="tab" | Profiles
  li > a href="#user" data-toggle="tab" | User
  li > a href="#session" data-toggle="tab" | Session

.tab-content
  #profile.tab-pane
    h2 | Profiles
    % if profiles and profiles.__len__
      h5 | Connect aditional providers account to view the information that EngineAuth collects.
      % for p in profiles
        h3 | {{ p.key.id() }}
        pre.prettyprint
          = p.to_dict()|do_pprint()
    % else
      .alert-message.block-message.info
        No data yet. Try connecting an account

  #user.tab-pane
    h2 | User
    % if user
      pre.prettyprint
        = user.to_dict()|do_pprint()
    % else
      .alert-message.block-message.info
        No data yet. Try connecting an account

  #session.tab-pane
    h2 | Session
    % if session
      pre.prettyprint
        = session.to_dict()|do_pprint()
    % else
      .alert-message.block-message.info
        No data yet. Try connecting an account

script
  | $(function () {
  |   window.prettyPrint && prettyPrint();
  |   $('.tabs a:first').tab('show')
  |   $('.pills a:first').tab('show')
  | })