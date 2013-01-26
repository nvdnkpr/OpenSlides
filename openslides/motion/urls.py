#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    openslides.motion.urls
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    URL list for the motion app.

    :copyright: 2011, 2012 by OpenSlides team, see AUTHORS.
    :license: GNU GPL, see LICENSE for more details.
"""

from django.conf.urls import url, patterns

urlpatterns = patterns('openslides.motion.views',
    url(r'^$',
        'motion_list',
        name='motion_list',
    ),

    url(r'^create/$',
        'motion_create',
        name='motion_new',
    ),

    url(r'^(?P<pk>\d+)/$',
        'motion_detail',
        name='motion_detail',
    ),

    url(r'^(?P<pk>\d+)/edit/$',
        'motion_edit',
        name='motion_edit',
    ),

    url(r'^(?P<pk>\d+)/version/(?P<version_id>[1-9]\d*)/$',
        'motion_detail',
        name='motion_version_detail',
    ),

    url(r'^(?P<pk>\d+)/support/$',
        'motion_support',
        name='motion_support',
    ),

    url(r'^(?P<pk>\d+)/unsupport/$',
        'motion_unsupport',
        name='motion_unsupport',
    ),
)
