<!doctype html>
<head>
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css" integrity="sha384-rwoIResjU2yc3z8GV/NPeZWAv56rSmLldC3R/AZzGRnGxQQKnKkoFVhFQhNUwEyJ" crossorigin="anonymous">
<script src="https://code.jquery.com/jquery-3.1.1.slim.min.js" integrity="sha384-A7FZj7v+d/sdmMqp                                                                                            /nOQwliLvUsJfDHW+k9Omg/a/EheAdgtzNs3hpfag6Ed950n" crossorigin="anonymous"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/tether/1.4.0/js/tether.min.js" integrity="sha384-DztdAPBWPRXSA/3eYEEUWrWCy7G5KFbe8fFjk5JAIxUYHKkDx6Qin1DkWx51bBrb" crossorigin="anonymous"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/js/bootstrap.min.js" integrity="sha384-vBWWzlZJ8ea9aCX4pEW3rVHjgjt7zpkNpZk+02D9phzyeVkE+jo0ieGizqPLForn" crossorigin="anonymous"></script>
 <title>{{ repo_name }} - Commits report</title>
</head>
<body>
<main class="container">
{% for commit, is_interesting in commits %}
{% if is_interesting %}
<h1>{{ commit.id }}</h1>
{% else %}
<h2>{{ commit.id }}</h2>
{% endif %}
<p>{{ commit.message|e|replace("\n", "<br>") }}</p>
<p>
{% if commit.author == commit.committer %}
Author & committer: {{ commit.author.name }} &lt;{{ commit.author.email }}&gt;<br>
Commit time: {{ signature_time_str(commit.author) }}<br>
{% else %}
Author: {{ commit.author.name }} &lt;{{ commit.author.email }}&gt;<br>
Author time: {{ signature_time_str(commit.author) }}<br>
Committer: {{ commit.committer.name }} &lt;{{ commit.committer.email }}&gt;<br>
Committer time: {{ signature_time_str(commit.committer) }}<br>
{% endif %}
</p>
{% for parent in commit.parents %}
{% set diff_text = parent.tree.diff_to_tree(commit.tree).patch|e|replace("\n", "<br>") %}
{% if diff_text|length > 1024*20 %}
Diff with parent {{ loop.index }} not shown, it is {{ diff_text|length }} characters in length
{% else %}
<details>
<summary>Diff with parent {{ loop.index }}</summary>
<code>
{{ diff_text }}
</code>
</details>
{% endif %}
{% endfor %}
{% endfor %}
</main>
</body>
</html>