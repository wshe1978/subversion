/* lock-nodes-table.h : internal interface to ops on `lock-nodes' table
 *
 * ====================================================================
 * Copyright (c) 2000-2004 CollabNet.  All rights reserved.
 *
 * This software is licensed as described in the file COPYING, which
 * you should have received as part of this distribution.  The terms
 * are also available at http://subversion.tigris.org/license-1.html.
 * If newer versions of this license are posted there, you may use a
 * newer version instead, at your option.
 *
 * This software consists of voluntary contributions made by many
 * individuals.  For exact contribution history, see the revision
 * history and logs, available at http://subversion.tigris.org/.
 * ====================================================================
 */

#ifndef SVN_LIBSVN_FS_LOCKS_TABLE_H
#define SVN_LIBSVN_FS_LOCKS_TABLE_H

#include "svn_fs.h"
#include "svn_error.h"
#include "../trail.h"
#include "../fs.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/* Open a `locks' table in ENV.  If CREATE is non-zero, create
   one if it doesn't exist.  Set *LOCKS_P to the new table.
   Return a Berkeley DB error code.  */
int svn_fs_bdb__open_lock_nodes_table (DB **locks_p,
                                       DB_ENV *env,
                                       svn_boolean_t create);


#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* SVN_LIBSVN_FS_LOCKS_TABLE_H */
