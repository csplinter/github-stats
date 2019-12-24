# github-stats
Pulls all public Github repos for an organization and writes their view counts to a csv.

### Prerequisites
1. Python 3
2. PyGithub installed - `pip install PyGithub`
3. Push access - the [Github Traffic API](https://developer.github.com/v3/repos/traffic/) requires push access to see statistics

### Running
```bash
python GithubStats.py -t <token> -o <github-org> -s <YYYY-MM-DD>
```

This will output text to the console and produce a .csv file named `github-stats-YYYY-MM-DD.csv`

This is hard-coded to pull stats for 7 days after the start date specified.
