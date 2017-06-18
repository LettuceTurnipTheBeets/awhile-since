# CHANGE LOG:
## 9/8/15
 +   Added Captcha to the registration form
 +   Fixed registration form email showing up not blank

9/12/15 - Added thumbnails and picture uploads to the tasks

9/13/15 - Changed enable variable names from (name)_en to en_(name)
     - Added real time javascript functionality with an actual timer
     - Added a script to table row color when hovered over
     - Changed title from "Changelog" to "changelog"
     - Moved the javascript functions from "profile_detail.html" to "functions.js" and I'm loading them in with the base template
	
9/18/15 - Changed "profile_detail.html" to have the non-time data be handled by the server and the time data be handled by Javascript in the client
     - Used Ajax to asynchronously submit the new task modal form data

9/27/15 - Changed the cursor to only be a pointer when you can click on something
     - Used Ajax to aynchronously submit the edit task modal form
     - The edit task modal form can update the task data, delete it, or cancel

9/28/15 - Went from using two modals for editing and creating to one modal
     - Cleaned up the JQuery functions for modals, their values, and their buttons
     - Fixed the modal hide/show buttons

11/8/15 - Removed the seconds and microseconds value from stored time
     - Removed the Django Allauth package
     - Removed the Swamp Dragon Package
     - Added an image view on the home page
     - Overall polished the site and got it ready for a test demo version
     - Installed and began to configure the Django REST framework (mostly for its API and authentication system)

12/6/15 - Removed Bootstrap entirely from the project and replaced it with JQuery Mobile
     
2/16/16 - Removed last acknowledged date from the profile and hide/due flags
     - Added category, category_warning, category_alarm variables
     - Tweaked views to allow for correct smartTRACKing functionality
     - Flash 'SmartTRACK in Progress' during smartTRACK enabled

2/19/16 - Fixed the acknowledge functionality
     - Edit Save now works correctly
     - Score is partially working
     - Fixed the acknowledge and create task views

2/21/16 - Met with Roop and have the below changes to implement:
     - Move the menu and name link from the right to the left
     - Have only the name displayed on the task link
     - Clicking the score button should do something
     - Remove picture uploading/display
     - Remove description
     - In add/edit task put name first, followed by frequency, then importance, and category last
     - Clicking on a link will pull up stats such as due date, frequency, time remaining, smartracking, etc. with an edit button at the bottom that leads to the edit task pop-up
     - Add an acknowledge_total variable that keeps track of total acknowledges
     - Move the custom category and pre-made task options off to the menu

2/25/16 - Started to add a star system to show importance: 1 star = least; 5 stars = most

3/17/16 - Scrapped the star system for now
     - Fixed the radio buttons incorrectly moving the screen when selected (the issue was Jquery fadeIn() was moving the screen while Show() would correctly not move focus)
     - Fixed the radio buttons not being set on an edit task pop-up or default task select
     - Moved the score from the body up to the header
     - Still trying to add ajax edit task/add task functionality (having difficulty adding to listview and then enhancing the content)
     - Removed a few variables from the model
     
7/26/16 - Moved Everything to Ubuntu 16.04
     - Changed DB from SQLite to MySQL
     - Installed and configured Apache

8/01/16 - Changed a line in main.js from "localhost:8000/Profile" to "localhost/Profile" to fit with  Apache2
     
8/09/16 - Consolidated the documentation into 'README.txt'