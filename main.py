import csv
import glob


class Rikor:
    uuid = ""
    uuid_easy = ""
    sn = ""
    sn_short = ""
    old_sn = ""
    old_uuid = ""
    order = ""
    disk = []

    def __init__(self, u, s):
        self.sn = s
        self.uuid_easy = u
        self.sn_short = self.__strip_sn()
        self.uuid = self.__strip_uuid()

    def __init__(self, u, s, ou, os, d):
        self.sn = s
        self.uuid_easy = u
        self.sn_short = self.__strip_sn()
        self.uuid = self.__strip_uuid()
        self.old_sn = os
        self.old_uuid = ou
        self.disk = d

    def __strip_sn(self):
        if self.sn.startswith("RIME-1554-000-"):
            return self.sn[len("RIME-1554-000-"):]
        if self.sn.startswith("RITI-1554."):
            return self.sn[len("RITI-1554."):]
        return ""

    def __strip_uuid(self):
        return self.uuid_easy[0:8] + "-" + self.uuid_easy[8:12] + "-" + self.uuid_easy[12:16] +\
               "-" + self.uuid_easy[16:20] + "-" + self.uuid_easy[20:]

    def get_order_from_path(self, path):
        path = path.split("\\")
        self.order = path[len(path) - 1].strip(".log")


def element_parser(el):
    if len(el) <= 1:
        return
    lst = el.split('\n')
    uuid = ""
    sn = ""
    old_sn = ""
    old_uuid = ""
    disk = []
    for elem in lst:
        if elem.startswith("Диск") and elem.endswith("очищен!"):
            disk.append(elem)
        if elem.startswith("(/SU)System UUID             R"):
            uuid = elem[len("(/SU)System UUID             R    Done   "):].strip(' ').strip('"').strip('h')
        if elem.startswith("(/SU)System UUID             R") and uuid != "":
            test = elem[len("(/SU)System UUID             R    Done   "):].strip(' ').strip('"')
            if (uuid.upper() + "h") != test:
                print(f"Ошибка: {uuid} -- {test}")
            if old_uuid == "":
                old_uuid = uuid
        if elem.startswith("(/SS)System Serial number"):
            if sn != elem[len("(/SS)System Serial number    R    Done   "):].strip('"'):
                sn = elem[len("(/SS)System Serial number    R    Done   "):].strip('"')
            if old_sn == "":
                old_sn = sn

    return Rikor(uuid, sn, old_uuid, old_sn, disk)


if __name__ == '__main__':
    rikors = set()
    diskparts = 0
    log_files = glob.glob('M:\\LOGS\\Rikor\\*.log')
    for lf in log_files:
        with open(lf, 'r', encoding='utf-8') as file:
            rik = element_parser(file.read())
            rik.get_order_from_path(lf)
            rikors.add(rik)

    with open('D:\\answer.csv', 'w', encoding='cp1251', newline='') as f:
        writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_NONNUMERIC)
        header = ['наш серийник', 'серийник до прошивки', 'серийный номер ноутбука', 'краткий серийник', 'UUID',
                  'UUID слитно', 'старый UUID']
        # write the header
        writer.writerow(header)
        # write the data
        for rikor in rikors:
            writer.writerow([rikor.order, rikor.old_sn, rikor.sn, rikor.sn_short, rikor.uuid, rikor.uuid_easy,
                             rikor.old_uuid])
            if len(rikor.disk) > 0:
                print(f"{rikor.disk} в компе {rikor.order}")
                diskparts += 1
    print(f"Готово! Выгружено {len(rikors)} единиц")
    print(f"Отдискпартчено {diskparts} дисков")
