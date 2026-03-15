## Acquisition

---

This file will change and be fixed later. I would rather not focus on writing readmes for now

This section of the code will not be covered in as much depth as the other sections as it does not directly affect the research.

Please ensure that you have followed the prerequisites described in the [src directory readme](https://github.com/Implycitt/AveResearch2026/blob/main/src/README.md) to be able to run this part of the code.

### environment variables

---

To run the crawler locally, ensure that the email and password in the .env is valid for an iNaturalist account and is declared in a .env in the in/ folder.\
For an example see the example.env.

```.env
EMAIL="yourInaturalistEmailHere"
PASSWORD="yourInaturalistPasswordHere"
```

If you do not plan on running the crawler to message others on the site yourself, then you do not have to worry about adding environment variables as the rest of the code does not depend on any secrets, passwords, or sensitive information.

## Files

---

### crawler.py

---

crawler functions that grabs users from the people page, grabs following and followers for each user and adds them to a queue.

### driver.py

---

Driver class implementing selenium webdriver.

### messenger.py

---

Uses the Driver class to login to iNaturalist platform and message users.