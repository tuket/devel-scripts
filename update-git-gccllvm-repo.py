#!/usr/bin/python3
"""Script to update LLVM or GCC trunk devel repo.

Auto-detects either plain git or git-on-svn, then locates
nested repos, then runs fetch/rebase.

"""

import getopt
import os
import sys

import script_utils as u

# Dry run mode
flag_dryrun = False

# Echo commands mode
flag_echo = False


def docmd(cmd):
  """Execute a command."""
  if flag_echo or flag_dryrun:
    sys.stderr.write("executing: " + cmd + "\n")
  if flag_dryrun:
    return
  u.docmd(cmd)


def dochdir(thedir):
  """Switch to dir."""
  if flag_echo or flag_dryrun:
    sys.stderr.write("cd " + thedir + "\n")
  try:
    os.chdir(thedir)
  except OSError as err:
    u.error("chdir failed: %s" % err)


def do_check(subdir):
  """Make sure this repo has the master branch checked out."""
  here = os.getcwd()
  dn = os.path.dirname(subdir)
  dochdir(dn)
  lines = u.docmdlines("git rev-parse --abbrev-ref HEAD")
  if lines[0] != "master":
    u.error("error: repo at %s not on master "
            "branch (on '%s' instead" % (dn, lines[0]))
  dochdir(here)


def do_fetch(subdir):
  """Fetch/update this repo."""
  here = os.getcwd()
  dn = os.path.dirname(subdir)
  dochdir(dn)
  if os.path.exists(".git/svn"):
    docmd("git fetch")
    docmd("git svn rebase -l")
  else:
    docmd("git fetch")
    docmd("git rebase")
  dochdir(here)


def perform():
  """Top level driver routine."""
  if not os.path.exists(".git"):
    u.error("unable to locate top level .git in current dir")
  lines = u.docmdlines("find . -depth -name .git -print")
  lines.reverse()
  repos = lines
  for r in repos:
    u.verbose(1, "checking %s" % r)
    do_check(r)
  for r in repos:
    u.verbose(1, "visiting %s" % r)
    do_fetch(r)


def usage(msgarg):
  """Print usage and exit."""
  me = os.path.basename(sys.argv[0])
  if msgarg:
    sys.stderr.write("error: %s\n" % msgarg)
  print("""\
    usage:  %s [options]

    options:
    -d    increase debug msg verbosity level
    -D    dryrun mode (echo commands but do not execute)

    """ % me)
  sys.exit(1)


def parse_args():
  """Command line argument parsing."""
  global flag_dryrun, flag_echo

  try:
    optlist, args = getopt.getopt(sys.argv[1:], "deD")
  except getopt.GetoptError as err:
    # unrecognized option
    usage(str(err))
  if args:
    usage("unknown extra args")

  for opt, _ in optlist:
    if opt == "-d":
      u.increment_verbosity()
    elif opt == "-e":
      flag_echo = True
    elif opt == "-D":
      flag_dryrun = True


parse_args()
u.setdeflanglocale()
perform()
