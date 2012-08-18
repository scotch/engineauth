
% macro quicklinks(github_user, github_repo, twitter_username, project_name, project_url)
  ul.quick-links
    li > strong | Quick Links
    li > a href="https://github.com/{{ github_user }}/{{ github_repo }}/" | GitHub
    li > a href="https://github.com/{{ github_user }}/{{ github_repo }}/issues?state=open" | Issues
    li.divider | &middot;
    li > iframe.github-btn src="http://ghbtns.com/github-btn.html?user={{ github_user }}&repo={{ github_repo }}&type=watch&count=true" allowtransparency="true" frameborder="0" scrolling="0" width="110px" height="20px" |
    li > iframe.github-btn src="http://ghbtns.com/github-btn.html?user={{ github_user }}&repo={{ github_repo }}&type=fork&count=true" allowtransparency="true" frameborder="0" scrolling="0" width="94px" height="20px" |
    li.divider | &middot;
    li.follow-btn > a href="https://twitter.com/{{ twitter_username }}" class="twitter-follow-button" data-width="145px" data-link-color="#0069D6" data-show-count="false" | Follow @{{ twitter_username }}
    li.tweet-btn > a.twitter-share-button href="https://twitter.com/share" data-url="{{ project_url }}" data-count="horizontal" data-via="twbootstrap" data-related="{{ twitter_username }}:Creator of {{ project_name }}" | Tweet
    li.plusone-container > g:plusone size="medium" |

    <!-- twitter -->
    script src="http://platform.twitter.com/widgets.js" type="text/javascript" |
