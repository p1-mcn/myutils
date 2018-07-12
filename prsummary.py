#!/usr/bin/python3
#
# 12/07/2018: p1-mcn created this util
#
# Utility to generate a summary of PTM repository pull requests
#
# Customizable parameters:
#
#   HL_USER -> highlight user name if review is required
#
#   CI_BRANCH -> name of the continuous integration branch, PRs printed in RED
#                are pending, PRs printed in green are in the CI branch.

from requests import get, post
import getopt, sys, subprocess

HL_USER     = 'p1-mcn'
CI_BRANCH   = 'ci-testing-5.5'
POST_LABEL  = 'Postponed'



##########################################################################
req = 'https://api.github.com/repos/P1sec/ptm/pulls?state=open&direction=asc&per_page=1000&access_token='
token = None

class txtcolor:
    YELLOW  = '\x1b[1;33m'
    GREEN   = '\x1b[1;32m'
    RED     = '\x1b[1;31m'
    MAGENTA = '\x1b[1;35m'
    CYAN    = '\x1b[1;36m'
    NONE    = '\x1b[0m'
    BOLD    = '\x1b[1m'
    BU      = '\x1b[1;4m'

def is_in_continuous_integration(labels):

    for label in labels:
        if label['name'] == CI_BRANCH:
            return True

    return False

def is_postponed(labels):

    for label in labels:
        if label['name'] == POST_LABEL:
            return True

    return False

def i_am_reviewer(reviewers):

    for r in reviewers:
        if r['login'] == HL_USER:
            return True
    return False

def main():

    token = subprocess.check_output(['cat', 'gh_token.txt']).decode(sys.stdout.encoding).strip()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "pr", ["postponed", "my-reviews"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    only_postponed = False
    only_my_reviews = False
    for o, a in opts:
        if o in ('-p', '--postponed'):
            only_postponed = True
        elif o in ("-r", "--my-reviews"):
            only_my_reviews = True
        else:
            assert False, "unhandled option"

    resp = get(req+str(token)).json()

    total_prs = 0
    ci_prs = 0

    for v in resp:
        pr_number       = v['number']
        pr_author       = v['user']['login']
        pr_title        = v['title']
        pr_reviewers    = v['requested_reviewers']
        pr_url          = v['html_url']
        pr_labels       = v['labels']

        br_label        = v['head']['label']

        total_prs = total_prs + 1

        if only_my_reviews and not i_am_reviewer(pr_reviewers):
            continue

        if only_postponed and not is_postponed(pr_labels):
            continue

        if is_in_continuous_integration(pr_labels):
            print(txtcolor.GREEN, end='')
            ci_prs = ci_prs + 1
        else:
            print(txtcolor.RED, end='')

        print("Pull request #" + str(pr_number) + " by " + str(pr_author), end='')
        print(txtcolor.NONE + " (" + txtcolor.YELLOW + pr_url + ")" + txtcolor.NONE)

        print(txtcolor.BOLD + "  Title:             " + txtcolor.NONE + pr_title)
        print(txtcolor.BOLD + "  Pending reviews:   " + txtcolor.NONE, end='')    

        for reviewer in pr_reviewers:
            r_login = reviewer['login']
            if r_login == HL_USER:
                print(txtcolor.CYAN + r_login + txtcolor.NONE + " ", end='')
            else:
                print(r_login + " ", end='')
        print("")

        print(txtcolor.BOLD + "  Branch label:      " + txtcolor.NONE  + br_label)

        print(txtcolor.BOLD + "  PR labels:         " + txtcolor.NONE , end='')
        for label in pr_labels:
            label_name = label['name']
            print("[" + label_name + "] ", end='')
        print("")

    if ( not (only_postponed or only_my_reviews) ):
        print("------------------------------------------------------------")
        print("PRs in continuous integration: %d/%d" % (ci_prs, total_prs)) 


if __name__ == "__main__":
    main()
