from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import UserSource
from django.contrib.auth.models import User
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

@login_required
def home(request):
    def getSource(url):
        r = requests.get(url)
        source = BeautifulSoup(r.content, "html.parser")
        return source

    def getTimeValue(timeSlice):
        for i in timeSlice:
            if i.isdigit():
                iIndex = timeSlice.index(i)
                if timeSlice[iIndex+1].isdigit():
                    timeValue = int(timeSlice[iIndex:iIndex+2])
                else:
                    timeValue = i
                return timeValue
                break
        return '0'

    def secondsAgo(timeValue):
        return datetime.now() - timedelta(seconds = timeValue)

    def minutesAgo(timeValue):
        return datetime.now() - timedelta(minutes = timeValue)

    def hoursAgo(timeValue):
        return datetime.now() - timedelta(hours = timeValue)

    def daysAgo(timeValue):
        return datetime.now() - timedelta(days = timeValue)

    def fetchWebtekno(news, items):
        url = "https://www.webtekno.com/haber"
        #get titles
        titles = []
        sourceCode = getSource(url)
        titleData = sourceCode.find_all("span", {"class": "content-timeline--underline"})
        for title in titleData:
            titles.append(str(title.text))
        #get images
        imageLinks = []
        imageLinkData = sourceCode.find_all("img", {"class": "content-timeline__media__image lazy"})
        for imageLink in imageLinkData:
            imageLinks.append(str(imageLink.get("data-original")))
        #get content links
        contentLinks = []
        for title in titles:
            contentLinks.append(str((sourceCode.find("a", {"title": title})).get("href")))
        #get dates
        dates = []
        timeSlices = []
        timeAgo = []
        data = sourceCode.find_all("span", {"class": "content-timeline__detail__time hide"})
        for date in data:
            timeText = str(date.find("time").text)
            timeSlices.append(timeText)
        for timeSlice in timeSlices:
            timeValue = int(getTimeValue(timeSlice))
            if 'sn' in timeSlice:
                dates.append(str(secondsAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' saniye önce')
            elif 'dk' in timeSlice:
                dates.append(str(minutesAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' dakika önce')
            elif 'sa' in timeSlice:
                dates.append(str(hoursAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' saat önce')
            elif 'gün' in timeSlice:
                dates.append(str(daysAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' gün önce')

        for i in range(items):
            dictionary = {
                'title': titles[i],
                'imageLink': imageLinks[i],
                'contentLink': contentLinks[i],
                'datePosted': dates[i],
                'timeAgo': timeAgo[i],
                'source': 'Webtekno'
            }
            news.append(dictionary)

    def fetchDonanimHaber(news, items):
        url = "https://www.donanimhaber.com"
        #get titles
        titles = []
        sourceCode = getSource(url)
        data = sourceCode.find_all("div", {"class": "medya"})
        for title in data:
            titles.append(str(title.find("a").get("data-title")))
        #get images
        imageLinks = []
        for imageLink in data:
            imageLinks.append(str(imageLink.find("img").get("data-src")))
        #get content links
        contentLinks = []
        for contentLink in data:
            contentLinks.append(url+str(contentLink.find("a").get("href")))
        #get dates
        dates = []
        timeSlices = []
        timeAgo = []
        def getTimeSlice(timeText):
            for i in timeText:
                if i.isdigit():
                    firstIndex = timeText.index(i)
                    lastIndex = firstIndex + 6
                    return timeText[firstIndex:lastIndex]
            return '0'
        for date in data:
            timeText = str(date.find("div", {"class": "bilgi"}).text)
            timeSlices.append(getTimeSlice(timeText))
        for timeSlice in timeSlices:
            timeValue = int(getTimeValue(timeSlice))
            if 'sn' in timeSlice:
                dates.append(str(secondsAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' saniye önce')
            elif 'dk' in timeSlice:
                dates.append(str(minutesAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' dakika önce')
            elif 'sa' in timeSlice:
                dates.append(str(hoursAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' saat önce')
            elif 'gün' in timeSlice:
                dates.append(str(daysAgo(timeValue)))
                timeAgo.append(str(timeValue) + ' gün önce')

        for i in range(items):
            dictionary = {
                'title': titles[i],
                'imageLink': imageLinks[i],
                'contentLink': contentLinks[i],
                'datePosted': dates[i],
                'timeAgo': timeAgo[i],
                'source': 'Donanım Haber'
            }
            news.append(dictionary)

    news = []
    items = 10        #limited to number of items that websites provide
    user = request.user
    sources = []
    for source in UserSource.objects.filter(user=user):
        sources.append(str(source.sources))

    #kayit = News.objects.create(title="Captain Marvel ilk haftasında gişe rekorlarını alt üst etti", content="Marvel sinematik evreninin Avengers: Endgame öncesi son filmi olan Captain Marvel, nihayet geçtiğimiz cuma günü sinamaseverlerle buluştu. Özellikle de ABD'de bazı ilginç tartışmalara neden olan filmin gişedeki ilk haftasında nasıl bir performans göstereceği büyük bir merak konusuydu. Bugün yayınlanan ilk rakamlara göre Captain Marvel, gişedeki macerasına beklentilerin de üzerinde inanılmaz hızlı bir giriş yaptı.Box Office Mojo'nun verilerine göre Captain Marvel, vizyondaki ilk haftasında dünya genelinde toplam 455 milyon dolarlık bir gişe hasılatı elde etti. Bu rakamın 153 milyon doları Kuzey Amerika bölgesine ait. Dünyanın geri kalanında ise 302 milyon dolarlık hasılat elde edilmiş.", source_id="2")

    #kayit.save()
    if "Webtekno" in sources:
        fetchWebtekno(news, items)

    if "Donanım Haber" in sources:
        fetchDonanimHaber(news, items)

    def sortByDate(val):
        return val['datePosted']

    news.sort(key = sortByDate, reverse = True)

    context = {
        #'userSources': UserSources.objects.all(),
        'newss': news,
        'sources': sources
    }
    return render(request, 'news/home.html', context)
