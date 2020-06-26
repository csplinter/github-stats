import argparse
import csv
import os
import pygsheets
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


def get_all_stats_for_day(g, repo, day=None, gsheet=False, gsheet_creds_file=None, gsheet_name=None, gsheet_worksheet_name=None, excluded_contributors=None):
    repo = g.get_repo(repo)

    row = []
    
    if not day:
        day = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    row.append(day)

    if gsheet:
        gsheet = pygsheets.authorize(service_file=gsheet_creds_file).open(gsheet_name)
        github_wks = gsheet.worksheet_by_title(gsheet_worksheet_name)
        cells = github_wks.get_all_values(include_tailing_empty=False, include_tailing_empty_rows=False, returnas='cells')
        last_row = len(cells)

    views_traffic = repo.get_views_traffic()
    views = views_traffic.get('views')
    data = dict()
    data[day] = {}
    
    for v in views:
        if v.timestamp.strftime("%Y-%m-%d") == day:
            data[day]['views unique'] = v.uniques
            data[day]['views count'] = v.count

    clones_traffic = repo.get_clones_traffic()
    clones = clones_traffic.get('clones')

    for c in clones:
        if c.timestamp.strftime("%Y-%m-%d") == day:
            data[day]['clones unique'] = c.uniques
            data[day]['clones count'] = c.count

    for k in data.keys():
        data[k]['stars'] = 0
        data[k]['forks'] = 0
        data[k]['issues'] = 0
        data[k]['issues names'] = ''
        data[k]['comments'] = 0
        data[k]['comments names'] = ''
        data[k]['reactions'] = 0
        data[k]['reactions names'] = ''

    forks = repo.get_forks()

    for f in forks:
        if f.created_at.strftime("%Y-%m-%d") in data.keys():
            data[f.created_at.strftime("%Y-%m-%d")]['forks'] += 1

    stars = repo.get_stargazers_with_dates()

    for s in stars:
        if s.starred_at.strftime("%Y-%m-%d") in data.keys():
            data[s.starred_at.strftime("%Y-%m-%d")]['stars'] += 1

    issues = repo.get_issues()

    for i in issues:
        if i.created_at.strftime("%Y-%m-%d") in data.keys() and i.user.login not in excluded_contributors:
            data[i.created_at.strftime("%Y-%m-%d")]['issues'] += 1
            data[i.created_at.strftime("%Y-%m-%d")]['issues names'] += i.user.login + '\n'
        if i.comments > 0:
            comments = i.get_comments()
            for c in comments:
                if c.created_at.strftime("%Y-%m-%d") in data.keys() and c.user.login not in excluded_contributors:
                    data[c.created_at.strftime("%Y-%m-%d")]['comments'] += 1
                    data[c.created_at.strftime("%Y-%m-%d")]['comments names'] += c.user.login + '\n'
        reactions = i.get_reactions()
        for r in reactions:
            if r.created_at.strftime("%Y-%m-%d") in data.keys() and r.user.login not in excluded_contributors:
                data[r.created_at.strftime("%Y-%m-%d")]['reactions'] += 1
                data[r.created_at.strftime("%Y-%m-%d")]['reactions names'] += r.user.login + '\n'

    for key, value in data.items():
        dictlist = [key]
        for val in value.values():
            dictlist.append(val)
        if gsheet:
            github_wks.insert_rows(last_row, number=1, values=dictlist)
        else:
            print(dictlist)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', default='mode', action='store')
    parser.add_argument('-o', '--github_org', action='store')
    parser.add_argument('-r', '--github_repo', action='store')
    parser.add_argument('-t', '--github_access_token', action='store')
    parser.add_argument('-s', '--start_date', action='store')
    parser.add_argument('-e', '--end_date', action='store')
    parser.add_argument('-x', '--term', action='store')
    parser.add_argument('-v', '--refdetails', action='store_true')
    parser.add_argument('-c', '--exclude_contributors', action='store', default=[])
    parser.add_argument('-g', '--gsheet', action='store_true')
    parser.add_argument('--gsheet_creds_file', action='store')
    parser.add_argument('--gsheet_name', action='store')
    parser.add_argument('--gsheet_worksheet_name', action='store')

    args = parser.parse_args()

    g = Github(args.github_access_token)

    if args.mode == 'usage':
        list_of_excluded_contributors = args.exclude_contributors
        if list_of_excluded_contributors is not []:
            list_of_excluded_contributors = args.exclude_contributors.split(',')

        if args.gsheet:
            if not args.gsheet_creds_file:
                raise Exception("Must specify --gsheet_creds_file when using -g")
            if not args.gsheet_name:
                raise Exception("Must specify --gsheet_name when using -g")
            if not args.gsheet_worksheet_name:
                raise Exception("Must specify --gsheet_worksheet_name when using -g")
            get_all_stats_for_day(g, args.github_org + '/' + args.github_repo,
                                  gsheet=True,
                                  gsheet_creds_file=args.gsheet_creds_file,
                                  gsheet_name=args.gsheet_name,
                                  gsheet_worksheet_name=args.gsheet_worksheet_name,
                                  excluded_contributors=list_of_excluded_contributors)
        else:
            get_all_stats_for_day(g, args.github_org + '/' + args.github_repo,
                                  excluded_contributors=list_of_excluded_contributors)

    if args.mode != 'contributors' and args.mode != 'usage':
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

    elif args.mode == 'refs':
        in_repo_name = g.search_repositories(query='{t} in:name created:{s}..{e}'.format(t=args.term, s=args.start_date, e=args.end_date))
        in_description = g.search_repositories(query='{t} in:description created:{s}..{e}'.format(t=args.term, s=args.start_date, e=args.end_date))
        in_readme = g.search_repositories(query='{t} in:readme created:{s}..{e}'.format(t=args.term, s=args.start_date, e=args.end_date))
        combined_list = []
        print('Found public repositories created between {s} and {e} with {t},'.format(s=args.start_date, e=args.end_date, t=args.term))
        print('in the name: {x}'.format(x=in_repo_name.totalCount))
        print('in the description: {x}'.format(x=in_description.totalCount))
        print('in the readme: {x}'.format(x=in_readme.totalCount))

        if args.refdetails:
            for repo in in_repo_name:
                combined_list.append(repo.full_name)

            for repo in in_description:
                combined_list.append(repo.full_name)

            for repo in in_readme:
                combined_list.append(repo.full_name)


            combined_set = set(combined_list)
            print('Count of unique repositories created since {s} referencing {t}: {x}'
                  ''.format(s=args.start_date, t=args.term, x=len(combined_set)))

            print(combined_set)

        # the code block below gets the most common words used in the repo names
        #wordcount = {}

        #for repo in combined_set:
        #    split_list = repo.split('/')[1].split('-')
        #    for word in split_list:
        #        if word not in wordcount:
        #            wordcount[word] = 1
        #        else:
        #            wordcount[word] += 1

        ##print({k: v for k, v in sorted(wordcount.items(), key=lambda item: item[1], reverse=True)})


if __name__ == "__main__":
    main()
    
