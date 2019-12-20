import argparse
from github import Github
from github.GithubException import GithubException


def get_views(g, repo, start):
    repo = g.get_repo(repo)
    print(repo)
    try:
        c = repo.get_views_traffic()
        print(c)

        views = c.get('views')
        if len(views) < 14:
            print("Detected less than 14 data entries, manual calculation required")
            print(views)
        else:
            track = 0
            week_count = 0
            end_date = "not-set"

            for v in views:
                if start in v.timestamp.strftime("%Y-%m-%d"):
                    print("found start_date in: " + str(v))
                    track += 1

                if 0 < track <= 7:
                    print("adding view count for day: " + str(v))
                    week_count += v.count
                    if track == 7:
                        end_date = v.timestamp.strftime("%Y-%m-%d")
                    track += 1

            print("Total View Count for " + start + " to " + end_date + ": " + str(week_count))

    except GithubException as e:
        print()
        print("Skipping " + repo.full_name + " because of exception")
        print(e)
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all', action='store')
    parser.add_argument('-o', '--github_org', action='store')
    parser.add_argument('-r', '--github_repo', action='store')
    parser.add_argument('-t', '--github_access_token', action='store')
    parser.add_argument('-s', '--start_date', action='store')

    args = parser.parse_args()
    g = Github(args.github_access_token)

    if args.all == "all":
        org = g.search_repositories(query='org:{o} is:public'.format(o=args.github_org))

        for r in org:
            get_views(g, r.full_name, args.start_date)
    else:
        get_views(g, args.github_org + "/" + args.github_repo, args.start_date)


if __name__ == "__main__":
    main()

