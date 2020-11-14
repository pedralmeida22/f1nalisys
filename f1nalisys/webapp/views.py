import xmltodict, requests

from BaseXClient import BaseXClient
from django.shortcuts import render
from lxml import etree

session = BaseXClient.Session('localhost', 1984, 'admin', 'admin')


# Create your views here.


def teams2(request):
    query = "xquery <root>{for $c in collection('f1')//Constructor return <elem> {$c/Name} {$c/Nationality} </elem>}</root> "
    # dá erro: nao encontra o local. Não sei em que pasta guardar os queries com as funçoes para chamar aqui
    # query = "xquery <root>{ local:get-constructors() }</root>"
    exe = session.execute(query)

    output = xmltodict.parse(exe)
    print("out: ", output)

    info = dict()
    for t in output['root']['elem']:
        info[t['Name']] = t['Nationality']

    tparams = {
        'title': 'teams',
        'teams': info,
    }

    return render(request, 'teams.html', tparams)


# teams com xslt
def teams(request, ano="2020"):
    query = "xquery for $c in collection('f1')//ConstructorTable where $c/@season=" + str(ano) + " return $c"
    exe = session.execute(query)
    print(exe)
    root = etree.fromstring(exe)
    print("root:", root)

    xsl_file = etree.parse('webapp/xsl_files/teams.xsl')
    tranform = etree.XSLT(xsl_file)
    html = tranform(root)

    tparams = {
        'urll': "/teams",
        'ano': ano,
        'title': 'teams',
        'html': html
    }
    return render(request, 'teams.html', tparams)


def tracks(request):
    query = "xquery <root>{for $c in collection('f1')//Circuit return <elem> {$c/CircuitName} {$c/Location} </elem>}</root> "
    # dá erro: nao encontra o local. Não sei em que pasta guardar os queries com as funçoes para chamar aqui
    # query = "xquery <root>{ local:get-constructors() }</root>"
    exe = session.execute(query)

    output = xmltodict.parse(exe)
    print("out: ", output)

    info = dict()
    for t in output['root']['elem']:
        info[t['CircuitName']] = (
        t['Location']['Locality'], t['Location']['Country'], getImagem(t['Location']['Country']))

    print(info)
    tparams = {
        'urll': "/tracks",
        'title': 'Tracks',
        'tracklist': info,
    }
    return render(request, 'tracks.html', tparams)


def standings2(request, ano):
    queryRace = "xquery <root>{for $c in collection('f1')//RaceTable return <elem> {$c/RaceName} {$c/Circuit/CircuitName} {$c/Location/Country}  </elem>}</root> "
    queryResults = "xquery <root>{for $c in collection('f1')//Driver return <elem> {$c/Result/Driver} {$c/Circuit/CircuitName} {$c/Location/Country}  </elem>}</root> "

    exe = session.execute(queryRace)

    output = xmltodict.parse(exe)
    print("out: ", output)

    info = dict()
    for t in output['root']['elem']:
        info[t['CircuitName']] = (
        t['Location']['Locality'], t['Location']['Country'], getImagem(t['Location']['Country']))

    print(info)
    tparams = {
        'title': 'Tracks',
        'tracklist': info,
    }
    return render(request, 'tracks.html', tparams)


def drivers_standings(request, ano):
    query = "xquery for $c in collection('f1')//StandingsTable where $c/@season=" + str(ano) + " where $c//child::DriverStanding return $c"
    exe = session.execute(query)
    root = etree.fromstring(exe)

    xsl_file = etree.parse("webapp/xsl_files/drivers-standings.xsl")
    tranform = etree.XSLT(xsl_file)
    html = tranform(root)

    tparams = {
        'title': 'Drivers Standings',
        'standings': html,
    }
    return render(request, 'drivers_standings.html', tparams)


def constructors_standings(request, ano):
    query = "xquery for $c in collection('f1')//StandingsTable where $c/@season=" + str(ano) + " where $c//child::ConstructorStanding return $c"
    exe = session.execute(query)
    root = etree.fromstring(exe)

    xsl_file = etree.parse("webapp/xsl_files/constructors-standings.xsl")
    tranform = etree.XSLT(xsl_file)
    html = tranform(root)

    tparams = {
        'title': 'Constructors Standings',
        'standings': html,
    }
    return render(request, 'constructors_standings.html', tparams)


def drivers(request, ano="2020"):
    query = "xquery for $p in collection('f1')//DriverTable where $p/@season=" + str(ano) + " return $p"
    exe = session.execute(query)
    root = etree.fromstring(exe)

    xsl_file = etree.parse("webapp/xsl_files/drivers.xsl")
    transform = etree.XSLT(xsl_file)
    drivers_html = transform(root)


    tparams = {
        'urll': "/drivers",
        'ano': ano,
        'title': 'drivers',
        'drivers_html': drivers_html,
    }

    return render(request, 'drivers.html', tparams)


def about(request):
    return render(request, 'about.html', {'title': 'About'})


def ano(request, ano="2020"):
    # races
    races_query = "xquery <Races>{ for $a in collection('f1')//RaceTable where $a/@season = " + str(ano) + " return $a/Race }</Races>"
    exe = session.execute(races_query)
    root = etree.fromstring(exe)

    xsl_file = etree.parse('webapp/xsl_files/races_overview.xsl')
    tranform = etree.XSLT(xsl_file)
    races_snippet = tranform(root)

    # top3 drivers
    top3drivers_query = "xquery <root>{ for $c in collection('f1')//StandingsTable where $c/@season=" + str(
        ano) + " return $c//DriverStanding[position() < 4] }</root>"
    exe_drivers = session.execute(top3drivers_query)
    root_drivers = etree.fromstring(exe_drivers)

    xsl_file_drivers = etree.parse('webapp/xsl_files/top3drivers.xsl')
    tranform_drivers = etree.XSLT(xsl_file_drivers)
    drivers_snippet = tranform_drivers(root_drivers)

    # top3 teams
    top3teams_query = "xquery <root>{ for $c in collection('f1')//StandingsTable where $c/@season=" + str(
        ano) + " return $c//ConstructorStanding[position() < 4] }</root>"
    exe_teams = session.execute(top3teams_query)
    root_teams = etree.fromstring(exe_teams)

    xsl_file_teams = etree.parse('webapp/xsl_files/top3teams.xsl')
    tranform_teams = etree.XSLT(xsl_file_teams)
    teams_snippet = tranform_teams(root_teams)

    tparams = {
        'urll': "/season",
        'ano': ano,
        'drivers_standings_url': "/season/" + str(ano),
        'constructors_standings_url': "/season/" + str(ano),
        'title': 'overview',
        'races_snippet': races_snippet,
        'drivers_snippet': drivers_snippet,
        'teams_snippet': teams_snippet,
    }
    return render(request, 'ano.html', tparams)


def index(request):
    # #Não esquecer de ligar o BaseXServer e o BaseXClient antes de correr estas funções, senão não liga à BD
    # try:
    #     session.execute("open for2")
    #     print(session.info())
    # except IOError:
    #     session.execute("create db for2")
    #     print(session.info()+"AHASUOD")

    # session.execute("open for2")
    # print(session.info())

    # #add document
    # root = etree.parse("webapp/Corridas/2018/2018_drivers.xml")
    # #print(root)
    #
    # session.add("Cons2018", etree.tostring(root).decode("iso-8859-1"))
    # #print(session.info())
    # #session.close()
    #
    # #session.execute("open cTeste (basex/data)")
    # input = "xquery <root>{ for $a in collection('for2') return <elem> {$a} </elem>} </root>"
    # query = session.execute(input)
    # #
    # #root = etree.parse("app/cursos.xml")
    # #info = dict()
    # res = xmltodict.parse(query)
    # print(res)
    session.execute("open f1")
    try:
        session.execute("delete RSS")
        print(session.info())
        # add document

        # GERAR

        exec(open('webapp/Corridas/rssGetter.py').read())

        root = etree.parse("rssf1.xml")
        # print(root)

        session.add("RSS", etree.tostring(root).decode("utf-8"))
        # print(session.info())
    except IOError:
        print(session.info() + "\n ERRO MPTS")

    input = "xquery <root>{ for $i in collection('f1')//item[position()<6] return <elem> {$i/title} {$i/pubDate} {$i/author} {$i/link} {$i/description} </elem>} </root>"
    query = session.execute(input)

    info = dict()
    capa = dict()
    res = xmltodict.parse(query)

    i = 1;
    for c in res["root"]["elem"]:
        c["description"] = c["description"].replace("<p>", "")
        c["description"] = c["description"].replace("</p>", "")
        if i == 1:
            capa[i] = (c["title"], c["pubDate"], c["author"], c["link"], c["description"])
        else:
            info[i] = (c["title"], c["pubDate"], c["author"], c["link"], c["description"])
        # print(info[i])
        i += 1

    tparams = {
        'news': info,
        'first_news': capa
    }

    return render(request, 'index.html', tparams)


def getImagem(pais):
    path = "/static/img/"
    if pais == "Italy":
        path = path + "italy.png"
    elif pais == "Spain":
        path = path + "spain.png"
    elif pais == "UK":
        path = path + "uk.png"
    elif pais == "Australia":
        path = path + "australia.png"
    elif pais == "USA":
        path = path + "usa.png"
    elif pais == "Bahrain":
        path = path + "bahrain.png"
    elif pais == "Azerbaijan":
        path = path + "azerbeijan.png"
    elif pais == "Germany":
        path = path + "germany.png"
    elif pais == "Hungary":
        path = path + "hungary.png"
    elif pais == "Brazil":
        path = path + "brazil.png"
    elif pais == "Turkey":
        path = path + "turkey.png"
    elif pais == "Singapore":
        path = path + "singapore.png"
    elif pais == "Monaco":
        path = path + "monaco.png"
    elif pais == "Austria":
        path = path + "austria.png"
    elif pais == "France":
        path = path + "france.png"
    elif pais == "Mexico":
        path = path + "mexico.png"
    elif pais == "China":
        path = path + "china.png"
    elif pais == "Russia":
        path = path + "russia.png"
    elif pais == "Belgium":
        path = path + "belgium.png"
    elif pais == "Japan":
        path = path + "japan.png"
    elif pais == "Canada":
        path = path + "canada.png"
    elif pais == "UAE":
        path = path + "abudhabi.png"
    elif pais == "Portugal":
        path = path + "portugal.png"

    return path

def getFlag(pais):
    path = "/static/img/"
    if pais == "Dutch" or pais == "Netherlands":
        path = path + "nethflag.png"
    elif pais == "British" or pais == "UK":
        path = path + "ukflag.png"
    elif pais == "Finnish" or pais == "Finland":
        path = path + "finflag.png"
    elif pais == "Deutsch" or pais == "Germany" or pais == "German":
        path = path + "gerflag.png"
    elif pais == "French" or pais == "France":
        path = path + "fraflag.png"
