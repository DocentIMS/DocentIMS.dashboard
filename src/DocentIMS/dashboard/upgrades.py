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


def reimport_project_type(setup_tool):
    """Reimport the Project type information.

    Picks up the new "Project Title", "Project Short Name" and "Project Very
    Short Name" fields and the removal of the plone.namefromtitle behavior
    (see profiles/default/types/Project.xml and content/project.xml).
    """
    setup_tool.runImportStepFromProfile(PROFILE_ID, "typeinfo")
    logger.info("Reimported type information for the Project content type")
