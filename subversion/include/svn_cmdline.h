/**
 * @copyright
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
 * @endcopyright
 *
 * @file svn_cmdline.h
 * @brief Support functions for command line programs
 */




#ifndef SVN_CMDLINE_H
#define SVN_CMDLINE_H

#ifndef DOXYGEN_SHOULD_SKIP_THIS
#define APR_WANT_STDIO
#endif
#include <apr_want.h>

#include "svn_utf.h"

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */


/** Set up the locale for character conversion, and initialize APR.
 * If @a error_stream is non-null, print error messages to the stream,
 * using @a progname as the program name. Return @c EXIT_SUCCESS if
 * successful, otherwise @c EXIT_FAILURE.
 *
 * @note This function should be called exactly once at program startup,
 *       before calling any other APR or Subversion functions.
 */
int svn_cmdline_init (const char *progname, FILE *error_stream);


/** Set @a *dest to an output-encoded C string from UTF-8 C string @a
 * src; allocate @a *dest in @a pool.
 */
svn_error_t *svn_cmdline_cstring_from_utf8 (const char **dest,
                                            const char *src,
                                            apr_pool_t *pool);

/** Like svn_utf_cstring_from_utf8_fuzzy, but converts to an
    output-encoded C string. */
const char *svn_cmdline_cstring_from_utf8_fuzzy (const char *src,
                                                 apr_pool_t *pool);

/** Set @a *dest to a UTF-8-encoded C string from input-encoded C
 * string @a src; allocate @a *dest in @a pool.
 */
svn_error_t * svn_cmdline_cstring_to_utf8 (const char **dest,
                                           const char *src,
                                           apr_pool_t *pool);

/** Set @a *dest to an output-encoded natively-formatted path string
 * from canonical path @a src; allocate @a *dest in @a pool.
 */
svn_error_t *svn_cmdline_path_local_style_from_utf8 (const char **dest,
                                                     const char *src,
                                                     apr_pool_t *pool);

#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* SVN_POOLS_H */
