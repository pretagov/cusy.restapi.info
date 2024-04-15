# -*- coding: utf-8 -*-
"""Service to get site information."""

from cusy.restapi.info.interfaces import ICusyRestapiInfoLayer
from plone.app.layout.navigation.root import getNavigationRootObject
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.CMFPlone.utils import getSiteLogo
from zope.component import adapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface

import plone.api


@implementer(IExpandableElement)
@adapter(Interface, ICusyRestapiInfoLayer)
class SiteInfo(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "siteinfo": {
                "@id": "{}/@siteinfo".format(self.context.absolute_url()),
            }
        }
        if not expand:
            return result

        registry = getUtility(IRegistry)
        site_settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)

        language_tool = plone.api.portal.get_tool(name="portal_languages")
        available_languages = language_tool.getSupportedLanguages()
        default_language = language_tool.getDefaultLanguage()

        portal = plone.api.portal.get()
        navigation_root = getNavigationRootObject(self.context, portal)
        logo = getSiteLogo(include_type=True)

        result["siteinfo"].update(
            {
                "title": site_settings.site_title,
                "navigation_root": navigation_root.absolute_url(),
                "logo_url": logo[0],
                "logo_type": logo[1],
                "logo_filename": logo[0][len(portal.absolute_url())+13:],
                "multilingual": len(available_languages) > 1,
                "available_languages": available_languages,
                "default_language": default_language,
            }
        )
        return result


class SiteInfoGet(Service):
    def reply(self):
        site_info = SiteInfo(self.context, self.request)
        return site_info(expand=True)["siteinfo"]
