# CHANGELOG

## 1.4.7 (2023-09-22)

* Changed the default value for the ```Public``` parameter of the ```/Submit``` command to ```True```.
* Adjusted the regex for detecting twitch.tv links to allow for a timestamp.

## 1.4.6 (2023-09-19)

* Fix for direct private submissions using the ```/Submit``` failing to resolve the admin group.
* Adjusted respawn time to be more accurate in the ```/Start_War``` command.
* Fix for timeout when submitting a private vod using the ```/Submit``` command.
* Fix for timeout when using the command ```/Force_Clockout``` and there were a lot of users still clocked in.

## 1.4.4 (2023-09-18)

* Added the public parameter to the ```/Submit``` command to allow private submissions.

## v1.4.1 (2023-09-13)

* Added the commands ```/Start_War``` and /End_War.
* Added permission restrictions to the commands ```/Start_War``` and ```/End_War```.

## v1.3.1 (2023-09-06)

* Updated the regex used for validating youtu.be domain links and associated tests.

## v1.3.0 (2023-09-02)

* Fixed an issue with exporting time entries using the ```/Get_TRime_Range``` command.
* Added the command ```/Adjust_Time_Entry```
* Changed the database schema to now use the server ID as the partition key. This allows batch updating on the ```/Force_Clockout``` command.

## v1.2.0 (2023-08-25)

* Moved over to the cogs system to organise the code better
* When the ```/Force_Clockout``` command is used it will now mention all users it is clocking out and how much time the added.

## v1.1.5 (2023-08-21)

* Added permissions restriction to ```/Force_Clockout```. Must be a member of support team role.
* Added permission restriction to ```/Get_Time_Range```. Must be a member of support team role.
* Added permission restriction to ```/Get_User_Time```. Must be a member of support team role.
* Changed the logic on clockin to only allow one open entry at a time.
