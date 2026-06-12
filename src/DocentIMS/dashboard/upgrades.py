# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

PROFILE_ID = "profile-DocentIMS.dashboard:default"


def reimport_actions(setup_tool):
    """Reimport portal actions.

    Removes the "Preferences" and the stock Plone "Dashboard" actions from
    the user pulldown for all users (see profiles/default/actions.xml).
    """
    setup_tool.runImportStepFromProfile(PROFILE_ID, "actions")
    logger.info(
        "Reimported actions: removed 'Preferences' and 'Dashboard' user actions"
    )
