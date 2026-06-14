# -*- coding: utf-8 -*-
import logging

from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getUtility

logger = logging.getLogger(__name__)

PROFILE_ID = "profile-DocentIMS.dashboard:default"

# Behaviors that put the standard "Title" and "Summary" (description) fields
# on the Project add/edit form. They are no longer wanted: the object title
# and id come from the required "Project Title" field (via the custom
# INameFromTitle adapter and the title-sync subscriber).
PROJECT_FORM_BEHAVIORS_TO_REMOVE = (
    "plone.basic",
    "plone.dublincore",
    "plone.namefromtitle",
)


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


def remove_title_summary_behaviors(setup_tool=None):
    """Remove the standard Title/Summary fields from the Project form.

    Reimporting the type info does not drop behaviors that are already on the
    stored FTI (the behaviors import is additive), so the "Title"
    (plone.namefromtitle) and "Summary"/description (plone.basic) fields keep
    showing on existing sites. Strip those behaviors from the FTI directly.
    """
    fti = getUtility(IDexterityFTI, name="Project")
    current = list(fti.behaviors)
    new = [b for b in current if b not in PROJECT_FORM_BEHAVIORS_TO_REMOVE]
    if new != current:
        removed = [b for b in current if b not in new]
        fti.behaviors = tuple(new)
        logger.info(
            "Removed behaviors from Project FTI: %s", ", ".join(removed)
        )
    else:
        logger.info("Project FTI had no Title/Summary behaviors to remove")
