#!/usr/bin/env python
#
#  actions.py:  routines that actually run the svn client.
#
#  Subversion is a tool for revision control. 
#  See http://subversion.tigris.org for more information.
#    
# ====================================================================
# Copyright (c) 2001 Collabnet.  All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.  The terms
# are also available at http://subversion.tigris.org/license-1.html.
# If newer versions of this license are posted there, you may use a
# newer version instead, at your option.
#
######################################################################

import os.path, shutil, string

import main, tree  # general svntest routines in this module.


######################################################################
# RA_LOCAL Utility:   creating local repositories
#
# Used by every RA_LOCAL test, so that they can run independently of
# one another.  The first time it's run, it executes 'svnadmin' to
# create a repository and then 'svn imports' the greek tree.
# Thereafter, every time this routine is called, it recursively copies
# the `pristine repos' to a new location.

def guarantee_greek_repository(path):
  """Guarantee that a local svn repository exists at PATH, containing
  nothing but the greek-tree at revision 1."""

  if path == main.pristine_dir:
    print "ERROR:  attempt to overwrite the pristine repos!  Aborting."
    exit(1)

  # If there's no pristine repos, create one.
  if not os.path.exists(main.pristine_dir):
    main.create_repos(main.pristine_dir)
    
    # dump the greek tree to disk.
    main.write_tree(main.greek_dump_dir,
                    [[x[0], x[1]] for x in main.greek_tree])

    # figger out the "file:" url needed to run import
    url = "file://" + os.path.abspath(main.pristine_dir)
    # import the greek tree.
    output = main.run_svn("import", url, main.greek_dump_dir)

    # verify the printed output of 'svn import'.
    lastline = string.strip(output.pop())
    if lastline != 'Commit succeeded.':
      print "ERROR:  import did not 'succeed', while creating greek repos."
      print "The final line from 'svn import' was:"
      print lastline
      exit(1)
    output_tree = tree.build_tree_from_commit(output)

    output_list = []
    path_list = [x[0] for x in main.greek_tree]
    for apath in path_list:
      item = [ os.path.join(".", apath), None, {}, {'verb' : 'Adding'}]
      output_list.append(item)
    expected_output_tree = tree.build_generic_tree(output_list)
      
    if tree.compare_trees(output_tree, expected_output_tree):
      print "ERROR:  output of import command is unexpected."
      exit(1)

  # Now that the pristine repos exists, copy it to PATH.
  if os.path.exists(path):
    shutil.rmtree(path)
  if not os.path.exists(os.path.dirname(path)):
    os.makedirs(os.path.dirname(path))
  shutil.copytree(main.pristine_dir, path)


######################################################################
# Subversion Actions
#
# These are all routines that invoke 'svn' in particular ways, and
# then verify the results by comparing expected trees with actual
# trees.
#
# For all the functions below, the OUTPUT_TREE and DISK_TREE args need
# to be created by feeding carefully constructed lists to
# tree.build_generic_tree().  A STATUS_TREE can be built by
# hand, or by editing the tree returned by get_virginal_status_list().


def run_and_verify_checkout(URL, wc_dir_name, output_tree, disk_tree,
                            singleton_handler_a = None,
                            a_baton = None,
                            singleton_handler_b = None,
                            b_baton = None):
  """Checkout the the URL into a new directory WC_DIR_NAME.

  The subcommand output will be verified against OUTPUT_TREE,
  and the working copy itself will be verified against DISK_TREE.
  SINGLETON_HANDLER_A and SINGLETON_HANDLER_B will be passed to
  tree.compare_trees - see that function's doc string for more details.
  Return 0 if successful."""

  # Remove dir if it's already there.
  main.remove_wc(wc_dir_name)

  # Checkout and make a tree of the output.
  output = main.run_svn ('co', URL, '-d', wc_dir_name)
  mytree = tree.build_tree_from_checkout (output)

  # Verify actual output against expected output.
  if tree.compare_trees (mytree, output_tree):
    return 1

  # Create a tree by scanning the working copy
  mytree = tree.build_tree_from_wc (wc_dir_name)

  # Verify expected disk against actual disk.
  if tree.compare_trees (mytree, disk_tree,
                                 singleton_handler_a, a_baton,
                                 singleton_handler_b, b_baton):
    return 1

  return 0


def run_and_verify_update(wc_dir_name,
                          output_tree, disk_tree, status_tree,
                          singleton_handler_a = None,
                          a_baton = None,
                          singleton_handler_b = None,
                          b_baton = None,
                          *args):
  """Update WC_DIR_NAME into a new directory WC_DIR_NAME.  *ARGS are
  any extra optional args to the update subcommand.

  The subcommand output will be verified against OUTPUT_TREE, and the
  working copy itself will be verified against DISK_TREE.  If optional
  STATUS_OUTPUT_TREE is given, then 'svn status' output will be
  compared.  (This is a good way to check that revision numbers were
  bumped.)  SINGLETON_HANDLER_A and SINGLETON_HANDLER_B will be passed to
  tree.compare_trees - see that function's doc string for more details.
  Return 0 if successful."""

  # Update and make a tree of the output.
  output = main.run_svn ('up', wc_dir_name, *args)
  mytree = tree.build_tree_from_checkout (output)

  # Verify actual output against expected output.
  if tree.compare_trees (mytree, output_tree):
    return 1

  # Create a tree by scanning the working copy
  mytree = tree.build_tree_from_wc (wc_dir_name)

  # Verify expected disk against actual disk.
  if tree.compare_trees (mytree, disk_tree,
                                 singleton_handler_a, a_baton,
                                 singleton_handler_b, b_baton):
    return 1

  # Verify via 'status' command too, if possible.
  if status_tree:
    if run_and_verify_status(wc_dir_name, status_tree):
      return 1
  
  return 0


def run_and_verify_commit(wc_dir_name, output_tree, status_output_tree,
                          singleton_handler_a = None,
                          a_baton = None,
                          singleton_handler_b = None,
                          b_baton = None,
                          *args):
  """Commit and verify results within working copy WC_DIR_NAME,
  sending ARGS to the commit subcommand.
  
  The subcommand output will be verified against OUTPUT_TREE.  If
  optional STATUS_OUTPUT_TREE is given, then 'svn status' output will
  be compared.  (This is a good way to check that revision numbers
  were bumped.)  SINGLETON_HANDLER_A and SINGLETON_HANDLER_B will be passed to
  tree.compare_trees - see that function's doc string for more details.
  Return 0 if successful."""

  # Commit.
  output = main.run_svn ('ci', *args)

  # Remove the final output line, and verify that 'Commit succeeded'.
  lastline = ""
  if len(output):
    lastline = string.strip(output.pop())

  if lastline != 'Commit succeeded.':
    print "ERROR:  commit did not 'succeed'."
    print "The final line from 'svn ci' was:"
    print lastline
    return 1

  # Convert the output into a tree.
  mytree = tree.build_tree_from_commit (output)

  # Verify actual output against expected output.
  if tree.compare_trees (mytree, output_tree):
    return 1

  # Verify via 'status' command too, if possible.
  if status_output_tree:
    if run_and_verify_status(wc_dir_name, status_output_tree):
      return 1

  return 0


def run_and_verify_status(wc_dir_name, output_tree,
                          singleton_handler_a = None,
                          a_baton = None,
                          singleton_handler_b = None,
                          b_baton = None):
  """Run 'status' on WC_DIR_NAME and compare it with the
  expected OUTPUT_TREE.  SINGLETON_HANDLER_A and SINGLETON_HANDLER_B will
  be passed to tree.compare_trees - see that function's doc string for
  more details.
  Return 0 on success."""

  output = main.run_svn ('status', wc_dir_name)

  mytree = tree.build_tree_from_status (output)

  # Verify actual output against expected output.
  if tree.compare_trees (mytree, output_tree,
                                 singleton_handler_a, a_baton,
                                 singleton_handler_b, b_baton):
    return 1

  return 0


######################################################################
# Other general utilities


# This allows a test to *quickly* bootstrap itself.
def make_repo_and_wc(test_name):
  """Create a fresh repository and checkout a wc from it.

  The repo and wc directories will both be named TEST_NAME, and
  repsectively live within the global dirs 'general_repo_dir' and
  'general_wc_dir' (variables defined at the top of this test
  suite.)  Return 0 on success, non-zero on failure."""

  # Where the repos and wc for this test should be created.
  wc_dir = os.path.join(main.general_wc_dir, test_name)
  repo_dir = os.path.join(main.general_repo_dir, test_name)

  # Create (or copy afresh) a new repos with a greek tree in it.
  guarantee_greek_repository(repo_dir)

  # Generate the expected output tree.
  output_list = []
  path_list = [x[0] for x in main.greek_tree]
  for path in path_list:
    item = [ os.path.join(wc_dir, path), None, {}, {'status' : 'A '} ]
    output_list.append(item)
  expected_output_tree = tree.build_generic_tree(output_list)

  # Generate an expected wc tree.
  expected_wc_tree = tree.build_generic_tree(main.greek_tree)

  # Do a checkout, and verify the resulting output and disk contents.
  url = 'file:///' + os.path.abspath(repo_dir)
  return run_and_verify_checkout(url, wc_dir,
                                 expected_output_tree,
                                 expected_wc_tree)


# Duplicate a working copy or other dir.
def duplicate_dir(wc_name, wc_copy_name):
  """Copy the working copy WC_NAME to WC_COPY_NAME.  Overwrite any
  existing tree at that location."""

  if os.path.exists(wc_copy_name):
    shutil.rmtree(wc_copy_name)
  shutil.copytree(wc_name, wc_copy_name)
  


# A generic starting state for the output of 'svn status'.
# Returns a list of the form:
#
#   [ ['repo', None, {}, {'status':'_ ', 'wc_rev':'1', 'repos_rev':'1'}],
#     ['repo/A', None, {}, {'status':'_ ', 'wc_rev':'1', 'repos_rev':'1'}],
#     ['repo/A/mu', None, {}, {'status':'_ ', 'wc_rev':'1', 'repos_rev':'1'}],
#     ... ]
#
def get_virginal_status_list(wc_dir, rev):
  """Given a WC_DIR, return a list describing the expected 'status'
  output of an up-to-date working copy at revision REV.  (i.e. the
  repository and working copy files are all at REV).

  WARNING:  REV is a string, not an integer. :)

  The list returned is suitable for passing to
  tree.build_generic_tree()."""

  output_list = [[wc_dir, None, {},
                  {'status' : '_ ',
                   'wc_rev' : rev,
                   'repos_rev' : rev}]]
  path_list = [x[0] for x in main.greek_tree]
  for path in path_list:
    item = [os.path.join(wc_dir, path), None, {},
            {'status' : '_ ',
             'wc_rev' : rev,
             'repos_rev' : rev}]
    output_list.append(item)

  return output_list




### End of file.
# local variables:
# eval: (load-file "../../../svn-dev.el")
# end:




