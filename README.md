# scrapingkeenai

Well,  I am a little late for this.  Keenai is closing its doors.  I am wrapping this up as an example of selfware

I set this project up to learn a little about scrapy.  I never really liked the application that Keenai provides for windows and they don't provide anything for Linux.  So I put this together as a way to learn.  Along the way, I also learned that this would be much easier if I would have just pulled the data directly from the api website from Keenai, but it isn't documented anywhere. By the time I figured out that it would have been eaiser, I was far enough down this path to continue

virtualenv -p python3 scrapingkeenai/ 
cd scrapingkeenai
source bin/activate
pip install scrapy
pip install ipython


scrapy crawl keenaiPipeline --loglevel=INFO -s USER_PASSWORD="your account info" -s USER_NAME="your account info"
