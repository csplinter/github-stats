import argparse
import csv
from datetime import datetime, timedelta
from github import Github
from github.GithubException import GithubException


CSV_NAME = 'github-stats-' + datetime.now().strftime("%Y-%m-%d") + '.csv'
DATES = []


def set_dates_for_week(start):
    DATES.append(start)

    start_date = datetime.strptime(start, '%Y-%m-%d')

    for x in range(1, 7):
        DATES.append(datetime.strftime(start_date + timedelta(days=x), '%Y-%m-%d'))


def get_views(g, repo):
    repo = g.get_repo(repo)
    print(repo.full_name)

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

        with open(CSV_NAME, mode='a') as output:
            writer = csv.writer(output, delimiter=',')
            writer.writerow(csv_row)

    except GithubException:
        print(repo.full_name + ": Skipping because of exception")
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', default='all', action='store')
    parser.add_argument('-o', '--github_org', action='store')
    parser.add_argument('-r', '--github_repo', action='store')
    parser.add_argument('-t', '--github_access_token', action='store')
    parser.add_argument('-s', '--start_date', action='store')

    args = parser.parse_args()

    g = Github(args.github_access_token)

    set_dates_for_week(args.start_date)

    with open(CSV_NAME, mode='w') as output:
        fields = ['Repository'] + DATES + ['Week Total']
        writer = csv.writer(output, delimiter=',')
        writer.writerow(fields)

    if args.all == "all":
        org = g.search_repositories(query='org:{o} is:public'.format(o=args.github_org))

        for r in org:
            get_views(g, r.full_name)
    else:
        get_views(g, args.github_org + "/" + args.github_repo)


if __name__ == "__main__":
    main()

