from flask import Flask, render_template, request, json
import folium
from folium.plugins import LocateControl
import requests


app = Flask(__name__)


@app.route("/map")
def peta():
    return render_template("petaku.html")


@app.route("/", methods=['POST', 'GET'])
def lic():
    if request.method == "POST":
        lat = request.form['id_lat']
        lon = request.form['id_lng']
        url = "https://nominatim.openstreetmap.org/reverse?format=json&lat="+lat+"&lon="+lon+"&zoom=18&addressdetails=1"
        payload = {}
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.request("GET", url, headers=headers, data=payload)
        adr = json.loads(response.text)['address']
        print(adr)
        notaddr = False
        notfind = True
        house = ''
        city = ''
        streetfull = ''
        street = ''
        licus = list()
        message = ''
        if adr.get('road') != None or adr.get('neighbourhood') != None:
            if adr.get('road') != None:
                streetfull = adr['road']
                street = streetfull.replace('-', '_').replace('проспект ', '').replace('улица ', '').replace('проезд ', '').replace('бульвар', '').replace(' улица', '').replace(' проспект', '').replace(' проезд', '').replace(' бульвар', '').replace('переулок ', '').replace(' переулок', '')
            else:
                streetfull = adr['neighbourhood']
                street = streetfull.replace('микрорайон ','').replace(' микрорайон', '').replace('-й','')
        else:
            notaddr = False
        if adr.get('city') != None or adr.get('town') != None or adr.get('village') != None:
            if adr.get('city') != None:
                city = adr['city']
            if adr.get('town') != None:
                city = adr['town']
            if adr.get('village') != None:
                city = adr['village']
            city = city.replace('-', '_').replace('городской округ ', '').replace('городское поселение ', '').replace('сельское поселение ', '')
        else:
            notaddr = True
        if adr.get('house_number') != None:
            house = adr['house_number']
        else:
            notaddr = True

        if notaddr == False:
            url = "https://data.admhmao.ru/api/data/index.php?id=5594436"
            payload = {}
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.request("GET", url, headers=headers, data=payload)
            resd = json.loads(response.text)['Items']
            print(resd[0])
            for i in range(len(resd)):
                if resd[i]['Cells']['MESTO_NAKHOZHDENIYA_ADRES_OBOSOBLENNOGO_'].find(city) != -1 and \
                    resd[i]['Cells']['MESTO_NAKHOZHDENIYA_ADRES_OBOSOBLENNOGO_'].find(street) != -1 and \
                        (resd[i]['Cells']['MESTO_NAKHOZHDENIYA_ADRES_OBOSOBLENNOGO_'].find(house) != -1 or resd[i]['Cells']['MESTO_NAKHOZHDENIYA_ADRES_OBOSOBLENNOGO_'].find(house.lower()) != -1):
                    if resd[i]['Cells']['SVEDENIYA_O_DEYSTVII_LITSENZII'] == 'действующая' or resd[i]['Cells']['SVEDENIYA_O_DEYSTVII_LITSENZII'] == 'приостановлена':
                        nameorg_tmp = resd[i]['Cells']['POLNOE_I_SOKRASHCHENNOE_NAIMENOVANIE_ORG'].replace("\\",'').replace("Общество с ограниченной ответственностью", 'ООО').replace("Акционерное общество", 'АО')
                        nameorg = nameorg_tmp.replace("\\", '').replace(
                                 "Общество с ограниченной ответственностью", 'ООО').replace(
                                 "Акционерное общество", 'АО').replace('" ', '"').replace('_', '-')
                        if nameorg.find('Сокращенно') != -1:
                            srez = nameorg.find('Сокращенно')
                            nameorg = nameorg[0:srez]
                        innorg = resd[i]['Cells']['INN_ORGANIZATSII_SELSKOKHOZYAYSTVENNOGO_']
                        addrobj_temp = resd[i]['Cells']['MESTO_NAKHOZHDENIYA_ADRES_OBOSOBLENNOGO_']
                        addrobj = addrobj_temp.replace("\\", '').replace('" ', '"').replace(',,', ',').replace(
                                 ',,', ',').replace(',,', ',').replace(',,', ',').replace(',,', ',').replace(',,',',').replace(
                                 '_', '-').replace('&', '').replace('amp;', '').replace('quot;', '')
                        listaddrobj = addrobj.split(',')
                        listaddrobj.pop(0)
                        listaddrobj.pop(0)
                        listaddrobj[0] = listaddrobj[0].replace(' Город', '').replace(' г', '').replace('Район', 'район')
                        addrobj = ', '.join(listaddrobj)
                        tiplic = resd[i]['Cells']['SVEDENIYA_O_DEYSTVII_LITSENZII']
                        vidlic = resd[i]['Cells']['VID_LITSENZIRUEMOY_DEYATELNOSTI_ORGANIZA']
                        date_endlic = resd[i]['Cells']['DATA_OKONCHANIYA_DEYSTVIYA_LITSENZII']
                        numlic = resd[i]['Cells']['NOMER_LITSENZII_SOOTVETSTVUYUSHCHIY_NOME']
                        numblanklic = resd[i]['Cells']['NOMER_BLANKA']
                        licus.append({'nameorg': nameorg, 'innorg': innorg, 'tiplic': tiplic, 'numlic': numlic, 'numblanklic': numblanklic, 'date_endlic': date_endlic, 'vidlic': vidlic, 'addrobj': addrobj})
                        notfind = False
                    notfind = False

        return render_template("licres.html", house=house, city=city, street=streetfull, licus=licus, notaddr=notaddr, notfind=notfind)
    else:
        lat = 61.253951181742984
        lon = 73.39638359095748
        print('else')
        peta = folium.Map(location = [lat, lon], zoom_start= 12)
        LocateControl(auto_start=True).add_to(peta)
        peta.add_child(folium.LatLngPopup())
        peta.save("templates/petaku.html")
        return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
