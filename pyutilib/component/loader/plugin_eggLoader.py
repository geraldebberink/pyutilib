#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

# This software is adapted from the Trac software (specifically, the trac.core
# module.  The Trac copyright statement is included below.

__all__ = ['EggLoader']

import os
import sys
import logging
from pyutilib.component.config import ManagedPlugin
from pyutilib.component.core import implements, ExtensionPoint, IPluginLoader

try:
    if not 'pkg_resources' in sys.modules:
        #
        # Avoid a re-import, which causes setup.py warnings...
        #
        import pkg_resources
    from pkg_resources import working_set, DistributionNotFound, VersionConflict, UnknownExtra, Environment
    pkg_resources_avail = True

    def pkg_environment(path):
        return Environment(path)
except ImportError:

    def pkg_environment(path):
        return None

    pkg_resources_avail = False

logger = logging.getLogger('pyutilib.component.core.pca')


class EggLoader(ManagedPlugin):
    """
    Loader that looks for Python egg files in the plugins directories.
    These files get exampled with the pkg_resources package, and
    Plugin classes are loaded.

    Note: this plugin should not be directly constructed.  Instead,
    the user should employ the PluginFactory_EggLoader function.
    """

    implements(IPluginLoader, service=True)

    def __init__(self, **kwds):
        """EggLoader constructor.  The 'namespace' keyword option is
        required."""
        if 'name' not in kwds:
            kwds['name'] = "EggLoader." + kwds['namespace']
        super(EggLoader, self).__init__(**kwds)
        self.entry_point_name = kwds['namespace'] + ".plugins"
        if not pkg_resources_avail:
            logger.warning(
                'A dummy EggLoader service is being constructed, because the pkg_resources package is not available on this machine.')

    def load(self, env, search_path, disable_re, name_re):
        generate_debug_messages = __debug__ and env.log.isEnabledFor(
            logging.DEBUG)
        if not pkg_resources_avail:
            if generate_debug_messages:
                env.log.debug(
                    'The EggLoader service is terminating early because the pkg_resources package is not available on this machine.')
            return

        env.log.info('BEGIN -  Loading plugins with an EggLoader service')
        distributions, errors = working_set.find_plugins(
            pkg_environment(search_path))
        for dist in distributions:
            if name_re.match(str(dist)):
                if generate_debug_messages:
                    env.log.debug('Adding plugin %r from %r', dist,
                                  dist.location)
                working_set.add(dist)
            else:
                if generate_debug_messages:
                    env.log.debug('Ignoring plugin %r from %r', dist,
                                  dist.location)

        def _log_error(item, e):
            gen_debug = __debug__ and env.log.isEnabledFor(logging.DEBUG)
            if isinstance(e, DistributionNotFound):
                if gen_debug:
                    env.log.debug('Skipping "%s": ("%s" not found)', item, e)
            elif isinstance(e, VersionConflict):
                if gen_debug:
                    env.log.debug('Skipping "%s": (version conflict "%s")',
                                  item, e)
            elif isinstance(e, UnknownExtra):
                env.log.error('Skipping "%s": (unknown extra "%s")', item, e)
            elif isinstance(e, ImportError):
                env.log.error('Skipping "%s": (can\'t import "%s")', item, e)
            else:
                env.log.error('Skipping "%s": (error "%s")', item, e)

        for dist, e in errors.items():
            _log_error(dist, e)

        for entry in working_set.iter_entry_points(self.entry_point_name):
            if generate_debug_messages:
                env.log.debug('Loading %r from %r', entry.name,
                              entry.dist.location)
            try:
                entry.load(require=True)
            except (ImportError, DistributionNotFound, VersionConflict,
                    UnknownExtra):
                e = sys.exc_info()[1]
                _log_error(entry, e)
            else:
                if not disable_re.match(os.path.dirname(
                        entry.module_name)) is None:
                    #_enable_plugin(env, entry.module_name)
                    pass

        env.log.info('END -    Loading plugins with an EggLoader service')

# Copyright (C) 2005-2008 Edgewall Software
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Christopher Lenz <cmlenz@gmx.de>
