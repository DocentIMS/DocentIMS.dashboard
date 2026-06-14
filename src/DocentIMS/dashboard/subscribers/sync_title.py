# -*- coding: utf-8 -*-
import logging


logger = logging.getLogger(__name__)


def sync_title_from_project_title(obj, event):
    """Keep the object title in sync with the "Project Title" field.

    The Add Project Connection form no longer exposes the standard "Title"
    field; "Project Title" is used the same way "Title" was used. We mirror it
    onto the object's title so listings, search results, breadcrumbs and the
    welcome emails all reflect the entered Project Title.
    """
    if getattr(obj, "portal_type", None) != "Project":
        return

    project_title = getattr(obj, "project_title", None)
    if project_title and obj.title != project_title:
        obj.title = project_title
        try:
            obj.reindexObject(idxs=["Title", "SearchableText", "sortable_title"])
        except Exception:  # pragma: no cover - reindex best effort
            logger.exception("Could not reindex Project after title sync")
