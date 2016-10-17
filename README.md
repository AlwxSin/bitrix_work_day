# bitrix_work_day

installation requires web driver:
chrome, firefox or phantom

First need to prepare secret file
```
# secret.py
LOGIN = 'bitrix_user@bitrix24.example
PASSWORD = 'very_secret_password'
MAIN_URL = 'bitrix24.example'
```

#### To run in headless mode
```
python main.py open|close
```

#### To run in browser mode
```
python main.py open|close browser
```
