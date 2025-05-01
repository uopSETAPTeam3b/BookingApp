# BookingApp

 - up2194051 - forester302

 - up2195798 - JoshNichols1

 - up2211837 - Theskyguard4

 - up2194801 - Ziyanasto

 - up2245678 - willdavies830

 - up2233199 -johanja04

## How to commit from CLI
- Switch to feature branch
  - if branch exists `git checkout <BRANCH_NAME>`
  - if branch does not exists `git checkout -b <BRANCH_NAME>`
- Stage changes
  - Stage all `git stage .` or `git add .`
- Commit changes
  - `git commit -m "<COMMIT_MESSAGE>"`
- Push changes
  - `git push origin <BRANCH_NAME>`
- Make a pull request from github
  - go to https://github.com/uopSETAPTeam3b
  - find branch
  - create pull request 


## How To Setup Notifications
- Create a .env file in your main directory
- add these lines

smtp_username = ""
smtp_password = ""

- ask lewis for the username and password (this cannot be saved on the github)

- now when the server tries to send a notification, it will use the google smtp api to send using the account i created.

## Accounts
- We all have an account and 3 bookings made for testing
  - Log in using your uni email
  - Passwords = welcome1234


