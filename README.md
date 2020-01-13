# github-stats
Pulls Github views, commits, or contributors for a repo and writes the data to a csv file

### Prerequisites
1. Python 3
2. PyGithub installed - `pip install PyGithub`
3. Push access - the [Github Traffic API](https://developer.github.com/v3/repos/traffic/) requires push access to see view statistics

### Running
Get views counts for all repos in an org for a 7 day period, beginning with the day specified as `-s`

This will output text to the console and produce a .csv file named `github-stats-views-<github-org>-YYYY-MM-DD.csv`
```bash
python GithubStats.py -m views -t <token> -o <github-org> -s <YYYY-MM-DD>
```

Get commits for a 7 day period, beginning with the day specified as `-s`

This will produce a .csv file named `github-stats-commits-<github-org>-<github-repo>-YYYY-MM-DD.csv`
```bash
python GithubStats.py -m commits -t <token> -o <github-org> -r <github-repo> -s <YYYY-MM-DD>
```

Get contributors count for a repo

This will produce a .csv file named `github-stats-contributors-<github-org>-<github-repo>-YYYY-MM-DD.csv`
```bash
python GithubStats.py -m contributors -t <token> -o <github-org> -r <github-repo> -s <YYYY-MM-DD>
```



