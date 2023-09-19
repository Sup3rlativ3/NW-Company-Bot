# CHANGELOG

## 1.4.5 (2023-09-19)

* Fix for direct private submissions using the /submit failing to resolve the admin group.

## 1.4.4 (2023-09-18)

* Added the public parameter to the /Submit command to allow private submissions.

## v1.4.1 (2023-09-13)

* Added the commands start_war and end_war.
* Added permission restrictions to the commands start_war and end_war.

## v1.3.1 (2023-09-06)

* Updated the regex used for validating youtu.be domain links and associated tests.

## v1.3.0 (2023-09-02)

* Fixed an issue with exporting time entries using the /get_time_range command.
* Added the command /adjust_time_entry
* Changed the database schema to now use the server ID as the partition key. This allows batch updating on the /force_clockout command.

## v1.2.0 (2023-08-25)

* Moved over to the cogs system to organise the code better
* When the Force_Clockout command is used it will now mention all users it is clocking out and how much time the added.

## v1.1.5 (2023-08-21)

* Added permissions restriction to force_clockout. Must be a member of support team role.
* Added permission restriction to get_time_range. Must be a member of support team role.
* Added permission restriction to get_user_time. Must be a member of support team role.
* Changed the logic on clockin to only allow one open entry at a time.
