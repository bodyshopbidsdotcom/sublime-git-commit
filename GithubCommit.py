import sublime
import sublime_plugin
import os
import subprocess
import re
import webbrowser

class GithubCommitCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    current_file = self.view.file_name()
    if current_file is None:
      return

    git_dir_path, repo_file_path = git_directories(current_file)

    if git_dir_path is None:
      sublime.message_dialog('Not a git repo')
      return

    owner, repo = owner_and_repo(git_dir_path)

    if owner is None or repo is None:
      sublime.message_dialog('No github remote found')
      return

    line_number = self.view.rowcol(self.view.sel()[0].begin())[0] + 1

    command = ['git', 'blame', '--porcelain', '-L', '{0},{0}'.format(line_number), repo_file_path]

    output = output_from_command(*command, cwd=git_dir_path)
    sha = output.split('\n')[0].split()[0].strip()

    url = "https://github.com/{owner}/{repo}/commit/{sha}".format(
      owner = owner,
      repo = repo,
      sha = sha
    )
    webbrowser.open(url)

def owner_and_repo(git_dir_path):
    remotes = output_from_command('git', 'remote', '-v', cwd = git_dir_path)
    match = re.search(r'github\.com(?::|\/)([\w\-]+)\/([\w\-]+)\.git \(fetch\)', remotes)
    owner = None
    repo = None
    if match is not None:
      owner = str(match.group(1))
      repo = str(match.group(2))

    return [owner, repo]

def git_directories(current_file):
  check_path = os.path.dirname(current_file)
  git_dir_path = None
  repo_file_path = [os.path.basename(current_file)]
  while (len(check_path) > 1) and (git_dir_path is None):
    dirs = [possible_dir for possible_dir in os.listdir(check_path) if os.path.isdir(os.path.join(check_path, possible_dir))]
    if '.git' in dirs:
      git_dir_path = check_path
    else:
      repo_file_path.insert(0, os.path.basename(check_path))

    check_path = os.path.dirname(check_path)

  repo_file_path = os.path.join(*repo_file_path)
  return [git_dir_path, repo_file_path]

def output_from_command(*cmd, cwd=None):
  return subprocess.check_output(cmd, stderr = subprocess.STDOUT, cwd=cwd).decode("utf-8").strip()
