# create github with body
import requests


def create_issue(title, body=None, assignee=None, milestone=None, labels=None):
  """Create an issue and return the issue number.

    :param title: str
    :param body: str
    :param assignee: str
    :param labels: list[str]
    :rtype: int
    :return: issue number

    """
  url = GITHUB_API_URL + '/repos/{assignee}/{repo}/issues'.format(assignee=assignee, repo=REPO_NAME)
  issue = {'title': title,
           'body': body,
           'assignee': assignee,
           'labels': labels,
           }
  if milestone:
    issue['milestone'] = milestone
  r = requests.post(url, json=issue, auth=AUTH)
  return r.json()['number']