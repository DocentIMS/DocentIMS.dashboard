# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s DocentIMS.dashboard -t test_project.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src DocentIMS.dashboard.testing.DOCENTIMS_DASHBOARD_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/DocentIMS/dashboard/tests/robot/test_project.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Project
  Given a logged-in site administrator
    and an add Project form
   When I type 'My Project' into the title field
    and I submit the form
   Then a Project with the title 'My Project' has been created

Scenario: As a site administrator I can view a Project
  Given a logged-in site administrator
    and a Project 'My Project'
   When I go to the Project view
   Then I can see the Project title 'My Project'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Project form
  Go To  ${PLONE_URL}/++add++Project

a Project 'My Project'
  Create content  type=Project  id=my-project  title=My Project

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Project view
  Go To  ${PLONE_URL}/my-project
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Project with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Project title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
