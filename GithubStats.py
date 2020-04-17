import argparse
import csv
import os
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException

DATES = []


def set_dates_for_week(start):
    DATES.append(start)

    start_date = datetime.strptime(start, '%Y-%m-%d')

    for x in range(1, 7):
        DATES.append(datetime.strftime(start_date + timedelta(days=x), '%Y-%m-%d'))


def get_views(g, repo):
    repo = g.get_repo(repo)
    print(repo.full_name)

    csv_name = 'github-stats-views-' + repo.full_name.split('/')[0] + '-' + datetime.now().strftime("%Y-%m-%d") + '.csv'

    if not os.path.exists(csv_name):
        with open(csv_name, mode='w') as output:
            fields = ['Repository'] + DATES + ['Week Total']
            writer = csv.writer(output, delimiter=',')
            writer.writerow(fields)

    csv_row = [repo.full_name]

    try:
        c = repo.get_views_traffic()

        views = c.get('views')

        weekly_view_count = 0

        for date in DATES:
            found = False
            for v in views:
                if date in v.timestamp.strftime("%Y-%m-%d"):
                    found = True
                    print("Adding views for " + date + " to weekly count for " + repo.full_name + ": " + str(v.count))
                    csv_row.append(v.count)
                    weekly_view_count += v.count
            if found is False:
                print("No stats entry found for date: " + date)
                csv_row.append(0)

        print(DATES[0] + " to " + DATES[6] + " view count for " + repo.full_name + ": " + str(weekly_view_count))
        print()
        csv_row.append(weekly_view_count)

        with open(csv_name, mode='a') as output:
            writer = csv.writer(output, delimiter=',')
            writer.writerow(csv_row)

    except GithubException:
        print(repo.full_name + ": Skipping because of exception")
        print()


def get_commits(g, repo, start, end):
    repo = g.get_repo(repo)

    csv_name = 'github-stats-commits-' + repo.full_name.replace('/', '-') + '-' + datetime.now().strftime("%Y-%m-%d") + '.csv'

    with open(csv_name, mode='w') as output:
        fields = ['Commit Date', 'Committer', 'Commit']
        writer = csv.writer(output, delimiter=',')
        writer.writerow(fields)

    commit_url = 'https://github.com/{orgrepo}/commit/'.format(orgrepo=repo.full_name)
    commits = repo.get_commits(since=start, until=end)
    with open(csv_name, mode='a') as output:
        for c in commits:
            csv_row = list()
            csv_row.append(c.commit.committer.date.strftime("%Y-%m-%d"))
            csv_row.append(c.commit.committer.name)
            csv_row.append(commit_url + c.sha[:7])

            writer = csv.writer(output, delimiter=',')
            writer.writerow(csv_row)


def get_contributors(g, repo):
    repo = g.get_repo(repo)
    contributors = repo.get_contributors()

    csv_name = 'github-stats-contributors-' + repo.full_name.replace('/', '-') + '-' + datetime.now().strftime(
        "%Y-%m-%d") + '.csv'

    if not os.path.exists(csv_name):
        with open(csv_name, mode='w') as output:
            fields = ['Date', 'Repository', 'Number of Contributors']
            writer = csv.writer(output, delimiter=',')
            writer.writerow(fields)

    with open(csv_name, mode='a') as output:
        writer = csv.writer(output, delimiter=',')
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), repo.full_name, contributors.totalCount])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', default='mode', action='store')
    parser.add_argument('-o', '--github_org', action='store')
    parser.add_argument('-r', '--github_repo', action='store')
    parser.add_argument('-t', '--github_access_token', action='store')
    parser.add_argument('-s', '--start_date', action='store')

    args = parser.parse_args()

    g = Github(args.github_access_token)

    if args.mode != 'contributors':
        set_dates_for_week(args.start_date)

    if args.mode == "views":
        org = g.search_repositories(query='org:{o}'.format(o=args.github_org))

        for r in org:
            get_views(g, r.full_name)

        if args.github_org == "KillrVideo":
            get_views(g, g.get_repo("KillrVideo/killrvideo-java").full_name)
            get_views(g, g.get_repo("KillrVideo/killrvideo-integration-tests").full_name)
            get_views(g, g.get_repo("KillrVideo/killrvideo-csharp").full_name)

    elif args.mode == "commits":
        get_commits(g, args.github_org + '/' + args.github_repo,
                    datetime.strptime(args.start_date, '%Y-%m-%d'),
                    datetime.strptime(DATES[6], '%Y-%m-%d') + timedelta(days=1))
    elif args.mode == 'contributors':
        get_contributors(g, args.github_org + '/' + args.github_repo)


if __name__ == "__main__":
    main()
