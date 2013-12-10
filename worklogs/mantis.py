import urllib2
import urllib
from ntlm import HTTPNtlmAuthHandler

import time
import Cookie
import re

from django.conf import settings


def clean_url(url, encoding):
    if isinstance(url, type("")):
        url = url.decode(encoding, "replace")
    url = url.strip()
    return urllib.quote(url.encode(encoding), "!*'();:@&=+$,/?%#[]~")


def clean_refresh_url(url):
    if ((url.startswith('"') and url.endswith('"')) or
            (url.startswith("'") and url.endswith("'"))):
        url = url[1:-1]
    return clean_url(url, "latin-1")


def parse_refresh_header(refresh):
    ii = refresh.find(";")
    if ii != -1:
        pause, newurl_spec = float(refresh[:ii]), refresh[ii + 1:]
        jj = newurl_spec.find("=")
        key = None
        if jj != -1:
            key, newurl = newurl_spec[:jj], newurl_spec[jj + 1:]
            newurl = clean_refresh_url(newurl)
        if key is None or key.strip().lower() != "url":
            raise ValueError()
    else:
        pause, newurl = float(refresh), None
    return pause, newurl


class HTTPRefreshProcessor(urllib2.BaseHandler):
    handler_order = 1000

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()

        if code == 200 and "refresh" in hdrs:
            refresh = hdrs.getheaders("refresh")[0]
            try:
                pause, newurl = parse_refresh_header(refresh)
            except ValueError:
                return response

            if newurl is None:
                newurl = response.geturl()
            time.sleep(pause)
            hdrs["location"] = newurl
            response = self.parent.error(
                "http", request, response,
                "refresh", msg, hdrs)
        return response

    https_response = http_response

user = settings.NTLM_USER
password = settings.NTLM_PASSWORD
base_uri = settings.NTLM_BASE_URI
passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
passman.add_password(None, base_uri, user, password)
auth_NTLM = HTTPNtlmAuthHandler.HTTPNtlmAuthHandler(passman)
opener = urllib2.build_opener(auth_NTLM)
urllib2.install_opener(opener)


def _rozlicz(worklog):
    if worklog.active:
        return 'Nie moge rozliczyc aktywnego loga'

    # cookies chcialem zeby byly globalnie, ale wtedy mantis nie chce logowac przy wchodzeniu  na drugi ticket :/
    C = Cookie.SimpleCookie()
    url = worklog.task.bugtracker_url()

    def _request(url):
        url = url.replace(' ', '%20')
        request = urllib2.Request(url)
        request.add_header('Cookie', C.output(header=""))
        response = urllib2.urlopen(request)
        if 'set-cookie' in response.headers:
            C.load(response.headers.getheader('set-cookie'))
        if 'refresh' in response.headers:
            url = parse_refresh_header(
                response.headers.getheader('refresh'))[1]
            return _request(url)
        else:
            return response

    response = _request(url)
    content = response.read()

    pattern = re.compile(r"onClick=" + r'"' + r"window.open\('(http:\/\/.*)','oknoRozliczenia','.*<b>Rozlicz")
    url = pattern.search(content).groups()[0].replace("&amp;", "&")

    response = _request(url)

    from ClientForm import ParseResponse
    forms = ParseResponse(response, backwards_compat=False)
    form = forms[0]

    seconds = worklog.duration
    hours = seconds / 3600
    minutes = (seconds / 60 % 60) + 1

    form['CzasPracyMin'] = str(minutes)
    form['CzasPracyMin-input'] = str(minutes)
    form['CzasPracyGodz'] = str(hours)
    form['OpisCzynnosci'] = """Prace programistyczne.
{0} - {1}""".format(worklog.start, worklog.end)

    request = form.click()
    request.add_header('Cookie', C.output(header=""))
    response = urllib2.urlopen(request)
    content = response.read()

    if response.code == 200:
        worklog.accounted = True
        worklog.save()
        return None
    else:
        return 'Odpowiedz na posta to %i.' % response.code


from .models import BugTracker, Task, Project
from django.contrib.auth.models import User


def get_mantis_page(mantis_id):
    url = "http://intranet.grupazpr.pl/apps/mantis/view.php?id={0}".format(mantis_id)
    return get_intranet_page(url)


def get_intranet_page(url):
    return get_intranet_response(url).read()


def get_intranet_response(url, cookie=None):
    # cookies chcialem zeby byly globalnie, ale wtedy mantis nie chce logowac przy wchodzeniu  na drugi ticket :/
    if cookie is None:
        C = Cookie.SimpleCookie()
    else:
        C = cookie

    def _request(url):
        url = url.replace(' ', '%20')
        request = urllib2.Request(url)
        request.add_header('Cookie', C.output(header=""))
        response = urllib2.urlopen(request)
        if 'set-cookie' in response.headers:
            C.load(response.headers.getheader('set-cookie'))
        if 'refresh' in response.headers:
            url = parse_refresh_header(
                response.headers.getheader('refresh'))[1]
            return _request(url)
        else:
            return response

    response = _request(url)
    return response


from lxml import html


def get_mantis_ticket(mantis_id):
    content = get_mantis_page(mantis_id)
    root = html.fromstring(content)

    xpaths = {
        'project_name': 'body/table[3]/tr[3]/td[2]',
        'client': 'body/table[3]/tr[5]/td[2]',
        'description': 'body/table[3]/tr[12]/td[2]',
    }
    ret = {}

    for key, xpath in xpaths.items():
        try:
            ret[key] = root.find(xpath).text
        except AttributeError:
            ret[key] = None

    return ret


def make_mantis_task(mantis_id):
    bugtracker = BugTracker.objects.get(name="mantis")
    ticket = get_mantis_ticket(mantis_id)
    task = Task()
    task.description = ticket.get('description').strip().lstrip('0').lstrip(str(mantis_id)).lstrip(':').lstrip()
    task.project, created = Project.objects.get_or_create(name=ticket.get('project_name'))
    task.client = get_client_object(ticket.get('client'))
    task.user = User.objects.get(username="rselewonko")
    task.bugtracker = bugtracker
    task.bugtracker_object_id = mantis_id
    task.save()
    return task


def get_user_data(login):
    url = r"http://intranet.grupazpr.pl/apps/KsiazkaTelefoniczna/Uzytkownicy"
    cookie = Cookie.SimpleCookie()
    response = get_intranet_response(url, cookie)

    from ClientForm import ParseResponse

    forms = ParseResponse(response, backwards_compat=False)

    form = forms[0]
    form['Login'] = login

    request = form.click()
    request.add_header('Cookie', cookie.output(header=""))
    response = urllib2.urlopen(request)
    content = unicode(response.read(), 'utf-8')

    if not response.code == 200:
        raise Exception('lipa: %i.' % response.code)

    root = html.fromstring(content)

    xpaths = {
        'name': 'body/div[1]/div[2]/div[1]/div/div/div/div/div/table/tr[2]/td[1]',
        'login': 'body/div[1]/div[2]/div[1]/div/div/div/div/div/table/tr[2]/td[2]',
        'position': 'body/div[1]/div[2]/div[1]/div/div/div/div/div/table/tr[2]/td[3]',
        'phone': 'body/div[1]/div[2]/div[1]/div/div/div/div/div/table/tr[2]/td[4]',
    }
    ret = {}

    for key, xpath in xpaths.items():
        try:
            ret[key] = root.find(xpath).text
        except AttributeError:
            ret[key] = None

    # wybieranie maila i jida
    xpath = 'body/div[1]/div[2]/div[1]/div/div/div/div/div/table/tr[2]/td[5]/a'
    for href in map(lambda e: e.get('href'), root.findall(xpath)):
        if href.startswith('mailto:'):
            ret['email'] = href.lstrip('mailto:')
        if href.startswith('xmpp:'):
            ret['xmpp'] = href.lstrip('xmpp:')

    return ret


def get_client_object(login):
    from .models import Client
    client, created = Client.objects.get_or_create(login=login)
    if created:
        data = get_user_data(login)
        client.name = data.get('name')
        client.position = data.get('position')
        client.phone = data.get('phone')
        client.email = data.get('email')
        client.xmpp = data.get('xmpp')
        client.save()
    return client
